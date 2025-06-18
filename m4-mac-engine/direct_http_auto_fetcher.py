#!/usr/bin/env python3
"""
直接HTTP自動取得システム
requestsとurllibで直接JRDBデータを自動取得
"""
import requests
from requests.auth import HTTPBasicAuth
import urllib.request
import base64
from pathlib import Path
from datetime import datetime, timedelta
import logging
import time
import subprocess
import schedule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectHTTPAutoFetcher:
    def __init__(self):
        self.username = "25067698"
        self.password = "87086387"
        self.base_url = "http://www.jrdb.com/member/data"
        self.download_dir = Path("data/jrdb_real")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 認証ヘッダー作成
        credentials = f"{self.username}:{self.password}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()
        
    def download_with_urllib(self, url, filename):
        """urllib経由でダウンロード"""
        try:
            # 認証マネージャー設定
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, url, self.username, self.password)
            
            auth_handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(auth_handler)
            urllib.request.install_opener(opener)
            
            # ダウンロード実行
            response = urllib.request.urlopen(url)
            content = response.read()
            
            if len(content) > 100:  # 有効なファイルサイズ
                output_path = self.download_dir / filename
                with open(output_path, 'wb') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            logger.debug(f"urllib失敗: {filename} - {e}")
            
        return False
    
    def download_with_requests(self, url, filename):
        """requests経由でダウンロード"""
        try:
            # セッション作成
            session = requests.Session()
            session.auth = (self.username, self.password)
            
            # ヘッダー設定
            headers = {
                'Authorization': f'Basic {self.auth_header}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200 and len(response.content) > 100:
                output_path = self.download_dir / filename
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
                
        except Exception as e:
            logger.debug(f"requests失敗: {filename} - {e}")
            
        return False
    
    def auto_fetch_latest_data(self):
        """最新データ自動取得"""
        logger.info("🚀 直接HTTP自動取得開始")
        
        successful = 0
        file_types = ["sed", "kyi", "bac"]
        
        # 最近の日付から順に試行
        for days_ago in range(30):
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%y%m%d")
            
            for file_type in file_types:
                filename = f"{file_type.upper()}{date_str}.lzh"
                url = f"{self.base_url}/{file_type}/{filename}"
                
                logger.info(f"📥 取得試行: {filename}")
                
                # 複数の方法で試行
                if self.download_with_urllib(url, filename):
                    logger.info(f"✅ urllib成功: {filename}")
                    successful += 1
                elif self.download_with_requests(url, filename):
                    logger.info(f"✅ requests成功: {filename}")
                    successful += 1
                else:
                    logger.debug(f"⏭️ スキップ: {filename}")
                
                # レート制限
                time.sleep(0.5)
                
                # 十分な数を取得したら終了
                if successful >= 15:
                    return successful
        
        return successful
    
    def process_downloaded_files(self):
        """ダウンロードファイル処理"""
        logger.info("📊 ダウンロードファイル処理")
        
        # LZHファイル展開
        lzh_files = list(self.download_dir.glob("*.lzh"))
        extracted = 0
        
        for lzh_file in lzh_files:
            try:
                # lhaコマンドで展開
                result = subprocess.run([
                    'lha', 'x', str(lzh_file), '-w', str(self.download_dir)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ 展開: {lzh_file.name}")
                    extracted += 1
                    
            except Exception as e:
                logger.error(f"展開エラー: {e}")
        
        # 統合処理実行
        if extracted > 0:
            try:
                subprocess.run(['python3', 'jrdb_consolidation_tool.py'])
                logger.info("✅ データ統合完了")
            except:
                pass
        
        return extracted
    
    def run_complete_cycle(self):
        """完全な取得サイクル実行"""
        logger.info(f"🕐 自動取得サイクル開始: {datetime.now()}")
        
        # 1. データ取得
        downloaded = self.auto_fetch_latest_data()
        logger.info(f"📥 ダウンロード: {downloaded}ファイル")
        
        # 2. ファイル処理
        if downloaded > 0:
            processed = self.process_downloaded_files()
            logger.info(f"🗜️ 処理完了: {processed}ファイル")
            
            # 3. システム再起動
            logger.info("🔄 予測システム再起動")
            subprocess.Popen(['python3', 'claude_main.py'])
            
            return True
        
        return False

def create_systemd_service():
    """Systemdサービス作成（Linux用）"""
    service_content = """[Unit]
Description=JRDB Auto Fetcher Service
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/path/to/keiba-prediction-v3/m4-mac-engine
ExecStart=/usr/bin/python3 /path/to/direct_http_auto_fetcher.py --daemon
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("jrdb-auto-fetcher.service")
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    logger.info(f"✅ Systemdサービスファイル作成: {service_file}")
    print("💡 インストール方法:")
    print("  sudo cp jrdb-auto-fetcher.service /etc/systemd/system/")
    print("  sudo systemctl enable jrdb-auto-fetcher")
    print("  sudo systemctl start jrdb-auto-fetcher")

def create_launchd_plist():
    """LaunchDaemon作成（macOS用）"""
    plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.keiba.jrdb-auto-fetcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/kokiriho/Documents/Projects/uma/pegasus-ai/keiba-prediction-v3/m4-mac-engine/direct_http_auto_fetcher.py</string>
        <string>--daemon</string>
    </array>
    <key>StartInterval</key>
    <integer>21600</integer>
    <key>WorkingDirectory</key>
    <string>/Users/kokiriho/Documents/Projects/uma/pegasus-ai/keiba-prediction-v3/m4-mac-engine</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
    
    plist_file = Path("com.keiba.jrdb-auto-fetcher.plist")
    with open(plist_file, 'w') as f:
        f.write(plist_content)
    
    logger.info(f"✅ LaunchDaemonファイル作成: {plist_file}")
    print("💡 インストール方法:")
    print("  sudo cp com.keiba.jrdb-auto-fetcher.plist /Library/LaunchDaemons/")
    print("  sudo launchctl load /Library/LaunchDaemons/com.keiba.jrdb-auto-fetcher.plist")

def daemon_mode():
    """デーモンモード実行"""
    logger.info("🤖 JRDBデータ自動取得デーモン起動")
    
    fetcher = DirectHTTPAutoFetcher()
    
    # スケジュール設定
    schedule.every(6).hours.do(fetcher.run_complete_cycle)
    schedule.every().day.at("06:00").do(fetcher.run_complete_cycle)
    schedule.every().day.at("18:00").do(fetcher.run_complete_cycle)
    
    # 初回実行
    fetcher.run_complete_cycle()
    
    # 永続実行
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    """メイン処理"""
    import sys
    
    if '--daemon' in sys.argv:
        daemon_mode()
    else:
        print("🤖 直接HTTP自動取得システム")
        print("=" * 50)
        
        fetcher = DirectHTTPAutoFetcher()
        
        # 単発実行
        success = fetcher.run_complete_cycle()
        
        if success:
            print("\n✅ 自動取得成功！")
            
            # ファイル確認
            lzh_files = list(fetcher.download_dir.glob("*.lzh"))
            txt_files = list(fetcher.download_dir.glob("*.txt"))
            
            print(f"📊 取得結果:")
            print(f"  LZHファイル: {len(lzh_files)}個")
            print(f"  テキストファイル: {len(txt_files)}個")
            
            # 自動化設定作成
            import platform
            if platform.system() == "Darwin":  # macOS
                create_launchd_plist()
            else:  # Linux
                create_systemd_service()
            
            print("\n🚀 完全自動化の準備完了！")
            print("💡 デーモンモードで実行: python3 direct_http_auto_fetcher.py --daemon")
            
        else:
            print("\n⚠️ 自動取得に失敗しました")
            print("💡 認証情報を確認してください")

if __name__ == "__main__":
    main()