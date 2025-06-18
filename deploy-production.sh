#!/bin/bash
# 本番環境デプロイスクリプト

set -e

echo "🚀 競馬予測システム v3.0 - 本番環境デプロイ開始"
echo "=================================="

# カラー設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 本番環境の確認
echo -e "${YELLOW}⚠️  本番環境にデプロイします。続行しますか? (y/N)${NC}"
read -p "" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "デプロイを中止しました。"
    exit 1
fi

# 前提条件チェック
echo "📋 前提条件チェック中..."

# Wranglerのログイン確認
if ! wrangler whoami > /dev/null 2>&1; then
    echo -e "${RED}❌ Wranglerにログインしていません${NC}"
    echo "wrangler login を実行してください"
    exit 1
fi

# Node.js バージョンチェック
NODE_VERSION=$(node --version)
echo "✅ Node.js: $NODE_VERSION"

# ドメイン設定確認
echo "🌐 本番環境URL:"
echo "  - API: https://api.keiba-prediction.com"
echo "  - Frontend: https://keiba-prediction.com"

# Workers APIのデプロイ
echo -e "${GREEN}📡 Workers API をデプロイ中...${NC}"
cd cloudflare-workers

# 依存関係インストール
npm install

# 本番環境にデプロイ
wrangler deploy --env production

echo "✅ Workers API デプロイ完了"

# Pages フロントエンドのデプロイ  
echo -e "${GREEN}🎨 Pages フロントエンドをデプロイ中...${NC}"
cd ../cloudflare-pages

# 依存関係インストール
npm install

# ビルド実行
npm run build

# 本番環境にデプロイ
wrangler pages deploy dist --project-name keiba-prediction --env production

echo "✅ Pages フロントエンドデプロイ完了"

# デプロイ後のヘルスチェック
echo -e "${GREEN}🏥 ヘルスチェック実行中...${NC}"
cd ..

# API ヘルスチェック
echo "API エンドポイントのテスト..."
if curl -f -s "https://api.keiba-prediction.com/api/health" > /dev/null; then
    echo "✅ API: オンライン"
else
    echo -e "${YELLOW}⚠️  API: 応答なし（DNSの浸透を待っています...）${NC}"
fi

# フロントエンドアクセステスト
echo "フロントエンドのテスト..."
if curl -f -s "https://keiba-prediction.com" > /dev/null; then
    echo "✅ Frontend: オンライン"
else
    echo -e "${YELLOW}⚠️  Frontend: 応答なし（DNSの浸透を待っています...）${NC}"
fi

# DNS設定案内
echo ""
echo -e "${YELLOW}📋 DNS設定が必要です:${NC}"
echo "Cloudflareダッシュボードで以下のDNS設定を確認してください:"
echo ""
echo "1. A レコード:"
echo "   keiba-prediction.com → [Cloudflare Pages IP]"
echo ""
echo "2. CNAME レコード:"
echo "   api.keiba-prediction.com → keiba-prediction-api.workers.dev"
echo ""
echo "3. カスタムドメイン設定:"
echo "   - Pages: keiba-prediction.com"
echo "   - Workers: api.keiba-prediction.com"

# 完了メッセージ
echo ""
echo -e "${GREEN}🎉 本番環境デプロイ完了！${NC}"
echo "=================================="
echo "🌐 アクセスURL:"
echo "  📱 フロントエンド: https://keiba-prediction.com"
echo "  🔧 API: https://api.keiba-prediction.com"
echo "  📊 管理画面: https://dash.cloudflare.com"
echo ""
echo "📋 次のステップ:"
echo "  1. DNS設定の完了を待つ (最大48時間)"
echo "  2. SSL証明書の発行確認"
echo "  3. M4 Mac エンジンの本番環境接続設定"
echo ""

# ログファイルにデプロイ記録
DEPLOY_TIME=$(date "+%Y-%m-%d %H:%M:%S")
echo "$DEPLOY_TIME - Production deployment completed" >> deploy.log