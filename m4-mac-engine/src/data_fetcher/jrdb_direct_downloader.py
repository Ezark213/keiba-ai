#!/usr/bin/env python3
"""
JRDB直接ダウンローダー
認証後のURLパターンを推測してダイレクトダウンロードを試行
"""
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import base64

from config import config


class JRDBDirectDownloader:
    """JRDB直接ダウンローダー"""
    
    def __init__(self):
        self.username = config.jrdb_username
        self.password = config.jrdb_password
        
        if not self.username or not self.password:
            raise ValueError("JRDBクレデンシャルが必要です")
        
        self.data_dir = config.data_dir / "jrdb_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 可能性のあるベースURL
        self.base_urls = [
            "https://jrdb.com",
            "https://www.jrdb.com",
            "https://data.jrdb.com",
            "https://download.jrdb.com"
        ]
        
        logger.info("JRDB直接ダウンローダー初期化完了")
    
    async def try_direct_download(self, session: aiohttp.ClientSession) -> bool:
        """直接ダウンロードを試行"""
        logger.info("🔍 直接ダウンロード試行中...")
        
        # 今日から過去7日間のデータを試行
        today = datetime.now()
        file_types = ["SED", "KYI", "BAC", "CYB", "KAB"]
        
        downloaded_count = 0
        
        for days_ago in range(7):
            target_date = today - timedelta(days=days_ago)
            date_str = target_date.strftime("%y%m%d")
            
            for file_type in file_types:
                filename = f"{file_type}{date_str}.lzh"
                
                # 様々なURLパターンを試行
                url_patterns = [
                    f"/data/{filename}",
                    f"/member/data/{filename}",
                    f"/download/{filename}",
                    f"/member/download/{filename}",
                    f"/files/{filename}",
                    f"/lzh/{filename}",
                    f"/{filename}",
                ]
                
                for base_url in self.base_urls:
                    for pattern in url_patterns:
                        url = f"{base_url}{pattern}"
                        
                        try:
                            # Basic認証を試行
                            auth = aiohttp.BasicAuth(self.username, self.password)
                            
                            async with session.get(url, auth=auth) as resp:
                                if resp.status == 200:
                                    content = await resp.read()
                                    
                                    # lzhファイルかチェック（マジックナンバー）
                                    if content.startswith(b'-lh'):
                                        file_path = self.data_dir / filename
                                        async with aiofiles.open(file_path, 'wb') as f:
                                            await f.write(content)
                                        
                                        logger.success(f"✅ ダウンロード成功: {filename}")
                                        downloaded_count += 1
                                        break
                                        
                        except Exception as e:
                            logger.debug(f"URL失敗: {url} - {e}")
                            continue
        
        return downloaded_count > 0
    
    async def try_session_download(self, session: aiohttp.ClientSession) -> bool:
        """セッション認証後のダウンロードを試行"""
        logger.info("🔐 セッション認証後ダウンロード試行...")
        
        # ログインフォームの送信を試行
        login_urls = [
            "https://jrdb.com/login",
            "https://jrdb.com/member/login",
            "https://www.jrdb.com/login",
            "https://www.jrdb.com/member/login",
        ]
        
        for login_url in login_urls:
            try:
                # ログイン試行
                login_data = {
                    "username": self.username,
                    "password": self.password,
                    "login_id": self.username,
                    "user_id": self.username,
                }
                
                async with session.post(login_url, data=login_data) as resp:
                    if resp.status in [200, 302]:  # 成功またはリダイレクト
                        logger.info(f"認証成功の可能性: {login_url}")
                        
                        # ログイン後のダウンロードを試行
                        if await self.try_direct_download(session):
                            return True
                            
            except Exception as e:
                logger.debug(f"認証失敗: {login_url} - {e}")
                continue
        
        return False
    
    async def download_real_data(self) -> bool:
        """実データダウンロード"""
        logger.info("🏇 JRDB実データダウンロード開始...")
        
        # SSL検証を無効にして接続性を優先
        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # 1. 直接ダウンロードを試行
            if await self.try_direct_download(session):
                return True
            
            # 2. セッション認証後のダウンロードを試行
            if await self.try_session_download(session):
                return True
            
            # 3. 特定の公開データパターンを試行
            if await self.try_public_data_patterns(session):
                return True
        
        logger.error("❌ 全てのダウンロード方法が失敗しました")
        return False
    
    async def try_public_data_patterns(self, session: aiohttp.ClientSession) -> bool:
        """公開データパターンを試行"""
        logger.info("📊 公開データパターン試行...")
        
        # JRDBの公開データやAPIの可能性
        public_patterns = [
            "https://jrdb.com/api/data/",
            "https://data.jrdb.com/api/",
            "https://api.jrdb.com/v1/",
            "https://jrdb.com/public/",
        ]
        
        for pattern in public_patterns:
            try:
                async with session.get(pattern) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if "lzh" in text.lower() or "download" in text.lower():
                            logger.info(f"有望なエンドポイント発見: {pattern}")
                            # さらなる調査が必要
                            
            except Exception as e:
                logger.debug(f"パブリックパターン失敗: {pattern} - {e}")
                continue
        
        return False


async def main():
    """メイン実行"""
    downloader = JRDBDirectDownloader()
    
    # 既存データをチェック
    existing_files = list(downloader.data_dir.glob("*.lzh"))
    if existing_files:
        logger.info(f"既存のLZHファイル: {len(existing_files)}個")
    
    # ダウンロード実行
    success = await downloader.download_real_data()
    
    if success:
        logger.success("✅ 実データダウンロード成功")
        
        # ダウンロード後のファイル確認
        new_files = list(downloader.data_dir.glob("*.lzh"))
        logger.info(f"ダウンロード後のLZHファイル: {len(new_files)}個")
        
        return True
    else:
        logger.error("❌ 実データダウンロード失敗")
        logger.info("手動ダウンロードが必要です:")
        logger.info("1. https://jrdb.com/member/ にログイン")
        logger.info("2. データダウンロードページから最新データを取得")
        logger.info(f"3. ファイルを {downloader.data_dir} に配置")
        
        return False


if __name__ == "__main__":
    asyncio.run(main())