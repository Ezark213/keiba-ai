"""
Claude Code統合 - ライブ分析システム
Claude自身がシステムを操作・改善するための統合レイヤー
"""
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger
import pandas as pd
import numpy as np

from config import config

class ClaudeLiveIntegration:
    """Claude Code環境での直接実行統合"""
    
    def __init__(self):
        self.state_file = config.base_dir / "claude_state.json"
        self.session_file = config.base_dir / "current_session.json"
        self.analysis_history = config.base_dir / "analysis_history.json"
        self.is_live_claude = True
        
        # 状態初期化
        self.load_state()
        
    def load_state(self):
        """状態読み込み"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            else:
                self.state = self._init_default_state()
                self.save_state()
        except Exception as e:
            logger.error(f"状態読み込みエラー: {e}")
            self.state = self._init_default_state()
    
    def save_state(self):
        """状態保存"""
        try:
            self.state['last_updated'] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"状態保存エラー: {e}")
    
    def _init_default_state(self) -> Dict[str, Any]:
        """デフォルト状態"""
        return {
            'cycle_count': 0,
            'best_return_rate': 0.0,
            'current_strategy': 'baseline',
            'active_features': config.feature_columns.copy(),
            'model_params': config.model_params.copy(),
            'performance_history': [],
            'improvement_log': [],
            'claude_insights': [],
            'last_analysis': None,
            'target_metrics': {
                'return_rate': config.target_return_rate,
                'hit_rate': 0.15,
                'max_drawdown': 0.1
            }
        }
    
    async def start_live_analysis_cycle(self):
        """ライブ分析サイクル開始"""
        logger.info("🤖 Claude主導の分析サイクル開始")
        
        # セッション情報記録
        session_info = {
            'session_id': f"claude_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'claude_version': 'claude-sonnet-4',
            'mode': 'live_analysis'
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, ensure_ascii=False, indent=2)
        
        while True:
            try:
                # 1. 現状分析
                analysis_result = await self.analyze_current_state()
                
                # 2. 改善実装
                if analysis_result['needs_improvement']:
                    await self.implement_improvements(analysis_result)
                
                # 3. 結果評価
                await self.evaluate_improvements()
                
                # 4. 状態更新
                self.state['cycle_count'] += 1
                self.save_state()
                
                # 次のサイクルまで待機
                logger.info(f"次のサイクルまで{config.cycle_interval_minutes}分待機...")
                await asyncio.sleep(config.cycle_interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("分析サイクル停止")
                break
            except Exception as e:
                logger.error(f"サイクルエラー: {e}")
                await asyncio.sleep(60)  # エラー時は1分待機
    
    async def analyze_current_state(self) -> Dict[str, Any]:
        """現状分析 - Claude自身が実行"""
        logger.info("🔍 現状分析実行中...")
        
        # パフォーマンスデータ読み込み
        performance_data = self.load_performance_data()
        
        # 分析実行
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.state['cycle_count'],
            'current_performance': performance_data,
            'needs_improvement': False,
            'improvement_suggestions': [],
            'confidence_level': 0.0
        }
        
        # 還元率チェック
        current_return_rate = performance_data.get('return_rate', 0)
        target_return_rate = self.state['target_metrics']['return_rate']
        
        if current_return_rate < target_return_rate:
            gap = target_return_rate - current_return_rate
            analysis['needs_improvement'] = True
            analysis['confidence_level'] = min(gap * 10, 1.0)  # ギャップに応じた信頼度
            
            # 改善提案生成
            suggestions = self.generate_improvement_suggestions(performance_data, gap)
            analysis['improvement_suggestions'] = suggestions
        
        # 履歴に追加
        self.state['claude_insights'].append(analysis)
        self.state['last_analysis'] = analysis
        
        logger.info(f"分析完了 - 改善必要: {analysis['needs_improvement']}")
        return analysis
    
    def generate_improvement_suggestions(self, performance_data: Dict[str, Any], gap: float) -> List[Dict[str, Any]]:
        """改善提案生成"""
        suggestions = []
        
        # ギャップの大きさに応じた提案
        if gap > 0.1:  # 10%以上のギャップ
            suggestions.append({
                'type': 'feature_engineering',
                'priority': 'high',
                'action': 'add_interaction_features',
                'description': '相互作用特徴量の追加で予測精度向上',
                'expected_improvement': 0.05
            })
            
            suggestions.append({
                'type': 'model_tuning',
                'priority': 'high', 
                'action': 'adjust_learning_rate',
                'description': '学習率を上げてより積極的な学習',
                'expected_improvement': 0.03
            })
            
        elif gap > 0.05:  # 5%以上のギャップ
            suggestions.append({
                'type': 'betting_strategy',
                'priority': 'medium',
                'action': 'increase_kelly_fraction',
                'description': 'より積極的なケリー基準',
                'expected_improvement': 0.02
            })
            
        else:  # 5%未満のギャップ
            suggestions.append({
                'type': 'fine_tuning',
                'priority': 'low',
                'action': 'optimize_thresholds',
                'description': '期待値閾値の微調整',
                'expected_improvement': 0.01
            })
        
        return suggestions
    
    async def implement_improvements(self, analysis_result: Dict[str, Any]):
        """改善実装 - Claude自身が実行"""
        logger.info("🔧 改善実装開始...")
        
        implemented_count = 0
        
        for suggestion in analysis_result['improvement_suggestions']:
            try:
                success = await self.execute_improvement(suggestion)
                if success:
                    implemented_count += 1
                    
                    # 実装ログ
                    self.state['improvement_log'].append({
                        'timestamp': datetime.now().isoformat(),
                        'suggestion': suggestion,
                        'status': 'implemented'
                    })
                    
            except Exception as e:
                logger.error(f"改善実装エラー: {e}")
                
        logger.info(f"改善実装完了: {implemented_count}件")
        
    async def execute_improvement(self, suggestion: Dict[str, Any]) -> bool:
        """個別改善実行"""
        action = suggestion['action']
        
        try:
            if action == 'add_interaction_features':
                return await self.add_interaction_features()
            elif action == 'adjust_learning_rate':
                return await self.adjust_learning_rate(suggestion)
            elif action == 'increase_kelly_fraction':
                return await self.adjust_kelly_fraction(suggestion)
            elif action == 'optimize_thresholds':
                return await self.optimize_thresholds(suggestion)
            else:
                logger.warning(f"未知の改善アクション: {action}")
                return False
                
        except Exception as e:
            logger.error(f"改善実行エラー {action}: {e}")
            return False
    
    async def add_interaction_features(self) -> bool:
        """相互作用特徴量追加"""
        new_features = [
            'idm_jockey_interaction',
            'trainer_distance_synergy', 
            'pace_track_affinity',
            'weight_condition_factor'
        ]
        
        # 特徴量リストに追加
        for feature in new_features:
            if feature not in self.state['active_features']:
                self.state['active_features'].append(feature)
                
        logger.info(f"相互作用特徴量追加: {new_features}")
        return True
    
    async def adjust_learning_rate(self, suggestion: Dict[str, Any]) -> bool:
        """学習率調整"""
        current_lr = self.state['model_params']['learning_rate']
        new_lr = min(current_lr * 1.2, 0.1)  # 20%増加、最大0.1
        
        self.state['model_params']['learning_rate'] = new_lr
        logger.info(f"学習率調整: {current_lr} → {new_lr}")
        return True
    
    async def adjust_kelly_fraction(self, suggestion: Dict[str, Any]) -> bool:
        """ケリー基準調整"""
        current_kelly = config.kelly_fraction
        new_kelly = min(current_kelly * 1.1, 0.4)  # 10%増加、最大0.4
        
        config.kelly_fraction = new_kelly
        logger.info(f"ケリー基準調整: {current_kelly} → {new_kelly}")
        return True
    
    async def optimize_thresholds(self, suggestion: Dict[str, Any]) -> bool:
        """閾値最適化"""
        current_threshold = config.min_expected_value
        new_threshold = max(current_threshold * 0.95, 1.1)  # 5%減少、最小1.1
        
        config.min_expected_value = new_threshold
        logger.info(f"期待値閾値調整: {current_threshold} → {new_threshold}")
        return True
    
    def load_performance_data(self) -> Dict[str, Any]:
        """パフォーマンスデータ読み込み"""
        try:
            # 最新のバックテスト結果読み込み
            performance_files = list(config.log_dir.glob("performance_*.json"))
            if performance_files:
                latest_file = max(performance_files, key=lambda x: x.stat().st_mtime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # デフォルト値
                return {
                    'return_rate': 0.70,
                    'hit_rate': 0.12,
                    'total_bets': 100,
                    'profit': -30000
                }
        except Exception as e:
            logger.error(f"パフォーマンスデータ読み込みエラー: {e}")
            return {'return_rate': 0.0, 'hit_rate': 0.0}
    
    async def evaluate_improvements(self):
        """改善評価"""
        logger.info("📊 改善効果評価中...")
        
        # 最新のパフォーマンス取得
        current_performance = self.load_performance_data()
        current_return_rate = current_performance.get('return_rate', 0)
        
        # 過去の性能と比較
        if self.state['performance_history']:
            previous_performance = self.state['performance_history'][-1]
            previous_return_rate = previous_performance.get('return_rate', 0)
            
            improvement = current_return_rate - previous_return_rate
            
            if improvement > 0:
                logger.success(f"✅ 改善効果確認: +{improvement:.1%}")
                self.state['best_return_rate'] = max(
                    self.state['best_return_rate'], 
                    current_return_rate
                )
            else:
                logger.warning(f"⚠️  性能低下: {improvement:.1%}")
        
        # 履歴に追加
        performance_record = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self.state['cycle_count'],
            **current_performance
        }
        
        self.state['performance_history'].append(performance_record)
        
        # 履歴サイズ制限（最新100件のみ保持）
        if len(self.state['performance_history']) > 100:
            self.state['performance_history'] = self.state['performance_history'][-100:]
    
    def get_analysis_prompt(self) -> str:
        """Claude自身への分析プロンプト"""
        current_state = self.state
        
        return f"""
        ## 競馬予測システム - 現状分析と改善提案

        あなたは競馬予測システムの運用責任者として、現在の状況を分析し、
        目標還元率{current_state['target_metrics']['return_rate']:.0%}達成のための改善策を立案してください。

        ### 現在の状況
        - サイクル数: {current_state['cycle_count']}
        - 最高還元率: {current_state['best_return_rate']:.1%}
        - 現在戦略: {current_state['current_strategy']}
        - アクティブ特徴量数: {len(current_state['active_features'])}

        ### 最新パフォーマンス
        {json.dumps(current_state.get('last_analysis', {}), ensure_ascii=False, indent=2)}

        ### 改善履歴（直近5件）
        {json.dumps(current_state['improvement_log'][-5:], ensure_ascii=False, indent=2)}

        ### 分析要求
        1. 現状の課題を特定
        2. 最も効果的な改善策を3つ提案
        3. 各改善策の期待効果を数値化
        4. 実装優先度を設定
        5. リスク評価を実施

        ### 出力形式
        JSON形式で以下の構造で回答：
        ```json
        {{
            "analysis": {{
                "current_status": "現状評価",
                "main_issues": ["課題1", "課題2"],
                "strength_points": ["強み1", "強み2"]
            }},
            "improvement_plan": [
                {{
                    "title": "改善策タイトル",
                    "description": "詳細説明",
                    "expected_improvement": 0.05,
                    "priority": "high",
                    "risk_level": "low",
                    "implementation_steps": ["ステップ1", "ステップ2"]
                }}
            ],
            "recommended_actions": [
                "即座に実行すべきアクション1",
                "即座に実行すべきアクション2"
            ]
        }}
        ```

        目標達成に向けて、具体的で実行可能な改善策を提案してください。
        """
    
    async def generate_feature_prompt(self) -> str:
        """特徴量生成プロンプト"""
        sample_data = self.load_sample_race_data()
        
        return f"""
        ## 新特徴量設計タスク

        競馬予測の精度向上のため、新しい特徴量を設計してください。

        ### 現在の特徴量
        {self.state['active_features']}

        ### サンプルデータ
        {json.dumps(sample_data, ensure_ascii=False, indent=2)[:2000]}...

        ### 設計要求
        1. 予測精度向上に直結する特徴量
        2. 計算が軽量で実装可能
        3. 他の特徴量と補完関係にある
        4. データの欠損に対して頑健

        ### 特徴量カテゴリ
        - 相互作用特徴量（既存特徴量の組み合わせ）
        - 時系列特徴量（トレンド、変化率）
        - 統計特徴量（順位、偏差値、正規化）
        - 外部要因特徴量（天候、馬場との相関）

        各特徴量について以下を含めて提案：
        - 特徴量名
        - 計算式
        - 期待効果
        - 実装難易度

        5-10個の実用的な特徴量を提案してください。
        """
    
    def load_sample_race_data(self) -> Dict[str, Any]:
        """サンプルレースデータ読み込み"""
        try:
            race_files = list(config.race_data_dir.glob("*.json"))
            if race_files:
                with open(race_files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data[0] if data else {}
            return {}
        except:
            return {}