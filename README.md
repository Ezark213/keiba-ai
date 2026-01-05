# 競馬予測システム v3.0 - Cloudflare & M4 Mac & Claude統合版

## 概要

最新技術スタックを活用した高精度競馬予測システム。目標還元率80%以上を実現するための完全自動化ソリューション。

**Claude Code**が直接システムを操作・分析・改善するユニークなアーキテクチャを採用しています。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code（統括）                        │
│         システム分析・改善計画・パラメータ最適化                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ M4 Mac Engine│    │  Cloudflare  │    │  Cloudflare  │
│  (ML学習)    │    │   Workers    │    │    Pages     │
│             │    │  (Edge API)  │    │ (Dashboard)  │
└─────────────┘    └─────────────┘    └─────────────┘
      │                   │                   │
      └───────────────────┴───────────────────┘
                     ▼
              JRDBデータ → 予測 → 結果表示
```

## ディレクトリ構造

```
keiba-ai/
├── cloudflare-workers/   # Workers API実装（エッジ予測）
├── cloudflare-pages/     # React フロントエンド（ダッシュボード）
├── m4-mac-engine/        # Python ML エンジン（ローカル学習）
├── instructions/         # AIエージェント用指示書
├── CLAUDE.md             # Claude Code統合ガイド
├── QUICKSTART.md         # クイックスタート
├── Makefile              # ビルド・デプロイコマンド
└── deploy.sh             # デプロイスクリプト
```

## クイックスタート

### 1. 環境変数設定

```bash
export CF_SYNC_TOKEN="your-sync-token"
export JRDB_USERNAME="your-jrdb-username"
export JRDB_PASSWORD="your-jrdb-password"
```

### 2. 依存関係インストール

```bash
make install-deps
```

または個別に：

```bash
# Workers
cd cloudflare-workers && npm install

# Pages
cd cloudflare-pages && npm install

# M4 Mac Engine
cd m4-mac-engine && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### 3. JRDBデータ取得（必須）

```bash
# JRDBデータダウンロード（Selenium使用）
python m4-mac-engine/working_jrdb_downloader.py

# LZHファイル展開
python m4-mac-engine/extract_lzh_files.py

# データ統合
python m4-mac-engine/jrdb_consolidation_tool.py
```

### 4. エンジン起動

**Claude主導エンジン（推奨）:**
```bash
make start-claude
```

**標準エンジン:**
```bash
make start-engine
```

### 5. デプロイ

```bash
# 本番環境
make deploy

# ステージング環境
make deploy-staging

# 開発サーバー
make dev-workers   # Workers
make dev-pages     # Pages
```

## 主要機能

| 機能 | 説明 |
|------|------|
| Claude主導分析 | AI自身がシステムを操作・改善 |
| リアルタイム予測 | エッジでの高速予測API |
| ダッシュボード | インタラクティブな成績監視 |
| 継続的改善 | 30分ごとの自動学習・最適化 |
| 無料枠運用 | Cloudflare無料枠での完全運用 |

## パフォーマンス目標

- **還元率**: 80%以上
- **応答速度**: <100ms (エッジレスポンス)
- **的中率**: 15%以上
- **コスト**: $0/月 (Cloudflare無料枠)

## 技術スタック

- **フロントエンド**: React + Cloudflare Pages
- **バックエンド**: Cloudflare Workers (エッジAPI)
- **ML処理**: Python + LightGBM (M4 Mac)
- **AI統合**: Claude Code直接実行
- **データ**: JRDB競馬データ

## Claude統合の仕組み

Claude Codeは以下のファイルを直接操作してシステムを改善します：

- `claude_state.json` - 状態管理と学習履歴
- `simulation_results.json` - シミュレーション結果
- `improvement_queue.json` - 改善キュー

詳細は [CLAUDE.md](./CLAUDE.md) を参照してください。

## 開発ガイドライン

### コード品質

- SOLID原則に従った設計
- 機密情報のコミット禁止
- ドキュメントの継続的更新

### セキュリティ

- `.env`ファイルはコミットしない
- JRDB認証情報はキーチェーンで管理
- 詳細は [SECURITY.md](./SECURITY.md) を参照

## コマンドリファレンス

```bash
make setup          # 初期セットアップ
make install-deps   # 依存関係インストール
make start-claude   # Claude主導エンジン起動
make start-engine   # 標準エンジン起動
make deploy         # 本番デプロイ
make deploy-staging # ステージングデプロイ
make dev-workers    # Workers開発サーバー
make dev-pages      # Pages開発サーバー
make test           # テスト実行
make check-env      # 環境チェック
make clean          # クリーンアップ
make logs           # ログ表示
```

## ライセンス

MIT License

## 関連ドキュメント

- [CLAUDE.md](./CLAUDE.md) - Claude Code統合詳細
- [QUICKSTART.md](./QUICKSTART.md) - 詳細なクイックスタート
- [SECURITY.md](./SECURITY.md) - セキュリティポリシー
- [CLAUDE_INTEGRATION.md](./CLAUDE_INTEGRATION.md) - 統合手順書
