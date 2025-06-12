#!/usr/bin/env python3
"""
動作するJRDBダウンローダー
画面に表示されているLzhリンクをクリックしてダウンロード
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging
from pathlib import Path
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingJRDBDownloader:
    def __init__(self):
        self.username = "25067698"
        self.password = "87086387"
        self.base_url = "http://www.jrdb.com"
        self.download_dir = Path("data/jrdb_real").absolute()
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_chrome(self):
        """Chrome設定（ダウンロード最適化）"""
        options = Options()
        
        # ダウンロード設定
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True,
        }
        options.add_experimental_option("prefs", prefs)
        
        # 基本設定
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        # ダウンロード許可
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(self.download_dir)
        })
        
        return driver
    
    def download_jrdb_data(self):
        """JRDBデータダウンロード実行"""
        logger.info("🚀 JRDBダウンロード開始")
        
        driver = self.setup_chrome()
        downloaded = 0
        
        try:
            # 1. 認証付きURLでアクセス
            auth_url = f"http://{self.username}:{self.password}@www.jrdb.com/member/data/"
            logger.info("📄 データページアクセス")
            driver.get(auth_url)
            time.sleep(3)
            
            # 2. ページが正しく表示されているか確認
            page_title = driver.title
            logger.info(f"📋 ページタイトル: {page_title}")
            
            # 3. Lzhリンクを見つけてクリック
            logger.info("🔍 Lzhリンク検索中...")
            
            # リンクテキスト「Lzh」を持つ要素を全て取得
            lzh_links = driver.find_elements(By.LINK_TEXT, "Lzh")
            logger.info(f"📊 Lzhリンク発見: {len(lzh_links)}個")
            
            # 各リンクをクリックしてダウンロード
            for i, link in enumerate(lzh_links[:15]):  # 最大15個
                try:
                    # リンクの情報取得
                    href = link.get_attribute('href')
                    
                    # 同じ行のテキストを取得してファイル名を推定
                    parent_row = link.find_element(By.XPATH, "./ancestor::tr")
                    row_text = parent_row.text
                    logger.info(f"📥 ダウンロード {i+1}: {row_text[:50]}...")
                    
                    # JavaScriptでクリック（より確実）
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)  # ダウンロード開始待機
                    
                    downloaded += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ ダウンロードエラー: {e}")
                    continue
            
            # 4. 別の方法: 直接URLパターンでアクセス
            if downloaded < 10:
                logger.info("📥 追加ダウンロード試行")
                
                # URLパターン: JRDB成績データ(SEC), 成績拡張データ(SED), 番組データ(BAC)など
                file_patterns = [
                    ("SEC", "JRDB成績データ"),
                    ("SED", "JRDB成績データ"),
                    ("SKB", "JRDB成績拡張データ"),
                    ("KAA", "JRDB開催データ"),
                    ("KAB", "JRDB開催データ"),
                    ("BAB", "JRDB番組データ"),
                    ("BAC", "JRDB番組データ"),
                    ("KTA", "JRDB登録馬データ"),
                    ("KZA", "JRDB騎手データ"),
                    ("CZA", "JRDB調教師データ"),
                    ("CSA", "JRDB調教師データ"),
                    ("MZA", "JRDB抹消馬データ"),
                    ("MSA", "JRDB抹消馬データ"),
                ]
                
                # 最近の日付で試行
                from datetime import datetime, timedelta
                today = datetime.now()
                
                for days_ago in range(7):
                    date = today - timedelta(days=days_ago)
                    date_str = date.strftime("%y%m%d")  # YYMMDD形式
                    
                    for file_code, description in file_patterns[:5]:  # 主要5種類
                        filename = f"{file_code}{date_str}.lzh"
                        file_url = f"{auth_url}{filename}"
                        
                        try:
                            logger.info(f"📥 直接アクセス: {filename}")
                            driver.get(file_url)
                            time.sleep(1)
                            
                            # ファイルが存在すればダウンロードされる
                            downloaded_file = self.download_dir / filename
                            if downloaded_file.exists():
                                logger.info(f"✅ ダウンロード成功: {filename}")
                                downloaded += 1
                                
                        except Exception as e:
                            logger.debug(f"スキップ: {filename}")
                            continue
                        
                        if downloaded >= 15:
                            break
                    
                    if downloaded >= 15:
                        break
            
            # 5. ダウンロード完了待機
            logger.info("⏳ ダウンロード完了待機中...")
            time.sleep(5)
            
            return downloaded
            
        except Exception as e:
            logger.error(f"❌ エラー: {e}")
            return downloaded
            
        finally:
            # デバッグ用スクリーンショット
            try:
                screenshot_path = self.download_dir / f"success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(str(screenshot_path))
                logger.info(f"📸 スクリーンショット保存: {screenshot_path}")
            except:
                pass
                
            driver.quit()

def check_downloads():
    """ダウンロードファイル確認"""
    download_dir = Path("data/jrdb_real")
    
    # ファイル一覧
    lzh_files = list(download_dir.glob("*.lzh"))
    zip_files = list(download_dir.glob("*.zip"))
    
    print(f"\n📊 ダウンロード結果:")
    print(f"  LZHファイル: {len(lzh_files)}個")
    print(f"  ZIPファイル: {len(zip_files)}個")
    
    if lzh_files or zip_files:
        print("\n📋 ダウンロード済みファイル:")
        all_files = sorted(lzh_files + zip_files, key=lambda x: x.stat().st_mtime, reverse=True)
        for f in all_files[:10]:
            size = f.stat().st_size
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            print(f"  {f.name} ({size:,} bytes) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return len(lzh_files) + len(zip_files)

def main():
    """メイン処理"""
    print("🏇 動作するJRDBダウンローダー")
    print("=" * 50)
    
    downloader = WorkingJRDBDownloader()
    
    # ダウンロード実行
    downloaded = downloader.download_jrdb_data()
    
    print(f"\n✅ ダウンロード試行: {downloaded}回")
    
    # ファイル確認
    total_files = check_downloads()
    
    if total_files > 0:
        print("\n🎉 ダウンロード成功！")
        print("💡 次のステップ:")
        print("  1. lha x *.lzh でファイル展開")
        print("  2. python jrdb_consolidation_tool.py でデータ統合")
        print("  3. python claude_main.py でシステム再起動")
    else:
        print("\n⚠️ ファイルが見つかりません")
        print("💡 ブラウザでの手動ダウンロードを検討してください")

if __name__ == "__main__":
    main()