#!/usr/bin/env python3
"""
完全自動JRDBデータ取得システム
ブラウザ自動化でJRDBから直接データを取得
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import logging
from pathlib import Path
import requests
from datetime import datetime, timedelta
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoJRDBFetcher:
    def __init__(self):
        self.username = "25067698"
        self.password = "87086387"
        self.base_url = "http://www.jrdb.com"
        self.download_dir = Path("data/jrdb_real").absolute()
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_chrome_with_auth(self):
        """認証対応Chrome設定"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # ダウンロード設定
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        options.add_experimental_option("prefs", prefs)
        
        # 認証情報を含むカスタムプロファイル
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return webdriver.Chrome(options=options)
    
    def auto_login(self, driver):
        """自動ログイン処理"""
        logger.info("🔐 JRDB自動ログイン開始")
        
        try:
            # メインページアクセス
            driver.get(f"{self.base_url}/member/")
            time.sleep(3)
            
            # HTTPベーシック認証の自動入力
            # 方法1: JavaScriptで認証情報を設定
            driver.execute_script(f"""
                var xhr = new XMLHttpRequest();
                xhr.open('GET', '{self.base_url}/member/', false, '{self.username}', '{self.password}');
                xhr.send();
            """)
            
            # 方法2: URLに認証情報を含める
            auth_url = f"http://{self.username}:{self.password}@www.jrdb.com/member/"
            driver.get(auth_url)
            time.sleep(2)
            
            # ログイン成功確認
            if "member" in driver.current_url:
                logger.info("✅ ログイン成功")
                return True
            else:
                logger.warning("⚠️ ログイン確認中...")
                return False
                
        except Exception as e:
            logger.error(f"❌ ログインエラー: {e}")
            return False
    
    def navigate_to_data_page(self, driver):
        """データページへ移動"""
        try:
            # データページへの直接アクセス
            data_url = f"http://{self.username}:{self.password}@www.jrdb.com/member/data/"
            driver.get(data_url)
            time.sleep(2)
            
            logger.info("📊 データページアクセス成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ ナビゲーションエラー: {e}")
            return False
    
    def auto_download_files(self, driver):
        """ファイル自動ダウンロード"""
        logger.info("📥 自動ダウンロード開始")
        
        downloaded = 0
        file_types = ["sed", "kyi", "bac"]
        
        # 最近30日のデータを取得
        for days_ago in range(30):
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%y%m%d")
            
            for file_type in file_types:
                try:
                    # ダウンロードURL構築
                    filename = f"{file_type.upper()}{date_str}.lzh"
                    download_url = f"http://{self.username}:{self.password}@www.jrdb.com/member/data/{file_type}/{filename}"
                    
                    # JavaScriptでダウンロード実行
                    driver.execute_script(f"""
                        var link = document.createElement('a');
                        link.href = '{download_url}';
                        link.download = '{filename}';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    """)
                    
                    time.sleep(1)
                    
                    # ファイル存在確認
                    downloaded_file = self.download_dir / filename
                    if downloaded_file.exists():
                        logger.info(f"✅ ダウンロード成功: {filename}")
                        downloaded += 1
                        
                        if downloaded >= 15:  # 十分な数
                            return downloaded
                    
                except Exception as e:
                    logger.debug(f"スキップ: {filename} - {e}")
                    continue
        
        return downloaded
    
    def extract_lzh_files(self):
        """LZHファイル自動展開"""
        logger.info("🗜️ LZHファイル自動展開")
        
        lzh_files = list(self.download_dir.glob("*.lzh"))
        extracted = 0
        
        for lzh_file in lzh_files:
            try:
                # lhaコマンドで展開
                result = subprocess.run([
                    'lha', 'x', str(lzh_file), '-w', str(self.download_dir)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ 展開成功: {lzh_file.name}")
                    extracted += 1
                    
                    # 展開後のLZHファイル削除（オプション）
                    # lzh_file.unlink()
                    
            except Exception as e:
                logger.error(f"❌ 展開エラー: {lzh_file.name} - {e}")
        
        return extracted
    
    def run_auto_fetch(self):
        """完全自動取得実行"""
        logger.info("🚀 完全自動JRDB取得開始")
        
        driver = None
        try:
            # 1. ブラウザ起動
            driver = self.setup_chrome_with_auth()
            
            # 2. 自動ログイン
            if not self.auto_login(driver):
                logger.warning("⚠️ ログイン失敗、別方法を試行")
                
            # 3. データページへ移動
            if self.navigate_to_data_page(driver):
                # 4. ファイル自動ダウンロード
                downloaded = self.auto_download_files(driver)
                logger.info(f"📊 ダウンロード完了: {downloaded}ファイル")
            
            # 5. LZHファイル展開
            extracted = self.extract_lzh_files()
            logger.info(f"🗜️ 展開完了: {extracted}ファイル")
            
            return downloaded > 0
            
        except Exception as e:
            logger.error(f"❌ 自動取得エラー: {e}")
            return False
            
        finally:
            if driver:
                driver.quit()

def create_auto_runner():
    """自動実行スケジューラー作成"""
    runner_code = '''#!/usr/bin/env python3
"""
JRDB自動取得スケジューラー
定期的にJRDBデータを自動取得
"""
import schedule
import time
from datetime import datetime
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_auto_fetch():
    """自動取得実行"""
    logger.info(f"🕐 自動取得開始: {datetime.now()}")
    
    try:
        # auto_jrdb_fetcher.py実行
        result = subprocess.run([
            'python3', 'auto_jrdb_fetcher.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ 自動取得成功")
            
            # データ処理も自動実行
            subprocess.run(['python3', 'jrdb_consolidation_tool.py'])
            
            # システム再起動
            subprocess.run(['python3', 'claude_main.py'])
            
        else:
            logger.error(f"❌ 自動取得失敗: {result.stderr}")
            
    except Exception as e:
        logger.error(f"❌ 実行エラー: {e}")

def main():
    """スケジューラーメイン"""
    logger.info("🤖 JRDB自動取得スケジューラー起動")
    
    # スケジュール設定
    schedule.every(6).hours.do(run_auto_fetch)  # 6時間ごと
    schedule.every().day.at("06:00").do(run_auto_fetch)  # 毎朝6時
    schedule.every().day.at("18:00").do(run_auto_fetch)  # 毎夕6時
    
    # 初回実行
    run_auto_fetch()
    
    # スケジュール実行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1分ごとにチェック

if __name__ == "__main__":
    main()
'''
    
    runner_file = Path("jrdb_auto_scheduler.py")
    with open(runner_file, 'w', encoding='utf-8') as f:
        f.write(runner_code)
    
    logger.info(f"✅ 自動実行スケジューラー作成: {runner_file}")
    return runner_file

def main():
    """メイン処理"""
    print("🤖 完全自動JRDBデータ取得システム")
    print("=" * 50)
    
    fetcher = AutoJRDBFetcher()
    
    # 自動取得実行
    success = fetcher.run_auto_fetch()
    
    if success:
        print("\n✅ 自動取得成功！")
        
        # データ確認
        txt_files = list(fetcher.download_dir.glob("*.txt"))
        lzh_files = list(fetcher.download_dir.glob("*.lzh"))
        
        print(f"📊 取得結果:")
        print(f"  LZHファイル: {len(lzh_files)}個")
        print(f"  テキストファイル: {len(txt_files)}個")
        
        # 自動実行スケジューラー作成
        scheduler_file = create_auto_runner()
        
        print(f"\n🤖 自動化設定:")
        print(f"  スケジューラー: {scheduler_file}")
        print(f"  実行: python3 {scheduler_file}")
        print(f"\n💡 これで完全自動化が実現します！")
        
    else:
        print("\n⚠️ 自動取得に問題があります")
        print("💡 手動での確認が必要かもしれません")

if __name__ == "__main__":
    main()