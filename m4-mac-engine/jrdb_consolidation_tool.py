#!/usr/bin/env python3
"""
JRDB分散ファイル統合ツール
機械学習用に分散したJRDBファイルを効率的に統合
"""
import pandas as pd
from pathlib import Path
import lzh
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JRDBConsolidationTool:
    def __init__(self):
        self.data_dir = Path("data/jrdb_real")
        self.consolidated_dir = Path("data/jrdb_consolidated")
        self.consolidated_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_lzh_files(self):
        """LZHファイルを一括展開"""
        logger.info("🗜️ LZHファイル展開開始")
        
        lzh_files = list(self.data_dir.glob("*.lzh"))
        extracted_count = 0
        
        for lzh_file in lzh_files:
            try:
                # lzh ライブラリを使用してファイル展開
                import subprocess
                extract_dir = self.data_dir / lzh_file.stem
                extract_dir.mkdir(exist_ok=True)
                
                # システムの lha コマンドを使用
                result = subprocess.run([
                    'lha', 'x', str(lzh_file), '-w', str(extract_dir)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✅ 展開完了: {lzh_file.name}")
                    extracted_count += 1
                else:
                    logger.warning(f"⚠️ 展開失敗: {lzh_file.name}")
                    
            except Exception as e:
                logger.error(f"❌ 展開エラー: {lzh_file.name} - {e}")
        
        logger.info(f"📊 展開完了: {extracted_count}/{len(lzh_files)}ファイル")
        return extracted_count
    
    def consolidate_by_type(self):
        """ファイルタイプ別に統合"""
        logger.info("📋 ファイルタイプ別統合開始")
        
        file_types = {
            'SED': '成績データ',
            'KYI': '競走馬データ', 
            'BAC': '番組データ',
            'CYB': 'サイバー指数',
            'KAB': 'カブリ指数'
        }
        
        consolidated_data = {}
        
        for file_type, description in file_types.items():
            logger.info(f"🔄 {file_type} ({description}) 統合中...")
            
            # 該当ファイル検索
            type_files = list(self.data_dir.glob(f"{file_type}*.txt"))
            
            if not type_files:
                logger.warning(f"⚠️ {file_type}ファイルが見つかりません")
                continue
            
            # ファイル統合
            all_data = []
            for txt_file in sorted(type_files):
                try:
                    # Shift-JISで読み込み
                    with open(txt_file, 'r', encoding='shift-jis', errors='ignore') as f:
                        lines = f.readlines()
                    
                    # 日付情報を追加
                    date_str = txt_file.stem[-6:]  # YYMMDDを抽出
                    for line in lines:
                        if line.strip():
                            all_data.append({
                                'date': date_str,
                                'data': line.strip(),
                                'source_file': txt_file.name
                            })
                    
                    logger.info(f"  📄 読み込み: {txt_file.name} ({len(lines)}行)")
                    
                except Exception as e:
                    logger.error(f"❌ 読み込みエラー: {txt_file.name} - {e}")
            
            if all_data:
                # 統合ファイル保存
                consolidated_file = self.consolidated_dir / f"{file_type}_consolidated.json"
                with open(consolidated_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)
                
                consolidated_data[file_type] = {
                    'count': len(all_data),
                    'files': len(type_files),
                    'description': description
                }
                
                logger.info(f"✅ {file_type}統合完了: {len(all_data)}レコード")
        
        return consolidated_data
    
    def create_ml_ready_dataset(self):
        """機械学習用データセット作成"""
        logger.info("🤖 ML用データセット作成")
        
        # 統合データ読み込み
        consolidated_files = list(self.consolidated_dir.glob("*_consolidated.json"))
        
        if not consolidated_files:
            logger.error("❌ 統合データが見つかりません")
            return False
        
        ml_dataset = {
            'races': [],
            'horses': [],
            'results': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source_files': len(consolidated_files),
                'data_period': 'latest'
            }
        }
        
        for consolidated_file in consolidated_files:
            file_type = consolidated_file.stem.replace('_consolidated', '')
            
            try:
                with open(consolidated_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                logger.info(f"📊 {file_type}: {len(data)}レコード処理中...")
                
                # ファイルタイプに応じて分類
                if file_type == 'SED':
                    ml_dataset['results'].extend(data)
                elif file_type == 'KYI':
                    ml_dataset['horses'].extend(data)
                elif file_type == 'BAC':
                    ml_dataset['races'].extend(data)
                
            except Exception as e:
                logger.error(f"❌ {file_type}処理エラー: {e}")
        
        # ML用データセット保存
        ml_file = self.consolidated_dir / "ml_ready_dataset.json"
        with open(ml_file, 'w', encoding='utf-8') as f:
            json.dump(ml_dataset, f, ensure_ascii=False, indent=2)
        
        total_records = (len(ml_dataset['races']) + 
                        len(ml_dataset['horses']) + 
                        len(ml_dataset['results']))
        
        logger.info(f"✅ ML用データセット作成完了: {total_records}レコード")
        logger.info(f"📁 保存先: {ml_file}")
        
        return True
    
    def generate_summary_report(self):
        """データ統合サマリーレポート生成"""
        logger.info("📋 サマリーレポート生成")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'data_sources': {},
            'consolidation_status': 'success',
            'recommendations': []
        }
        
        # 元ファイル確認
        lzh_files = list(self.data_dir.glob("*.lzh"))
        txt_files = list(self.data_dir.glob("*.txt"))
        consolidated_files = list(self.consolidated_dir.glob("*.json"))
        
        report['data_sources'] = {
            'lzh_files': len(lzh_files),
            'txt_files': len(txt_files),
            'consolidated_files': len(consolidated_files)
        }
        
        # 推奨事項
        if len(txt_files) < 15:
            report['recommendations'].append("追加のJRDBデータダウンロードを推奨")
        
        if len(consolidated_files) >= 3:
            report['recommendations'].append("機械学習に十分なデータが準備済み")
        
        # レポート保存
        report_file = self.consolidated_dir / "consolidation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report

def main():
    """メイン処理"""
    print("🏇 JRDB分散ファイル統合ツール")
    print("=" * 50)
    
    tool = JRDBConsolidationTool()
    
    # 1. LZHファイル展開
    extracted = tool.extract_lzh_files()
    
    # 2. ファイルタイプ別統合
    consolidated = tool.consolidate_by_type()
    
    # 3. ML用データセット作成
    ml_ready = tool.create_ml_ready_dataset()
    
    # 4. サマリーレポート
    report = tool.generate_summary_report()
    
    # 結果表示
    print("\n" + "=" * 50)
    print("🎉 統合処理完了")
    print("=" * 50)
    
    print(f"📊 処理結果:")
    print(f"  LZH展開: {extracted}ファイル")
    print(f"  統合完了: {len(consolidated)}タイプ")
    print(f"  ML準備: {'✅' if ml_ready else '❌'}")
    
    if consolidated:
        print(f"\n📋 統合データ:")
        for file_type, info in consolidated.items():
            print(f"  {file_type}: {info['count']}レコード ({info['description']})")
    
    print(f"\n💡 推奨事項:")
    for rec in report.get('recommendations', []):
        print(f"  • {rec}")
    
    if ml_ready:
        print(f"\n🚀 次のステップ:")
        print(f"  システムで統合データを使用して性能向上を実現")

if __name__ == "__main__":
    main()