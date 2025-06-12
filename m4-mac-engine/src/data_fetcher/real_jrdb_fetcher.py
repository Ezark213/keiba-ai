# 本物のJRDBデータフェッチャー - デモモード完全排除版
import asyncio
import ftplib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import lhafile
import io
import struct

from config import config


class RealJRDBFetcher:
    """本物のJRDBデータ専用フェッチャー（デモモード排除）"""
    
    def __init__(self):
        """初期化 - 認証情報必須チェック"""
        self.username = config.jrdb_username
        self.password = config.jrdb_password
        
        # 認証情報の厳格チェック
        if not self.username or not self.password:
            raise ValueError(
                "\n" + "="*60 + "\n"
                "❌ JRDBクレデンシャルが設定されていません！\n"
                "本物のデータを使用するには必須です。\n\n"
                "設定方法:\n"
                "1. cd m4-mac-engine\n"
                "2. source venv/bin/activate\n"
                "3. python -m src.utils.secure_config\n"
                "4. ユーザー名とパスワードを入力\n"
                "="*60
            )
        
        # JRDBのFTPサーバー設定（.comドメイン）
        self.ftp_host = config.jrdb_ftp_host  # ftp.jrdb.com
        self.data_dir = config.data_dir / "jrdb_real"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ 本物のJRDBデータフェッチャー初期化完了: {self.username[:3]}***")
    
    async def fetch_latest_races(self) -> List[Dict[str, Any]]:
        """最新の本物のレースデータ取得"""
        logger.info("🏇 本物のJRDBデータ取得開始...")
        
        try:
            # FTP接続
            ftp = await self._connect_ftp()
            
            # 最新のSED（成績）ファイルを取得
            today = datetime.now()
            races = []
            
            # 過去7日分のデータを取得
            for days_ago in range(7):
                target_date = today - timedelta(days=days_ago)
                date_str = target_date.strftime("%y%m%d")
                
                # JRDBデータは.lzh形式
                # SEDファイル（成績データ）
                sed_file = f"SED{date_str}.lzh"
                if await self._download_file(ftp, sed_file, sed_file):
                    race_data = await self._parse_sed_file(sed_file)
                    races.extend(race_data)
                
                # KYIファイル（競走馬データ）
                kyi_file = f"KYI{date_str}.lzh"
                if await self._download_file(ftp, kyi_file, kyi_file):
                    horse_data = await self._parse_kyi_file(kyi_file)
                    # レースデータとマージ
                    races = self._merge_horse_data(races, horse_data)
            
            ftp.quit()
            logger.success(f"✅ 本物のデータ取得完了: {len(races)}レース")
            return races
            
        except Exception as e:
            logger.error(f"❌ JRDB接続エラー: {e}")
            raise RuntimeError(
                f"JRDBからのデータ取得に失敗しました: {e}\n"
                "認証情報を確認してください。"
            )
    
    async def _connect_ftp(self) -> ftplib.FTP:
        """FTP接続"""
        try:
            logger.info(f"🔄 FTP接続試行: {self.ftp_host}")
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_host, 21, timeout=30)
            ftp.login(self.username, self.password)
            logger.success(f"✅ JRDB FTP接続成功")
            
            # ディレクトリ一覧を取得
            logger.info("📁 利用可能なディレクトリ:")
            dirs = []
            ftp.retrlines('LIST', dirs.append)
            for d in dirs[:10]:  # 最初の10件を表示
                logger.info(f"  {d}")
                
            return ftp
        except Exception as e:
            logger.error(f"❌ FTP接続失敗: {e}")
            raise ConnectionError(
                f"JRDB FTPサーバーへの接続に失敗しました: {e}\n"
                f"サーバー: {self.ftp_host}\n"
                f"ユーザー: {self.username}"
            )
    
    async def _download_file(self, ftp: ftplib.FTP, remote_file: str, local_name: str) -> bool:
        """ファイルダウンロード"""
        try:
            local_path = self.data_dir / local_name
            # JRDBはJRDB/ディレクトリにデータを格納
            remote_path = f"JRDB/{remote_file}"
            
            logger.debug(f"🔽 ダウンロード中: {remote_path}")
            with open(local_path, 'wb') as f:
                ftp.retrbinary(f'RETR {remote_path}', f.write)
            logger.debug(f"📥 ダウンロード完了: {local_name} ({local_path.stat().st_size} bytes)")
            return True
        except Exception as e:
            logger.debug(f"ダウンロードエラー: {remote_file} - {e}")
            return False
    
    async def _parse_sed_file(self, filename: str) -> List[Dict[str, Any]]:
        """SEDファイル（成績データ）のパース"""
        file_path = self.data_dir / filename
        races = []
        
        try:
            # lzhファイルを解凍
            with lhafile.Lhafile(str(file_path)) as lha:
                for info in lha.infoiter():
                    name = info.filename
                    if name.upper().endswith('.SED'):
                        # ファイル内容を読み込み
                        content = lha.read(name).decode('cp932', errors='ignore')
                        # 実際のSEDフォーマットに基づいてパース
                        races.extend(self._parse_sed_content(content))
        except Exception as e:
            logger.error(f"SEDファイルパースエラー: {e}")
        
        return races
    
    def _parse_sed_content(self, content: str) -> List[Dict[str, Any]]:
        """SEDコンテンツの詳細パース"""
        races = []
        lines = content.strip().split('\n')
        
        for line in lines:
            if len(line) < 200:  # 最小長チェック
                continue
            
            try:
                # JRDBのSEDフォーマットに基づく実装
                race_data = {
                    'race_id': line[0:8].strip(),
                    'date': self._parse_date(line[8:16]),
                    'place': self._get_place_name(line[16:18]),
                    'race_num': int(line[18:20]),
                    'distance': int(line[20:24]),
                    'track': line[24:26].strip(),
                    'track_condition': line[26:28].strip(),
                    'horses': self._parse_horses_from_sed(line[28:])
                }
                races.append(race_data)
            except Exception as e:
                logger.debug(f"行パースエラー: {e}")
                continue
        
        return races
    
    def _parse_horses_from_sed(self, horse_section: str) -> List[Dict[str, Any]]:
        """馬データのパース"""
        horses = []
        # 各馬のデータは固定長
        horse_length = 60
        num_horses = len(horse_section) // horse_length
        
        for i in range(num_horses):
            start = i * horse_length
            end = start + horse_length
            horse_data = horse_section[start:end]
            
            try:
                horse = {
                    'horse_num': int(horse_data[0:2]),
                    'horse_name': horse_data[2:18].strip(),
                    'sex': horse_data[18:20].strip(),
                    'age': int(horse_data[20:22]),
                    'weight': float(horse_data[22:25]),
                    'jockey_name': horse_data[25:37].strip(),
                    'trainer_name': horse_data[37:49].strip(),
                    'odds': float(horse_data[49:55]) / 10,  # オッズは10倍して格納
                    'popularity': int(horse_data[55:57]),
                    'idm': float(horse_data[57:60])  # IDM指数
                }
                horses.append(horse)
            except:
                continue
        
        return horses
    
    async def _parse_kyi_file(self, filename: str) -> Dict[str, Any]:
        """KYIファイル（競走馬データ）のパース"""
        file_path = self.data_dir / filename
        horse_data = {}
        
        try:
            # lzhファイルを解凍
            with lhafile.Lhafile(str(file_path)) as lha:
                for info in lha.infoiter():
                    name = info.filename
                    if name.upper().endswith('.KYI'):
                        # ファイル内容を読み込み
                        content = lha.read(name).decode('cp932', errors='ignore')
                        horse_data.update(self._parse_kyi_content(content))
        except Exception as e:
            logger.error(f"KYIファイルパースエラー: {e}")
        
        return horse_data
    
    def _parse_kyi_content(self, content: str) -> Dict[str, Any]:
        """KYIコンテンツの詳細パース"""
        horse_data = {}
        lines = content.strip().split('\n')
        
        for line in lines:
            if len(line) < 300:  # KYIは長いフォーマット
                continue
            
            try:
                race_id = line[0:8].strip()
                horse_num = int(line[8:10])
                
                # 各種指数
                data = {
                    'idm': float(line[50:53]),
                    'jockey_index': float(line[53:56]),
                    'info_index': float(line[56:59]),
                    'trainer_index': float(line[59:62]),
                    'pace_index': float(line[62:65]),
                    'rising_index': float(line[65:68]),
                    'position_index': float(line[68:71]),
                    'distance_aptitude': float(line[71:74]) / 100,
                    'track_aptitude': float(line[74:77]) / 100,
                    'heavy_track_aptitude': float(line[77:80]) / 100,
                    'days_since_last_race': int(line[80:83]),
                    'career_wins': int(line[83:86]),
                    'career_races': int(line[86:89]),
                    'prize_money': float(line[89:95]) * 10000  # 万円単位
                }
                
                key = f"{race_id}_{horse_num}"
                horse_data[key] = data
                
            except Exception as e:
                logger.debug(f"KYI行パースエラー: {e}")
                continue
        
        return horse_data
    
    def _merge_horse_data(self, races: List[Dict[str, Any]], 
                         horse_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """レースデータと馬データのマージ"""
        for race in races:
            for horse in race['horses']:
                key = f"{race['race_id']}_{horse['horse_num']}"
                if key in horse_data:
                    horse.update(horse_data[key])
        
        return races
    
    def _parse_date(self, date_str: str) -> str:
        """日付パース"""
        try:
            year = 2000 + int(date_str[0:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            return f"{year}-{month:02d}-{day:02d}"
        except:
            return datetime.now().strftime("%Y-%m-%d")
    
    def _get_place_name(self, code: str) -> str:
        """場所コードから場所名取得"""
        place_map = {
            '01': '札幌', '02': '函館', '03': '福島', '04': '新潟',
            '05': '東京', '06': '中山', '07': '中京', '08': '京都',
            '09': '阪神', '10': '小倉'
        }
        return place_map.get(code, '東京')
    
    async def fetch_historical_data(self, days: int = 365) -> List[Dict[str, Any]]:
        """過去の本物のデータ取得（学習用）"""
        logger.info(f"📚 過去{days}日分の本物のデータ取得開始...")
        
        all_races = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            ftp = await self._connect_ftp()
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%y%m%d")
                
                # SEDファイル取得（.lzh形式）
                sed_file = f"SED{date_str}.lzh"
                if await self._download_file(ftp, sed_file, sed_file):
                    race_data = await self._parse_sed_file(sed_file)
                    
                    # KYIファイル取得（.lzh形式）
                    kyi_file = f"KYI{date_str}.lzh"
                    if await self._download_file(ftp, kyi_file, kyi_file):
                        horse_data = await self._parse_kyi_file(kyi_file)
                        race_data = self._merge_horse_data(race_data, horse_data)
                    
                    all_races.extend(race_data)
                
                current_date += timedelta(days=1)
                
                # 進捗表示
                if len(all_races) % 100 == 0:
                    logger.info(f"📊 取得済み: {len(all_races)}レース")
            
            ftp.quit()
            logger.success(f"✅ 過去データ取得完了: {len(all_races)}レース")
            return all_races
            
        except Exception as e:
            logger.error(f"❌ 過去データ取得エラー: {e}")
            raise


# 使用例
async def test_real_data():
    """本物のデータ取得テスト"""
    fetcher = RealJRDBFetcher()
    races = await fetcher.fetch_latest_races()
    
    if races:
        logger.info(f"✅ テスト成功: {len(races)}レース取得")
        logger.info(f"サンプルレース: {races[0]['race_id']} - {races[0]['place']}")
        logger.info(f"馬数: {len(races[0]['horses'])}")
        logger.info(f"サンプル馬: {races[0]['horses'][0]}")
    else:
        logger.error("❌ データ取得失敗")

if __name__ == "__main__":
    asyncio.run(test_real_data())