"""
Cloudflare同期ユーティリティ
"""
import asyncio
import aiohttp
import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from config import config

class CloudflareSync:
    """Cloudflare Workers/R2同期クライアント"""
    
    def __init__(self):
        self.api_url = config.cloudflare_api_url
        self.sync_token = config.cloudflare_sync_token
        
    async def upload_model(self, model_path: Path, metadata: Dict[str, Any]) -> bool:
        """モデルファイルをCloudflareに同期"""
        try:
            logger.info(f"モデル同期開始: {model_path}")
            
            if not model_path.exists():
                logger.error(f"モデルファイルが見つかりません: {model_path}")
                return False
            
            # マルチパートフォームデータ作成
            async with aiohttp.ClientSession() as session:
                with open(model_path, 'rb') as model_file:
                    data = aiohttp.FormData()
                    data.add_field(
                        'model', 
                        model_file,
                        filename=model_path.name,
                        content_type='application/octet-stream'
                    )
                    data.add_field(
                        'metadata',
                        json.dumps(metadata),
                        content_type='application/json'
                    )
                    
                    headers = {
                        'Authorization': f'Bearer {self.sync_token}'
                    }
                    
                    # アップロード実行
                    async with session.post(
                        f'{self.api_url}/api/model/sync',
                        data=data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=300)  # 5分タイムアウト
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            logger.success(f"モデル同期成功: {result.get('version')}")
                            
                            # 改善度ログ
                            improvements = result.get('improvements', {})
                            if improvements.get('previous_return_rate'):
                                prev_rate = improvements['previous_return_rate']
                                current_rate = improvements['return_rate']
                                improvement = current_rate - prev_rate
                                logger.info(f"還元率変化: {prev_rate:.1%} → {current_rate:.1%} ({improvement:+.1%})")
                            
                            return True
                        else:
                            error_text = await response.text()
                            logger.error(f"モデル同期失敗: {response.status} - {error_text}")
                            return False
                            
        except asyncio.TimeoutError:
            logger.error("モデル同期タイムアウト")
            return False
        except Exception as e:
            logger.error(f"モデル同期エラー: {e}")
            return False
    
    async def get_current_status(self) -> Optional[Dict[str, Any]]:
        """現在のシステムステータス取得"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_url}/api/status',
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"ステータス取得失敗: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"ステータス取得エラー: {e}")
            return None
    
    async def update_performance_stats(self, stats: Dict[str, Any]) -> bool:
        """パフォーマンス統計を更新"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.sync_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(
                    f'{self.api_url}/api/performance/update',
                    json=stats,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        logger.info("パフォーマンス統計更新成功")
                        return True
                    else:
                        logger.warning(f"統計更新失敗: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"統計更新エラー: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """接続テスト"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.api_url}/health',
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        logger.info("Cloudflare接続テスト成功")
                        return True
                    else:
                        logger.warning(f"接続テスト失敗: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"接続テストエラー: {e}")
            return False
    
    async def sync_race_data(self, race_data: Dict[str, Any]) -> bool:
        """レースデータ同期"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.sync_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.post(
                    f'{self.api_url}/api/races/sync',
                    json=race_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        logger.info(f"レースデータ同期成功: {race_data.get('date')}")
                        return True
                    else:
                        logger.warning(f"レースデータ同期失敗: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"レースデータ同期エラー: {e}")
            return False
    
    async def get_model_performance_history(self, days: int = 30) -> Optional[Dict[str, Any]]:
        """モデルパフォーマンス履歴取得"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {'days': days}
                async with session.get(
                    f'{self.api_url}/api/performance/history',
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"履歴取得失敗: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"履歴取得エラー: {e}")
            return None
    
    async def cleanup_old_models(self, keep_versions: int = 10) -> bool:
        """古いモデルをクリーンアップ"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.sync_token}',
                    'Content-Type': 'application/json'
                }
                
                data = {'keep_versions': keep_versions}
                async with session.post(
                    f'{self.api_url}/api/model/cleanup',
                    json=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"モデルクリーンアップ完了: {result.get('deleted_count', 0)}件削除")
                        return True
                    else:
                        logger.warning(f"クリーンアップ失敗: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")
            return False