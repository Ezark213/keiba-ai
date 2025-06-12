# 特徴量エンジニアリング基底クラス
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd


class FeatureEngineer(ABC):
    """特徴量エンジニアリングの基底抽象クラス (Open/Closed Principle)"""
    
    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """この特徴量エンジニアが生成する特徴量名を返す"""
        pass
    
    @abstractmethod
    def create_features(self, horse_data: Dict, race_data: Dict) -> Dict[str, float]:
        """馬データとレースデータから特徴量を生成"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """特徴量エンジニアの名前"""
        pass
    
    @property
    def description(self) -> str:
        """特徴量エンジニアの説明（オプション）"""
        return f"{self.name} feature engineer"


class FeatureEngineRegistry:
    """特徴量エンジニアの登録・管理クラス (Single Responsibility)"""
    
    def __init__(self):
        self._engineers: List[FeatureEngineer] = []
        self._engineer_map: Dict[str, FeatureEngineer] = {}
    
    def register(self, engineer: FeatureEngineer) -> None:
        """特徴量エンジニアを登録"""
        if engineer.name in self._engineer_map:
            raise ValueError(f"Feature engineer '{engineer.name}' already registered")
        
        self._engineers.append(engineer)
        self._engineer_map[engineer.name] = engineer
    
    def unregister(self, name: str) -> None:
        """特徴量エンジニアの登録を解除"""
        if name not in self._engineer_map:
            raise ValueError(f"Feature engineer '{name}' not found")
        
        engineer = self._engineer_map[name]
        self._engineers.remove(engineer)
        del self._engineer_map[name]
    
    def get_engineer(self, name: str) -> FeatureEngineer:
        """名前で特徴量エンジニアを取得"""
        if name not in self._engineer_map:
            raise ValueError(f"Feature engineer '{name}' not found")
        return self._engineer_map[name]
    
    def list_engineers(self) -> List[str]:
        """登録済み特徴量エンジニアのリストを取得"""
        return list(self._engineer_map.keys())
    
    def create_all_features(self, horse_data: Dict, race_data: Dict) -> Dict[str, float]:
        """すべての登録済み特徴量エンジニアを使用して特徴量を生成"""
        all_features = {}
        
        for engineer in self._engineers:
            try:
                features = engineer.create_features(horse_data, race_data)
                all_features.update(features)
            except Exception as e:
                # ログを出力し、その特徴量はスキップして継続
                print(f"Warning: Failed to create features from {engineer.name}: {e}")
                continue
        
        return all_features
    
    def get_all_feature_names(self) -> List[str]:
        """すべての特徴量名を取得"""
        all_names = []
        for engineer in self._engineers:
            all_names.extend(engineer.get_feature_names())
        return all_names


class FeatureProcessor:
    """特徴量処理の統括クラス (Single Responsibility + Dependency Inversion)"""
    
    def __init__(self, registry: FeatureEngineRegistry):
        self.registry = registry
    
    def process_horse_features(self, horses_data: List[Dict], race_data: Dict) -> pd.DataFrame:
        """複数の馬のデータから特徴量を生成してDataFrameを返す"""
        features_list = []
        
        for horse_data in horses_data:
            features = self.registry.create_all_features(horse_data, race_data)
            features_list.append(features)
        
        # DataFrameに変換
        df = pd.DataFrame(features_list)
        
        # 欠損値を適切なデフォルト値で埋める
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                df[col] = df[col].fillna(0.0)
            else:
                df[col] = df[col].fillna('unknown')
        
        return df
    
    def get_feature_importance_mapping(self) -> Dict[str, str]:
        """特徴量名とその生成元エンジニアのマッピングを取得"""
        mapping = {}
        for engineer in self.registry._engineers:
            for feature_name in engineer.get_feature_names():
                mapping[feature_name] = engineer.name
        return mapping