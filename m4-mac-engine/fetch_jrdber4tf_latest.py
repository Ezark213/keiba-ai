#!/usr/bin/env python3
"""
JRDBer4TF最新版取得スクリプト
最新バージョン1.0.2のダウンロードリンクを探す
"""
import requests
from bs4 import BeautifulSoup
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_latest_version():
    """最新バージョンページから情報取得"""
    # 最新バージョンページ（1.0.2）
    latest_url = "https://iamryosuke.com/archives/123"
    
    logger.info(f"🔍 最新バージョンページ確認: {latest_url}")
    
    try:
        response = requests.get(latest_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # タイトル確認
            title = soup.find('h1', class_='entry-title')
            if title:
                logger.info(f"📋 ページタイトル: {title.get_text(strip=True)}")
            
            # コンテンツエリア
            content = soup.find('div', class_='entry-content')
            if content:
                # ダウンロードリンクを探す
                download_found = False
                
                # すべてのリンクをチェック
                for link in content.find_all('a'):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # ダウンロードリンクパターン
                    if any(pattern in href.lower() for pattern in ['download', '.zip', '.lzh', 'drive.google', 'github']):
                        logger.info(f"📥 ダウンロードリンク候補:")
                        logger.info(f"   テキスト: {text}")
                        logger.info(f"   URL: {href}")
                        download_found = True
                
                # テキスト内容も確認
                paragraphs = content.find_all('p')
                for p in paragraphs:
                    text = p.get_text()
                    if any(keyword in text for keyword in ['ダウンロード', 'download', 'リリース', 'release']):
                        logger.info(f"📝 関連情報: {text[:200]}...")
                
                if not download_found:
                    logger.warning("⚠️ 直接的なダウンロードリンクが見つかりません")
                    
            # JRDBer4TFタグページも確認
            tag_url = "https://iamryosuke.com/archives/tag/jrdber4tf"
            logger.info(f"\n🔍 タグページ確認: {tag_url}")
            
            tag_response = requests.get(tag_url, timeout=10)
            if tag_response.status_code == 200:
                tag_soup = BeautifulSoup(tag_response.content, 'html.parser')
                
                # 記事リスト
                articles = tag_soup.find_all('article')
                logger.info(f"📋 JRDBer4TF関連記事: {len(articles)}件")
                
                for article in articles[:5]:  # 最新5件
                    title_elem = article.find(['h2', 'h3'], class_='entry-title')
                    if title_elem:
                        article_link = title_elem.find('a')
                        if article_link:
                            logger.info(f"  • {title_elem.get_text(strip=True)}")
                            logger.info(f"    {article_link.get('href')}")
            
            # 手動ダウンロード手順
            print("\n" + "=" * 50)
            print("📋 JRDBer4TF入手方法")
            print("=" * 50)
            
            print("1. ブラウザでアクセス:")
            print("   https://iamryosuke.com/archives/123")
            print("   （最新版 ver1.0.2）")
            
            print("\n2. ページ内でダウンロードリンクを探す")
            print("   • 「ダウンロード」ボタン")
            print("   • Google Drive リンク")
            print("   • GitHub リンク")
            
            print("\n3. JRDBer4TF設定:")
            print("   • JRDBアカウント: 25067698")
            print("   • パスワード: 87086387")
            
            print("\n4. 使用方法:")
            print("   • TARGET frontier JVと連携")
            print("   • JRDBデータを自動取り込み")
            print("   • CSVエクスポート機能で出力")
            
        else:
            logger.error(f"❌ ページアクセス失敗: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ 取得エラー: {e}")

def create_manual_guide():
    """手動セットアップガイド作成"""
    guide_content = """# JRDBer4TF セットアップガイド

## 概要
JRDBer4TFは、JRDBデータをTARGET frontier JVに取り込むための優れたツールです。

## 入手方法
1. https://iamryosuke.com/ にアクセス
2. JRDBer4TF関連記事を探す
3. 最新版（ver1.0.2）をダウンロード

## 必要環境
- Windows PC
- TARGET frontier JV（JRA-VANデータラボ契約必要）
- JRDBアカウント

## セットアップ手順

### 1. JRDBer4TFインストール
```
1. ダウンロードしたファイルを解凍
2. JRDBer4TF.exe を実行
3. 初回設定ウィザードに従う
```

### 2. JRDB認証情報設定
```
ユーザー名: 25067698
パスワード: 87086387
```

### 3. データ取り込み
```
1. TARGET frontier JVを起動
2. JRDBer4TFを起動
3. 「データ取り込み」ボタンをクリック
4. 取り込むデータタイプを選択（SED, KYI, BAC等）
5. 期間を指定して実行
```

### 4. データエクスポート
```
1. TARGETのメニューから「外部出力」
2. CSV形式を選択
3. 出力先: data/target_export/
```

## 自動化スクリプト

以下のPythonスクリプトでエクスポートデータを処理：

```python
python jrdber4tf_pipeline.py
```

## トラブルシューティング

### 認証エラーの場合
- JRDBアカウントの有効期限確認
- ユーザー名/パスワードの再入力

### データ取り込みエラー
- インターネット接続確認
- TARGET frontier JVの更新確認
- JRDBer4TFの最新版確認

## サポート
- 作者サイト: https://iamryosuke.com/
- JRDBer4TF専用ページで質問可能
"""
    
    guide_file = Path("JRDBER4TF_SETUP_GUIDE.md")
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    logger.info(f"✅ セットアップガイド作成: {guide_file}")
    return guide_file

def main():
    """メイン処理"""
    print("🏇 JRDBer4TF 最新版情報取得")
    print("=" * 50)
    
    # 最新版情報取得
    fetch_latest_version()
    
    # セットアップガイド作成
    guide_file = create_manual_guide()
    
    print("\n" + "=" * 50)
    print("🎯 まとめ")
    print("=" * 50)
    
    print("JRDBer4TFを使用することで：")
    print("✅ JRDBの認証問題を完全に回避")
    print("✅ 分散ファイルを統合してデータ取得")
    print("✅ TARGETの分析機能も活用可能")
    print("✅ 確実なデータ取得が可能")
    
    print(f"\n📋 詳細手順: {guide_file}")
    print("💡 JRDBer4TFで効率的にデータを取得しましょう！")

if __name__ == "__main__":
    main()