#!/usr/bin/env python3
"""
確実なJRDBダウンローダー
Seleniumでブラウザ操作を完全自動化
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import logging
from pathlib import Path
from datetime import datetime, timedelta
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReliableJRDBDownloader:
    def __init__(self):
        self.username = "25067698"
        self.password = "87086387"
        self.base_url = "http://www.jrdb.com"
        self.download_dir = Path("data/jrdb_real").absolute()
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_chrome_for_download(self):
        """ダウンロード最適化Chrome設定"""
        options = Options()
        
        # ダウンロード設定
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.default_content_settings.popups": 0
        }
        options.add_experimental_option("prefs", prefs)
        
        # ヘッドレスモードは使わない（ダウンロードのため）
        # options.add_argument('--headless')
        
        # その他の設定
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 認証情報を保存
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        
        # ダウンロード動作を有効化
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(self.download_dir)
        })
        
        return driver
    
    def handle_http_auth(self, driver):
        """HTTPベーシック認証処理"""
        logger.info("🔐 認証処理開始")
        
        try:
            # 方法1: Alert経由での認証
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert = Alert(driver)
            alert.send_keys(f"{self.username}\t{self.password}")
            alert.accept()
            logger.info("✅ Alert認証成功")
            return True
        except:
            pass
        
        try:
            # 方法2: URL認証
            auth_url = f"http://{self.username}:{self.password}@www.jrdb.com/member/"
            driver.get(auth_url)
            time.sleep(3)
            logger.info("✅ URL認証成功")
            return True
        except:
            pass
        
        # 方法3: JavaScript認証
        try:
            driver.execute_script("""
                var username = arguments[0];
                var password = arguments[1];
                
                // XMLHttpRequestで認証
                var xhr = new XMLHttpRequest();
                xhr.open('GET', '/member/', false, username, password);
                xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
                xhr.send();
            """, self.username, self.password)
            logger.info("✅ JavaScript認証成功")
            return True
        except:
            pass
        
        return False
    
    def download_file_directly(self, driver, file_url, filename):
        """ファイル直接ダウンロード"""
        try:
            # JavaScriptでダウンロード実行
            driver.execute_script("""
                var url = arguments[0];
                var filename = arguments[1];
                
                // Fetch APIで取得
                fetch(url, {
                    credentials: 'include',
                    headers: {
                        'Authorization': 'Basic ' + btoa(arguments[2] + ':' + arguments[3])
                    }
                })
                .then(response => response.blob())
                .then(blob => {
                    var a = document.createElement('a');
                    var url = window.URL.createObjectURL(blob);
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                });
            """, file_url, filename, self.username, self.password)
            
            time.sleep(2)  # ダウンロード待機
            
            # ファイル存在確認
            downloaded_file = self.download_dir / filename
            if downloaded_file.exists() and downloaded_file.stat().st_size > 100:
                return True
                
        except Exception as e:
            logger.debug(f"ダウンロードエラー: {filename} - {e}")
            
        return False
    
    def reliable_download_process(self):
        """確実なダウンロードプロセス"""
        logger.info("🚀 確実なダウンロードプロセス開始")
        
        driver = self.setup_chrome_for_download()
        downloaded = 0
        
        try:
            # 1. メインページアクセス
            logger.info("📄 JRDBメインページアクセス")
            driver.get(f"{self.base_url}/member/")
            time.sleep(3)
            
            # 2. 認証処理
            if self.handle_http_auth(driver):
                logger.info("✅ 認証成功")
            else:
                logger.warning("⚠️ 認証確認中...")
            
            # 3. データページへ移動
            logger.info("📊 データページへ移動")
            driver.get(f"{self.base_url}/member/data/")
            time.sleep(2)
            
            # 4. ファイルリンクを探してダウンロード
            file_types = ["sed", "kyi", "bac"]
            
            for file_type in file_types:
                logger.info(f"🔍 {file_type.upper()}ファイル検索中...")
                
                # フォルダリンクをクリック
                try:
                    folder_link = driver.find_element(By.LINK_TEXT, file_type)
                    folder_link.click()
                    time.sleep(2)
                    
                    # ファイルリンクを取得
                    file_links = driver.find_elements(By.XPATH, f"//a[contains(@href, '.lzh')]")
                    
                    for link in file_links[:5]:  # 各タイプ5個まで
                        href = link.get_attribute('href')
                        filename = link.text
                        
                        logger.info(f"📥 ダウンロード試行: {filename}")
                        
                        # クリックでダウンロード
                        try:
                            link.click()
                            time.sleep(2)
                            
                            # ファイル確認
                            downloaded_file = self.download_dir / filename
                            if downloaded_file.exists():
                                logger.info(f"✅ ダウンロード成功: {filename}")
                                downloaded += 1
                            else:
                                # 直接ダウンロード試行
                                if self.download_file_directly(driver, href, filename):
                                    logger.info(f"✅ 直接ダウンロード成功: {filename}")
                                    downloaded += 1
                                    
                        except Exception as e:
                            logger.debug(f"クリックエラー: {filename} - {e}")
                    
                    # 戻る
                    driver.back()
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"フォルダアクセスエラー: {file_type} - {e}")
            
            # 5. 直接URLでダウンロード試行
            if downloaded < 5:
                logger.info("📥 直接URLダウンロード試行")
                
                for days_ago in range(7):
                    date = datetime.now() - timedelta(days=days_ago)
                    date_str = date.strftime("%y%m%d")
                    
                    for file_type in file_types:
                        filename = f"{file_type.upper()}{date_str}.lzh"
                        file_url = f"{self.base_url}/member/data/{file_type}/{filename}"
                        
                        # 認証付きURL
                        auth_url = f"http://{self.username}:{self.password}@www.jrdb.com/member/data/{file_type}/{filename}"
                        
                        logger.info(f"📥 直接URL試行: {filename}")
                        
                        # 新しいタブで開く
                        driver.execute_script(f"window.open('{auth_url}', '_blank');")
                        time.sleep(2)
                        
                        # タブを閉じる
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        
                        # ファイル確認
                        downloaded_file = self.download_dir / filename
                        if downloaded_file.exists() and downloaded_file.stat().st_size > 100:
                            logger.info(f"✅ ダウンロード成功: {filename}")
                            downloaded += 1
                            
                            if downloaded >= 15:
                                break
                    
                    if downloaded >= 15:
                        break
            
            return downloaded
            
        except Exception as e:
            logger.error(f"❌ プロセスエラー: {e}")
            return downloaded
            
        finally:
            # スクリーンショット保存（デバッグ用）
            try:
                screenshot_path = self.download_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(str(screenshot_path))
                logger.info(f"📸 スクリーンショット保存: {screenshot_path}")
            except:
                pass
                
            time.sleep(5)  # ダウンロード完了待機
            driver.quit()

def main():
    """メイン処理"""
    print("🏇 確実なJRDBダウンローダー")
    print("=" * 50)
    
    downloader = ReliableJRDBDownloader()
    
    # ダウンロード実行
    downloaded = downloader.reliable_download_process()
    
    # 結果表示
    print("\n" + "=" * 50)
    print("📊 ダウンロード結果")
    print("=" * 50)
    print(f"✅ ダウンロード成功: {downloaded}ファイル")
    
    # ファイル確認
    lzh_files = list(downloader.download_dir.glob("*.lzh"))
    txt_files = list(downloader.download_dir.glob("*.txt"))
    
    print(f"📁 保存先: {downloader.download_dir}")
    print(f"📦 LZHファイル: {len(lzh_files)}個")
    print(f"📄 テキストファイル: {len(txt_files)}個")
    
    if lzh_files:
        print("\n📋 ダウンロード済みファイル:")
        for f in sorted(lzh_files)[:10]:
            size = f.stat().st_size
            print(f"  {f.name} ({size:,} bytes)")
    
    # デバッグ画像確認
    debug_images = list(downloader.download_dir.glob("debug_*.png"))
    if debug_images:
        print(f"\n📸 デバッグ画像: {len(debug_images)}枚")
        print("  ブラウザ画面を確認してください")
    
    if downloaded > 0:
        print("\n🎉 ダウンロード成功！")
        print("💡 次のステップ:")
        print("  1. LZHファイルを展開")
        print("  2. データ処理実行")
        print("  3. 予測システム再起動")
    else:
        print("\n⚠️ ダウンロードできませんでした")
        print("💡 デバッグ画像を確認してください")

if __name__ == "__main__":
    main()