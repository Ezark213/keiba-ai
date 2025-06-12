# 同期サービスインターフェース
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class ModelSyncService(ABC):
    """モデル同期サービスの抽象インターフェース (Interface Segregation)"""
    
    @abstractmethod
    async def upload_model(self, model_path: Path, metadata: Dict[str, Any]) -> bool:
        """モデルをアップロード"""
        pass
    
    @abstractmethod
    async def download_model(self, model_id: str, destination: Path) -> bool:
        """モデルをダウンロード"""
        pass
    
    @abstractmethod
    async def delete_model(self, model_id: str) -> bool:
        """モデルを削除"""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """利用可能なモデルをリスト"""
        pass


class StatusService(ABC):
    """ステータス管理サービスの抽象インターフェース (Interface Segregation)"""
    
    @abstractmethod
    async def get_current_status(self) -> Optional[Dict[str, Any]]:
        """現在のステータスを取得"""
        pass
    
    @abstractmethod
    async def update_status(self, status: Dict[str, Any]) -> bool:
        """ステータスを更新"""
        pass
    
    @abstractmethod
    async def get_health_check(self) -> Dict[str, Any]:
        """ヘルスチェック結果を取得"""
        pass


class PerformanceService(ABC):
    """パフォーマンス管理サービスの抽象インターフェース (Interface Segregation)"""
    
    @abstractmethod
    async def update_performance_stats(self, stats: Dict[str, Any]) -> bool:
        """パフォーマンス統計を更新"""
        pass
    
    @abstractmethod
    async def get_performance_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """パフォーマンス履歴を取得"""
        pass
    
    @abstractmethod
    async def get_current_metrics(self) -> Dict[str, Any]:
        """現在のメトリクスを取得"""
        pass


class SyncService(ModelSyncService, StatusService, PerformanceService):
    """統合同期サービス（必要に応じて複数のサービスを組み合わせ）"""
    pass