"""
JRDBデータフェッチャー
"""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
from loguru import logger

from config import config

class JRDBFetcher:
    """JRDBデータ取得クラス"""
    
    def __init__(self):
        self.ftp_host = config.jrdb_ftp_host
        self.username = config.jrdb_username
        self.password = config.jrdb_password
        
    async def fetch_latest(self) -> Dict[str, Any]:
        """最新データ取得"""
        if not self.username or not self.password:
            logger.warning("JRDB認証情報なし - デモモードで実行")
            return await self.generate_demo_data()
        
        try:
            # FTP接続してデータ取得（実装省略）
            logger.info("JRDBから最新データを取得中...")
            # 実際の実装では、ftplibやaioftpを使用してFTP接続
            
            # デモ実装
            return await self.generate_demo_data()
            
        except Exception as e:
            logger.error(f"JRDB取得エラー: {e}")
            return await self.generate_demo_data()
    
    async def generate_demo_data(self) -> Dict[str, Any]:
        """デモデータ生成"""
        today = datetime.now()
        races = []
        
        # 各競馬場のレースデータ生成
        places = ['東京', '中山', '阪神', '京都', '新潟', '福島']
        
        for place in places[:4]:  # 4場開催と仮定
            for race_num in range(1, 13):  # 12レース
                race_id = f"{today.strftime('%Y%m%d')}{self._get_place_code(place)}{race_num:02d}"
                
                # レース情報
                race_info = {
                    'race_id': race_id,
                    'date': today.strftime('%Y-%m-%d'),
                    'place': place,
                    'race_num': race_num,
                    'race_name': self._generate_race_name(race_num),
                    'distance': self._generate_distance(race_num),
                    'track': np.random.choice(['芝', 'ダート']),
                    'weather': np.random.choice(['晴', '曇', '雨']),
                    'track_condition': np.random.choice(['良', '稍重', '重', '不良']),
                    'post_time': f"{10 + race_num // 2}:{(race_num % 2) * 30:02d}",
                    'horses': []
                }
                
                # 出走馬データ生成
                num_horses = np.random.randint(10, 19)
                for horse_num in range(1, num_horses + 1):
                    horse_data = self._generate_horse_data(horse_num)
                    race_info['horses'].append(horse_data)
                
                races.append(race_info)
        
        # データ保存
        await self._save_race_data(races)
        
        return {
            'races': races,
            'date': today.strftime('%Y-%m-%d'),
            'total_races': len(races)
        }
    
    def _get_place_code(self, place: str) -> str:
        """競馬場コード取得"""
        place_codes = {
            '東京': '05', '中山': '06', '阪神': '09',
            '京都': '08', '新潟': '04', '福島': '03'
        }
        return place_codes.get(place, '00')
    
    def _generate_race_name(self, race_num: int) -> str:
        """レース名生成"""
        if race_num == 11:
            return np.random.choice(['〇〇ステークス', '〇〇記念', '〇〇カップ'])
        elif race_num >= 9:
            return np.random.choice(['〇〇特別', '〇〇賞'])
        else:
            return f"{race_num}R"
    
    def _generate_distance(self, race_num: int) -> int:
        """距離生成"""
        distances = [1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2500, 3000]
        return np.random.choice(distances)
    
    def _generate_horse_data(self, horse_num: int) -> Dict[str, Any]:
        """馬データ生成"""
        # 基本情報
        horse_name = f"テストホース{horse_num:02d}"
        
        # 各種指数（JRDB風）
        idm = np.random.normal(60, 10)  # IDM指数
        idm = max(30, min(90, idm))
        
        # その他の指数も正規分布で生成
        indices = {
            'idm': round(idm, 1),
            'jockey_index': round(np.random.normal(55, 8), 1),
            'trainer_index': round(np.random.normal(55, 8), 1),
            'info_index': round(np.random.normal(55, 8), 1),
            'pace_index': round(np.random.normal(50, 10), 1),
            'rising_index': round(np.random.normal(50, 10), 1),
            'position_index': round(np.random.normal(50, 10), 1)
        }
        
        # 適性
        aptitudes = {
            'distance_aptitude': round(np.random.uniform(0.8, 1.2), 2),
            'track_aptitude': round(np.random.uniform(0.8, 1.2), 2),
            'heavy_track_aptitude': round(np.random.uniform(0.7, 1.3), 2)
        }
        
        # 馬の属性
        attributes = {
            'age': np.random.choice([2, 3, 4, 5, 6]),
            'sex': np.random.choice(['牡', '牝', 'セ']),
            'weight': np.random.randint(440, 520),
            'weight_change': np.random.choice([-4, -2, 0, 2, 4]),
            'days_since_last_race': np.random.choice([14, 21, 28, 35, 42, 56]),
            'career_wins': np.random.randint(0, 10),
            'career_races': np.random.randint(1, 30),
            'prize_money': np.random.randint(0, 50000) * 1000
        }
        
        # オッズ（IDMに基づいて調整）
        base_odds = 100 / (idm + np.random.normal(0, 5))
        odds = round(max(1.5, min(99.9, base_odds)), 1)
        
        return {
            'horse_num': horse_num,
            'horse_name': horse_name,
            'odds': odds,
            **indices,
            **aptitudes,
            **attributes
        }
    
    async def _save_race_data(self, races: List[Dict[str, Any]]):
        """レースデータ保存"""
        today = datetime.now().strftime('%Y%m%d')
        file_path = config.race_data_dir / f"{today}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(races, f, ensure_ascii=False, indent=2)
        
        logger.info(f"レースデータ保存: {file_path}")
    
    async def fetch_historical_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """過去データ取得"""
        historical_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            file_path = config.race_data_dir / f"{date.strftime('%Y%m%d')}.json"
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    historical_data.extend(data)
            else:
                # ファイルがない場合はデモデータ生成
                demo_data = await self._generate_historical_demo_data(date)
                historical_data.extend(demo_data)
        
        return historical_data
    
    async def _generate_historical_demo_data(self, date: datetime) -> List[Dict[str, Any]]:
        """過去のデモデータ生成"""
        # 基本的に現在のデモデータ生成と同じロジック
        # ただし、結果データも含める
        races = []
        
        for place in ['東京', '中山']:
            for race_num in range(1, 7):  # 簡略化のため6レースのみ
                race_id = f"{date.strftime('%Y%m%d')}{self._get_place_code(place)}{race_num:02d}"
                
                race_info = {
                    'race_id': race_id,
                    'date': date.strftime('%Y-%m-%d'),
                    'place': place,
                    'race_num': race_num,
                    'horses': [],
                    'result': None  # 結果データ
                }
                
                num_horses = np.random.randint(8, 16)
                horses = []
                
                for horse_num in range(1, num_horses + 1):
                    horse_data = self._generate_horse_data(horse_num)
                    horses.append(horse_data)
                
                # 結果をシミュレート（IDMベースで順位決定）
                sorted_horses = sorted(horses, key=lambda x: x['idm'] + np.random.normal(0, 5), reverse=True)
                
                race_info['horses'] = horses
                race_info['result'] = {
                    'winner': sorted_horses[0]['horse_num'],
                    'second': sorted_horses[1]['horse_num'],
                    'third': sorted_horses[2]['horse_num']
                }
                
                races.append(race_info)
        
        return races