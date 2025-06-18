#!/usr/bin/env python3
"""
JRDBer4TF取得スクリプト
iamryosuke.comから JRDBer4TFツールを調査・取得
"""
import requests
from bs4 import BeautifulSoup
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JRDBer4TFFetcher:
    def __init__(self):
        self.base_url = "https://iamryosuke.com"
        self.download_dir = Path("tools/jrdber4tf")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch_jrdber4tf_info(self):
        """JRDBer4TF情報取得"""
        logger.info("🔍 JRDBer4TF情報取得開始")
        
        # JRDBer4TF公開ページ
        jrdber_url = f"{self.base_url}/archives/77"
        
        try:
            response = requests.get(jrdber_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # タイトル確認
                title = soup.find('h1', class_='entry-title')
                if title:
                    logger.info(f"📋 記事タイトル: {title.get_text(strip=True)}")
                
                # ダウンロードリンク検索
                download_links = []
                
                # リンクパターン
                patterns = [
                    r'JRDBer4TF.*\.zip',
                    r'JRDBer4TF.*\.lzh',
                    r'download.*JRDBer4TF',
                    r'https://.*JRDBer4TF.*'
                ]
                
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # パターンマッチ
                    for pattern in patterns:
                        if re.search(pattern, href, re.IGNORECASE) or re.search(pattern, text, re.IGNORECASE):
                            full_url = requests.compat.urljoin(self.base_url, href)
                            download_links.append({
                                'text': text,
                                'url': full_url,
                                'filename': href.split('/')[-1] if '/' in href else 'JRDBer4TF.zip'
                            })
                            break
                
                # 本文中のダウンロード情報
                content = soup.find('div', class_='entry-content')
                if content:
                    # ダウンロード情報抽出
                    paragraphs = content.find_all('p')
                    for p in paragraphs:
                        text = p.get_text()
                        if 'ダウンロード' in text or 'download' in text.lower():
                            logger.info(f"📝 ダウンロード情報: {text[:100]}...")
                
                # 結果表示
                if download_links:
                    logger.info(f"✅ ダウンロードリンク発見: {len(download_links)}個")
                    for link in download_links:
                        print(f"  📥 {link['text']}: {link['url']}")
                    return download_links
                else:
                    logger.warning("⚠️ 直接ダウンロードリンクが見つかりません")
                    
                    # 代替手順表示
                    self.show_manual_instructions()
                    
            else:
                logger.error(f"❌ ページアクセス失敗: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ 取得エラー: {e}")
            
        return []
    
    def show_manual_instructions(self):
        """手動ダウンロード手順"""
        print("\n" + "=" * 50)
        print("📋 JRDBer4TF手動取得手順")
        print("=" * 50)
        
        print("1. ブラウザでアクセス:")
        print(f"   {self.base_url}/archives/77")
        
        print("\n2. ページ内のダウンロードリンクを探す:")
        print("   - 「JRDBer4TF」というファイル名")
        print("   - zipまたはlzh形式")
        
        print("\n3. ダウンロード先:")
        print(f"   {self.download_dir.absolute()}")
        
        print("\n4. TARGET環境準備:")
        print("   - TARGET frontier JVインストール")
        print("   - JRA-VANデータラボ契約")
        
        print("\n5. JRDBer4TF設定:")
        print("   - JRDBアカウント情報設定")
        print("   - データ取り込み実行")
    
    def create_data_pipeline(self):
        """データパイプライン作成"""
        pipeline_code = '''#!/usr/bin/env python3
"""
JRDBer4TF データパイプライン
TARGET経由でJRDBデータを効率的に取得・処理
"""
import subprocess
from pathlib import Path
import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JRDBDataPipeline:
    def __init__(self):
        self.target_dir = Path("C:/TARGET")  # Windows標準パス
        self.export_dir = Path("data/target_export")
        self.jrdb_dir = Path("data/jrdb_real")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.jrdb_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_jrdber4tf(self):
        """JRDBer4TF初期設定"""
        logger.info("🔧 JRDBer4TF設定")
        
        config = {
            'jrdb_username': '25067698',
            'jrdb_password': '87086387',
            'target_path': str(self.target_dir),
            'auto_update': True,
            'data_types': ['SED', 'KYI', 'BAC', 'CYB', 'KAB']
        }
        
        config_file = Path("jrdber4tf_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 設定ファイル作成: {config_file}")
        return config
    
    def execute_data_import(self):
        """データインポート実行"""
        logger.info("🚀 データインポート開始")
        
        # JRDBer4TF実行コマンド（仮想）
        commands = [
            # TARGETでJRDBデータ取り込み
            f"JRDBer4TF.exe /import /all",
            
            # データエクスポート
            f"TARGET.exe /export /format:csv /output:{self.export_dir}",
        ]
        
        logger.info("📋 実行予定コマンド:")
        for cmd in commands:
            print(f"  > {cmd}")
        
        # 実際の実装では subprocess で実行
        # subprocess.run(cmd, shell=True)
        
        return True
    
    def process_exported_data(self):
        """エクスポートデータ処理"""
        logger.info("📊 エクスポートデータ処理")
        
        csv_files = list(self.export_dir.glob("*.csv"))
        processed_data = {
            'races': [],
            'horses': [],
            'results': [],
            'metadata': {}
        }
        
        for csv_file in csv_files:
            logger.info(f"処理中: {csv_file.name}")
            
            try:
                # CSVデータ読み込み
                df = pd.read_csv(csv_file, encoding='shift-jis')
                
                # データタイプ判定と処理
                if 'SED' in csv_file.name:
                    processed_data['results'].extend(df.to_dict('records'))
                elif 'KYI' in csv_file.name:
                    processed_data['horses'].extend(df.to_dict('records'))
                elif 'BAC' in csv_file.name:
                    processed_data['races'].extend(df.to_dict('records'))
                
            except Exception as e:
                logger.error(f"処理エラー: {csv_file.name} - {e}")
        
        # 統合データ保存
        output_file = self.jrdb_dir / "jrdb_integrated_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 統合データ保存: {output_file}")
        return processed_data
    
    def create_batch_script(self):
        """バッチスクリプト作成"""
        batch_content = """@echo off
echo ========================================
echo JRDBer4TF 自動実行バッチ
echo ========================================

echo 1. JRDBデータ取り込み中...
JRDBer4TF.exe /import /all /auto

echo 2. TARGETでデータエクスポート中...
TARGET.exe /export /format:csv /output:data\\target_export

echo 3. 完了！
echo エクスポートされたCSVファイルを確認してください。
pause
"""
        
        batch_file = Path("run_jrdber4tf.bat")
        with open(batch_file, 'w', encoding='shift-jis') as f:
            f.write(batch_content)
        
        logger.info(f"✅ バッチファイル作成: {batch_file}")
        return batch_file

def main():
    """メイン処理"""
    print("🏇 JRDBer4TF データパイプライン")
    print("=" * 50)
    
    pipeline = JRDBDataPipeline()
    
    # 1. 初期設定
    config = pipeline.setup_jrdber4tf()
    
    # 2. バッチスクリプト作成
    batch_file = pipeline.create_batch_script()
    
    # 3. 手順表示
    print("\\n📋 実行手順:")
    print("1. JRDBer4TFをダウンロード・インストール")
    print("2. TARGET frontier JVを起動")
    print(f"3. {batch_file} を実行")
    print("4. エクスポートされたCSVを確認")
    print("5. このスクリプトを再実行してデータ処理")
    
    # 4. エクスポートデータチェック
    csv_files = list(pipeline.export_dir.glob("*.csv"))
    if csv_files:
        print(f"\\n✅ エクスポートデータ発見: {len(csv_files)}ファイル")
        processed = pipeline.process_exported_data()
        print(f"📊 処理完了:")
        print(f"  レース: {len(processed['races'])}件")
        print(f"  馬データ: {len(processed['horses'])}件")
        print(f"  結果: {len(processed['results'])}件")
    else:
        print(f"\\n⚠️ エクスポートデータがありません")
        print(f"💡 バッチファイルを実行してデータをエクスポートしてください")

if __name__ == "__main__":
    main()
'''
        
        # パイプライン保存
        pipeline_file = Path("jrdber4tf_pipeline.py")
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write(pipeline_code)
        
        logger.info(f"✅ データパイプライン作成: {pipeline_file}")
        return pipeline_file

def main():
    """メイン処理"""
    print("🏇 JRDBer4TF 取得・設定ツール")
    print("=" * 50)
    
    fetcher = JRDBer4TFFetcher()
    
    # 1. JRDBer4TF情報取得
    download_links = fetcher.fetch_jrdber4tf_info()
    
    # 2. データパイプライン作成
    pipeline_file = fetcher.create_data_pipeline()
    
    # 3. 総合手順
    print("\n" + "=" * 50)
    print("🎯 JRDBデータ取得の完全手順")
    print("=" * 50)
    
    print("【準備】")
    print("1. TARGET frontier JVをインストール")
    print("2. JRA-VANデータラボ契約")
    print("3. JRDBer4TFをダウンロード")
    
    print("\n【実行】")
    print("1. JRDBer4TFでJRDBデータをTARGETに取り込み")
    print("2. TARGETでCSVエクスポート")
    print(f"3. python {pipeline_file} でデータ処理")
    print("4. 処理済みデータで予測システム実行")
    
    print("\n💡 このアプローチの利点:")
    print("  • JRDBの認証問題を完全回避")
    print("  • ファイル分散問題の解決")
    print("  • TARGETの強力な分析機能も活用可能")
    print("  • 確実なデータ取得")

if __name__ == "__main__":
    main()