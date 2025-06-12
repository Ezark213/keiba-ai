#!/usr/bin/env python3
"""
競馬予測システム - M4 Mac実行エンジン
Cloudflare連携・Claude API統合版
"""

import sys
import asyncio
import signal
from datetime import datetime
from loguru import logger

from config import config
from src.auto_improvement_loop import AutoImprovementLoop

# ロガー設定
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    config.log_dir / "keiba_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)

class KeibaMLEngine:
    """メインエンジンクラス"""
    
    def __init__(self):
        self.loop = None
        self.running = False
        
    async def start(self):
        """エンジン起動"""
        logger.info("🚀 競馬予測システム v3.0 起動")
        logger.info(f"目標還元率: {config.target_return_rate:.0%}")
        logger.info(f"実行間隔: {config.cycle_interval_minutes}分")
        
        # 設定検証
        if not config.validate():
            logger.error("設定エラー: 必要な環境変数を設定してください")
            return
        
        # 自動改善ループ初期化
        self.loop = AutoImprovementLoop()
        self.running = True
        
        # 初回実行
        await self.loop.run_cycle()
        
        # 定期実行
        while self.running:
            await asyncio.sleep(config.cycle_interval_minutes * 60)
            if self.running:
                await self.loop.run_cycle()
    
    async def stop(self):
        """エンジン停止"""
        logger.info("🛑 停止処理中...")
        self.running = False
        
        if self.loop:
            await self.loop.cleanup()
        
        logger.info("✅ 正常に停止しました")

def main():
    """メイン実行"""
    print("""
    ╔════════════════════════════════════════════════╗
    ║     競馬予測システム v3.0 - M4 Mac Engine     ║
    ║         Cloudflare & Claude 統合版             ║
    ╚════════════════════════════════════════════════╝
    """)
    
    print(f"""
    設定内容:
    - Cloudflare API: {config.cloudflare_api_url}
    - 目標還元率: {config.target_return_rate:.0%}
    - 実行間隔: {config.cycle_interval_minutes}分
    - データ保存先: {config.data_dir}
    
    環境変数ステータス:
    - CLAUDE_API_KEY: {'✓' if config.claude_api_key else '✗'}
    - CF_SYNC_TOKEN: {'✓' if config.cloudflare_sync_token else '✗'}
    - JRDB認証: {'✓' if config.jrdb_username else '✗ (必須)'}
    """)
    
    # JRDB認証情報を必須に
    if not all([config.claude_api_key, config.cloudflare_sync_token, config.jrdb_username, config.jrdb_password]):
        print("\n⚠️  必要な環境変数が設定されていません。")
        print("本物のデータを使用するため、以下の全ての環境変数が必須です:")
        print("  export CLAUDE_API_KEY='your-api-key'")
        print("  export CF_SYNC_TOKEN='your-sync-token'")
        print("  export JRDB_USERNAME='your-username' (必須)")
        print("  export JRDB_PASSWORD='your-password' (必須)")
        print("\n※ デモモードは廃止されました。常に本物のデータを使用します。")
        return
    
    print("\n開始するにはEnterキーを押してください (終了: Ctrl+C)")
    input()
    
    # エンジン起動
    engine = KeibaMLEngine()
    
    # シグナルハンドラー設定
    def signal_handler(signum, frame):
        logger.info("終了シグナルを受信しました")
        asyncio.create_task(engine.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 非同期実行
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        logger.info("キーボード割り込みを検出")
    except Exception as e:
        logger.exception(f"予期しないエラー: {e}")
    finally:
        logger.info("プログラムを終了します")

if __name__ == "__main__":
    main()