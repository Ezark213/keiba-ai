# データソース抽象インターフェース
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import date


class DataSource(ABC):
    """データ取得の抽象インターフェース (Dependency Inversion Principle)"""
    
    @abstractmethod
    async def fetch_latest_races(self, date_range: int = 7) -> List[Dict[str, Any]]:
        """最新のレースデータを取得"""
        pass
    
    @abstractmethod
    async def fetch_race_details(self, race_id: str) -> Optional[Dict[str, Any]]:
        """特定のレースの詳細データを取得"""
        pass
    
    @abstractmethod
    async def fetch_horse_history(self, horse_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """馬の過去成績を取得"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """データソース名を取得"""
        pass
    
    @property
    @abstractmethod
    def supports_realtime(self) -> bool:
        """リアルタイムデータ取得をサポートするか"""
        pass