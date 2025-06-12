#!/usr/bin/env python3
"""
JRDBデータダウンロード手順表示
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config

def show_download_instructions():
    """ダウンロード手順を表示"""
    data_dir = config.data_dir / "jrdb_real"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*70)
    print("🏇 JRDBデータダウンロード手順")
    print("="*70)
    print()
    print("1. JRDBにログイン:")
    print(f"   URL: https://www.jrdb.com/member/")
    print(f"   ユーザー名: {config.jrdb_username}")
    print(f"   パスワード: {config.jrdb_password}")
    print()
    print("2. データダウンロードページへ移動")
    print("   https://www.jrdb.com/member/datadownload/")
    print()
    print("3. 以下のファイルをダウンロード（最新の日付分）:")
    print("   - SED******.lzh (成績データ)")
    print("   - KYI******.lzh (競走馬データ)")
    print("   - BAC******.lzh (番組データ)")
    print("   - CYB******.lzh (調教データ)")
    print("   - KAB******.lzh (開催データ)")
    print()
    print("4. ダウンロードしたファイルを以下のディレクトリに配置:")
    print(f"   {data_dir}")
    print()
    print("5. その後、以下のコマンドを実行:")
    print("   python download_jrdb_data.py")
    print()
    print("="*70)
    print()
    print("現在のデータディレクトリ状態:")
    print(f"パス: {data_dir}")
    
    # 既存ファイルチェック
    existing_files = list(data_dir.glob("*"))
    if existing_files:
        print(f"既存ファイル数: {len(existing_files)}")
        for f in existing_files[:5]:  # 最初の5個のみ表示
            print(f"  - {f.name}")
        if len(existing_files) > 5:
            print(f"  ... 他 {len(existing_files) - 5} ファイル")
    else:
        print("⚠️ まだファイルがありません")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    show_download_instructions()