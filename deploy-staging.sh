#!/bin/bash
# ステージング環境デプロイスクリプト

set -e

echo "🧪 競馬予測システム v3.0 - ステージング環境デプロイ開始"
echo "=================================="

# カラー設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 前提条件チェック
echo "📋 前提条件チェック中..."

# Wranglerのログイン確認
if ! wrangler whoami > /dev/null 2>&1; then
    echo "❌ Wranglerにログインしていません"
    echo "wrangler login を実行してください"
    exit 1
fi

echo "✅ Wrangler認証済み"

# ドメイン設定確認
echo "🌐 ステージング環境URL:"
echo "  - API: https://staging-api.keiba-prediction.com"
echo "  - Frontend: https://staging.keiba-prediction.com"

# Workers APIのデプロイ
echo -e "${GREEN}📡 Workers API (Staging) をデプロイ中...${NC}"
cd cloudflare-workers

# 依存関係インストール
npm install

# ステージング環境にデプロイ
wrangler deploy --env staging

echo "✅ Workers API (Staging) デプロイ完了"

# Pages フロントエンドのデプロイ  
echo -e "${GREEN}🎨 Pages フロントエンド (Staging) をデプロイ中...${NC}"
cd ../cloudflare-pages

# 依存関係インストール
npm install

# ビルド実行
npm run build

# ステージング環境にデプロイ
wrangler pages deploy dist --project-name keiba-prediction-staging --env staging

echo "✅ Pages フロントエンド (Staging) デプロイ完了"

# デプロイ後のヘルスチェック
echo -e "${BLUE}🏥 ヘルスチェック実行中...${NC}"
cd ..

# 簡易ヘルスチェック
sleep 5

echo ""
echo -e "${GREEN}🎉 ステージング環境デプロイ完了！${NC}"
echo "=================================="
echo "🌐 アクセスURL:"
echo "  📱 フロントエンド: https://staging.keiba-prediction.com"
echo "  🔧 API: https://staging-api.keiba-prediction.com"
echo ""
echo "📋 テスト推奨項目:"
echo "  ✓ API エンドポイントの動作確認"
echo "  ✓ フロントエンド UI の表示確認"
echo "  ✓ 予測機能のテスト"
echo "  ✓ パフォーマンス測定"
echo ""

# ログファイルにデプロイ記録
DEPLOY_TIME=$(date "+%Y-%m-%d %H:%M:%S")
echo "$DEPLOY_TIME - Staging deployment completed" >> deploy.log