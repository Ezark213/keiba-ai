# 分析クライアントインターフェース
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AnalysisClient(ABC):
    """分析クライアントの抽象インターフェース (Dependency Inversion)"""
    
    @abstractmethod
    async def analyze_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """パフォーマンスデータを分析"""
        pass
    
    @abstractmethod
    async def suggest_improvements(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """改善提案を生成"""
        pass
    
    @abstractmethod
    async def generate_feature_suggestions(self, 
                                         current_features: List[str],
                                         performance_data: Dict[str, Any]) -> List[str]:
        """新しい特徴量を提案"""
        pass
    
    @abstractmethod
    async def analyze_model_drift(self, 
                                current_performance: Dict[str, Any],
                                historical_performance: List[Dict[str, Any]]) -> Dict[str, Any]:
        """モデルドリフトを分析"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """分析サービスが利用可能かチェック"""
        pass
    
    @property
    @abstractmethod
    def client_type(self) -> str:
        """クライアントタイプを返す"""
        pass