#!/usr/bin/env python3
"""
TARGET エクスポートデータ処理ツール
TARGETから出力されたJRDBデータを本システムに取り込む
"""
import pandas as pd
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TargetDataProcessor:
    def __init__(self):
        self.import_dir = Path("data/target_export")
        self.output_dir = Path("data/jrdb_real")
        self.import_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process_target_csv(self, csv_file):
        """TARGET CSVファイル処理"""
        logger.info(f"📊 TARGET CSV処理: {csv_file}")
        
        try:
            # CSVデータ読み込み（エンコーディング自動判定）
            for encoding in ['shift-jis', 'cp932', 'utf-8']:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    break
                except:
                    continue
            
            # データ構造解析
            logger.info(f"  行数: {len(df)}")
            logger.info(f"  列数: {len(df.columns)}")
            logger.info(f"  列名: {list(df.columns)[:10]}")
            
            # JRDB形式に変換
            jrdb_data = self.convert_to_jrdb_format(df)
            
            # ファイル出力
            output_file = self.output_dir / f"TARGET_IMPORT_{csv_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(jrdb_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 変換完了: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 処理エラー: {e}")
            return False
    
    def convert_to_jrdb_format(self, df):
        """JRDB形式への変換"""
        jrdb_data = {
            'races': [],
            'horses': [],
            'results': [],
            'metadata': {
                'source': 'TARGET_EXPORT',
                'records': len(df)
            }
        }
        
        # データタイプを推定して分類
        if '馬名' in df.columns or '馬番' in df.columns:
            # 馬データ
            for _, row in df.iterrows():
                jrdb_data['horses'].append(row.to_dict())
        
        elif 'レース名' in df.columns or '開催' in df.columns:
            # レースデータ
            for _, row in df.iterrows():
                jrdb_data['races'].append(row.to_dict())
        
        else:
            # その他（結果データとして扱う）
            for _, row in df.iterrows():
                jrdb_data['results'].append(row.to_dict())
        
        return jrdb_data

def main():
    """メイン処理"""
    print("🎯 TARGET エクスポートデータ処理")
    print("=" * 50)
    
    processor = TargetDataProcessor()
    
    # インポートディレクトリのCSVファイル処理
    csv_files = list(processor.import_dir.glob("*.csv"))
    
    if csv_files:
        print(f"📁 発見: {len(csv_files)}個のCSVファイル")
        
        for csv_file in csv_files:
            processor.process_target_csv(csv_file)
        
        print("\n✅ 処理完了")
        print("💡 次のステップ: システムで変換データを使用")
    else:
        print("❌ CSVファイルが見つかりません")
        print(f"💡 TARGETからエクスポートしたCSVを以下に配置:")
        print(f"   {processor.import_dir.absolute()}")

if __name__ == "__main__":
    main()
