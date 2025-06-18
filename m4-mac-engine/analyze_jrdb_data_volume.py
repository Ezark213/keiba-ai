#!/usr/bin/env python3
"""
JRDBデータ量分析
機械学習に適切なデータ量かを評価
"""
from pathlib import Path
import pandas as pd

def analyze_jrdb_data_volume():
    """JRDBデータ量を分析"""
    
    data_dir = Path("data/jrdb_real")
    
    print("="*70)
    print("📊 JRDBデータ量分析 - 機械学習適性評価")
    print("="*70)
    
    # ファイル別データ量
    total_records = 0
    total_size_mb = 0
    
    file_analysis = {
        'SED': {'files': 0, 'records': 0, 'size_mb': 0, 'description': '成績データ（レース結果）'},
        'KYI': {'files': 0, 'records': 0, 'size_mb': 0, 'description': '競走馬データ'},
        'BAC': {'files': 0, 'records': 0, 'size_mb': 0, 'description': '番組データ（レース情報）'}
    }
    
    for txt_file in data_dir.glob("*.txt"):
        file_type = txt_file.name[:3].upper()
        
        if file_type in file_analysis:
            # ファイルサイズ
            size_mb = txt_file.stat().st_size / (1024 * 1024)
            
            # 行数（レコード数）
            with open(txt_file, 'r', encoding='shift_jis', errors='ignore') as f:
                records = sum(1 for line in f if line.strip())
            
            file_analysis[file_type]['files'] += 1
            file_analysis[file_type]['records'] += records
            file_analysis[file_type]['size_mb'] += size_mb
            
            total_records += records
            total_size_mb += size_mb
            
            print(f"📁 {txt_file.name}: {records:,}レコード ({size_mb:.1f}MB)")
    
    print("\n" + "="*70)
    print("📈 データタイプ別サマリー")
    print("="*70)
    
    for file_type, data in file_analysis.items():
        if data['files'] > 0:
            print(f"{file_type} ({data['description']}):")
            print(f"  ファイル数: {data['files']}個")
            print(f"  レコード数: {data['records']:,}件")
            print(f"  総サイズ: {data['size_mb']:.1f}MB")
            print(f"  平均レコード/ファイル: {data['records']//data['files']:,}件")
            print()
    
    print("="*70)
    print("🎯 機械学習適性評価")
    print("="*70)
    
    # 機械学習に必要なデータ量の評価
    print(f"📊 現在のデータ量:")
    print(f"  総レコード数: {total_records:,}件")
    print(f"  総データサイズ: {total_size_mb:.1f}MB")
    
    # SEDデータ（レース結果）が最重要
    sed_records = file_analysis['SED']['records']
    
    print(f"\n🏇 競馬予測用データ評価:")
    print(f"  レース結果データ: {sed_records:,}件")
    
    # 機械学習適性判定
    print(f"\n✅ 機械学習適性判定:")
    
    if sed_records >= 10000:
        rating = "優秀"
        color = "🟢"
    elif sed_records >= 5000:
        rating = "良好"
        color = "🟡"
    elif sed_records >= 1000:
        rating = "最低限"
        color = "🟠"
    else:
        rating = "不足"
        color = "🔴"
    
    print(f"  {color} 評価: {rating}")
    
    if sed_records >= 1000:
        print(f"  ✅ 機械学習に適用可能")
        print(f"  ✅ 予測モデル構築可能")
        
        if sed_records >= 5000:
            print(f"  ✅ 高精度予測が期待できる")
        
        if sed_records >= 10000:
            print(f"  ✅ 十分なデータ量で安定した予測が可能")
    else:
        print(f"  ❌ データ量不足 - 追加データ取得が必要")
    
    # 推奨されるデータ量
    print(f"\n📚 推奨データ量（競馬予測）:")
    print(f"  最低限: 1,000レース以上")
    print(f"  推奨: 5,000レース以上")
    print(f"  理想: 10,000レース以上")
    
    # 年間データ量の推定
    daily_races = sed_records / file_analysis['SED']['files'] if file_analysis['SED']['files'] > 0 else 0
    yearly_estimate = daily_races * 365
    
    print(f"\n🗓️ 年間データ量推定:")
    print(f"  1日平均: {daily_races:.0f}レース")
    print(f"  年間推定: {yearly_estimate:,.0f}レース")
    
    # データ拡張の提案
    if sed_records < 5000:
        print(f"\n💡 データ拡張提案:")
        print(f"  1. 過去データを追加取得（過去1-2年分）")
        print(f"  2. 地方競馬データも含める")
        print(f"  3. より多くのJRDBファイルタイプを活用")
    
    print("\n" + "="*70)
    
    return {
        'total_records': total_records,
        'sed_records': sed_records,
        'rating': rating,
        'is_sufficient': sed_records >= 1000
    }

if __name__ == "__main__":
    result = analyze_jrdb_data_volume()
    
    if result['is_sufficient']:
        print("🎉 データ量は機械学習に適用可能です！")
    else:
        print("⚠️ 追加データが必要です。")