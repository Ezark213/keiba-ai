#!/usr/bin/env python3
"""
シンプルなJRDBダウンローダー
HTTPポップアップ認証による実データ取得
"""
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleJRDBDownloader:
    def __init__(self):
        self.username = "25067698"
        self.password = "87086387"
        self.base_url = "http://www.jrdb.com/member/data"
        self.download_dir = Path("data/jrdb_real")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_chrome(self):
        """Chrome設定（シンプル）"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # ダウンロード設定
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        return webdriver.Chrome(options=options)
    
    def login_and_download(self, file_types=["sed", "kyi", "bac"], days_back=30):
        """ログインして指定ファイルをダウンロード"""
        driver = self.setup_chrome()
        successful_downloads = 0
        
        try:
            logger.info("🚀 JRDBダウンロード開始")
            
            # 各ファイルタイプごとにダウンロード
            for file_type in file_types:
                logger.info(f"📊 {file_type.upper()}ファイル取得中...")
                
                # 最近の日付を試行
                for days_ago in range(days_back):
                    try:
                        # 日付計算
                        from datetime import datetime, timedelta
                        target_date = datetime.now() - timedelta(days=days_ago)
                        date_str = target_date.strftime("%y%m%d")
                        
                        # ファイル名とURL構築
                        filename = f"{file_type.upper()}{date_str}.lzh"
                        download_url = f"{self.base_url}/{file_type}/{filename}"
                        
                        logger.info(f"📥 試行: {filename}")
                        
                        # ページアクセス
                        driver.get(download_url)
                        
                        # HTTPベーシック認証のポップアップ処理
                        time.sleep(2)
                        
                        # 認証情報入力（HTTPポップアップ）
                        try:
                            # ポップアップが表示された場合
                            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                            alert.authenticate(self.username, self.password)
                        except:
                            # URLに認証情報を含める方法
                            auth_url = f"http://{self.username}:{self.password}@www.jrdb.com/member/data/{file_type}/{filename}"
                            driver.get(auth_url)
                        
                        time.sleep(3)
                        
                        # ダウンロード成功チェック
                        downloaded_file = self.download_dir / filename
                        if downloaded_file.exists() and downloaded_file.stat().st_size > 100:
                            logger.info(f"✅ 成功: {filename}")
                            successful_downloads += 1
                            
                            # 各タイプ10個で十分
                            if successful_downloads % len(file_types) == 0 and successful_downloads >= 10:
                                break
                        else:
                            logger.info(f"⏭️  スキップ: {filename}")
                            
                    except Exception as e:
                        logger.debug(f"エラー: {filename} - {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"❌ ダウンロードエラー: {e}")
            
        finally:
            driver.quit()
            
        return successful_downloads
    
    def download_with_requests(self):
        """requests + HTTPベーシック認証でダウンロード"""
        logger.info("🔄 requests経由でのダウンロード試行")
        
        successful = 0
        auth = (self.username, self.password)
        
        # 重要ファイルのみ試行
        file_types = ["sed", "kyi", "bac"]
        recent_dates = []
        
        # 最近10日の日付生成
        from datetime import datetime, timedelta
        for i in range(10):
            date = datetime.now() - timedelta(days=i)
            recent_dates.append(date.strftime("%y%m%d"))
        
        for file_type in file_types:
            for date_str in recent_dates:
                try:
                    filename = f"{file_type.upper()}{date_str}.lzh"
                    url = f"{self.base_url}/{file_type}/{filename}"
                    
                    logger.info(f"📥 requests試行: {filename}")
                    
                    response = requests.get(url, auth=auth, timeout=10)
                    
                    if response.status_code == 200 and len(response.content) > 100:
                        output_path = self.download_dir / filename
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        
                        logger.info(f"✅ requests成功: {filename}")
                        successful += 1
                        
                        if successful >= 15:  # 十分な数
                            return successful
                    else:
                        logger.debug(f"❌ {filename}: {response.status_code}")
                        
                except Exception as e:
                    logger.debug(f"requests エラー: {filename} - {e}")
                    continue
        
        return successful

def main():
    """メイン実行"""
    downloader = SimpleJRDBDownloader()
    
    print("🏇 JRDBシンプルダウンローダー")
    print("=" * 50)
    
    # 方法1: requests（高速）
    logger.info("🚀 方法1: requests + HTTPベーシック認証")
    requests_success = downloader.download_with_requests()
    
    if requests_success < 5:
        # 方法2: Selenium（確実）
        logger.info("🚀 方法2: Selenium + ブラウザ認証")
        selenium_success = downloader.login_and_download()
        total_success = requests_success + selenium_success
    else:
        total_success = requests_success
    
    # 結果表示
    print("\n" + "=" * 50)
    print("🎉 ダウンロード完了")
    print("=" * 50)
    print(f"📊 成功ファイル数: {total_success}")
    
    # ダウンロードしたファイル確認
    downloaded_files = list(downloader.download_dir.glob("*.lzh"))
    print(f"📁 LZHファイル: {len(downloaded_files)}個")
    
    if downloaded_files:
        print("\n🎯 ダウンロード済みファイル:")
        for f in sorted(downloaded_files)[:10]:
            size = f.stat().st_size
            print(f"  {f.name} ({size:,} bytes)")
    
    if total_success >= 5:
        print("\n✅ 十分なデータを取得しました！")
        print("💡 次のステップ:")
        print("  python download_jrdb_data.py  # ファイル展開")
        print("  make start-claude             # システム再起動")
        return True
    else:
        print("\n⚠️ データが不足しています")
        print("💡 手動ダウンロードを検討してください")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)