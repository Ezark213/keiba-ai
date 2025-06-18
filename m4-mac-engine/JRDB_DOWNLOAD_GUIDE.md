# 📥 JRDBデータダウンロードガイド

## 概要
このガイドでは、JRDBから実データを確実にダウンロードする方法を説明します。

## 🚀 推奨方法: working_jrdb_downloader.py

### 動作原理
1. **Seleniumブラウザ自動化**でJRDBにアクセス
2. **HTTPベーシック認証**を自動処理
3. 画面に表示される**「Lzh」リンクを自動クリック**
4. **15個のファイルを自動ダウンロード**

### 使用方法
```bash
# 仮想環境を有効化
source venv/bin/activate

# JRDBデータダウンロード実行
python working_jrdb_downloader.py
```

### 認証情報
- **ユーザー名**: 25067698
- **パスワード**: 87086387
- **URL**: http://www.jrdb.com/member/data/

### ダウンロードされるファイル例
```
📋 ダウンロード済みファイル:
  BAC250614.lzh (996 bytes) - 番組データ
  BAB250614.lzh (978 bytes) - 番組データ
  KAB250614.lzh (164 bytes) - 開催データ
  KAA250614.lzh (148 bytes) - 開催データ
  KTA250615.lzh (53,200 bytes) - 登録馬データ
  SKB250607.lzh (20,189 bytes) - 成績拡張データ
```

## 📦 ダウンロード後の処理

### 1. LZHファイル展開
```bash
# Pythonツールで展開
python extract_lzh_files.py
```

### 2. データ統合
```bash
# 分散ファイルを機械学習用に統合
python jrdb_consolidation_tool.py
```

### 3. システム起動
```bash
# Claude主導エンジン起動
python claude_main.py
```

## 🔧 トラブルシューティング

### lhaコマンドがない場合
macOSの場合:
```bash
brew install lha
```

Linuxの場合:
```bash
sudo apt-get install lha
```

### Seleniumエラーの場合
1. ChromeDriverを最新版に更新
2. Chromeブラウザを最新版に更新

### ダウンロードできない場合
1. デバッグ画像（`debug_*.png`）を確認
2. 手動でブラウザアクセスして認証情報を確認
3. ネットワーク接続を確認

## 📋 その他のダウンロード方法

### 方法2: JRDBer4TF経由
1. https://iamryosuke.com/archives/123 からJRDBer4TFをダウンロード
2. TARGET frontier JVと連携
3. CSVエクスポート後、`jrdber4tf_pipeline.py`で処理

### 方法3: 手動ダウンロード
1. ブラウザで http://www.jrdb.com/member/ にアクセス
2. ユーザー名/パスワードでログイン
3. データページから必要なLzhファイルをダウンロード
4. `data/jrdb_real/`に保存

## 📊 データ確認
```bash
# ダウンロードファイル確認
ls -la data/jrdb_real/*.lzh

# 展開後のファイル確認
ls -la data/jrdb_real/*.txt
```

## ⚠️ 注意事項
- **サンプルデータは絶対に使用しない**
- **必ず実データをダウンロードする**
- **認証情報は安全に管理する**
- **過度なアクセスは避ける**（レート制限あり）