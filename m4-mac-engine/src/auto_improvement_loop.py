"""
自動改善ループ
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
import json

from config import config
from .data_fetcher.jrdb_fetcher import JRDBFetcher
from .ml_engine.trainer import MLTrainer
from .ml_engine.simulator import RaceSimulator
from .claude_integration.claude_client import ClaudeClient
from .utils.cloudflare_sync import CloudflareSync

class AutoImprovementLoop:
    """自動改善ループ実装"""
    
    def __init__(self):
        self.cycle_count = 0
        self.best_return_rate = 0.0
        self.current_model_version = None
        
        # コンポーネント初期化
        self.data_fetcher = JRDBFetcher()
        self.ml_trainer = MLTrainer()
        self.simulator = RaceSimulator()
        self.claude_client = ClaudeClient()
        self.cf_sync = CloudflareSync()
        
        # パフォーマンス履歴
        self.performance_history = []
        
    async def run_cycle(self):
        """1サイクル実行"""
        self.cycle_count += 1
        cycle_start = datetime.now()
        
        logger.info(f"{'='*60}")
        logger.info(f"🔄 サイクル {self.cycle_count} 開始")
        logger.info(f"現在の最高還元率: {self.best_return_rate:.1%}")
        
        try:
            # Phase 1: データ取得
            logger.info("📊 Phase 1: データ取得")
            new_data = await self._fetch_latest_data()
            
            # Phase 2: 特徴量生成
            logger.info("🔧 Phase 2: 特徴量生成")
            train_data = await self._prepare_training_data(new_data)
            
            # Phase 3: Claude分析（5サイクルごと）
            if self.cycle_count % 5 == 0:
                logger.info("🤖 Phase 3: Claude分析")
                suggestions = await self._analyze_with_claude()
                await self._apply_suggestions(suggestions)
            
            # Phase 4: モデル学習
            logger.info("📚 Phase 4: モデル学習")
            model_info = await self._train_model(train_data)
            
            # Phase 5: シミュレーション
            logger.info("🎯 Phase 5: シミュレーション")
            performance = await self._run_simulation(model_info)
            
            # Phase 6: Cloudflare同期
            logger.info("☁️  Phase 6: モデル同期")
            await self._sync_to_cloudflare(model_info, performance)
            
            # 結果評価
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            self._evaluate_results(performance, cycle_duration)
            
        except Exception as e:
            logger.error(f"サイクルエラー: {e}", exc_info=True)
            
    async def _fetch_latest_data(self) -> Dict[str, Any]:
        """最新データ取得"""
        try:
            # JRDBからデータ取得（デモモードの場合は生成）
            if config.jrdb_username:
                return await self.data_fetcher.fetch_latest()
            else:
                logger.warning("JRDBクレデンシャル未設定 - デモデータを使用")
                return await self.data_fetcher.generate_demo_data()
        except Exception as e:
            logger.error(f"データ取得エラー: {e}")
            # エラー時はデモデータで継続
            return await self.data_fetcher.generate_demo_data()
    
    async def _prepare_training_data(self, raw_data: Dict[str, Any]) -> Any:
        """学習データ準備"""
        # 特徴量エンジニアリング
        processed_data = await self.ml_trainer.prepare_features(raw_data)
        
        # データ品質チェック
        quality_report = self.ml_trainer.check_data_quality(processed_data)
        logger.info(f"データ品質: {quality_report}")
        
        return processed_data
    
    async def _analyze_with_claude(self) -> Dict[str, Any]:
        """Claude APIで分析"""
        # 現在のパフォーマンス情報
        current_performance = {
            'return_rate': self.best_return_rate,
            'cycle_count': self.cycle_count,
            'history': self.performance_history[-10:],  # 直近10サイクル
            'current_features': config.feature_columns
        }
        
        # Claude分析実行
        suggestions = await self.claude_client.analyze_performance(current_performance)
        logger.info(f"Claude提案: {json.dumps(suggestions, ensure_ascii=False, indent=2)}")
        
        return suggestions
    
    async def _apply_suggestions(self, suggestions: Dict[str, Any]):
        """Claude提案を適用"""
        # 新しい特徴量の追加
        if 'new_features' in suggestions:
            for feature in suggestions['new_features']:
                if feature not in config.feature_columns:
                    config.feature_columns.append(feature)
                    logger.info(f"新特徴量追加: {feature}")
        
        # モデルパラメータの更新
        if 'model_params' in suggestions:
            config.model_params.update(suggestions['model_params'])
            logger.info(f"モデルパラメータ更新: {suggestions['model_params']}")
    
    async def _train_model(self, train_data: Any) -> Dict[str, Any]:
        """モデル学習"""
        # 学習実行
        model, metrics = await self.ml_trainer.train(train_data)
        
        # モデル情報
        model_info = {
            'version': f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'metrics': metrics,
            'feature_importance': self.ml_trainer.get_feature_importance(),
            'feature_count': len(config.feature_columns),
            'training_samples': len(train_data)
        }
        
        self.current_model_version = model_info['version']
        logger.info(f"モデル学習完了: {model_info['version']}")
        
        return model_info
    
    async def _run_simulation(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """シミュレーション実行"""
        # 過去30日分のデータでシミュレーション
        simulation_results = await self.simulator.run_backtest(
            self.ml_trainer.model,
            days=30
        )
        
        performance = {
            'return_rate': simulation_results['return_rate'],
            'hit_rate': simulation_results['hit_rate'],
            'total_bets': simulation_results['total_bets'],
            'profit': simulation_results['profit'],
            'max_drawdown': simulation_results['max_drawdown'],
            'sharpe_ratio': simulation_results['sharpe_ratio']
        }
        
        logger.info(f"シミュレーション結果: 還元率 {performance['return_rate']:.1%}")
        
        return performance
    
    async def _sync_to_cloudflare(self, model_info: Dict[str, Any], performance: Dict[str, Any]):
        """Cloudflareにモデル同期"""
        try:
            # モデルファイル保存
            model_path = config.model_dir / f"{model_info['version']}.lgb"
            self.ml_trainer.save_model(str(model_path))
            
            # メタデータ作成
            metadata = {
                'version': model_info['version'],
                'return_rate': performance['return_rate'],
                'hit_rate': performance['hit_rate'],
                'accuracy': model_info['metrics']['auc'],
                'feature_importance': model_info['feature_importance'],
                'timestamp': datetime.now().isoformat(),
                'cycle_count': self.cycle_count
            }
            
            # アップロード
            success = await self.cf_sync.upload_model(model_path, metadata)
            
            if success:
                logger.info("✅ モデル同期成功")
            else:
                logger.error("❌ モデル同期失敗")
                
        except Exception as e:
            logger.error(f"同期エラー: {e}")
    
    def _evaluate_results(self, performance: Dict[str, Any], cycle_duration: float):
        """結果評価"""
        # パフォーマンス履歴に追加
        self.performance_history.append({
            'cycle': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'return_rate': performance['return_rate'],
            'hit_rate': performance['hit_rate'],
            'duration_seconds': cycle_duration
        })
        
        # 最高記録更新チェック
        if performance['return_rate'] > self.best_return_rate:
            self.best_return_rate = performance['return_rate']
            logger.success(f"🎉 新記録達成! 還元率 {performance['return_rate']:.1%}")
            
            # 記録保存
            self._save_best_model(performance)
        
        # 目標達成チェック
        if performance['return_rate'] >= config.target_return_rate:
            logger.success(f"🏆 目標達成! 還元率 {performance['return_rate']:.1%}")
        else:
            gap = config.target_return_rate - performance['return_rate']
            logger.info(f"目標まであと {gap:.1%}")
        
        logger.info(f"サイクル実行時間: {cycle_duration:.1f}秒")
    
    def _save_best_model(self, performance: Dict[str, Any]):
        """最良モデルを保存"""
        best_model_info = {
            'version': self.current_model_version,
            'cycle': self.cycle_count,
            'performance': performance,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(config.model_dir / 'best_model.json', 'w') as f:
            json.dump(best_model_info, f, ensure_ascii=False, indent=2)
    
    async def cleanup(self):
        """クリーンアップ処理"""
        logger.info("クリーンアップ実行中...")
        
        # 最終レポート生成
        if self.performance_history:
            report = {
                'total_cycles': self.cycle_count,
                'best_return_rate': self.best_return_rate,
                'performance_history': self.performance_history,
                'final_model_version': self.current_model_version
            }
            
            report_path = config.log_dir / f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"最終レポート保存: {report_path}")