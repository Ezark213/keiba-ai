#!/usr/bin/env python3
"""
手動JRDB取得サポートツール
ユーザーが手動でダウンロードする際のサポート
"""
from pathlib import Path
from datetime import datetime, timedelta
import shutil

def generate_download_urls():
    """ダウンロード用URL生成"""
    print("🏇 JRDBダウンロード用URL生成ツール")
    print("=" * 50)
    
    base_url = "http://www.jrdb.com/member/data"
    file_types = ["sed", "kyi", "bac", "cyb", "kab"]
    
    # 最近30日のURL生成
    urls = []
    for days_ago in range(30):
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime("%y%m%d")
        
        for file_type in file_types:
            filename = f"{file_type.upper()}{date_str}.lzh"
            url = f"{base_url}/{file_type}/{filename}"
            urls.append((filename, url))
    
    print(f"📋 生成URL数: {len(urls)}個")
    print("\n🎯 重要ファイル（最新7日分）:")
    
    # 重要ファイルのみ表示
    important_urls = []
    for days_ago in range(7):
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime("%y%m%d")
        
        for file_type in ["sed", "kyi", "bac"]:
            filename = f"{file_type.upper()}{date_str}.lzh"
            url = f"{base_url}/{file_type}/{filename}"
            important_urls.append((filename, url))
            print(f"  {filename}: {url}")
    
    # URL一覧をファイルに保存
    url_file = Path("jrdb_download_urls.txt")
    with open(url_file, 'w', encoding='utf-8') as f:
        f.write("# JRDB ダウンロード用URL一覧\n")
        f.write("# 手動ダウンロード用\n\n")
        f.write("## 重要ファイル（最新7日分）\n")
        for filename, url in important_urls:
            f.write(f"{filename}\t{url}\n")
        
        f.write("\n## 全ファイル（最新30日分）\n")
        for filename, url in urls:
            f.write(f"{filename}\t{url}\n")
    
    print(f"\n📁 URL一覧を保存: {url_file}")
    
    return important_urls

def manual_download_instructions():
    """手動ダウンロード手順"""
    print("\n" + "=" * 50)
    print("📋 手動ダウンロード手順")
    print("=" * 50)
    
    print("1. ブラウザでJRDBにアクセス:")
    print("   http://www.jrdb.com/member/")
    
    print("\n2. ログイン情報:")
    print("   ユーザー名: 25067698")
    print("   パスワード: 87086387")
    
    print("\n3. データダウンロードページ:")
    print("   http://www.jrdb.com/member/data/")
    
    print("\n4. 重要ファイル:")
    print("   - SED: 成績データ（最重要）")
    print("   - KYI: 競走馬データ（重要）") 
    print("   - BAC: 番組データ（推奨）")
    
    print("\n5. ダウンロード先:")
    download_dir = Path("data/jrdb_real")
    print(f"   {download_dir.absolute()}")
    
    print("\n6. 必要数:")
    print("   各タイプ5-10ファイルで十分")
    
    return str(download_dir.absolute())

def check_manual_downloads():
    """手動ダウンロードファイルチェック"""
    download_dir = Path("data/jrdb_real")
    
    print("\n" + "=" * 50)
    print("🔍 ダウンロードファイルチェック")
    print("=" * 50)
    
    # LZHファイル確認
    lzh_files = list(download_dir.glob("*.lzh"))
    print(f"📁 LZHファイル: {len(lzh_files)}個")
    
    if lzh_files:
        print("\n📋 ダウンロード済みファイル:")
        file_types = {"SED": 0, "KYI": 0, "BAC": 0, "CYB": 0, "KAB": 0}
        
        for f in sorted(lzh_files):
            size = f.stat().st_size
            file_type = f.name[:3]
            if file_type in file_types:
                file_types[file_type] += 1
            print(f"  {f.name} ({size:,} bytes)")
        
        print(f"\n📊 ファイルタイプ別数:")
        for ftype, count in file_types.items():
            status = "✅" if count >= 5 else "⚠️" if count > 0 else "❌"
            print(f"  {status} {ftype}: {count}個")
        
        total_sufficient = sum(1 for count in file_types.values() if count >= 5)
        
        if total_sufficient >= 3:
            print(f"\n🎉 十分なデータが揃いました！")
            print(f"💡 次のステップ: python download_jrdb_data.py")
            return True
        else:
            print(f"\n⚠️ データが不足しています")
            print(f"💡 追加ダウンロードが必要: 各タイプ5個以上")
            return False
    else:
        print("\n❌ ダウンロードファイルが見つかりません")
        return False

def setup_download_folder():
    """ダウンロードフォルダ準備"""
    download_dir = Path("data/jrdb_real")
    download_dir.mkdir(parents=True, exist_ok=True)
    
    # サブフォルダも準備
    for subdir in ["sed", "kyi", "bac", "cyb", "kab"]:
        (download_dir / subdir).mkdir(exist_ok=True)
    
    print(f"📁 ダウンロードフォルダ準備完了: {download_dir.absolute()}")

def main():
    """メイン処理"""
    setup_download_folder()
    
    # URL生成
    important_urls = generate_download_urls()
    
    # 手動ダウンロード手順
    download_path = manual_download_instructions()
    
    # 現在のファイルチェック
    has_enough = check_manual_downloads()
    
    print("\n" + "=" * 50)
    print("🎯 まとめ")
    print("=" * 50)
    
    if has_enough:
        print("✅ 十分なデータがあります")
        print("🚀 システム再起動可能")
    else:
        print("📥 手動ダウンロードが必要")
        print("📋 重要URL一覧: jrdb_download_urls.txt")
        print(f"📁 保存先: {download_path}")
        print("💡 各タイプ5-10ファイルをダウンロードしてください")

if __name__ == "__main__":
    main()