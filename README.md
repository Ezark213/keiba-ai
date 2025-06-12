# 競馬予測システム v3.0 - Cloudflare & M4 Mac & Claude統合版

## 概要
最新技術スタックを活用した高精度競馬予測システム。目標還元率80%以上を実現するための完全自動化ソリューション。

## システム構成
- **フロントエンド**: Cloudflare Pages (React SPA)
- **バックエンド**: Cloudflare Workers (エッジAPI)
- **ML処理**: M4 Mac (ローカル学習環境)
- **AI支援**: Claude Code直接実行 (理論構築・改善)

## ディレクトリ構造
```
keiba-prediction-v3/
├── cloudflare-workers/   # Workers API実装
├── cloudflare-pages/     # React フロントエンド
├── m4-mac-engine/        # Python ML エンジン
└── docs/                 # ドキュメント
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
# Workers
cd cloudflare-workers && npm install

# Pages
cd ../cloudflare-pages && npm install

# M4 Mac Engine
cd ../m4-mac-engine && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### 3. デプロイ
```bash
# 本番環境（推奨）
make deploy-prod

# ステージング環境
make deploy-staging

# 開発環境
make deploy
```

### 4. JRDBデータ取得
```bash
# 確実な方法でJRDBデータをダウンロード
python m4-mac-engine/working_jrdb_downloader.py

# LZHファイル展開
python m4-mac-engine/extract_lzh_files.py

# データ統合
python m4-mac-engine/jrdb_consolidation_tool.py
```

### 5. Claude主導エンジン起動（推奨）
```bash
make start-claude
```

または標準エンジン：
```bash
make start-engine
```

## 🎯 主要機能
- 🤖 **Claude主導分析**: AI自身がシステムを操作・改善
- 🏇 **リアルタイム予測**: エッジでの高速予測API (https://api.keiba-prediction.com)
- 📊 **ダッシュボード**: インタラクティブな成績監視 (https://keiba-prediction.com)
- 💰 **無料枠最適化**: Cloudflare無料枠での完全運用
- 🔄 **継続的改善**: 30分ごとの自動学習・最適化
- 🎯 **目標還元率80%**: AI駆動の段階的改善
- 🔧 **SOLID原則準拠**: 保守性・拡張性に優れた設計
- 🔐 **セキュア運用**: キーチェーン認証による安全な認証情報管理
- 🔌 **プラグイン式特徴量**: 拡張可能な特徴量エンジニアリング
- 📈 **柔軟なベッティング戦略**: Kelly・固定額・比例戦略

## パフォーマンス目標
- **還元率**: 80%以上
- **応答速度**: <100ms (エッジレスポンス)
- **的中率**: 15%以上
- **コスト**: $0/月 (Cloudflare無料枠)
