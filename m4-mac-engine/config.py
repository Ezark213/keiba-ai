"""
システム設定
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# セキュア設定のインポート
try:
    from src.utils.secure_config import SecureConfigManager
    _secure_manager = SecureConfigManager()
except ImportError:
    _secure_manager = None

@dataclass
class SystemConfig:
    """システム設定"""
    # API設定
    cloudflare_api_url: str = os.getenv("CLOUDFLARE_API_URL", "https://api.keiba-prediction.com")
    cloudflare_sync_token: str = os.getenv("CF_SYNC_TOKEN", "")
    
    # Claude統合（Claude Code環境での直接実行）
    use_live_claude: bool = True  # Claude Code環境での実行
    claude_api_key: str = ""  # API不使用
    
    # JRDBデータ形式
    jrdb_data_format: str = "lzh"  # lha圧縮形式
    
    # JRDB設定（セキュア取得を優先）
    jrdb_username: Optional[str] = None
    jrdb_password: Optional[str] = None
    
    def __post_init__(self):
        """初期化後処理"""
        # セキュアな認証情報取得を試行
        if _secure_manager:
            jrdb_creds = _secure_manager.get_jrdb_credentials()
            if jrdb_creds:
                self.jrdb_username = jrdb_creds["username"]
                self.jrdb_password = jrdb_creds["password"]
            
            api_creds = _secure_manager.get_api_credentials()
            if api_creds:
                self.cloudflare_sync_token = api_creds.get("cf_sync_token", "")
        
        # フォールバック: 環境変数から取得
        if not self.jrdb_username:
            self.jrdb_username = os.getenv("JRDB_USERNAME")
            self.jrdb_password = os.getenv("JRDB_PASSWORD")
        
        if not self.cloudflare_sync_token:
            self.cloudflare_sync_token = os.getenv("CF_SYNC_TOKEN", "")
        
        # ディレクトリ作成
        for dir_path in [self.data_dir, self.model_dir, self.cache_dir, 
                        self.race_data_dir, self.log_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    # JRDBの正しいドメインは.com
    jrdb_ftp_host: str = "ftp.jrdb.com"
    
    # 実行設定
    cycle_interval_minutes: int = 1  # 高速サイクルで80%達成を目指す
    target_return_rate: float = 0.80
    max_concurrent_tasks: int = 10
    
    # ローカルパス
    base_dir: Path = Path(__file__).parent
    data_dir: Path = base_dir / "data"
    model_dir: Path = data_dir / "models"
    cache_dir: Path = data_dir / "cache"
    race_data_dir: Path = data_dir / "races"
    log_dir: Path = base_dir / "logs"
    
    # モデル設定
    model_params = {
        'objective': 'binary',
        'metric': 'auc',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'num_threads': 8,  # M4最適化
        'force_col_wise': True,
        'seed': 42
    }
    
    # 特徴量設定
    feature_columns = [
        'idm', 'jockey_index', 'trainer_index', 'info_index',
        'pace_index', 'rising_index', 'position_index',
        'distance_aptitude', 'track_aptitude', 'heavy_track_aptitude',
        'days_since_last_race', 'career_wins', 'career_races',
        'prize_money', 'weight_change', 'age', 'sex'
    ]
    
    # ベッティング設定
    kelly_fraction: float = 0.25  # 1/4ケリー
    max_bet_fraction: float = 0.05  # 最大5%
    min_expected_value: float = 1.2  # 最小期待値
    
    def validate(self) -> bool:
        """設定の検証 - 本物のデータのみ使用"""
        if not self.cloudflare_sync_token:
            print("⚠️  CF_SYNC_TOKEN が設定されていません")
            return False
        
        # JRDB認証情報を必須に
        if not self.jrdb_username or not self.jrdb_password:
            print("⚠️  JRDB認証情報が設定されていません")
            print("本物のデータを使用するため、JRDB_USERNAMEとJRDB_PASSWORDが必須です")
            return False
        
        return True

# グローバル設定インスタンス
config = SystemConfig()