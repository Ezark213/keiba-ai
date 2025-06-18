#!/usr/bin/env python3
"""
TARGET/JRDB連携調査ツール
iamryosuke.comのツールを調査してJRDBデータ取得方法を探る
"""
import requests
from bs4 import BeautifulSoup
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def investigate_target_integration():
    """TARGET連携ツールの調査"""
    print("🎯 TARGET/JRDB連携ツール調査")
    print("=" * 50)
    
    # iamryosuke.comサイト調査
    target_site = "https://iamryosuke.com/"
    
    try:
        logger.info(f"🔍 サイト調査: {target_site}")
        
        response = requests.get(target_site, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # JRDBデータ関連のリンクを探す
            jrdb_links = []
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if 'jrdb' in href.lower() or 'jrdb' in text.lower():
                    jrdb_links.append({
                        'text': text,
                        'href': href,
                        'full_url': requests.compat.urljoin(target_site, href)
                    })
            
            if jrdb_links:
                print("\n📋 JRDB関連リンク発見:")
                for link in jrdb_links:
                    print(f"  - {link['text']}: {link['full_url']}")
            
            # TARGET連携ツールの特徴
            print("\n🎯 TARGET連携の利点:")
            print("  1. JRA-VANデータラボ経由でデータアクセス")
            print("  2. TARGETフロンティアJVで統合分析")
            print("  3. JRDB独自データを手軽に分析")
            print("  4. 会員提供ツールで信頼性あり")
            
            # 代替アプローチ
            print("\n💡 このアプローチの活用方法:")
            print("  1. TARGET経由でJRDBデータを取得")
            print("  2. エクスポート機能でデータ抽出")
            print("  3. 抽出データを本システムに取り込み")
            
        else:
            logger.warning(f"サイトアクセス失敗: {response.status_code}")
            
    except Exception as e:
        logger.error(f"調査エラー: {e}")
    
    # 代替案の提示
    print("\n" + "=" * 50)
    print("🎯 データ取得戦略の提案")
    print("=" * 50)
    
    strategies = [
        {
            "方法": "TARGET連携ツール活用",
            "利点": "確実なデータ取得、統合分析可能",
            "欠点": "JRA-VAN契約必要、手動エクスポート"
        },
        {
            "方法": "JRDB直接ダウンロード",
            "利点": "直接アクセス、自動化可能",
            "欠点": "認証の複雑さ、分散ファイル"
        },
        {
            "方法": "APIラッパー開発",
            "利点": "完全自動化、効率的",
            "欠点": "開発時間必要"
        }
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"\n{i}. {strategy['方法']}")
        print(f"   利点: {strategy['利点']}")
        print(f"   欠点: {strategy['欠点']}")
    
    return True

def create_target_export_processor():
    """TARGET エクスポートデータ処理ツール作成"""
    processor_code = '''#!/usr/bin/env python3
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
        
        print("\\n✅ 処理完了")
        print("💡 次のステップ: システムで変換データを使用")
    else:
        print("❌ CSVファイルが見つかりません")
        print(f"💡 TARGETからエクスポートしたCSVを以下に配置:")
        print(f"   {processor.import_dir.absolute()}")

if __name__ == "__main__":
    main()
'''
    
    # ツール保存
    tool_file = Path("target_export_processor.py")
    with open(tool_file, 'w', encoding='utf-8') as f:
        f.write(processor_code)
    
    logger.info(f"✅ TARGET処理ツール作成: {tool_file}")
    return tool_file

def main():
    """メイン処理"""
    # TARGET連携調査
    investigate_target_integration()
    
    # エクスポート処理ツール作成
    processor_file = create_target_export_processor()
    
    # 使用手順の表示
    print("\n" + "=" * 50)
    print("📋 推奨手順")
    print("=" * 50)
    print("1. iamryosuke.com からTARGET連携ツールをダウンロード")
    print("2. TARGETでJRDBデータを取り込み")
    print("3. 必要なデータをCSV形式でエクスポート")
    print("4. エクスポートしたCSVを data/target_export/ に配置")
    print(f"5. python {processor_file} で変換処理")
    print("6. 変換されたデータで本システムを実行")
    
    print("\n💡 このアプローチの利点:")
    print("  • 確実なデータ取得")
    print("  • ファイル分散問題の回避")
    print("  • TARGET の強力な分析機能も活用可能")

if __name__ == "__main__":
    main()