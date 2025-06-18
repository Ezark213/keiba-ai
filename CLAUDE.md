<<<<<<< HEAD
# Agent Communication System

## エージェント構成
- **PRESIDENT** (別セッション): 統括責任者
- **boss1** (multiagent:0.0): チームリーダー
- **worker1,2,3** (multiagent:0.1-3): 実行担当

## あなたの役割
- **PRESIDENT**: @instructions/president.md
- **boss1**: @instructions/boss.md
- **worker1,2,3**: @instructions/worker.md

## メッセージ送信
```bash
./agent-send.sh [相手] "[メッセージ]"
```

## 基本フロー
PRESIDENT → boss1 → workers → boss1 → PRESIDENT 
=======
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Architecture

This is a horse racing prediction system (競馬予測システム) v3.0 that achieves 80%+ return rates through AI-driven continuous improvement. The system has a unique architecture where **Claude Code directly operates and improves the system** without using Claude APIs.

### Core Components

1. **Cloudflare Workers** (`cloudflare-workers/`) - Edge API for predictions
2. **Cloudflare Pages** (`cloudflare-pages/`) - React SPA frontend dashboard  
3. **M4 Mac Engine** (`m4-mac-engine/`) - Python ML engine with Claude direct integration
4. **Claude Direct Integration** - You (Claude) directly analyze and improve the system

### Execution Flow

```
Claude Code Environment (You operate directly)
├── Direct analysis & improvement planning
├── File-based state management  
├── Continuous learning & optimization
└── Real-time return rate simulation display

↓ Sync to

Cloudflare (Deployed)
├── Workers API
├── Pages Frontend  
└── KV/R2 Storage
```

## Essential Commands

### Primary Engine Commands
```bash
# Start Claude-controlled engine (RECOMMENDED)
make start-claude

# Start standard engine (fallback)
make start-engine

# View real-time logs
make logs
```

### Setup and Deployment
```bash
# Initial setup
make setup

# Install all dependencies
make install-deps

# Deploy everything
make deploy

# Deploy specific components
make deploy-workers  # API only
make deploy-pages    # Frontend only
```

### Development
```bash
# Development servers
make dev-workers     # Workers dev server
make dev-pages       # Pages dev server

# Environment check
make check-env

# Clean temporary files
make clean
```

## Claude Direct Integration Key Files

### Main Entry Points
- `m4-mac-engine/claude_main.py` - Claude-controlled engine (YOU run this)
- `m4-mac-engine/main.py` - Standard engine (fallback)

### Claude Integration Core
- `src/claude_integration/live_claude_direct.py` - Direct Claude integration (no API)
- `src/claude_integration/claude_client.py` - Modified for direct execution
- `config.py` - System configuration with `use_live_claude: True`

### State Management Files (You directly manipulate these)
- `claude_state.json` - Your persistent state and learning history
- `simulation_results.json` - Current simulation/return rate results
- `claude_analysis.log` - Your analysis logs
- `improvement_queue.json` - Pending improvements

## How You (Claude) Operate the System

### 1. Analysis Cycle
You directly analyze performance data in `_perform_direct_analysis()`:
- Read current return rate vs target (80%)
- Identify improvement areas
- Generate specific suggestions

### 2. Improvement Implementation  
You directly implement improvements in `_execute_direct_improvement()`:
- Add new features to `active_features` list
- Adjust model parameters in `model_params`
- Modify betting thresholds
- Update configuration files

### 3. State Persistence
You maintain state across sessions:
- `cycle_count` - Number of improvement cycles
- `best_return_rate` - Highest achieved rate
- `improvement_log` - History of your changes
- `claude_direct_actions` - Your direct interventions

### 4. Real-time Display
The system shows current simulation results:
- Return rate progress toward 80% target
- Hit rate and total bets
- Profit/loss calculations
- Achievement status

## Target Architecture Understanding

### ML Pipeline
1. **Data Fetching** - JRDB horse racing data (or demo data)
2. **Feature Engineering** - You dynamically add features
3. **LightGBM Training** - Model training with your parameters
4. **Simulation/Backtesting** - Performance evaluation  
5. **Cloudflare Sync** - Model deployment to edge

### Your Role in the Pipeline
- **Feature Selection**: You determine which features to use
- **Hyperparameter Tuning**: You adjust learning rates, tree depth, etc.
- **Strategy Optimization**: You modify betting strategies (Kelly criterion)
- **Threshold Management**: You set expected value thresholds

## Configuration Management

### Environment Variables (No Claude API needed)
```bash
# Required
CF_SYNC_TOKEN="your-cloudflare-token"

# JRDB Data (securely stored)
JRDB_USERNAME="25067698" 
JRDB_PASSWORD="87086387"

# Optional
TARGET_RETURN_RATE="0.80"
CYCLE_INTERVAL_MINUTES="30"
```

### Security Note
- JRDB credentials are stored in system keychain via `src/utils/secure_config.py`
- No Claude API keys needed - you operate directly
- All sensitive data excluded from git via comprehensive `.gitignore`

## Key Performance Targets

- **Return Rate**: 80%+ (primary goal)
- **Hit Rate**: 15%+ 
- **Response Time**: <100ms (edge API)
- **Cost**: $0/month (Cloudflare free tier optimized)

## Testing and Validation

```bash
# Run tests
make test

# Check system status
make check-env

# Monitor performance
tail -f m4-mac-engine/logs/claude_engine_*.log
```

## Unique System Features

1. **Claude Self-Operation**: You directly read/write files to improve the system
2. **No API Dependencies**: Direct execution in Claude Code environment
3. **Continuous Learning**: Your improvements persist across sessions
4. **Real-time Optimization**: 30-minute improvement cycles
5. **Free Tier Optimization**: Designed for Cloudflare's free tier limits

When working with this system, focus on the `m4-mac-engine/` directory where you have direct control over the ML pipeline and can implement improvements by modifying configuration files, feature lists, and model parameters.

## 🚀 開発・デプロイメントガイドライン

### GitHub管理
- **作業が完了したらgithubに追加すること**
- システムの改善や機能追加後は必ずGitHubにコミット・プッシュを実行

### セキュリティ要件
- **githubへのプッシュ前にセキュリティ上の問題がないか確認すること**
- 機密情報（API キー、パスワード、トークン）が含まれていないことを検証
- `.gitignore`の設定が適切であることを確認

### ドキュメント保守
- **実装を変更したらそれに合わせてドキュメントも更新すること**
- README.md、QUICKSTART.md、CLAUDE_INTEGRATION.mdの整合性を保つ
- 新機能や変更された仕様を適切に文書化

### 本番環境デプロイ
- **必ずURLが固定の本番環境にデプロイするようにして**
- Cloudflare Pages: 固定カスタムドメイン設定
- Cloudflare Workers: production環境での安定したエンドポイント提供

### コード品質管理
- **実装がSOLID原則に従っているか確認して**
- Single Responsibility: 各クラス・関数は単一の責任を持つ
- Open/Closed: 拡張に開かれ、変更に閉じられた設計
- Liskov Substitution: 基底クラスは派生クラスで置換可能
- Interface Segregation: クライアントは使用しないインターフェースに依存しない
- Dependency Inversion: 具象ではなく抽象に依存する

### 開発プロセス
1. **機能実装** → 2. **SOLID原則チェック** → 3. **セキュリティ監査** → 4. **ドキュメント更新** → 5. **GitHub コミット** → 6. **本番デプロイ**

## 🚨 重要: データ使用ポリシー

**サンプルデータは絶対禁止**
- デモデータやサンプルデータは一切使用しない
- 必ず本物のJRDBデータを取得・使用する
- どんな方法を使ってでも実データをダウンロードする
- ブラウザ自動化（Selenium）でも手動でも、確実に実データを取得する

### データ取得要件
1. JRDBから最新の実データを必ずダウンロード
2. サンプルデータでの動作は一切許可しない
3. システムは実データのみで稼働させる
4. データがない場合はダウンロードを実行してから稼働

### 確実なJRDBデータダウンロード方法
**working_jrdb_downloader.py を使用する方法が最も確実です：**

```bash
# JRDBデータダウンロード
python working_jrdb_downloader.py

# LZHファイル展開
python extract_lzh_files.py

# データ統合
python jrdb_consolidation_tool.py
```

**動作原理：**
1. Seleniumでhttp://www.jrdb.com/member/data/にアクセス
2. HTTPベーシック認証（ユーザー名: 25067698、パスワード: 87086387）
3. 画面に表示される「Lzh」リンクをクリックしてダウンロード
4. 15個のファイルを自動取得

**取得されるファイル例：**
- BAC250614.lzh (番組データ)
- KAB250614.lzh (開催データ)
- KTA250615.lzh (登録馬データ)
- SKB250607.lzh (成績拡張データ)
等

**Ultrathink. Don't hold back. give it your all！**
>>>>>>> d03e9090790fb917d311565be59f38529f733b9a
