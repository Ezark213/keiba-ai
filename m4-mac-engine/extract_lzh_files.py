#!/usr/bin/env python3
"""
LZHファイル展開ツール
"""
import lhafile
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_all_lzh():
    """全LZHファイル展開"""
    data_dir = Path("data/jrdb_real")
    lzh_files = list(data_dir.glob("*.lzh"))
    
    logger.info(f"📦 LZHファイル展開開始: {len(lzh_files)}個")
    
    extracted = 0
    for lzh_file in lzh_files:
        try:
            with lhafile.Lhafile(str(lzh_file)) as archive:
                for info in archive.infolist():
                    with open(data_dir / info.filename, 'wb') as f:
                        f.write(archive.read(info.filename))
                    logger.info(f"✅ 展開: {info.filename}")
                    extracted += 1
        except Exception as e:
            logger.error(f"❌ 展開エラー: {lzh_file.name} - {e}")
    
    logger.info(f"📊 展開完了: {extracted}ファイル")
    return extracted

if __name__ == "__main__":
    extract_all_lzh()