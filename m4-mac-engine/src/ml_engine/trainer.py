"""
機械学習トレーナー
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss
from typing import Tuple, Dict, Any, Optional
from loguru import logger
import joblib

from config import config

class MLTrainer:
    """LightGBMトレーナー"""
    
    def __init__(self):
        self.model = None
        self.feature_importance = {}
        self.feature_columns = config.feature_columns
        
    async def prepare_features(self, raw_data: Dict[str, Any]) -> pd.DataFrame:
        """特徴量準備"""
        all_samples = []
        
        for race in raw_data.get('races', []):
            race_features = self._extract_race_features(race)
            
            for horse in race['horses']:
                # 基本特徴量
                features = {col: horse.get(col, 0) for col in self.feature_columns}
                
                # レース特徴量を追加
                features.update(race_features)
                
                # 相互作用特徴量
                features.update(self._create_interaction_features(horse, race))
                
                # ターゲット（結果がある場合）
                if race.get('result'):
                    features['is_winner'] = 1 if horse['horse_num'] == race['result']['winner'] else 0
                else:
                    features['is_winner'] = None
                
                features['race_id'] = race['race_id']
                features['horse_num'] = horse['horse_num']
                
                all_samples.append(features)
        
        df = pd.DataFrame(all_samples)
        
        # 欠損値処理
        df = self._handle_missing_values(df)
        
        # 特徴量エンコーディング
        df = self._encode_categorical_features(df)
        
        logger.info(f"特徴量準備完了: {len(df)}サンプル, {len(df.columns)}特徴量")
        
        return df
    
    def _extract_race_features(self, race: Dict[str, Any]) -> Dict[str, Any]:
        """レース特徴量抽出"""
        return {
            'race_distance': race.get('distance', 1600),
            'is_turf': 1 if race.get('track') == '芝' else 0,
            'is_heavy': 1 if race.get('track_condition') in ['重', '不良'] else 0,
            'field_size': len(race.get('horses', [])),
            'race_grade': self._get_race_grade(race.get('race_name', ''))
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
    
    def _create_interaction_features(self, horse: Dict[str, Any], race: Dict[str, Any]) -> Dict[str, Any]:
        """相互作用特徴量作成"""
        features = {}
        
        # IDM × 距離適性
        features['idm_distance_interaction'] = (
            horse.get('idm', 50) * horse.get('distance_aptitude', 1.0)
        )
        
        # 騎手 × 調教師シナジー
        features['jockey_trainer_synergy'] = (
            horse.get('jockey_index', 50) * horse.get('trainer_index', 50) / 100
        )
        
        # 馬場適性スコア
        if race.get('track') == '芝':
            track_score = horse.get('track_aptitude', 1.0)
        else:
            track_score = 2.0 - horse.get('track_aptitude', 1.0)
        
        if race.get('track_condition') in ['重', '不良']:
            track_score *= horse.get('heavy_track_aptitude', 1.0)
        
        features['track_score'] = track_score
        
        # 調子指数（各種指数の調和平均）
        indices = [
            horse.get('idm', 50),
            horse.get('pace_index', 50),
            horse.get('rising_index', 50)
        ]
        features['condition_index'] = len(indices) / sum(1/x for x in indices if x > 0)
        
        return features
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """欠損値処理"""
        # 数値特徴量は中央値で補完
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['is_winner', 'horse_num']:
                df[col].fillna(df[col].median(), inplace=True)
        
        # カテゴリ特徴量は最頻値で補完
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown', inplace=True)
        
        return df
    
    def _encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """カテゴリ特徴量エンコーディング"""
        # 性別エンコーディング
        if 'sex' in df.columns:
            sex_mapping = {'牡': 0, '牝': 1, 'セ': 2}
            df['sex_encoded'] = df['sex'].map(sex_mapping).fillna(0)
        
        return df
    
    def check_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """データ品質チェック"""
        return {
            'total_samples': len(df),
            'training_samples': len(df[df['is_winner'].notna()]),
            'missing_ratio': df.isnull().sum().sum() / (df.shape[0] * df.shape[1]),
            'positive_ratio': df['is_winner'].sum() / len(df[df['is_winner'].notna()]) if 'is_winner' in df else None,
            'feature_count': len([col for col in df.columns if col not in ['race_id', 'horse_num', 'is_winner']])
        }
    
    async def train(self, train_data: pd.DataFrame) -> Tuple[Any, Dict[str, float]]:
        """モデル学習"""
        # 学習データのみ抽出
        train_df = train_data[train_data['is_winner'].notna()].copy()
        
        if len(train_df) < 100:
            raise ValueError(
                f"学習データが少なすぎます: {len(train_df)}サンプル\n"
                "本物のJRDBデータが必要です。JRDB認証情報を確認してください。"
            )
        
        # 特徴量とターゲット
        feature_cols = [col for col in train_df.columns 
                       if col not in ['race_id', 'horse_num', 'is_winner']]
        X = train_df[feature_cols]
        y = train_df['is_winner']
        
        # 学習/検証分割
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # LightGBMデータセット作成
        train_dataset = lgb.Dataset(X_train, label=y_train)
        val_dataset = lgb.Dataset(X_val, label=y_val, reference=train_dataset)
        
        # コールバック設定
        callbacks = [
            lgb.early_stopping(stopping_rounds=50),
            lgb.log_evaluation(period=0)
        ]
        
        # 学習実行
        logger.info("LightGBMモデル学習開始...")
        self.model = lgb.train(
            config.model_params,
            train_dataset,
            num_boost_round=1000,
            valid_sets=[val_dataset],
            callbacks=callbacks
        )
        
        # 予測と評価
        y_pred = self.model.predict(X_val, num_iteration=self.model.best_iteration)
        
        metrics = {
            'auc': roc_auc_score(y_val, y_pred),
            'accuracy': accuracy_score(y_val, (y_pred > 0.5).astype(int)),
            'log_loss': log_loss(y_val, y_pred)
        }
        
        # 特徴量重要度
        importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importance(importance_type='gain')
        }).sort_values('importance', ascending=False)
        
        self.feature_importance = dict(zip(
            importance['feature'].head(20), 
            (importance['importance'] / importance['importance'].sum()).head(20)
        ))
        
        logger.info(f"学習完了 - AUC: {metrics['auc']:.4f}")
        logger.info(f"重要特徴量TOP5: {list(self.feature_importance.keys())[:5]}")
        
        return self.model, metrics
    
    # デモモデル作成メソッドを削除 - 本物のデータのみ使用
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """予測実行"""
        if self.model is None:
            logger.warning("モデルが学習されていません")
            return np.zeros(len(features))
        
        # LightGBMモデルの場合
        if hasattr(self.model, 'predict'):
            return self.model.predict(features, num_iteration=self.model.best_iteration)
        else:
            # sklearn互換モデルの場合
            return self.model.predict_proba(features)[:, 1]
    
    def get_feature_importance(self) -> Dict[str, float]:
        """特徴量重要度取得"""
        return self.feature_importance
    
    def save_model(self, path: str):
        """モデル保存"""
        if self.model is None:
            logger.warning("保存するモデルがありません")
            return
        
        if hasattr(self.model, 'save_model'):
            # LightGBMモデル
            self.model.save_model(path)
        else:
            # sklearn互換モデル
            joblib.dump(self.model, path)
        
        logger.info(f"モデル保存: {path}")
    
    def load_model(self, path: str):
        """モデル読み込み"""
        if path.endswith('.lgb') or path.endswith('.txt'):
            # LightGBMモデル
            self.model = lgb.Booster(model_file=path)
        else:
            # sklearn互換モデル
            self.model = joblib.load(path)
        
        logger.info(f"モデル読み込み: {path}")