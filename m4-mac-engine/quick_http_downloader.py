#!/usr/bin/env python3
"""
超シンプルHTTPダウンローダー
直接HTTPベーシック認証でJRDBデータ取得
"""
import requests
from pathlib import Path
from datetime import datetime, timedelta
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_download():
    """シンプルなHTTP直接ダウンロード"""
    username = "25067698"
    password = "87086387"
    base_url = "http://www.jrdb.com/member/data"
    download_dir = Path("data/jrdb_real")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    auth = (username, password)
    successful = 0
    
    print("🏇 JRDBクイックダウンロード")
    print("=" * 40)
    
    # 過去7日の重要ファイルのみ
    file_types = ["sed", "kyi", "bac"]
    
    for days_ago in range(7):
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime("%y%m%d")
        
        for file_type in file_types:
            filename = f"{file_type.upper()}{date_str}.lzh"
            url = f"{base_url}/{file_type}/{filename}"
            output_path = download_dir / filename
            
            try:
                print(f"📥 試行: {filename}")
                
                # タイムアウト短縮でクイック試行
                response = requests.get(url, auth=auth, timeout=5)
                
                print(f"  ステータス: {response.status_code}")
                print(f"  サイズ: {len(response.content)} bytes")
                
                if response.status_code == 200 and len(response.content) > 100:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ 成功: {filename}")
                    successful += 1
                else:
                    print(f"⏭️  スキップ: {filename} (ステータス: {response.status_code})")
                    
            except Exception as e:
                print(f"❌ エラー: {filename} - {e}")
                
            # 成功したら15個で十分
            if successful >= 15:
                break
                
        if successful >= 15:
            break
    
    print(f"\n🎉 完了: {successful}個のファイルをダウンロード")
    
    # ダウンロードしたファイル確認
    downloaded = list(download_dir.glob("*.lzh"))
    if downloaded:
        print(f"📁 ダウンロード済み: {len(downloaded)}ファイル")
        for f in sorted(downloaded)[:5]:
            size = f.stat().st_size
            print(f"  {f.name} ({size:,} bytes)")
    
    return successful > 0

if __name__ == "__main__":
    success = quick_download()
    print(f"\n{'✅ 成功' if success else '❌ 失敗'}")