#!/bin/bash
# 競馬予測システム v3.0 デプロイスクリプト

set -e

echo "╔════════════════════════════════════════════════╗"
echo "║     競馬予測システム v3.0 デプロイスクリプト    ║"
echo "╚════════════════════════════════════════════════╝"

# 環境変数チェック
check_env() {
    echo "🔍 環境変数をチェック中..."
    
    if [ -z "$CLAUDE_API_KEY" ]; then
        echo "❌ CLAUDE_API_KEY が設定されていません"
        echo "以下のコマンドで設定してください:"
        echo "export CLAUDE_API_KEY='your-api-key'"
        exit 1
    fi
    
    if [ -z "$CF_SYNC_TOKEN" ]; then
        echo "❌ CF_SYNC_TOKEN が設定されていません"
        echo "以下のコマンドで設定してください:"
        echo "export CF_SYNC_TOKEN='your-sync-token'"
        exit 1
    fi
    
    echo "✅ 環境変数チェック完了"
}

# 依存関係インストール
install_dependencies() {
    echo "📦 依存関係をインストール中..."
    
    # Cloudflare Workers
    echo "Workers依存関係インストール..."
    cd cloudflare-workers
    npm install
    cd ..
    
    # Cloudflare Pages
    echo "Pages依存関係インストール..."
    cd cloudflare-pages
    npm install
    cd ..
    
    # M4 Mac Engine (オプション)
    if command -v python3 &> /dev/null; then
        echo "Python依存関係インストール..."
        cd m4-mac-engine
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
    else
        echo "⚠️  Python3が見つかりません。M4 Macエンジンのセットアップをスキップします。"
    fi
    
    echo "✅ 依存関係インストール完了"
}

# Cloudflare Workers デプロイ
deploy_workers() {
    echo "☁️  Workers APIをデプロイ中..."
    
    cd cloudflare-workers
    
    # KVネームスペース作成（初回のみ）
    echo "KVネームスペースを作成中..."
    wrangler kv:namespace create "MODELS" || true
    wrangler kv:namespace create "PREDICTIONS" || true
    
    # R2バケット作成（初回のみ）
    echo "R2バケットを作成中..."
    wrangler r2 bucket create keiba-models || true
    
    # デプロイ実行
    echo "Workersをデプロイ中..."
    wrangler publish
    
    cd ..
    echo "✅ Workers APIデプロイ完了"
}

# Cloudflare Pages デプロイ
deploy_pages() {
    echo "🌐 Pagesフロントエンドをデプロイ中..."
    
    cd cloudflare-pages
    
    # ビルド実行
    echo "フロントエンドをビルド中..."
    npm run build
    
    # デプロイ実行
    echo "Pagesをデプロイ中..."
    wrangler pages publish dist
    
    cd ..
    echo "✅ Pagesフロントエンドデプロイ完了"
}

# M4 Mac Engine セットアップ
setup_m4_engine() {
    echo "🖥️  M4 Macエンジンをセットアップ中..."
    
    if [ ! -d "m4-mac-engine/venv" ]; then
        echo "Python仮想環境を作成中..."
        cd m4-mac-engine
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
    fi
    
    # systemdサービスファイル作成（Linux/macOS用）
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "systemdサービスを作成中..."
        create_systemd_service
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "launchdサービスを作成中..."
        create_launchd_service
    fi
    
    echo "✅ M4 Macエンジンセットアップ完了"
}

# systemdサービス作成
create_systemd_service() {
    SERVICE_FILE="/tmp/keiba-ml.service"
    
    cat > $SERVICE_FILE << EOF
[Unit]
Description=Keiba ML Engine
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/m4-mac-engine
Environment=PATH=$(pwd)/m4-mac-engine/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=CLAUDE_API_KEY=$CLAUDE_API_KEY
Environment=CF_SYNC_TOKEN=$CF_SYNC_TOKEN
Environment=JRDB_USERNAME=$JRDB_USERNAME
Environment=JRDB_PASSWORD=$JRDB_PASSWORD
ExecStart=$(pwd)/m4-mac-engine/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "systemdサービスファイルが作成されました: $SERVICE_FILE"
    echo "以下のコマンドでサービスを有効化してください:"
    echo "sudo cp $SERVICE_FILE /etc/systemd/system/"
    echo "sudo systemctl enable keiba-ml"
    echo "sudo systemctl start keiba-ml"
}

# launchdサービス作成
create_launchd_service() {
    PLIST_FILE="$HOME/Library/LaunchAgents/com.keiba.ml.plist"
    
    cat > $PLIST_FILE << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.keiba.ml</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/m4-mac-engine/venv/bin/python</string>
        <string>$(pwd)/m4-mac-engine/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)/m4-mac-engine</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>CLAUDE_API_KEY</key>
        <string>$CLAUDE_API_KEY</string>
        <key>CF_SYNC_TOKEN</key>
        <string>$CF_SYNC_TOKEN</string>
        <key>JRDB_USERNAME</key>
        <string>$JRDB_USERNAME</string>
        <key>JRDB_PASSWORD</key>
        <string>$JRDB_PASSWORD</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

    echo "launchdサービスファイルが作成されました: $PLIST_FILE"
    echo "以下のコマンドでサービスを有効化してください:"
    echo "launchctl load $PLIST_FILE"
    echo "launchctl start com.keiba.ml"
}

# デプロイ状況確認
check_deployment() {
    echo "🔍 デプロイ状況を確認中..."
    
    # Workers確認
    echo "Workers APIステータス:"
    curl -s https://api.keiba-prediction.com/health || echo "Workers APIにアクセスできません"
    
    # Pages確認
    echo "Pagesフロントエンドステータス:"
    curl -s https://keiba-prediction.pages.dev/ || echo "Pagesにアクセスできません"
    
    echo "✅ デプロイ状況確認完了"
}

# メイン実行
main() {
    echo "デプロイを開始します..."
    echo "オプション: --workers-only, --pages-only, --setup-only"
    
    case ${1:-all} in
        --workers-only)
            check_env
            install_dependencies
            deploy_workers
            ;;
        --pages-only)
            check_env
            install_dependencies
            deploy_pages
            ;;
        --setup-only)
            check_env
            install_dependencies
            setup_m4_engine
            ;;
        all|*)
            check_env
            install_dependencies
            deploy_workers
            deploy_pages
            setup_m4_engine
            check_deployment
            ;;
    esac
    
    echo ""
    echo "🎉 デプロイ完了!"
    echo ""
    echo "次のステップ:"
    echo "1. wrangler.tomlのKV namespace IDを実際の値に更新"
    echo "2. .env.exampleを.envにコピーして環境変数を設定"
    echo "3. M4 Macエンジンを起動: cd m4-mac-engine && python main.py"
    echo ""
    echo "アクセスURL:"
    echo "- フロントエンド: https://keiba-prediction.pages.dev/"
    echo "- API: https://api.keiba-prediction.com/"
}

# 実行
main "$@"