#!/usr/bin/env python3
"""
JRDB シンプルデータフェッチャー
最もシンプルで確実な方法でJRDBデータを取得
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import pandas as pd
import numpy as np

# jrdb_libのパスを追加
jrdb_lib_path = Path(__file__).parent.parent.parent / "jrdb_lib"
sys.path.insert(0, str(jrdb_lib_path))
from jrdb import load, parse

from config import config


class JRDBSimpleFetcher:
    """JRDBシンプルデータフェッチャー"""
    
    def __init__(self):
        """初期化"""
        self.username = config.jrdb_username
        self.password = config.jrdb_password
        
        if not self.username or not self.password:
            raise ValueError(
                "JRDBクレデンシャルが設定されていません！\n"
                "python -m src.utils.secure_config で設定してください。"
            )
        
        self.data_dir = config.data_dir / "jrdb_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # JRDBパーサー
        self.loader = load.FileLoader()
        self.parser = parse.JrdbDataParser()
        
        logger.info("✅ JRDBシンプルフェッチャー初期化完了")
    
    def fetch_sample_data(self) -> Dict[str, Any]:
        """サンプルデータを使用してシステムテスト"""
        logger.info("📊 サンプルデータでシステムテスト開始...")
        
        # サンプルレースデータ（東京11R）
        sample_races = []
        
        # サンプルレース1: 東京11R（GI）
        race1 = {
            'race_id': '20250111050011',
            'date': '2025-01-11',
            'place': '東京',
            'race_num': 11,
            'race_name': '金杯',
            'distance': 2000,
            'track': '芝',
            'weather': '晴',
            'track_condition': '良',
            'post_time': '15:40',
            'horses': []
        }
        
        # サンプル馬データ生成
        horse_names = [
            "イクイノックス", "ドウデュース", "ジャスティンパレス",
            "ダノンベルーガ", "プログノーシス", "スターズオンアース",
            "タイトルホルダー", "パンサラッサ", "ジャックドール",
            "ソダシ", "エフフォーリア", "レッドジェネシス"
        ]
        
        for i, name in enumerate(horse_names, 1):
            horse = {
                'horse_num': i,
                'horse_name': name,
                'age': np.random.choice([3, 4, 5, 6]),
                'sex': np.random.choice(['牡', '牝', 'セ']),
                'weight': np.random.randint(450, 520),
                'weight_change': np.random.choice([-4, -2, 0, 2, 4]),
                'jockey_name': f"騎手{i}",
                'trainer_name': f"調教師{i}",
                'odds': round(np.random.uniform(2.0, 50.0), 1),
                
                # JRDB指数（現実的な範囲で生成）
                'idm': round(np.random.normal(60, 10), 1),
                'jockey_index': round(np.random.normal(55, 8), 1),
                'trainer_index': round(np.random.normal(55, 8), 1),
                'info_index': round(np.random.normal(55, 8), 1),
                'pace_index': round(np.random.normal(50, 10), 1),
                'rising_index': round(np.random.normal(50, 10), 1),
                'position_index': round(np.random.normal(50, 10), 1),
                
                # 適性
                'distance_aptitude': round(np.random.uniform(0.8, 1.2), 2),
                'track_aptitude': round(np.random.uniform(0.8, 1.2), 2),
                'heavy_track_aptitude': round(np.random.uniform(0.7, 1.3), 2),
                
                # キャリア情報
                'days_since_last_race': np.random.choice([14, 21, 28, 35, 42]),
                'career_wins': np.random.randint(0, 15),
                'career_races': np.random.randint(5, 30),
                'prize_money': np.random.randint(5000, 50000) * 10000
            }
            race1['horses'].append(horse)
        
        # 人気順にオッズを調整（現実的に）
        race1['horses'] = sorted(race1['horses'], key=lambda x: x['idm'], reverse=True)
        for i, horse in enumerate(race1['horses']):
            if i < 3:  # 上位人気
                horse['odds'] = round(np.random.uniform(2.0, 5.0), 1)
            elif i < 6:  # 中位人気
                horse['odds'] = round(np.random.uniform(5.0, 15.0), 1)
            else:  # 下位人気
                horse['odds'] = round(np.random.uniform(15.0, 50.0), 1)
        
        sample_races.append(race1)
        
        # サンプルレース2: 中山10R
        race2 = {
            'race_id': '20250111060010',
            'date': '2025-01-11',
            'place': '中山',
            'race_num': 10,
            'race_name': 'ニューイヤーS',
            'distance': 1600,
            'track': 'ダート',
            'weather': '曇',
            'track_condition': '良',
            'post_time': '15:10',
            'horses': []
        }
        
        # 同様に馬データ生成（簡略化）
        for i in range(1, 11):
            horse = {
                'horse_num': i,
                'horse_name': f"テスト馬{i}",
                'age': np.random.choice([3, 4, 5]),
                'sex': np.random.choice(['牡', '牝']),
                'weight': np.random.randint(450, 500),
                'weight_change': np.random.choice([-2, 0, 2]),
                'jockey_name': f"騎手{i}",
                'trainer_name': f"調教師{i}",
                'odds': round(np.random.uniform(3.0, 30.0), 1),
                'idm': round(np.random.normal(55, 8), 1),
                'jockey_index': round(np.random.normal(50, 7), 1),
                'trainer_index': round(np.random.normal(50, 7), 1),
                'info_index': round(np.random.normal(50, 7), 1),
                'pace_index': round(np.random.normal(48, 8), 1),
                'rising_index': round(np.random.normal(48, 8), 1),
                'position_index': round(np.random.normal(48, 8), 1),
                'distance_aptitude': round(np.random.uniform(0.8, 1.1), 2),
                'track_aptitude': round(np.random.uniform(0.9, 1.2), 2),
                'heavy_track_aptitude': round(np.random.uniform(0.8, 1.2), 2),
                'days_since_last_race': np.random.choice([14, 21, 28]),
                'career_wins': np.random.randint(0, 8),
                'career_races': np.random.randint(3, 20),
                'prize_money': np.random.randint(1000, 20000) * 10000
            }
            race2['horses'].append(horse)
        
        sample_races.append(race2)
        
        logger.success(f"✅ サンプルデータ生成完了: {len(sample_races)}レース")
        
        return {
            'races': sample_races,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_races': len(sample_races),
            'is_sample': True  # サンプルデータフラグ
        }
    
    def parse_jrdb_file(self, file_path: Path, data_type: str) -> pd.DataFrame:
        """JRDBファイルをパース"""
        try:
            # ファイル読み込み
            text_data = self.loader.load(str(file_path))
            
            # データパース
            df = self.parser.parse(text_data, data_type)
            
            logger.info(f"✅ ファイルパース完了: {file_path.name}")
            return df
            
        except Exception as e:
            logger.error(f"❌ パースエラー: {e}")
            return pd.DataFrame()
    
    async def fetch_latest_races(self) -> List[Dict[str, Any]]:
        """最新のレースデータ取得（実データのみ）"""
        logger.info("🏇 実データ取得開始...")
        
        # 実データファイルをチェック
        data_files = self.check_data_files()
        
        if not any(data_files.values()):
            raise RuntimeError(
                "❌ 実データが見つかりません！\n"
                "サンプルデータは禁止されています。\n"
                "JRDBから実データをダウンロードしてください。"
            )
        
        # 実データからレース情報を解析
        races = []
        
        # SEDファイル（成績データ）から実際のレースを構築
        sed_files = data_files.get('SED', [])
        if sed_files:
            latest_sed = max(sed_files, key=lambda x: x.stat().st_mtime)
            races = await self._parse_real_sed_file(latest_sed)
        
        logger.success(f"✅ 実データから {len(races)} レースを取得")
        return races
    
    def check_data_files(self) -> Dict[str, List[Path]]:
        """データディレクトリ内のJRDBファイルをチェック"""
        logger.info(f"📁 データディレクトリチェック: {self.data_dir}")
        
        file_types = {
            'SED': [],  # 成績データ
            'KYI': [],  # 競走馬データ
            'BAC': [],  # 番組データ
            'CYB': [],  # 調教データ
            'KAB': [],  # 開催データ
        }
        
        # .txtファイルを探す
        for file_path in self.data_dir.glob("*.txt"):
            file_name = file_path.name.upper()
            for file_type in file_types:
                if file_name.startswith(file_type):
                    file_types[file_type].append(file_path)
        
        # 結果表示
        for file_type, files in file_types.items():
            if files:
                logger.info(f"  {file_type}: {len(files)}ファイル")
                for f in files[:3]:  # 最初の3つを表示
                    logger.info(f"    - {f.name}")
            else:
                logger.info(f"  {file_type}: なし")
        
        return file_types


async def test_simple_fetcher():
    """シンプルフェッチャーのテスト"""
    fetcher = JRDBSimpleFetcher()
    
    # データファイルチェック
    fetcher.check_data_files()
    
    # サンプルデータ取得
    races = await fetcher.fetch_latest_races()
    
    if races:
        logger.info(f"\n📊 取得データサマリー:")
        logger.info(f"  レース数: {len(races)}")
        logger.info(f"  最初のレース: {races[0]['place']} {races[0]['race_num']}R")
        logger.info(f"  出走頭数: {len(races[0]['horses'])}")
        logger.info(f"  1番人気: {races[0]['horses'][0]['horse_name']} ({races[0]['horses'][0]['odds']}倍)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_simple_fetcher())