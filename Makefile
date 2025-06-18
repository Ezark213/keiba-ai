# 競馬予測システム v3.0 Makefile

.PHONY: help setup install-deps deploy deploy-workers deploy-pages start-engine stop-engine clean

# デフォルトターゲット
help:
	@echo "競馬予測システム v3.0 - コマンド一覧"
	@echo ""
	@echo "セットアップ:"
	@echo "  make setup          - 初回セットアップ（環境構築）"
	@echo "  make install-deps   - 依存関係インストール"
	@echo ""
	@echo "デプロイ:"
	@echo "  make deploy         - 全体デプロイ"
	@echo "  make deploy-workers - Workers APIのみデプロイ"
	@echo "  make deploy-pages   - Pagesフロントエンドのみデプロイ"
	@echo "  make deploy-prod    - 本番環境デプロイ"
	@echo "  make deploy-staging - ステージング環境デプロイ"
	@echo ""
	@echo "M4 Macエンジン:"
	@echo "  make start-engine   - 標準エンジン起動"
	@echo "  make start-claude   - Claude主導エンジン起動（推奨）"
	@echo "  make stop-engine    - エンジン停止"
	@echo ""
	@echo "開発:"
	@echo "  make dev-workers    - Workers開発サーバー起動"
	@echo "  make dev-pages      - Pages開発サーバー起動"
	@echo "  make test           - テスト実行"
	@echo ""
	@echo "ユーティリティ:"
	@echo "  make clean          - 一時ファイル削除"
	@echo "  make logs           - エンジンログ表示"

# 初回セットアップ
setup:
	@echo "🚀 初回セットアップを開始..."
	@cp .env.example .env
	@echo "✅ .envファイルを作成しました。必要な環境変数を設定してください。"
	@$(MAKE) install-deps
	@echo ""
	@echo "📝 次のステップ:"
	@echo "1. .envファイルを編集して環境変数を設定"
	@echo "2. make deploy でデプロイ実行"
	@echo "3. make start-engine でM4 Macエンジン起動"

# 依存関係インストール
install-deps:
	@echo "📦 依存関係をインストール中..."
	
	# Workers
	@echo "Workers依存関係..."
	@cd cloudflare-workers && npm install
	
	# Pages  
	@echo "Pages依存関係..."
	@cd cloudflare-pages && npm install
	
	# Python (M4 Mac Engine)
	@if command -v python3 >/dev/null 2>&1; then \
		echo "Python依存関係..."; \
		cd m4-mac-engine && \
		python3 -m venv venv && \
		. venv/bin/activate && \
		pip install -r requirements.txt; \
	else \
		echo "⚠️  Python3が見つかりません"; \
	fi
	
	@echo "✅ 依存関係インストール完了"

# 全体デプロイ
deploy:
	@./deploy.sh

# Workers APIデプロイ
deploy-workers:
	@./deploy.sh --workers-only

# Pagesフロントエンドデプロイ
deploy-pages:
	@./deploy.sh --pages-only

# 本番環境デプロイ
deploy-prod:
	@echo "🚀 本番環境にデプロイ中..."
	@./deploy-production.sh

# ステージング環境デプロイ  
deploy-staging:
	@echo "🧪 ステージング環境にデプロイ中..."
	@./deploy-staging.sh

# M4 Macエンジン起動
start-engine:
	@echo "🖥️  M4 Macエンジンを起動中..."
	@cd m4-mac-engine && \
	if [ -f .env ]; then export $$(cat .env | xargs); fi && \
	. venv/bin/activate && \
	python main.py

# Claude主導エンジン起動
start-claude:
	@echo "🤖 Claude主導エンジンを起動中..."
	@cd m4-mac-engine && \
	if [ -f .env ]; then export $$(cat .env | xargs); fi && \
	. venv/bin/activate && \
	python claude_main.py

# M4 Macエンジン停止（バックグラウンド実行用）
stop-engine:
	@echo "🛑 M4 Macエンジンを停止中..."
	@pkill -f "python main.py" || echo "エンジンは実行されていません"

# Workers開発サーバー
dev-workers:
	@echo "🔧 Workers開発サーバーを起動中..."
	@cd cloudflare-workers && npm run dev

# Pages開発サーバー
dev-pages:
	@echo "🔧 Pages開発サーバーを起動中..."
	@cd cloudflare-pages && npm run dev

# テスト実行
test:
	@echo "🧪 テストを実行中..."
	@cd m4-mac-engine && \
	. venv/bin/activate && \
	python -m pytest tests/ -v || echo "テストディレクトリが見つかりません"

# 一時ファイル削除
clean:
	@echo "🧹 一時ファイルを削除中..."
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf cloudflare-pages/dist 2>/dev/null || true
	@rm -rf cloudflare-pages/node_modules/.cache 2>/dev/null || true
	@echo "✅ クリーンアップ完了"

# ログ表示
logs:
	@echo "📋 M4 Macエンジンログを表示中..."
	@tail -f m4-mac-engine/logs/keiba_$(shell date +%Y-%m-%d).log 2>/dev/null || \
	echo "ログファイルが見つかりません"

# 環境確認
check-env:
	@echo "🔍 環境を確認中..."
	@echo "Node.js: $$(node --version 2>/dev/null || echo '未インストール')"
	@echo "Python: $$(python3 --version 2>/dev/null || echo '未インストール')"
	@echo "Wrangler: $$(wrangler --version 2>/dev/null || echo '未インストール')"
	@echo ""
	@echo "環境変数:"
	@echo "CLAUDE_API_KEY: $$([ -n "$$CLAUDE_API_KEY" ] && echo '設定済み' || echo '未設定')"
	@echo "CF_SYNC_TOKEN: $$([ -n "$$CF_SYNC_TOKEN" ] && echo '設定済み' || echo '未設定')"

# 開発環境初期化
dev-setup: install-deps
	@echo "🔧 開発環境を初期化中..."
	@echo "Wranglerログイン状態を確認中..."
	@wrangler whoami || echo "wrangler login を実行してください"
	@echo "✅ 開発環境初期化完了"