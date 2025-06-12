#!/usr/bin/env python3
"""
Netkeiba実データスクレイパー
実際の競馬データをnetkeibaから取得
"""
import asyncio
import aiohttp
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import re
import json
from bs4 import BeautifulSoup
import pandas as pd

from config import config


class NetkeibaRealDataScraper:
    """Netkeiba実データスクレイパー"""
    
    def __init__(self):
        self.base_url = "https://race.netkeiba.com"
        self.data_dir = config.data_dir / "netkeiba_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # レート制限（サイトに負荷をかけないため）
        self.request_delay = 1.0  # 1秒間隔
        
        logger.info("Netkeiba実データスクレイパー初期化完了")
    
    async def get_recent_race_ids(self, session: aiohttp.ClientSession, days_back: int = 3) -> List[str]:
        """最近のレースIDを取得"""
        logger.info(f"📅 過去{days_back}日間のレースID取得中...")
        
        race_ids = []
        today = datetime.now()
        
        # 過去の確実にレースがあった日程を使用（2024年12月の有馬記念など）
        known_race_dates = ["20241229", "20241228", "20241222", "20241221", "20241215", "20241208", "20241201"]
        
        for date_str in known_race_dates[:days_back]:
            
            # 中央競馬場のコード
            kaisai_codes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
            
            for kaisai_code in kaisai_codes:
                for race_num in range(1, 13):  # 1-12R
                    race_id = f"{date_str}{kaisai_code}{race_num:02d}"
                    race_ids.append(race_id)
        
        logger.info(f"✅ {len(race_ids)}レースID生成完了")
        return race_ids
    
    async def scrape_race_result(self, session: aiohttp.ClientSession, race_id: str) -> Optional[Dict[str, Any]]:
        """レース結果をスクレイピング"""
        try:
            url = f"{self.base_url}/race/result.html?race_id={race_id}"
            
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                
                html = await resp.text(encoding='euc-jp', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                # レース情報を抽出
                race_info = await self._extract_race_info(soup, race_id)
                if not race_info:
                    return None
                
                # 着順結果を抽出
                result_table = soup.find('table', class_='race_table_01')
                if not result_table:
                    return None
                
                horses = []
                rows = result_table.find_all('tr')[1:]  # ヘッダー行をスキップ
                
                for row in rows:
                    horse_data = await self._extract_horse_data(row)
                    if horse_data:
                        horses.append(horse_data)
                
                race_info['horses'] = horses
                
                # レースが実際に開催されていたかチェック
                if horses and len(horses) > 0:
                    logger.info(f"✅ 実データ取得: {race_id} ({len(horses)}頭)")
                    return race_info
                
        except Exception as e:
            logger.debug(f"レース取得失敗: {race_id} - {e}")
        
        return None
    
    async def _extract_race_info(self, soup: BeautifulSoup, race_id: str) -> Optional[Dict[str, Any]]:
        """レース基本情報を抽出"""
        try:
            # レース名
            race_title = soup.find('h1', class_='raceTitle')
            if not race_title:
                return None
            
            race_name = race_title.get_text().strip()
            
            # レース条件
            race_data = soup.find('div', class_='racedata')
            if not race_data:
                return None
            
            race_text = race_data.get_text()
            
            # 距離・コース種別を抽出
            distance_match = re.search(r'(\d+)m', race_text)
            distance = int(distance_match.group(1)) if distance_match else 1600
            
            track_type = "芝" if "芝" in race_text else "ダート" if "ダート" in race_text else "芝"
            
            # 天候・馬場状態
            weather = "晴"
            track_condition = "良"
            if "曇" in race_text:
                weather = "曇"
            elif "雨" in race_text:
                weather = "雨"
            
            if "稍重" in race_text:
                track_condition = "稍重"
            elif "重" in race_text:
                track_condition = "重"
            elif "不良" in race_text:
                track_condition = "不良"
            
            # 開催場所
            place_name = "東京"  # デフォルト
            if "中山" in race_text:
                place_name = "中山"
            elif "阪神" in race_text:
                place_name = "阪神"
            elif "京都" in race_text:
                place_name = "京都"
            elif "中京" in race_text:
                place_name = "中京"
            
            return {
                'race_id': race_id,
                'race_name': race_name,
                'distance': distance,
                'track': track_type,
                'weather': weather,
                'track_condition': track_condition,
                'place': place_name,
                'date': race_id[:8],  # YYYYMMDD
                'race_num': int(race_id[10:12]),
            }
            
        except Exception as e:
            logger.debug(f"レース情報抽出失敗: {race_id} - {e}")
            return None
    
    async def _extract_horse_data(self, row) -> Optional[Dict[str, Any]]:
        """馬データを抽出"""
        try:
            cells = row.find_all('td')
            if len(cells) < 10:
                return None
            
            # 着順
            chakuji_cell = cells[0]
            chakuji = chakuji_cell.get_text().strip()
            if not chakuji.isdigit():
                return None
            
            # 馬名
            horse_name_link = cells[3].find('a')
            horse_name = horse_name_link.get_text().strip() if horse_name_link else "不明"
            
            # 性齢
            sex_age = cells[4].get_text().strip()
            sex = sex_age[0] if sex_age else "牡"
            age = int(sex_age[1:]) if len(sex_age) > 1 and sex_age[1:].isdigit() else 4
            
            # 斤量
            weight_text = cells[5].get_text().strip()
            weight = float(weight_text) if weight_text.replace('.', '').isdigit() else 56.0
            
            # 騎手
            jockey_link = cells[6].find('a')
            jockey_name = jockey_link.get_text().strip() if jockey_link else "不明"
            
            # タイム
            time_text = cells[7].get_text().strip()
            
            # オッズ
            odds_text = cells[9].get_text().strip()
            odds = float(odds_text) if odds_text.replace('.', '').isdigit() else 10.0
            
            # 人気
            popularity_text = cells[10].get_text().strip() if len(cells) > 10 else "1"
            popularity = int(popularity_text) if popularity_text.isdigit() else 1
            
            return {
                'horse_num': len(cells),  # 暫定
                'chakuji': int(chakuji),
                'horse_name': horse_name,
                'sex': sex,
                'age': age,
                'weight': weight,
                'jockey_name': jockey_name,
                'time': time_text,
                'odds': odds,
                'popularity': popularity,
            }
            
        except Exception as e:
            logger.debug(f"馬データ抽出失敗: {e}")
            return None
    
    async def fetch_real_data(self, max_races: int = 50) -> List[Dict[str, Any]]:
        """実データを取得"""
        logger.info("🏇 Netkeibaから実データ取得開始...")
        
        connector = aiohttp.TCPConnector(limit=1)  # 同時接続数制限
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # レースID取得
            race_ids = await self.get_recent_race_ids(session, days_back=7)
            
            real_races = []
            processed = 0
            
            for race_id in race_ids[:max_races * 3]:  # 余裕を持って取得
                if processed >= max_races:
                    break
                
                # レート制限
                await asyncio.sleep(self.request_delay)
                
                race_data = await self.scrape_race_result(session, race_id)
                if race_data:
                    real_races.append(race_data)
                    processed += 1
                    
                    # 保存
                    filename = f"race_{race_id}.json"
                    file_path = self.data_dir / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(race_data, f, ensure_ascii=False, indent=2)
        
        logger.success(f"✅ 実データ取得完了: {len(real_races)}レース")
        return real_races
    
    async def fetch_latest_races(self) -> List[Dict[str, Any]]:
        """最新レースデータ取得（実データのみ）"""
        logger.info("🏇 最新実データ取得...")
        
        # 既存の実データファイルをチェック
        existing_files = list(self.data_dir.glob("race_*.json"))
        
        if existing_files:
            logger.info(f"既存の実データファイル: {len(existing_files)}個")
            
            # 最新のファイルから読み込み
            races = []
            for file_path in existing_files[-20:]:  # 最新20レース
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        race_data = json.load(f)
                        races.append(race_data)
                except Exception as e:
                    logger.debug(f"ファイル読み込み失敗: {file_path} - {e}")
            
            if races:
                logger.success(f"✅ 既存実データ読み込み: {len(races)}レース")
                return races
        
        # 新規データ取得
        return await self.fetch_real_data(max_races=20)


async def main():
    """メイン実行"""
    try:
        scraper = NetkeibaRealDataScraper()
        races = await scraper.fetch_latest_races()
        
        logger.success(f"✅ {len(races)}レースの実データを取得")
        
        if races:
            sample_race = races[0]
            logger.info(f"サンプルレース: {sample_race['race_name']}")
            logger.info(f"  距離: {sample_race['distance']}m")
            logger.info(f"  出走数: {len(sample_race.get('horses', []))}頭")
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")


if __name__ == "__main__":
    asyncio.run(main())