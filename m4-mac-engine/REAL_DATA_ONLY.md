# 本物のデータ専用システム - デモモード完全排除

## 概要
このシステムは**本物のJRDBデータのみ**を使用するように更新されました。
デモモードやフェイクデータは完全に排除されています。

## 主な変更点

### 1. データフェッチャー
- `JRDBFetcher` → `RealJRDBFetcher` に変更
- JRDB認証情報がない場合はエラーを発生させる
- デモデータ生成機能を完全削除

### 2. 機械学習トレーナー
- 学習データが不足している場合はエラーを発生させる
- デモモデル作成機能を削除

### 3. シミュレーター
- 本物のデータがない場合はエラーを発生させる
- デモ結果生成機能を削除

### 4. メインプログラム
- JRDB認証情報を必須に変更
- 環境変数チェックを強化

## 必須環境変数

```bash
# 全て必須
export CLAUDE_API_KEY='your-api-key'
export CF_SYNC_TOKEN='your-sync-token'
export JRDB_USERNAME='your-username'  # 必須
export JRDB_PASSWORD='your-password'  # 必須
```

## セットアップ方法

1. JRDB認証情報を設定:
```bash
cd m4-mac-engine
source venv/bin/activate
python -m src.utils.secure_config
```

2. 環境変数を設定:
```bash
export JRDB_USERNAME='your-username'
export JRDB_PASSWORD='your-password'
export CF_SYNC_TOKEN='your-sync-token'
```

3. システムを起動:
```bash
python main.py
```

## エラーメッセージ

JRDB認証情報が設定されていない場合:
```
❌ JRDBクレデンシャルが設定されていません！
本物のデータを使用するには必須です。

設定方法:
1. cd m4-mac-engine
2. source venv/bin/activate
3. python -m src.utils.secure_config
4. ユーザー名とパスワードを入力
```

## テスト

本物のデータ使用の強制をテスト:
```bash
python test_real_data.py
```

## 注意事項

- **デモモードは完全に廃止されました**
- **常に本物のJRDBデータが必要です**
- **JRDB認証情報なしでは動作しません**

## 更新されたファイル

1. `/src/auto_improvement_loop.py` - RealJRDBFetcherを使用
2. `/src/ml_engine/trainer.py` - デモモデル機能を削除
3. `/src/ml_engine/simulator.py` - デモ結果生成を削除
4. `/main.py` - JRDB認証を必須化
5. `/config.py` - 検証ロジックを更新