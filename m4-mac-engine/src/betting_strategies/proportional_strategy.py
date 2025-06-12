# プロポーショナルベッティング戦略
from typing import Dict, Any
from ..interfaces.simulator_interface import BettingStrategy


class ProportionalStrategy(BettingStrategy):
    """確率に比例したベッティング戦略"""
    
    def __init__(self, base_percentage: float = 0.02, confidence_threshold: float = 0.6,
                 max_bet_percentage: float = 0.05):
        """
        Args:
            base_percentage: 基本ベット率（資金の何割）
            confidence_threshold: 高信頼度の閾値
            max_bet_percentage: 最大ベット率
        """
        self.base_percentage = base_percentage
        self.confidence_threshold = confidence_threshold
        self.max_bet_percentage = max_bet_percentage
    
    def calculate_bet_size(self, win_probability: float, odds: float, 
                          bankroll: float) -> float:
        """確率に比例してベットサイズを計算"""
        if not self.should_bet(win_probability, odds):
            return 0.0
        
        # 確率に基づいてベット率を調整
        if win_probability >= self.confidence_threshold:
            # 高信頼度の場合はベット率を上げる
            bet_percentage = self.base_percentage * (win_probability / self.confidence_threshold)
        else:
            # 通常はベース率
            bet_percentage = self.base_percentage * win_probability
        
        # 最大ベット率制限
        bet_percentage = min(bet_percentage, self.max_bet_percentage)
        
        return bankroll * bet_percentage
    
    def should_bet(self, win_probability: float, odds: float) -> bool:
        """ベットすべきかどうかを判定"""
        # 期待値がプラスの場合のみベット
        expected_value = (win_probability * odds) - 1
        return expected_value > 0
    
    @property
    def strategy_name(self) -> str:
        return "Proportional"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            'base_percentage': self.base_percentage,
            'confidence_threshold': self.confidence_threshold,
            'max_bet_percentage': self.max_bet_percentage
        }
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """パラメータを更新"""
        if 'base_percentage' in new_params:
            self.base_percentage = new_params['base_percentage']
        if 'confidence_threshold' in new_params:
            self.confidence_threshold = new_params['confidence_threshold']
        if 'max_bet_percentage' in new_params:
            self.max_bet_percentage = new_params['max_bet_percentage']