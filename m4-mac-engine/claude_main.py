#!/usr/bin/env python3
"""
競馬予測システム - Claude主導実行エンジン
Claude自身がシステムを操作・改善する特別版
"""

import sys
import asyncio
import signal
from datetime import datetime
from loguru import logger

from config import config
from src.claude_integration.live_claude_direct import ClaudeDirectIntegration
from src.auto_improvement_loop import AutoImprovementLoop

# ロガー設定
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    config.log_dir / "claude_engine_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days", 
    level="DEBUG"
)

class ClaudeControlledEngine:
    """Claude主導の競馬予測エンジン"""
    
    def __init__(self):
        self.claude_integration = ClaudeDirectIntegration()
        self.auto_loop = AutoImprovementLoop()
        self.running = False
        
    async def start(self):
        """Claude主導エンジン起動"""
        logger.info("🤖 Claude主導競馬予測システム起動")
        logger.info("="*60)
        logger.info("🎯 目標: Claude自身による継続的改善で還元率80%達成")
        logger.info("🔄 動作: Claude Code環境でリアルタイム分析・改善")
        logger.info("📊 監視: 30分ごとの自動学習・最適化サイクル")
        logger.info("="*60)
        
        # 設定検証
        if not config.validate():
            logger.error("設定エラー: 必要な環境変数を設定してください")
            return
        
        # 初期状態確認
        await self._initial_system_check()
        
        self.running = True
        
        # メインループ選択
        mode = await self._select_execution_mode()
        
        if mode == "claude_live":
            await self._run_claude_live_mode()
        elif mode == "hybrid":
            await self._run_hybrid_mode()
        else:
            await self._run_standard_mode()
    
    async def _initial_system_check(self):
        """初期システムチェック"""
        logger.info("🔍 システム初期チェック中...")
        
        # データディレクトリ確認
        data_exists = any(config.race_data_dir.glob("*.json"))
        logger.info(f"レースデータ: {'✓' if data_exists else '✗'}")
        
        # モデルファイル確認
        model_exists = any(config.model_dir.glob("*.lgb"))
        logger.info(f"学習済みモデル: {'✓' if model_exists else '✗'}")
        
        # Claude状態確認
        claude_state = self.claude_integration.state
        logger.info(f"Claudeサイクル数: {claude_state['cycle_count']}")
        logger.info(f"最高還元率: {claude_state['best_return_rate']:.1%}")
        
        logger.info("✅ システムチェック完了")
    
    async def _select_execution_mode(self) -> str:
        """実行モード選択"""
        logger.info("実行モード選択:")
        logger.info("1. claude_live - Claude主導リアルタイム分析")
        logger.info("2. hybrid     - Claude統合ハイブリッド")
        logger.info("3. standard   - 従来の自動改善ループ")
        
        # 環境に応じて自動選択
        if hasattr(sys, '_getframe'):
            # Claude Code環境検出（簡易版）
            return "claude_live"
        else:
            return "hybrid"
    
    async def _run_claude_live_mode(self):
        """Claude主導ライブモード"""
        logger.success("🤖 Claude主導ライブモード開始")
        logger.info("Claude自身がシステムを直接操作・改善します")
        
        try:
            # Claudeによる継続的分析・改善（直接実行）
            await self.claude_integration.start_direct_analysis_cycle()
            
        except Exception as e:
            logger.error(f"Claude主導モードエラー: {e}")
            logger.info("ハイブリッドモードにフォールバック...")
            await self._run_hybrid_mode()
    
    async def _run_hybrid_mode(self):
        """ハイブリッドモード"""
        logger.info("🔄 ハイブリッドモード開始")
        logger.info("従来ループ + Claude分析の組み合わせ")
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"🔄 ハイブリッドサイクル {cycle_count} 開始")
                
                # 1. 従来の改善ループ実行
                await self.auto_loop.run_cycle()
                
                # 2. Claude分析（5サイクルごと）
                if cycle_count % 5 == 0:
                    logger.info("🤖 Claude追加分析実行...")
                    claude_analysis = await self.claude_integration.analyze_current_state_direct()
                    
                    if claude_analysis['needs_improvement']:
                        await self.claude_integration.implement_improvements_direct(claude_analysis)
                
                # 次のサイクルまで待機
                await asyncio.sleep(config.cycle_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"ハイブリッドサイクルエラー: {e}")
                await asyncio.sleep(60)
    
    async def _run_standard_mode(self):
        """標準モード"""
        logger.info("⚙️  標準自動改善モード開始")
        await self.auto_loop.run_cycle()
    
    async def stop(self):
        """エンジン停止"""
        logger.info("🛑 Claude主導エンジン停止処理中...")
        self.running = False
        
        # 最終レポート生成
        await self._generate_final_report()
        
        logger.info("✅ 正常に停止しました")
    
    async def _generate_final_report(self):
        """最終レポート生成"""
        claude_state = self.claude_integration.state
        
        report = {
            'session_end': datetime.now().isoformat(),
            'total_cycles': claude_state['cycle_count'],
            'best_return_rate': claude_state['best_return_rate'],
            'improvements_implemented': len(claude_state['improvement_log']),
            'claude_insights_count': len(claude_state['claude_insights']),
            'final_performance': claude_state.get('last_analysis', {}),
            'target_achievement': claude_state['best_return_rate'] >= config.target_return_rate
        }
        
        report_path = config.log_dir / f"claude_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 最終レポート保存: {report_path}")
        
        # サマリー表示
        logger.info("📈 セッションサマリー:")
        logger.info(f"  総サイクル数: {report['total_cycles']}")
        logger.info(f"  最高還元率: {report['best_return_rate']:.1%}")
        logger.info(f"  目標達成: {'✅' if report['target_achievement'] else '❌'}")
        logger.info(f"  実装改善数: {report['improvements_implemented']}")

def main():
    """メイン実行"""
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║        🤖 Claude主導競馬予測システム v3.0           ║
    ║                                                      ║
    ║    Claude自身がシステムを操作・改善する特別版        ║
    ║          リアルタイム分析・継続的最適化             ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    print(f"""
    🎯 システム設定:
    - 目標還元率: {config.target_return_rate:.0%}
    - 実行間隔: {config.cycle_interval_minutes}分
    - Claude統合: ✓ 直接実行モード（API不使用）
    - JRDB接続: {'✓' if config.jrdb_username else '○ デモモード'}
    
    🤖 Claude機能:
    - 直接分析・改善実装
    - リアルタイム還元率表示
    - 継続的最適化
    - 状態保持・学習
    
    """)
    
    if not config.validate():
        print("⚠️  設定を確認してください")
        return
    
    print("🚀 Claude主導エンジンを開始します...")
    print("終了: Ctrl+C")
    print("="*60)
    
    # エンジン起動
    engine = ClaudeControlledEngine()
    
    # シグナルハンドラー設定
    def signal_handler(signum, frame):
        logger.info("終了シグナルを受信")
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
        logger.info("Claude主導エンジン終了")

if __name__ == "__main__":
    main()