#!/usr/bin/env python3
"""
JRDBデータダウンロードヘルパー
ユーザーがJRDBから手動でダウンロードしたデータを整理
"""
import os
import sys
from pathlib import Path
from loguru import logger
import shutil
import lhafile
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config


class JRDBDataHelper:
    """JRDBデータダウンロードヘルパー"""
    
    def __init__(self):
        self.data_dir = config.data_dir / "jrdb_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # ダウンロードディレクトリ（ユーザーのダウンロードフォルダ）
        self.download_dir = Path.home() / "Downloads"
        
        logger.info("JRDBデータヘルパー初期化完了")
    
    def show_instructions(self):
        """ダウンロード手順を表示"""
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
        print()
        print("3. 以下のファイルをダウンロード（最新の日付分）:")
        print("   - SED******.lzh (成績データ)")
        print("   - KYI******.lzh (競走馬データ)")
        print("   - BAC******.lzh (番組データ)")
        print("   - CYB******.lzh (調教データ)")
        print("   - KAB******.lzh (開催データ)")
        print()
        print("4. ダウンロード完了後、このスクリプトを再実行してください")
        print()
        print("="*70)
        print()
    
    def find_downloaded_files(self):
        """ダウンロードフォルダからJRDBファイルを検索"""
        logger.info(f"📁 ダウンロードフォルダをスキャン: {self.download_dir}")
        
        jrdb_files = []
        patterns = ["SED*.lzh", "KYI*.lzh", "BAC*.lzh", "CYB*.lzh", "KAB*.lzh"]
        
        for pattern in patterns:
            files = list(self.download_dir.glob(pattern))
            jrdb_files.extend(files)
        
        if jrdb_files:
            logger.info(f"✅ {len(jrdb_files)}個のJRDBファイルを発見:")
            for file in jrdb_files:
                logger.info(f"  - {file.name}")
        else:
            logger.warning("⚠️ JRDBファイルが見つかりません")
        
        return jrdb_files
    
    def move_files_to_data_dir(self, files):
        """ファイルをデータディレクトリへ移動"""
        moved_count = 0
        
        for file in files:
            try:
                dest = self.data_dir / file.name
                shutil.move(str(file), str(dest))
                logger.success(f"✅ 移動完了: {file.name}")
                moved_count += 1
            except Exception as e:
                logger.error(f"❌ 移動失敗: {file.name} - {e}")
        
        return moved_count
    
    def extract_lzh_files(self):
        """LZHファイルを展開"""
        lzh_files = list(self.data_dir.glob("*.lzh"))
        
        if not lzh_files:
            logger.warning("⚠️ 展開するLZHファイルがありません")
            return 0
        
        extracted_count = 0
        
        for lzh_file in lzh_files:
            try:
                logger.info(f"📦 展開中: {lzh_file.name}")
                
                with lhafile.Lhafile(str(lzh_file)) as lha:
                    for info in lha.infoiter():
                        # テキストファイルを展開
                        content = lha.read(info.filename)
                        
                        # ファイル名を大文字に変換して保存
                        txt_filename = info.filename.upper()
                        if not txt_filename.endswith('.TXT'):
                            txt_filename = txt_filename.replace('.', '.TXT')
                        
                        txt_path = self.data_dir / txt_filename
                        
                        with open(txt_path, 'wb') as f:
                            f.write(content)
                        
                        logger.info(f"  → {txt_filename}")
                        extracted_count += 1
                
                # 展開後、LZHファイルは保持（必要に応じて削除可能）
                # lzh_file.unlink()
                
            except Exception as e:
                logger.error(f"❌ 展開エラー: {lzh_file.name} - {e}")
        
        return extracted_count
    
    def show_data_status(self):
        """データディレクトリの状態を表示"""
        print("\n" + "="*70)
        print("📊 JRDBデータ状態")
        print("="*70)
        print(f"データディレクトリ: {self.data_dir}")
        print()
        
        # ファイルタイプ別にカウント
        file_types = {
            'SED': 0,  # 成績データ
            'KYI': 0,  # 競走馬データ
            'BAC': 0,  # 番組データ
            'CYB': 0,  # 調教データ
            'KAB': 0,  # 開催データ
        }
        
        txt_files = list(self.data_dir.glob("*.txt")) + list(self.data_dir.glob("*.TXT"))
        
        for txt_file in txt_files:
            file_name = txt_file.name.upper()
            for file_type in file_types:
                if file_name.startswith(file_type):
                    file_types[file_type] += 1
        
        print("ファイルタイプ別:")
        for file_type, count in file_types.items():
            status = "✅" if count > 0 else "❌"
            print(f"  {status} {file_type}: {count}ファイル")
        
        print()
        print(f"合計: {len(txt_files)}ファイル")
        print("="*70)
    
    def run(self):
        """メイン処理"""
        print("\n🏇 JRDB データヘルパー")
        print("競馬予測システム v3.0 - 本物のデータで80%還元率を目指す！")
        
        # 手順表示
        self.show_instructions()
        
        # ダウンロードファイルを検索
        downloaded_files = self.find_downloaded_files()
        
        if downloaded_files:
            response = input("\n💾 ファイルをシステムに取り込みますか？ (y/n): ")
            
            if response.lower() == 'y':
                # ファイル移動
                moved = self.move_files_to_data_dir(downloaded_files)
                logger.info(f"✅ {moved}個のファイルを移動しました")
                
                # LZH展開
                extracted = self.extract_lzh_files()
                logger.info(f"✅ {extracted}個のテキストファイルを展開しました")
        
        # 最終状態表示
        self.show_data_status()
        
        if any(self.data_dir.glob("*.txt")) or any(self.data_dir.glob("*.TXT")):
            print("\n✅ データの準備が完了しました！")
            print("以下のコマンドでシステムを起動できます:")
            print("  make start-claude")
        else:
            print("\n⚠️ まだデータがありません。上記の手順に従ってダウンロードしてください。")


if __name__ == "__main__":
    helper = JRDBDataHelper()
    helper.run()