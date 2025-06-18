#!/usr/bin/env python3
"""
JRDB ブラウザベースデータフェッチャー
Seleniumを使用してWebサイトからデータをダウンロード
"""
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import lhafile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import config


class JRDBBrowserFetcher:
    """JRDBブラウザベースデータフェッチャー"""
    
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
        self.data_dir = config.data_dir / "jrdb_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # ダウンロードディレクトリ設定
        self.download_dir = self.data_dir / "downloads"
        self.download_dir.mkdir(exist_ok=True)
        
        self.driver = None
        logger.info("✅ JRDBブラウザフェッチャー初期化完了")
    
    def setup_driver(self):
        """Chromeドライバーのセットアップ"""
        logger.info("🌐 Chromeドライバーセットアップ中...")
        
        # Chromeオプション
        options = webdriver.ChromeOptions()
        
        # ダウンロード設定
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        # デバッグのためヘッドレスモードを無効にする
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # ドライバー作成
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        logger.success("✅ Chromeドライバー準備完了")
    
    def login(self) -> bool:
        """JRDBにログイン"""
        try:
            logger.info("🔐 JRDBログイン中...")
            
            # ログインページへ（複数パターンを試行）
            login_urls = [
                "https://jrdb.com/member/",
                "https://jrdb.com/login/",
                "https://www.jrdb.com/member/",
                "https://www.jrdb.com/login/"
            ]
            
            login_success = False
            for login_url in login_urls:
                try:
                    logger.info(f"ログインURL試行: {login_url}")
                    self.driver.get(login_url)
                    time.sleep(3)
                    
                    # ページソースを確認
                    if "login" in self.driver.page_source.lower() or "ログイン" in self.driver.page_source:
                        logger.info(f"ログインページ発見: {login_url}")
                        login_success = True
                        break
                except Exception as e:
                    logger.warning(f"URL失敗: {login_url} - {e}")
                    continue
            
            if not login_success:
                logger.error("ログインページが見つかりません")
                return False
            
            # ページ読み込み待機
            wait = WebDriverWait(self.driver, 10)
            
            # ログインフォームを探す（複数パターンを試行）
            try:
                # フォーム要素のパターンを複数試行
                username_patterns = [
                    (By.NAME, "login_id"),
                    (By.NAME, "username"),
                    (By.NAME, "user_id"),
                    (By.ID, "username"),
                    (By.ID, "login_id"),
                    (By.CLASS_NAME, "username"),
                ]
                
                password_patterns = [
                    (By.NAME, "password"),
                    (By.ID, "password"),
                    (By.CLASS_NAME, "password"),
                ]
                
                button_patterns = [
                    (By.XPATH, "//input[@type='submit'][@value='ログイン']"),
                    (By.XPATH, "//button[contains(text(), 'ログイン')]"),
                    (By.XPATH, "//input[@type='submit']"),
                    (By.XPATH, "//button[@type='submit']"),
                    (By.CLASS_NAME, "login-button"),
                ]
                
                # ユーザー名入力フィールドを探す
                username_input = None
                for pattern in username_patterns:
                    try:
                        username_input = wait.until(EC.presence_of_element_located(pattern))
                        logger.info(f"ユーザー名フィールド発見: {pattern}")
                        break
                    except:
                        continue
                
                if not username_input:
                    logger.error("ユーザー名入力フィールドが見つかりません")
                    # スクリーンショット保存
                    self.driver.save_screenshot(str(self.data_dir / "login_form_not_found.png"))
                    return False
                
                username_input.clear()
                username_input.send_keys(self.username)
                
                # パスワード入力フィールドを探す
                password_input = None
                for pattern in password_patterns:
                    try:
                        password_input = self.driver.find_element(*pattern)
                        logger.info(f"パスワードフィールド発見: {pattern}")
                        break
                    except:
                        continue
                
                if not password_input:
                    logger.error("パスワード入力フィールドが見つかりません")
                    return False
                
                password_input.clear()
                password_input.send_keys(self.password)
                
                # ログインボタンを探す
                login_button = None
                for pattern in button_patterns:
                    try:
                        login_button = self.driver.find_element(*pattern)
                        logger.info(f"ログインボタン発見: {pattern}")
                        break
                    except:
                        continue
                
                if not login_button:
                    logger.error("ログインボタンが見つかりません")
                    return False
                
                login_button.click()
                
                # ログイン成功確認（URLの変化またはページ内容で判断）
                time.sleep(3)  # ページ遷移待機
                
                # ログイン後のページ確認
                if "member" in self.driver.current_url:
                    logger.success("✅ ログイン成功")
                    return True
                else:
                    logger.warning("⚠️ ログイン後のページ確認失敗")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ ログインフォーム操作エラー: {e}")
                # スクリーンショット保存（デバッグ用）
                self.driver.save_screenshot(str(self.data_dir / "login_error.png"))
                return False
                
        except Exception as e:
            logger.error(f"❌ ログインエラー: {e}")
            return False
    
    def navigate_to_data_page(self) -> bool:
        """データダウンロードページへ移動"""
        try:
            logger.info("📊 データページへ移動中...")
            
            # データページのURL（推定）
            data_url = f"{self.base_url}/member/data_download.php"
            self.driver.get(data_url)
            
            time.sleep(2)
            
            # ページタイトルやコンテンツでページ確認
            if "データ" in self.driver.title or "download" in self.driver.current_url:
                logger.success("✅ データページ到達")
                return True
            else:
                logger.warning("⚠️ データページ未到達")
                # 代替URLを試す
                alt_urls = [
                    f"{self.base_url}/member/data.php",
                    f"{self.base_url}/member/download/",
                    f"{self.base_url}/data/",
                ]
                
                for url in alt_urls:
                    self.driver.get(url)
                    time.sleep(2)
                    if "データ" in self.driver.page_source:
                        logger.success(f"✅ データページ発見: {url}")
                        return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ ナビゲーションエラー: {e}")
            return False
    
    def download_data_file(self, file_type: str, date: datetime) -> Optional[Path]:
        """特定のデータファイルをダウンロード"""
        try:
            date_str = date.strftime("%y%m%d")
            filename = f"{file_type}{date_str}.lzh"
            
            logger.info(f"📥 ダウンロード試行: {filename}")
            
            # ダウンロードリンクを探す
            try:
                # ファイル名でリンクを検索
                link = self.driver.find_element(By.PARTIAL_LINK_TEXT, filename)
                link.click()
                
                # ダウンロード完了待機
                downloaded_file = self.download_dir / filename
                for i in range(30):  # 最大30秒待機
                    if downloaded_file.exists():
                        logger.success(f"✅ ダウンロード完了: {filename}")
                        return downloaded_file
                    time.sleep(1)
                
                logger.warning(f"⚠️ ダウンロードタイムアウト: {filename}")
                return None
                
            except Exception as e:
                logger.debug(f"リンク検索失敗: {filename} - {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ ダウンロードエラー: {e}")
            return None
    
    async def fetch_latest_races(self) -> List[Dict[str, Any]]:
        """最新のレースデータ取得"""
        logger.info("🏇 ブラウザ経由でデータ取得開始...")
        
        # ドライバーセットアップ
        self.setup_driver()
        
        try:
            # ログイン
            if not self.login():
                raise RuntimeError("JRDBへのログインに失敗しました")
            
            # データページへ移動
            if not self.navigate_to_data_page():
                # ページ内容を確認
                logger.info("📄 現在のページ内容を確認...")
                self.driver.save_screenshot(str(self.data_dir / "current_page.png"))
                
                # 利用可能なリンクを探す
                links = self.driver.find_elements(By.TAG_NAME, "a")
                logger.info(f"発見したリンク数: {len(links)}")
                
                for link in links[:20]:  # 最初の20個を表示
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    if text and ("データ" in text or "download" in text.lower() or ".lzh" in text):
                        logger.info(f"  - {text}: {href}")
            
            races = []
            today = datetime.now()
            
            # 最新のデータファイルを探してダウンロード
            # 過去7日分を試行
            for days_ago in range(7):
                target_date = today - timedelta(days=days_ago)
                
                # SEDファイル（成績データ）
                sed_file = self.download_data_file("SED", target_date)
                if sed_file:
                    race_data = await self._parse_sed_file(sed_file)
                    races.extend(race_data)
                
                # KYIファイル（競走馬データ）
                kyi_file = self.download_data_file("KYI", target_date)
                if kyi_file:
                    horse_data = await self._parse_kyi_file(kyi_file)
                    races = self._merge_horse_data(races, horse_data)
            
            logger.success(f"✅ データ取得完了: {len(races)}レース")
            return races
            
        finally:
            # ブラウザを閉じる
            if self.driver:
                self.driver.quit()
    
    async def _parse_sed_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """SEDファイルのパース"""
        races = []
        
        try:
            with lhafile.Lhafile(str(file_path)) as lha:
                for info in lha.infoiter():
                    if info.filename.upper().endswith('.SED'):
                        content = lha.read(info.filename).decode('cp932', errors='ignore')
                        # TODO: 実際のSEDフォーマットに基づいてパース
                        logger.info(f"SEDファイル内容サンプル: {content[:200]}")
        except Exception as e:
            logger.error(f"SEDパースエラー: {e}")
        
        return races
    
    async def _parse_kyi_file(self, file_path: Path) -> Dict[str, Any]:
        """KYIファイルのパース"""
        horse_data = {}
        
        try:
            with lhafile.Lhafile(str(file_path)) as lha:
                for info in lha.infoiter():
                    if info.filename.upper().endswith('.KYI'):
                        content = lha.read(info.filename).decode('cp932', errors='ignore')
                        # TODO: 実際のKYIフォーマットに基づいてパース
                        logger.info(f"KYIファイル内容サンプル: {content[:200]}")
        except Exception as e:
            logger.error(f"KYIパースエラー: {e}")
        
        return horse_data
    
    def _merge_horse_data(self, races: List[Dict[str, Any]], 
                         horse_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """レースデータと馬データのマージ"""
        # TODO: 実装
        return races


async def test_browser_fetcher():
    """ブラウザフェッチャーのテスト"""
    fetcher = JRDBBrowserFetcher()
    
    try:
        races = await fetcher.fetch_latest_races()
        logger.info(f"取得レース数: {len(races)}")
        
    except Exception as e:
        logger.error(f"テストエラー: {e}")


if __name__ == "__main__":
    asyncio.run(test_browser_fetcher())