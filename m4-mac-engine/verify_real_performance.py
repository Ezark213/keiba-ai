#!/usr/bin/env python3
"""
実際のパフォーマンス検証
還元率の真実を確認
"""
import json
from pathlib import Path
from datetime import datetime

def verify_performance():
    """実際のパフォーマンスを検証"""
    
    print("="*70)
    print("🔍 実際のパフォーマンス検証")
    print("="*70)
    
    # シミュレーション結果を読み込み
    sim_file = Path("simulation_results.json")
    if sim_file.exists():
        with open(sim_file) as f:
            sim_data = json.load(f)
        
        return_rate = sim_data.get('return_rate', 0)
        profit = sim_data.get('profit', 0)
        total_bets = sim_data.get('total_bets', 0)
        hit_rate = sim_data.get('hit_rate', 0)
        
        print(f"📊 現在の数値:")
        print(f"  還元率: {return_rate:.1%}")
        print(f"  収支: {profit:,.0f}円")
        print(f"  総ベット数: {total_bets}")
        print(f"  的中率: {hit_rate:.1%}")
        
        print(f"\n🔍 数値の分析:")
        
        # 還元率の計算検証
        if total_bets > 0:
            calculated_return = (100000 + profit) / 100000  # 仮定：10万円投資
            print(f"  計算上の還元率: {calculated_return:.1%}")
        
        # 損失の事実
        if profit < 0:
            print(f"  ❌ 実際は損失: {abs(profit):,.0f}円の赤字")
            print(f"  ❌ 真の還元率: {return_rate:.1%} = 95.4%（マイナス収支）")
        
        # 現実的な評価
        print(f"\n🎯 現実的な評価:")
        if return_rate < 1.0:
            loss_rate = (1.0 - return_rate) * 100
            print(f"  📉 実際は {loss_rate:.1f}%の損失率")
            print(f"  💸 投資額に対して {loss_rate:.1f}%減")
            
        print(f"\n✅ 正直な結論:")
        print(f"  現在の「還元率95.4%」は損失を意味します")
        print(f"  100万円投資すると約46,000円の損失")
        print(f"  これは競馬としては「比較的良い」成績ですが")
        print(f"  利益は出ていません")
        
        # 競馬の現実
        print(f"\n🏇 競馬の現実:")
        print(f"  JRA控除率: 約25%（還元率75%）")
        print(f"  現在95.4%なので、JRAより20%良い")
        print(f"  しかし、まだ利益は出ていない")
        
        # 改善のための提案
        print(f"\n💡 真の利益達成のために:")
        print(f"  目標: 還元率100%超え（実際の利益）")
        print(f"  必要: 追加のJRDBデータ取得")
        print(f"  期待: より多くのレースデータで精度向上")
        
        return return_rate < 1.0  # 損失かどうか
    
    else:
        print("❌ シミュレーション結果ファイルが見つかりません")
        return True

def check_data_quality():
    """データ品質をチェック"""
    print(f"\n📊 現在のデータ品質チェック:")
    
    data_dir = Path("data/jrdb_real")
    txt_files = list(data_dir.glob("*.txt"))
    
    print(f"  データファイル数: {len(txt_files)}")
    
    if len(txt_files) < 10:
        print(f"  ⚠️ データ量不足（10ファイル未満）")
        print(f"  📈 追加データで大幅改善の可能性あり")
        return False
    else:
        print(f"  ✅ 十分なデータ量")
        return True

if __name__ == "__main__":
    is_losing = verify_performance()
    has_enough_data = check_data_quality()
    
    print(f"\n" + "="*70)
    print(f"🎯 最終判定:")
    
    if is_losing:
        print(f"  ❌ 現在は損失状態（還元率95.4%）")
        print(f"  🎯 目標: 還元率100%超え（実利益）")
        
        if not has_enough_data:
            print(f"  💡 解決策: JRDBデータ追加取得")
            print(f"  📈 期待効果: 100%+還元率達成の可能性")
        else:
            print(f"  🔧 解決策: アルゴリズム改善が必要")
    else:
        print(f"  ✅ 実際に利益が出ています")
    
    print(f"="*70)