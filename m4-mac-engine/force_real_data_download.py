#!/usr/bin/env python3
"""
強制的に本物のJRDBデータをダウンロード
あらゆる手段を使って実データを取得
"""
import subprocess
import sys
import time
from pathlib import Path
from loguru import logger

def force_download_real_jrdb_data():
    """本物のJRDBデータを強制ダウンロード"""
    
    logger.info("🚨 本物のJRDBデータ強制ダウンロード開始")
    logger.info("ユーザーの環境でブラウザを開いてJRDBにアクセスします")
    
    # ユーザーのブラウザでJRDBにアクセス
    jrdb_url = "https://jrdb.com/member/"
    
    print("\n" + "="*70)
    print("🏇 JRDBデータ取得 - 重要指示")
    print("="*70)
    print("以下の手順を実行してください:")
    print()
    print("1. ブラウザが自動で開きます")
    print("2. JRDBにログイン:")
    print("   ユーザー名: 25067698")
    print("   パスワード: 87086387")
    print()
    print("3. データダウンロードページへ移動")
    print("4. 最新の以下ファイルをダウンロード:")
    print("   - SED******.lzh (成績データ)")
    print("   - KYI******.lzh (競走馬データ)")
    print("   - BAC******.lzh (番組データ)")
    print()
    print("5. ダウンロード完了後、Enterキーを押してください")
    print("="*70)
    
    # ブラウザを開く
    try:
        if sys.platform.startswith('darwin'):  # macOS
            subprocess.run(['open', jrdb_url])
        elif sys.platform.startswith('win'):   # Windows
            subprocess.run(['start', jrdb_url], shell=True)
        else:  # Linux
            subprocess.run(['xdg-open', jrdb_url])
        
        logger.success("✅ ブラウザでJRDBを開きました")
        
    except Exception as e:
        logger.error(f"ブラウザ起動失敗: {e}")
        print(f"\n手動でアクセスしてください: {jrdb_url}")
    
    # ユーザーの操作を待機
    input("\nダウンロード完了後、Enterキーを押してください...")
    
    # ダウンロードフォルダをチェック
    download_dir = Path.home() / "Downloads"
    logger.info(f"📁 ダウンロードフォルダをチェック: {download_dir}")
    
    # JRDBファイルを検索
    jrdb_files = []
    patterns = ["SED*.lzh", "KYI*.lzh", "BAC*.lzh", "CYB*.lzh", "KAB*.lzh"]
    
    for pattern in patterns:
        files = list(download_dir.glob(pattern))
        jrdb_files.extend(files)
    
    if jrdb_files:
        logger.success(f"✅ {len(jrdb_files)}個のJRDBファイルを発見")
        for file in jrdb_files:
            logger.info(f"  - {file.name}")
        
        # ファイル移動の確認
        response = input("\nこれらのファイルをシステムに取り込みますか？ (y/n): ")
        
        if response.lower() == 'y':
            # download_jrdb_data.pyを実行
            logger.info("🔄 データ取り込み実行中...")
            try:
                subprocess.run([sys.executable, "download_jrdb_data.py"], check=True)
                logger.success("✅ 本物のJRDBデータ取り込み完了")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ データ取り込み失敗: {e}")
                return False
        else:
            logger.warning("データ取り込みをキャンセルしました")
            return False
    else:
        logger.error("❌ JRDBファイルが見つかりません")
        logger.info("以下を確認してください:")
        logger.info("1. JRDBに正しくログインできているか")
        logger.info("2. データダウンロードページにアクセスできているか")
        logger.info("3. ファイルが正常にダウンロードされているか")
        return False


if __name__ == "__main__":
    success = force_download_real_jrdb_data()
    
    if success:
        print("\n✅ 本物のJRDBデータ取得成功！")
        print("システムを起動してください: make start-claude")
    else:
        print("\n❌ データ取得に失敗しました")
        print("手動でJRDBからデータをダウンロードしてください")