# JRDBer4TF セットアップガイド

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
