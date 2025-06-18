"""
レースシミュレーター
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from loguru import logger

from config import config
from ..data_fetcher.real_jrdb_fetcher import RealJRDBFetcher

class RaceSimulator:
    """バックテストシミュレーター"""
    
    def __init__(self):
        self.data_fetcher = RealJRDBFetcher()  # 本物のデータフェッチャーのみ
        self.results = []
        
    async def run_backtest(self, model: Any, days: int = 30) -> Dict[str, Any]:
        """バックテスト実行"""
        logger.info(f"{days}日間のバックテスト開始...")
        
        # 本物の過去データ取得
        historical_data = await self.data_fetcher.fetch_historical_data(days)
        
        if not historical_data:
            raise ValueError(
                "バックテスト用の本物のデータがありません。"
                "JRDB認証情報を確認してください。"
            )
        
        # 日別にシミュレーション
        daily_results = []
        total_bet = 0
        total_return = 0
        total_races = 0
        winning_bets = 0
        
        # レースごとに予測と結果評価
        for race in historical_data:
            if not race.get('result'):
                continue
                
            # 予測実行
            predictions = await self._predict_race(model, race)
            
            if not predictions:
                continue
            
            # ベッティング決定
            bets = self._decide_bets(predictions)
            
            if not bets:
                continue
            
            # 結果評価
            race_result = self._evaluate_bets(bets, race['result'], race['horses'])
            
            total_bet += race_result['bet_amount']
            total_return += race_result['return_amount']
            total_races += 1
            
            if race_result['is_win']:
                winning_bets += len([b for b in bets if b['horse_num'] == race['result']['winner']])
            
            daily_results.append(race_result)
        
        # 統計計算
        return_rate = total_return / total_bet if total_bet > 0 else 0
        hit_rate = winning_bets / len(daily_results) if daily_results else 0
        
        # 詳細分析
        analysis = self._analyze_results(daily_results)
        
        results = {
            'return_rate': return_rate,
            'hit_rate': hit_rate,
            'total_bets': len(daily_results),
            'total_races': total_races,
            'profit': total_return - total_bet,
            'roi': (total_return - total_bet) / total_bet if total_bet > 0 else 0,
            'max_drawdown': analysis['max_drawdown'],
            'sharpe_ratio': analysis['sharpe_ratio'],
            'winning_streak': analysis['winning_streak'],
            'daily_results': daily_results
        }
        
        logger.info(f"バックテスト完了 - 還元率: {return_rate:.1%}, 的中率: {hit_rate:.1%}")
        
        return results
    
    async def _predict_race(self, model: Any, race: Dict[str, Any]) -> List[Dict[str, Any]]:
        """レース予測"""
        try:
            # 特徴量準備（簡易版）
            predictions = []
            
            for horse in race['horses']:
                # 基本特徴量
                features = {col: horse.get(col, 0) for col in config.feature_columns}
                
                # 予測実行（デモ用の簡易計算）
                if hasattr(model, 'predict'):
                    # 実際のモデル予測
                    feature_values = [features.get(col, 0) for col in config.feature_columns]
                    win_prob = float(model.predict([feature_values])[0])
                else:
                    # モデルがない場合はエラー
                    raise ValueError("予測モデルが利用できません")
                
                predictions.append({
                    'horse_num': horse['horse_num'],
                    'win_prob': win_prob,
                    'odds': horse.get('odds', 10.0),
                    'expected_value': win_prob * horse.get('odds', 10.0)
                })
            
            return sorted(predictions, key=lambda x: x['expected_value'], reverse=True)
            
        except Exception as e:
            logger.error(f"予測エラー: {e}")
            return []
    
    def _decide_bets(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ベッティング決定"""
        bets = []
        
        for pred in predictions[:5]:  # 上位5頭まで検討
            # 期待値チェック
            if pred['expected_value'] < config.min_expected_value:
                continue
            
            # ケリー基準計算
            kelly_bet = self._calculate_kelly_bet(
                pred['win_prob'], 
                pred['odds']
            )
            
            if kelly_bet > 0:
                bets.append({
                    'horse_num': pred['horse_num'],
                    'bet_fraction': kelly_bet,
                    'win_prob': pred['win_prob'],
                    'odds': pred['odds'],
                    'expected_value': pred['expected_value']
                })
        
        # 最大3点まで
        return bets[:3]
    
    def _calculate_kelly_bet(self, win_prob: float, odds: float) -> float:
        """ケリー基準計算"""
        edge = win_prob * odds - 1
        
        if edge <= 0:
            return 0
        
        q = 1 - win_prob
        b = odds - 1
        full_kelly = (win_prob * b - q) / b
        
        # 保守的なケリー
        conservative_kelly = full_kelly * config.kelly_fraction
        
        # 最大制限
        return min(conservative_kelly, config.max_bet_fraction)
    
    def _evaluate_bets(self, bets: List[Dict[str, Any]], result: Dict[str, Any], 
                      horses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ベット結果評価"""
        total_bet = sum(b['bet_fraction'] for b in bets) * 10000  # 1万円基準
        total_return = 0
        
        winner = result['winner']
        
        for bet in bets:
            if bet['horse_num'] == winner:
                # 勝利時のリターン
                return_amount = bet['bet_fraction'] * 10000 * bet['odds']
                total_return += return_amount
        
        return {
            'bet_amount': total_bet,
            'return_amount': total_return,
            'profit': total_return - total_bet,
            'is_win': total_return > 0,
            'bets': bets,
            'winner': winner
        }
    
    def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """結果分析"""
        if not results:
            return {
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'winning_streak': 0
            }
        
        # 累積収益計算
        cumulative_profit = []
        running_profit = 0
        
        for r in results:
            running_profit += r['profit']
            cumulative_profit.append(running_profit)
        
        # 最大ドローダウン
        peak = 0
        max_drawdown = 0
        
        for profit in cumulative_profit:
            if profit > peak:
                peak = profit
            drawdown = peak - profit
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # シャープレシオ（簡易版）
        returns = [r['profit'] / r['bet_amount'] if r['bet_amount'] > 0 else 0 
                  for r in results]
        
        if returns:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 連勝数
        winning_streak = 0
        current_streak = 0
        
        for r in results:
            if r['is_win']:
                current_streak += 1
                winning_streak = max(winning_streak, current_streak)
            else:
                current_streak = 0
        
        return {
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'winning_streak': winning_streak
        }
    
    # デモ結果生成メソッドを削除 - 本物のデータのみ使用