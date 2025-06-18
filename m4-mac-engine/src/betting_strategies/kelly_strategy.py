# ケリー基準ベッティング戦略
from typing import Dict, Any
from ..interfaces.simulator_interface import BettingStrategy


class KellyStrategy(BettingStrategy):
    """ケリー基準によるベッティング戦略 (Open/Closed Principle)"""
    
    def __init__(self, kelly_fraction: float = 0.25, min_edge: float = 0.05, 
                 max_bet_size: float = 0.1):
        """
        Args:
            kelly_fraction: ケリー比率の調整係数（リスク調整）
            min_edge: 最小期待値（これ以下では賭けない）
            max_bet_size: 最大ベットサイズ（資金の何割まで）
        """
        self.kelly_fraction = kelly_fraction
        self.min_edge = min_edge
        self.max_bet_size = max_bet_size
    
    def calculate_bet_size(self, win_probability: float, odds: float, 
                          bankroll: float) -> float:
        """ケリー基準でベットサイズを計算"""
        # 期待値計算
        expected_value = (win_probability * odds) - 1
        
        # 最小期待値チェック
        if expected_value < self.min_edge:
            return 0.0
        
        # ケリー比率計算
        kelly_ratio = expected_value / (odds - 1)
        
        # リスク調整
        adjusted_ratio = kelly_ratio * self.kelly_fraction
        
        # 最大ベットサイズ制限
        bet_ratio = min(adjusted_ratio, self.max_bet_size)
        
        # 負の値の場合は0
        bet_ratio = max(0, bet_ratio)
        
        return bankroll * bet_ratio
    
    def should_bet(self, win_probability: float, odds: float) -> bool:
        """ベットすべきかどうかを判定"""
        expected_value = (win_probability * odds) - 1
        return expected_value >= self.min_edge
    
    @property
    def strategy_name(self) -> str:
        return "Kelly Criterion"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            'kelly_fraction': self.kelly_fraction,
            'min_edge': self.min_edge,
            'max_bet_size': self.max_bet_size
        }
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """パラメータを更新"""
        if 'kelly_fraction' in new_params:
            self.kelly_fraction = new_params['kelly_fraction']
        if 'min_edge' in new_params:
            self.min_edge = new_params['min_edge']
        if 'max_bet_size' in new_params:
            self.max_bet_size = new_params['max_bet_size']