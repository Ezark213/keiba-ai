#!/usr/bin/env python3
"""
JRDB HTTPデータフェッチャー
Webサイト経由でデータをダウンロード
"""
import asyncio
import aiohttp
import lhafile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import io

from config import config


class JRDBHTTPFetcher:
    """JRDB HTTPベースのデータフェッチャー"""
    
    def __init__(self):
        """初期化"""
        self.username = config.jrdb_username
        self.password = config.jrdb_password
        
        if not self.username or not self.password:
            raise ValueError(
                "JRDBクレデンシャルが設定されていません！\n"
                "python -m src.utils.secure_config で設定してください。"
            )
        
        self.base_url = "https://www.jrdb.com"
        self.member_url = f"{self.base_url}/member"
        self.data_dir = config.data_dir / "jrdb_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # セッション管理
        self.session = None
        self.cookies = None
        
        logger.info(f"✅ JRDB HTTPフェッチャー初期化完了")
    
    async def __aenter__(self):
        """非同期コンテキストマネージャー入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー出口"""
        if self.session:
            await self.session.close()
    
    async def login(self) -> bool:
        """JRDBにログイン"""
        try:
            logger.info("🔐 JRDBログイン中...")
            
            # ログインページにアクセス
            login_url = f"{self.member_url}/new_index.php"
            
            # ログインフォームデータ
            login_data = {
                "login_id": self.username,
                "password": self.password,
                "submit": "ログイン"
            }
            
            async with self.session.post(login_url, data=login_data) as resp:
                if resp.status == 200:
                    # クッキーを保存
                    self.cookies = resp.cookies
                    logger.success("✅ ログイン成功")
                    return True
                else:
                    logger.error(f"❌ ログイン失敗: ステータス {resp.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ ログインエラー: {e}")
            return False
    
    async def fetch_data_file(self, file_type: str, date: datetime) -> Optional[bytes]:
        """データファイルをダウンロード"""
        try:
            date_str = date.strftime("%y%m%d")
            filename = f"{file_type}{date_str}.lzh"
            
            # ダウンロードURL（推定）
            # 実際のURLパターンはJRDBのサイト構造による
            download_url = f"{self.member_url}/download/{filename}"
            
            logger.info(f"📥 ダウンロード試行: {filename}")
            
            async with self.session.get(download_url, cookies=self.cookies) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    
                    # ローカルに保存
                    local_path = self.data_dir / filename
                    with open(local_path, 'wb') as f:
                        f.write(data)
                    
                    logger.success(f"✅ ダウンロード完了: {filename}")
                    return data
                else:
                    logger.warning(f"⚠️ ファイルなし: {filename}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ ダウンロードエラー: {e}")
            return None
    
    async def fetch_latest_races(self) -> List[Dict[str, Any]]:
        """最新のレースデータ取得"""
        logger.info("🏇 最新データ取得開始...")
        
        # ログイン
        if not await self.login():
            raise RuntimeError("JRDBへのログインに失敗しました")
        
        races = []
        today = datetime.now()
        
        # 過去7日分のデータを取得
        for days_ago in range(7):
            target_date = today - timedelta(days=days_ago)
            
            # SEDファイル（成績データ）
            sed_data = await self.fetch_data_file("SED", target_date)
            if sed_data:
                race_data = await self._parse_sed_data(sed_data)
                races.extend(race_data)
            
            # KYIファイル（競走馬データ）
            kyi_data = await self.fetch_data_file("KYI", target_date)
            if kyi_data:
                horse_data = await self._parse_kyi_data(kyi_data)
                races = self._merge_horse_data(races, horse_data)
        
        logger.success(f"✅ データ取得完了: {len(races)}レース")
        return races
    
    async def _parse_sed_data(self, data: bytes) -> List[Dict[str, Any]]:
        """SEDデータのパース"""
        races = []
        
        try:
            # lzhデータを解凍
            with io.BytesIO(data) as f:
                with lhafile.Lhafile(f) as lha:
                    for info in lha.infoiter():
                        if info.filename.upper().endswith('.SED'):
                            content = lha.read(info.filename).decode('cp932', errors='ignore')
                            races.extend(self._parse_sed_content(content))
        except Exception as e:
            logger.error(f"SEDパースエラー: {e}")
        
        return races
    
    async def _parse_kyi_data(self, data: bytes) -> Dict[str, Any]:
        """KYIデータのパース"""
        horse_data = {}
        
        try:
            # lzhデータを解凍
            with io.BytesIO(data) as f:
                with lhafile.Lhafile(f) as lha:
                    for info in lha.infoiter():
                        if info.filename.upper().endswith('.KYI'):
                            content = lha.read(info.filename).decode('cp932', errors='ignore')
                            horse_data.update(self._parse_kyi_content(content))
        except Exception as e:
            logger.error(f"KYIパースエラー: {e}")
        
        return horse_data
    
    def _parse_sed_content(self, content: str) -> List[Dict[str, Any]]:
        """SEDコンテンツのパース（実装は仕様書に基づく）"""
        # TODO: 実際のSEDフォーマットに基づいて実装
        return []
    
    def _parse_kyi_content(self, content: str) -> Dict[str, Any]:
        """KYIコンテンツのパース（実装は仕様書に基づく）"""
        # TODO: 実際のKYIフォーマットに基づいて実装
        return {}
    
    def _merge_horse_data(self, races: List[Dict[str, Any]], 
                         horse_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """レースデータと馬データのマージ"""
        # TODO: 実装
        return races


async def test_http_fetcher():
    """HTTPフェッチャーのテスト"""
    async with JRDBHTTPFetcher() as fetcher:
        try:
            # ログインテスト
            success = await fetcher.login()
            if success:
                logger.info("✅ ログインテスト成功")
                
                # データ取得テスト
                races = await fetcher.fetch_latest_races()
                logger.info(f"取得レース数: {len(races)}")
            else:
                logger.error("❌ ログインテスト失敗")
                
        except Exception as e:
            logger.error(f"テストエラー: {e}")


if __name__ == "__main__":
    asyncio.run(test_http_fetcher())