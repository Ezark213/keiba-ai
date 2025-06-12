# 固定額ベッティング戦略
from typing import Dict, Any
from ..interfaces.simulator_interface import BettingStrategy


class FixedStakeStrategy(BettingStrategy):
    """固定額ベッティング戦略"""
    
    def __init__(self, stake_amount: float = 1000, min_odds: float = 1.5,
                 min_probability: float = 0.4):
        """
        Args:
            stake_amount: 固定ベット額
            min_odds: 最小オッズ（これ以下では賭けない）
            min_probability: 最小勝率（これ以下では賭けない）
        """
        self.stake_amount = stake_amount
        self.min_odds = min_odds
        self.min_probability = min_probability
    
    def calculate_bet_size(self, win_probability: float, odds: float, 
                          bankroll: float) -> float:
        """固定額でベットサイズを計算"""
        if not self.should_bet(win_probability, odds):
            return 0.0
        
        # 資金不足の場合は利用可能な金額
        return min(self.stake_amount, bankroll)
    
    def should_bet(self, win_probability: float, odds: float) -> bool:
        """ベットすべきかどうかを判定"""
        return (win_probability >= self.min_probability and 
                odds >= self.min_odds)
    
    @property
    def strategy_name(self) -> str:
        return "Fixed Stake"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            'stake_amount': self.stake_amount,
            'min_odds': self.min_odds,
            'min_probability': self.min_probability
        }
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """パラメータを更新"""
        if 'stake_amount' in new_params:
            self.stake_amount = new_params['stake_amount']
        if 'min_odds' in new_params:
            self.min_odds = new_params['min_odds']
        if 'min_probability' in new_params:
            self.min_probability = new_params['min_probability']