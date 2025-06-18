# 🔐 セキュリティガイド

競馬予測システムのセキュリティ対策と機密情報の安全な管理について説明します。

## 🚨 重要な変更

### Claude API不使用に変更
- **Claude API**: 使用しない（Claude Code環境で直接実行）
- **Claude APIキー**: 設定不要
- **実行方式**: あなた（Claude）が直接システムを操作

## 🔒 機密情報の管理

### 1. 認証情報の種類

#### 必須項目
- `CF_SYNC_TOKEN`: Cloudflare同期トークン
- `JRDB_USERNAME`: JRDB ユーザー名（キーチェーンで管理）
- `JRDB_PASSWORD`: JRDB パスワード（キーチェーンで管理）

#### ✅ セキュリティ実装状況
- ✅ JRDBクレデンシャル: キーチェーンに安全に保存済み
- ✅ .env ファイル: プレースホルダーのみ（実際の値なし）
- ✅ .gitignore: 機密情報ファイルを完全除外
- ✅ 本番環境URL: 固定ドメイン設定完了

#### オプション項目
- その他のAPI認証情報

### 2. セキュア保存方式

#### A. システムキーチェーン（推奨）
```bash
# セキュア設定スクリプト実行
cd m4-mac-engine
python -m src.utils.secure_config
```
- macOS: Keychain Access
- Windows: Credential Manager
- Linux: Secret Service API

#### B. 暗号化ファイル
- 認証情報を暗号化して保存
- AES-256暗号化
- 600パーミッション（所有者のみアクセス）

#### C. 環境変数（開発用）
```bash
export CF_SYNC_TOKEN="your-token"
# ⚠️ JRDBクレデンシャルは環境変数ではなくキーチェーンで管理
# export JRDB_USERNAME="your-username"  # 使用禁止
# export JRDB_PASSWORD="your-password"  # 使用禁止
```

### 4. セキュリティ改善実装

#### キーチェーン統合の確認
```bash
# キーチェーンからの認証情報読み込みテスト
cd m4-mac-engine
source venv/bin/activate
python3 -c "
from src.utils.secure_config import SecureConfigManager
secure_config = SecureConfigManager()
creds = secure_config.get_jrdb_credentials()
print('✅ キーチェーン認証:', '成功' if creds else '失敗')
"
```

#### SOLID原則準拠アーキテクチャ
- **単一責任原則**: 各クラスが単一の責任を持つ
- **開放閉鎖原則**: 拡張可能な特徴量エンジニアリング
- **依存性逆転**: インターフェースベースの設計
- **プラグイン式ベッティング戦略**: Kelly・固定額・比例戦略

### 3. .envファイルの保護

```bash
# .envファイルのパーミッション設定
chmod 600 .env

# Git追跡除外確認
git status  # .envが表示されないことを確認
```

## 📁 保護されるファイル

### .gitignoreで除外済み
```
.env
*.env
.env.local
.env.production
*api_key*
*token*
*secret*
*password*
credentials.json
claude_state.json
data/races/*.json
logs/
```

### セキュアディレクトリ
```
~/.config/keiba-prediction/  # 設定ディレクトリ
├── secure_config.enc        # 暗号化設定
├── .encryption_key          # 暗号化キー
└── backup/                  # バックアップ
```

## 🛡️ セキュリティベストプラクティス

### 1. 認証情報のローテーション
```bash
# 定期的な認証情報更新（推奨: 3ヶ月ごと）
python -m src.utils.secure_config
```

### 2. アクセス制御
```bash
# ファイルパーミッション確認
ls -la .env claude_state.json

# 適切なパーミッション設定
chmod 600 .env
chmod 600 claude_state.json
```

### 3. ログの機密情報除外
```python
# ログから機密情報を除外
logger.info(f"JRDB接続: {username[:3]}***")  # 一部のみ表示
logger.info(f"Token: {token[:8]}...")        # 冒頭のみ表示
```

### 4. バックアップの暗号化
```bash
# 設定のバックアップ
python -c "
from src.utils.secure_config import SecureConfigManager
manager = SecureConfigManager()
# 自動でバックアップが暗号化保存される
"
```

## 🔧 セキュア設定の使い方

### 初回設定
```bash
cd m4-mac-engine
python -m src.utils.secure_config
```

### 対話的設定
```
🔐 競馬予測システム - セキュア設定
==================================================
Claude API Key: （不要 - スキップ）
Cloudflare Sync Token: your-token-here
JRDB Username: 25067698
JRDB Password: [隠し入力]

この情報をキーチェーンに保存しますか？ (y/N): y
✅ 全ての認証情報を安全に保存しました
```

### 設定確認
```bash
python -c "
from src.utils.secure_config import SecureConfigManager
manager = SecureConfigManager()
jrdb = manager.get_jrdb_credentials()
api = manager.get_api_credentials()
print('JRDB:', '✓' if jrdb else '✗')
print('API:', '✓' if api else '✗')
"
```

### 設定クリア
```bash
python -c "
from src.utils.secure_config import SecureConfigManager
manager = SecureConfigManager()
manager.clean_credentials()
"
```

## ⚡ クイックセットアップ

### セキュア設定付きでシステム開始
```bash
# 1. セキュア認証情報設定
cd m4-mac-engine
python -m src.utils.secure_config

# 2. システム起動
make start-claude
```

## 🚨 インシデント対応

### 認証情報漏洩時の対応
1. **即座に認証情報を変更**
2. **古い認証情報を無効化**
3. **システムの設定を更新**
4. **ログの確認**

```bash
# 緊急時の認証情報クリア
python -m src.utils.secure_config clean

# 新しい認証情報で再設定
python -m src.utils.secure_config
```

### ログ監視
```bash
# セキュリティ関連ログ監視
tail -f logs/claude_engine_*.log | grep -i "auth\|credential\|token"
```

## 📋 セキュリティチェックリスト

- [ ] .envファイルが.gitignoreに含まれている
- [ ] 認証情報がキーチェーンに保存されている
- [ ] ファイルパーミッションが適切（600）
- [ ] ログに機密情報が含まれていない
- [ ] 定期的な認証情報ローテーション計画
- [ ] バックアップが暗号化されている

## 🔍 セキュリティ監査

### 月次チェック
```bash
# 1. 認証情報の有効性確認
make check-env

# 2. ファイルパーミッション確認
find . -name "*.env" -o -name "*credential*" | xargs ls -la

# 3. ログの機密情報チェック
grep -r "password\|token\|key" logs/ || echo "機密情報なし"
```

---

**🛡️ セキュリティは継続的な取り組みです。定期的な見直しと更新を心がけてください。**