#!/usr/bin/env python3
"""
JRDB リアルタイムデータフェッチャー
実際のJRDBサイトから最新データを取得
"""
import asyncio
import aiohttp
import base64
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import re

from config import config


class JRDBRealtimeFetcher:
    """JRDBリアルタイムデータフェッチャー"""
    
    def __init__(self):
        self.username = config.jrdb_username
        self.password = config.jrdb_password
        
        if not self.username or not self.password:
            raise ValueError("JRDBクレデンシャルが必要です")
        
        self.data_dir = config.data_dir / "jrdb_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # JRDBの実際のエンドポイント
        self.base_url = "https://jrdb.com"
        
        logger.info("JRDBリアルタイムフェッチャー初期化完了")
    
    async def get_direct_data_urls(self, session: aiohttp.ClientSession) -> List[str]:
        """JRDBの直接データURLを取得"""
        logger.info("🔍 直接データURL探索中...")
        
        # 実際のJRDBデータダウンロードページのパターン
        potential_urls = [
            f"{self.base_url}/program/",
            f"{self.base_url}/data/",
            f"{self.base_url}/member/datadownload/",
            f"{self.base_url}/download/",
        ]
        
        valid_urls = []
        
        for url in potential_urls:
            try:
                # Basic認証を含むリクエスト
                auth = aiohttp.BasicAuth(self.username, self.password)
                
                async with session.get(url, auth=auth, allow_redirects=True) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        
                        # データファイルのリンクを探す
                        lzh_links = re.findall(r'href=["\']([^"\']*\.lzh)["\']', text)
                        if lzh_links:
                            logger.success(f"✅ データリンク発見: {url}")
                            valid_urls.extend([f"{self.base_url}{link}" if link.startswith('/') else link for link in lzh_links])
                        
                        # 今日のファイルパターンを探す
                        today = datetime.now().strftime("%y%m%d")
                        if today in text:
                            logger.info(f"今日のデータパターン発見: {url}")
                            
            except Exception as e:
                logger.debug(f"URL探索失敗: {url} - {e}")
                continue
        
        return valid_urls
    
    async def download_data_file(self, session: aiohttp.ClientSession, url: str) -> Optional[Path]:
        """データファイルをダウンロード"""
        try:
            filename = Path(url).name
            logger.info(f"📥 ダウンロード: {filename}")
            
            # 認証付きでダウンロード
            auth = aiohttp.BasicAuth(self.username, self.password)
            
            async with session.get(url, auth=auth) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    
                    # lzhファイルかチェック
                    if content.startswith(b'-lh'):
                        file_path = self.data_dir / filename
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        
                        logger.success(f"✅ ダウンロード成功: {filename}")
                        return file_path
                    else:
                        logger.warning(f"⚠️ 不正なファイル形式: {filename}")
                        
        except Exception as e:
            logger.error(f"❌ ダウンロード失敗: {url} - {e}")
        
        return None
    
    async def fetch_latest_data(self) -> bool:
        """最新データを取得"""
        logger.info("🏇 JRDBリアルタイムデータ取得開始...")
        
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # 1. データURLを探索
            data_urls = await self.get_direct_data_urls(session)
            
            if not data_urls:
                logger.warning("データURLが見つかりません。直接ファイルURLを試行...")
                
                # 2. 今日のファイルを直接試行
                today = datetime.now()
                file_types = ["SED", "KYI", "BAC", "CYB", "KAB"]
                
                for days_ago in range(3):  # 今日から3日前まで
                    date = today - timedelta(days=days_ago)
                    date_str = date.strftime("%y%m%d")
                    
                    for file_type in file_types:
                        filename = f"{file_type}{date_str}.lzh"
                        
                        # 可能性のあるURL
                        direct_urls = [
                            f"{self.base_url}/data/{filename}",
                            f"{self.base_url}/download/{filename}",
                            f"{self.base_url}/member/data/{filename}",
                            f"{self.base_url}/files/{filename}",
                        ]
                        
                        for url in direct_urls:
                            downloaded = await self.download_data_file(session, url)
                            if downloaded:
                                return True
            
            else:
                # 見つかったURLからダウンロード
                for url in data_urls[:10]:  # 最初の10個まで
                    downloaded = await self.download_data_file(session, url)
                    if downloaded:
                        return True
        
        logger.error("❌ 実データ取得に失敗しました")
        return False
    
    async def fetch_latest_races(self) -> List[Dict[str, Any]]:
        """最新レースデータ取得"""
        logger.info("🏇 最新レースデータ取得...")
        
        # 実データダウンロードを試行
        if await self.fetch_latest_data():
            logger.success("実データダウンロード成功")
            
            # ダウンロードしたファイルを解析
            # 実装は既存のJRDBSimpleFetcherを利用
            from .jrdb_simple_fetcher import JRDBSimpleFetcher
            fetcher = JRDBSimpleFetcher()
            return await fetcher.fetch_latest_races()
        
        else:
            raise RuntimeError(
                "❌ 本物のJRDBデータ取得に失敗しました。\n"
                "手動ダウンロードが必要です。"
            )


async def main():
    """メイン実行"""
    try:
        fetcher = JRDBRealtimeFetcher()
        races = await fetcher.fetch_latest_races()
        
        logger.success(f"✅ {len(races)} レースのデータを取得")
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")


if __name__ == "__main__":
    asyncio.run(main())