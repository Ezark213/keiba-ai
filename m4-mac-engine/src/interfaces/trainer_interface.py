# トレーナーインターフェース定義
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path


class PredictionModel(ABC):
    """予測モデルの統一インターフェース (Liskov Substitution Principle)"""
    
    @abstractmethod
    def predict_probability(self, features: pd.DataFrame) -> np.ndarray:
        """勝率を予測（0-1の確率値を返す）"""
        pass
    
    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """特徴量重要度を取得"""
        pass
    
    @abstractmethod
    def save_model(self, path: Path) -> bool:
        """モデルを保存"""
        pass
    
    @abstractmethod
    def load_model(self, path: Path) -> bool:
        """モデルを読み込み"""
        pass
    
    @property
    @abstractmethod
    def is_trained(self) -> bool:
        """モデルが学習済みかチェック"""
        pass
    
    @property
    @abstractmethod
    def model_type(self) -> str:
        """モデルタイプを返す"""
        pass


class TrainerInterface(ABC):
    """ML トレーナーの抽象インターフェース (Single Responsibility + Interface Segregation)"""
    
    @abstractmethod
    def train_model(self, training_data: pd.DataFrame, target: pd.Series) -> PredictionModel:
        """モデルを学習"""
        pass
    
    @abstractmethod
    def evaluate_model(self, model: PredictionModel, 
                      test_data: pd.DataFrame, test_target: pd.Series) -> Dict[str, float]:
        """モデルを評価"""
        pass
    
    @abstractmethod
    def get_training_metrics(self) -> Dict[str, Any]:
        """学習時のメトリクスを取得"""
        pass
    
    @abstractmethod
    def optimize_hyperparameters(self, training_data: pd.DataFrame, 
                                target: pd.Series) -> Dict[str, Any]:
        """ハイパーパラメータ最適化"""
        pass
    
    @property
    @abstractmethod
    def supported_algorithms(self) -> List[str]:
        """サポートするアルゴリズムのリスト"""
        pass


class DataProcessor(ABC):
    """データ前処理の抽象インターフェース (Single Responsibility)"""
    
    @abstractmethod
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """データクリーニング"""
        pass
    
    @abstractmethod
    def handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """欠損値処理"""
        pass
    
    @abstractmethod
    def encode_categorical(self, data: pd.DataFrame) -> pd.DataFrame:
        """カテゴリカル変数のエンコーディング"""
        pass
    
    @abstractmethod
    def split_data(self, data: pd.DataFrame, target: pd.Series, 
                  test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """データの分割"""
        pass