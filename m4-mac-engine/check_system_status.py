#!/usr/bin/env python3
"""
システム状態チェック
"""
import json
from pathlib import Path
from datetime import datetime

def check_status():
    """システム状態をチェック"""
    print("\n" + "="*70)
    print("🏇 競馬予測システム v3.0 - ステータスチェック")
    print("="*70)
    
    # シミュレーション結果
    sim_file = Path("simulation_results.json")
    if sim_file.exists():
        with open(sim_file) as f:
            sim_data = json.load(f)
        
        print("\n📊 最新シミュレーション結果:")
        print(f"  還元率: {sim_data['return_rate']:.1%}")
        print(f"  的中率: {sim_data['hit_rate']:.1%}")
        print(f"  総ベット数: {sim_data['total_bets']}")
        print(f"  収支: {sim_data['profit']:,.0f}円")
        print(f"  更新時刻: {sim_data['simulation_date']}")
        
        if sim_data['return_rate'] >= 0.8:
            print("  ✅ 目標達成！")
        else:
            print(f"  ⚠️ 目標まであと: {(0.8 - sim_data['return_rate'])*100:.1f}%")
    
    # Claude状態
    claude_file = Path("claude_state.json")
    if claude_file.exists():
        with open(claude_file) as f:
            claude_data = json.load(f)
        
        print("\n🤖 Claude統合状態:")
        print(f"  サイクル数: {claude_data['cycle_count']}")
        print(f"  アクティブ特徴量: {len(claude_data['active_features'])}個")
        print(f"  現在の戦略: {claude_data.get('current_strategy', 'baseline')}")
    
    # データディレクトリ
    data_dir = Path("data/jrdb_real")
    if data_dir.exists():
        files = list(data_dir.glob("*"))
        txt_files = [f for f in files if f.suffix.lower() in ['.txt', '.sed', '.kyi']]
        lzh_files = [f for f in files if f.suffix.lower() == '.lzh']
        
        print("\n📁 データディレクトリ状態:")
        print(f"  パス: {data_dir}")
        print(f"  総ファイル数: {len(files)}")
        print(f"  テキストファイル: {len(txt_files)}")
        print(f"  LZHファイル: {len(lzh_files)}")
        
        if txt_files:
            print("  ✅ 実データあり")
        else:
            print("  ⚠️ 実データなし（サンプルデータ使用中）")
    
    print("\n" + "="*70)
    print("\n次のステップ:")
    if not txt_files:
        print("1. JRDBから実データをダウンロード")
        print("   python show_jrdb_instructions.py")
        print("2. データを配置後、システム起動")
        print("   make start-claude")
    else:
        print("1. システムを起動")
        print("   make start-claude")
        print("2. Claudeが自動的に改善を進めます")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    check_status()