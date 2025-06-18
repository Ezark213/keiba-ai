# シミュレーター・ベッティング戦略インターフェース
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd


class BettingStrategy(ABC):
    """ベッティング戦略の抽象インターフェース (Open/Closed Principle)"""
    
    @abstractmethod
    def calculate_bet_size(self, win_probability: float, odds: float, 
                          bankroll: float) -> float:
        """ベットサイズを計算"""
        pass
    
    @abstractmethod
    def should_bet(self, win_probability: float, odds: float) -> bool:
        """ベットすべきかどうかを判定"""
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """戦略名を返す"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """戦略のパラメータを返す"""
        pass
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """パラメータを更新（オプション）"""
        pass


class PerformanceAnalyzer(ABC):
    """パフォーマンス分析の抽象インターフェース (Single Responsibility)"""
    
    @abstractmethod
    def calculate_return_rate(self, bets: List[Dict], results: List[Dict]) -> float:
        """還元率を計算"""
        pass
    
    @abstractmethod
    def calculate_hit_rate(self, predictions: List[bool], actuals: List[bool]) -> float:
        """的中率を計算"""
        pass
    
    @abstractmethod
    def calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """シャープレシオを計算"""
        pass
    
    @abstractmethod
    def generate_performance_report(self, simulation_results: Dict) -> Dict[str, Any]:
        """パフォーマンスレポートを生成"""
        pass
    
    @abstractmethod
    def analyze_drawdown(self, balance_history: List[float]) -> Dict[str, float]:
        """ドローダウン分析"""
        pass


class SimulatorInterface(ABC):
    """シミュレーターの抽象インターフェース (Single Responsibility + Interface Segregation)"""
    
    @abstractmethod
    def run_backtest(self, historical_data: pd.DataFrame, 
                    model, betting_strategy: BettingStrategy,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Dict[str, Any]:
        """バックテストを実行"""
        pass
    
    @abstractmethod
    def simulate_single_race(self, race_data: Dict, model, 
                           betting_strategy: BettingStrategy) -> Dict[str, Any]:
        """単一レースのシミュレーション"""
        pass
    
    @abstractmethod
    def get_simulation_summary(self) -> Dict[str, Any]:
        """シミュレーション結果の要約を取得"""
        pass
    
    @property
    @abstractmethod
    def last_simulation_results(self) -> Optional[Dict[str, Any]]:
        """最後のシミュレーション結果"""
        pass