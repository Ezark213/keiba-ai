# リファクタリング後のMLトレーナー - SOLID原則準拠
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss
from typing import Tuple, Dict, Any, Optional, List
from loguru import logger
import joblib
from pathlib import Path

# 新しいインターフェースとクラスをインポート
from ..interfaces.trainer_interface import TrainerInterface, PredictionModel, DataProcessor
from ..feature_engineering import FeatureEngineRegistry, FeatureProcessor


class LightGBMModel(PredictionModel):
    """LightGBMモデルラッパー (Liskov Substitution Principle)"""
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.model = None
        self.params = params or {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        self._feature_importance = {}
        self._is_trained = False
    
    def predict_probability(self, features: pd.DataFrame) -> np.ndarray:
        """勝率を予測"""
        if not self.is_trained:
            raise ValueError("Model is not trained yet")
        
        return self.model.predict(features, num_iteration=self.model.best_iteration)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """特徴量重要度を取得"""
        if not self.is_trained:
            return {}
        
        if not self._feature_importance:
            importance = self.model.feature_importance(importance_type='gain')
            feature_names = self.model.feature_name()
            self._feature_importance = dict(zip(feature_names, importance))
        
        return self._feature_importance
    
    def save_model(self, path: Path) -> bool:
        """モデルを保存"""
        try:
            if self.model:
                self.model.save_model(str(path))
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, path: Path) -> bool:
        """モデルを読み込み"""
        try:
            self.model = lgb.Booster(model_file=str(path))
            self._is_trained = True
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    @property
    def is_trained(self) -> bool:
        return self._is_trained
    
    @property
    def model_type(self) -> str:
        return "LightGBM"
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> None:
        """モデルを学習"""
        train_data = lgb.Dataset(X_train, label=y_train)
        
        valid_sets = [train_data]
        if X_val is not None and y_val is not None:
            valid_data = lgb.Dataset(X_val, label=y_val)
            valid_sets.append(valid_data)
        
        self.model = lgb.train(
            self.params,
            train_data,
            valid_sets=valid_sets,
            num_boost_round=1000,
            callbacks=[lgb.early_stopping(100), lgb.log_evaluation(0)]
        )
        
        self._is_trained = True


class HorseDataProcessor(DataProcessor):
    """競馬データ専用のデータプロセッサ (Single Responsibility)"""
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """データクリーニング"""
        # 外れ値検出と処理
        cleaned_data = data.copy()
        
        # 数値列の外れ値処理
        numeric_columns = cleaned_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['is_winner', 'horse_num', 'race_id']:
                Q1 = cleaned_data[col].quantile(0.25)
                Q3 = cleaned_data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # 外れ値をクリップ
                cleaned_data[col] = cleaned_data[col].clip(lower_bound, upper_bound)
        
        return cleaned_data
    
    def handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """欠損値処理"""
        filled_data = data.copy()
        
        # 数値特徴量は中央値で補完
        numeric_columns = filled_data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['is_winner', 'horse_num']:
                filled_data[col] = filled_data[col].fillna(filled_data[col].median())
        
        # カテゴリ特徴量は最頻値で補完
        categorical_columns = filled_data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            mode_value = filled_data[col].mode()
            fill_value = mode_value[0] if not mode_value.empty else 'unknown'
            filled_data[col] = filled_data[col].fillna(fill_value)
        
        return filled_data
    
    def encode_categorical(self, data: pd.DataFrame) -> pd.DataFrame:
        """カテゴリカル変数のエンコーディング"""
        encoded_data = data.copy()
        
        # 性別エンコーディング
        if 'sex' in encoded_data.columns:
            sex_mapping = {'牡': 0, '牝': 1, 'セ': 2}
            encoded_data['sex_encoded'] = encoded_data['sex'].map(sex_mapping).fillna(0)
        
        # 馬場状態エンコーディング
        if 'track_condition' in encoded_data.columns:
            condition_mapping = {'良': 0, '稍重': 1, '重': 2, '不良': 3}
            encoded_data['track_condition_encoded'] = encoded_data['track_condition'].map(condition_mapping).fillna(0)
        
        return encoded_data
    
    def split_data(self, data: pd.DataFrame, target: pd.Series, 
                  test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """データの分割"""
        return train_test_split(data, target, test_size=test_size, 
                               stratify=target, random_state=42)


class RefactoredMLTrainer(TrainerInterface):
    """リファクタリング後のMLトレーナー (SOLID原則準拠)"""
    
    def __init__(self, 
                 feature_registry: FeatureEngineRegistry,
                 data_processor: DataProcessor,
                 model_params: Optional[Dict[str, Any]] = None):
        """
        依存性注入によるコンストラクタ (Dependency Inversion Principle)
        """
        self.feature_registry = feature_registry
        self.data_processor = data_processor
        self.feature_processor = FeatureProcessor(feature_registry)
        self.model_params = model_params
        self._training_metrics = {}
    
    def train_model(self, training_data: pd.DataFrame, target: pd.Series) -> PredictionModel:
        """モデルを学習 (Single Responsibility)"""
        logger.info(f"モデル学習開始: {len(training_data)}サンプル")
        
        # データ前処理
        processed_data = self._preprocess_data(training_data)
        
        # 学習・検証データ分割
        X_train, X_val, y_train, y_val = self.data_processor.split_data(
            processed_data, target, test_size=0.2
        )
        
        # モデル作成・学習
        model = LightGBMModel(self.model_params)
        model.train(X_train, y_train, X_val, y_val)
        
        # 学習メトリクス記録
        self._training_metrics = {
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'features_count': len(X_train.columns),
            'feature_names': list(X_train.columns)
        }
        
        logger.info("モデル学習完了")
        return model
    
    def evaluate_model(self, model: PredictionModel, 
                      test_data: pd.DataFrame, test_target: pd.Series) -> Dict[str, float]:
        """モデルを評価"""
        processed_data = self._preprocess_data(test_data)
        predictions = model.predict_probability(processed_data)
        
        binary_predictions = (predictions > 0.5).astype(int)
        
        return {
            'accuracy': accuracy_score(test_target, binary_predictions),
            'auc': roc_auc_score(test_target, predictions),
            'log_loss': log_loss(test_target, predictions)
        }
    
    def get_training_metrics(self) -> Dict[str, Any]:
        """学習時のメトリクスを取得"""
        return self._training_metrics.copy()
    
    def optimize_hyperparameters(self, training_data: pd.DataFrame, 
                                target: pd.Series) -> Dict[str, Any]:
        """ハイパーパラメータ最適化（簡易版）"""
        # 実装例：グリッドサーチの簡易版
        param_grid = {
            'num_leaves': [15, 31, 63],
            'learning_rate': [0.01, 0.05, 0.1],
            'feature_fraction': [0.8, 0.9, 1.0]
        }
        
        best_score = 0
        best_params = {}
        
        processed_data = self._preprocess_data(training_data)
        
        for num_leaves in param_grid['num_leaves']:
            for lr in param_grid['learning_rate']:
                for ff in param_grid['feature_fraction']:
                    params = self.model_params.copy() if self.model_params else {}
                    params.update({
                        'num_leaves': num_leaves,
                        'learning_rate': lr,
                        'feature_fraction': ff
                    })
                    
                    # 3-fold CV で評価
                    scores = []
                    kfold = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
                    
                    for train_idx, val_idx in kfold.split(processed_data, target):
                        X_train, X_val = processed_data.iloc[train_idx], processed_data.iloc[val_idx]
                        y_train, y_val = target.iloc[train_idx], target.iloc[val_idx]
                        
                        model = LightGBMModel(params)
                        model.train(X_train, y_train, X_val, y_val)
                        
                        predictions = model.predict_probability(X_val)
                        score = roc_auc_score(y_val, predictions)
                        scores.append(score)
                    
                    avg_score = np.mean(scores)
                    if avg_score > best_score:
                        best_score = avg_score
                        best_params = params.copy()
        
        return {
            'best_params': best_params,
            'best_score': best_score
        }
    
    @property
    def supported_algorithms(self) -> List[str]:
        """サポートするアルゴリズムのリスト"""
        return ["LightGBM"]
    
    def prepare_features_from_raw_data(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """生データから特徴量を準備（新しい特徴量エンジニアリングシステムを使用）"""
        all_samples = []
        
        for race in raw_data.get('races', []):
            race_features = self._extract_race_features(race)
            
            for horse in race['horses']:
                # 新しい特徴量エンジニアリングシステムを使用
                features = self.feature_registry.create_all_features(horse, race_features)
                
                # ターゲット（結果がある場合）
                if race.get('result'):
                    features['is_winner'] = 1 if horse['horse_num'] == race['result']['winner'] else 0
                else:
                    features['is_winner'] = None
                
                features['race_id'] = race['race_id']
                features['horse_num'] = horse['horse_num']
                
                all_samples.append(features)
        
        df = pd.DataFrame(all_samples)
        logger.info(f"特徴量準備完了: {len(df)}サンプル, {len(df.columns)}特徴量")
        
        return df
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """データ前処理パイプライン"""
        # データクリーニング
        cleaned_data = self.data_processor.clean_data(data)
        
        # 欠損値処理
        filled_data = self.data_processor.handle_missing_values(cleaned_data)
        
        # カテゴリカルエンコーディング
        encoded_data = self.data_processor.encode_categorical(filled_data)
        
        # メタデータ列を除去
        feature_columns = [col for col in encoded_data.columns 
                          if col not in ['is_winner', 'race_id', 'horse_num']]
        
        return encoded_data[feature_columns]
    
    def _extract_race_features(self, race: Dict[str, Any]) -> Dict[str, Any]:
        """レース特徴量抽出"""
        return {
            'distance': race.get('distance', 1600),
            'track': race.get('track', 'turf'),
            'track_condition': race.get('track_condition', 'good'),
            'field_size': len(race.get('horses', [])),
            'class': self._get_race_grade(race.get('race_name', ''))
        }
    
    def _get_race_grade(self, race_name: str) -> int:
        """レースグレード判定"""
        if any(keyword in race_name for keyword in ['G1', 'GⅠ']):
            return 1
        elif any(keyword in race_name for keyword in ['G2', 'GⅡ']):
            return 2
        elif any(keyword in race_name for keyword in ['G3', 'GⅢ']):
            return 3
        elif any(keyword in race_name for keyword in ['ステークス', '記念']):
            return 4
        else:
            return 5