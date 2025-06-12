# 🏇 競馬予測システム v3.0 - クイックスタートガイド

このガイドに従って、競馬予測システムを簡単にセットアップできます。

## ⚡ 1分でセットアップ

### 1. リポジトリクローン
```bash
git clone <your-repo-url>
cd keiba-prediction-v3
```

### 2. 環境変数設定
```bash
# 環境設定ファイルをコピー
cp .env.example .env

# 必要な環境変数を設定
export CLAUDE_API_KEY="your-claude-api-key"
export CF_SYNC_TOKEN="your-sync-token"
```

### 3. 依存関係インストール
```bash
make install-deps
```

### 4. デプロイ実行
```bash
# 開発環境
make deploy

# 本番環境（推奨）
make deploy-prod

# ステージング環境
make deploy-staging
```

### 5. JRDBデータ取得（重要）
```bash
# JRDBから実データをダウンロード
cd m4-mac-engine
python working_jrdb_downloader.py

# ダウンロード成功確認後、データを処理
python extract_lzh_files.py
python jrdb_consolidation_tool.py
cd ..
```

### 6. M4 Macエンジン起動
```bash
make start-engine
```

## 🎯 動作確認

### 本番環境
1. **フロントエンド**: https://keiba-prediction.com
2. **API**: https://api.keiba-prediction.com/api/health
3. **M4エンジン**: ログで動作確認

### ステージング環境  
1. **フロントエンド**: https://staging.keiba-prediction.com
2. **API**: https://staging-api.keiba-prediction.com/api/health

### 開発環境
1. **フロントエンド**: https://keiba-prediction.pages.dev/
2. **API**: https://keiba-prediction-api.workers.dev/api/health

## 📋 主要コマンド

```bash
# ヘルプ表示
make help

# 開発サーバー起動
make dev-workers    # Workers開発サーバー
make dev-pages      # Pages開発サーバー

# 個別デプロイ
make deploy-workers # API のみ
make deploy-pages   # フロントエンドのみ

# 環境別デプロイ
make deploy-prod    # 本番環境
make deploy-staging # ステージング環境

# エンジン管理
make start-engine   # エンジン起動
make stop-engine    # エンジン停止
make logs          # ログ表示

# メンテナンス
make clean         # 一時ファイル削除
make check-env     # 環境確認
```

## 🔧 環境変数詳細

### 必須項目
- `CLAUDE_API_KEY`: Claude APIキー（[Anthropic Console](https://console.anthropic.com/)で取得）
- `CF_SYNC_TOKEN`: Cloudflare同期トークン（ランダム文字列で設定）

### オプション項目
- `JRDB_USERNAME`: JRDBユーザー名（未設定時はデモモード）
- `JRDB_PASSWORD`: JRDBパスワード
- `TARGET_RETURN_RATE`: 目標還元率（デフォルト: 0.80）
- `CYCLE_INTERVAL_MINUTES`: 実行間隔（デフォルト: 30分）

## 🌊 ワークフロー

1. **データ取得**: JRDBまたはデモデータ
2. **ML学習**: LightGBMで予測モデル構築
3. **Claude分析**: AI による改善提案
4. **シミュレーション**: バックテストで性能評価
5. **同期**: Cloudflareにモデルアップロード
6. **予測配信**: エッジでリアルタイム予測

## 🎮 フロントエンド機能

- **リアルタイムダッシュボード**: 還元率・的中率の監視
- **予測パネル**: レース選択と予測実行
- **パフォーマンスチャート**: 成績推移の可視化
- **推奨ベット**: ケリー基準による最適配分

## 🔍 トラブルシューティング

### よくある問題

#### 1. Wranglerログインエラー
```bash
wrangler login
```

#### 2. Python依存関係エラー
```bash
cd m4-mac-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Claude API エラー
- API キーが正しく設定されているか確認
- レート制限に達していないか確認

#### 4. Cloudflare同期エラー
- CF_SYNC_TOKEN が設定されているか確認
- Workers がデプロイ済みか確認

### ログ確認
```bash
# エンジンログ
make logs

# Workers ログ
wrangler tail

# Pages ログ
ブラウザのデベロッパーツールで確認
```

## 📊 パフォーマンス目標

- **還元率**: 80%以上
- **的中率**: 15%以上
- **応答時間**: <100ms
- **稼働率**: 99%以上

## 🔄 継続的改善

システムは30分ごとに自動で以下を実行：

1. 新データ取得
2. モデル再学習
3. Claude分析
4. 性能評価
5. 自動改善

## 🚀 本格運用に向けて

### 1. JRDB接続設定
```bash
export JRDB_USERNAME="your-username"
export JRDB_PASSWORD="your-password"
```

### 2. 監視システム構築
- Cloudflare Analytics で使用量監視
- アラート設定で異常検知

### 3. バックアップ設定
- モデルファイルの定期バックアップ
- 設定ファイルのバージョン管理

### 4. セキュリティ強化
- API トークンの定期更新
- アクセス制限の設定

## 🎉 成功のポイント

1. **継続的監視**: ダッシュボードで日次確認
2. **段階的改善**: 小さな改善を積み重ね
3. **データ品質**: 良質なデータを継続投入
4. **リスク管理**: 適切なベッティング制限

---

**🎯 目標還元率80%達成に向けて頑張りましょう！**

質問や問題がある場合は、ログを確認して適切に対処してください。