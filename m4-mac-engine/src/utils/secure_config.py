"""
セキュアな設定管理
機密情報の安全な取得・保存
"""
import os
import keyring
import getpass
import json
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from cryptography.fernet import Fernet
import base64

class SecureConfigManager:
    """セキュアな設定管理クラス"""
    
    def __init__(self, service_name: str = "keiba-prediction-system"):
        self.service_name = service_name
        self.config_dir = Path.home() / ".config" / "keiba-prediction"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.encrypted_config_path = self.config_dir / "secure_config.enc"
        
    def set_jrdb_credentials(self, username: str, password: str):
        """JRDBクレデンシャルをキーチェーンに安全に保存"""
        try:
            # macOSキーチェーン / Windows資格情報マネージャーに保存
            keyring.set_password(self.service_name, "jrdb_username", username)
            keyring.set_password(self.service_name, "jrdb_password", password)
            logger.info("✅ JRDBクレデンシャルを安全に保存しました")
            return True
        except Exception as e:
            logger.error(f"クレデンシャル保存エラー: {e}")
            return False
    
    def get_jrdb_credentials(self) -> Optional[Dict[str, str]]:
        """JRDBクレデンシャルをキーチェーンから取得"""
        try:
            username = keyring.get_password(self.service_name, "jrdb_username")
            password = keyring.get_password(self.service_name, "jrdb_password")
            
            if username and password:
                return {"username": username, "password": password}
            else:
                logger.warning("キーチェーンにJRDBクレデンシャルが見つかりません")
                return None
        except Exception as e:
            logger.error(f"クレデンシャル取得エラー: {e}")
            return None
    
    def setup_jrdb_credentials_interactive(self):
        """対話式でJRDBクレデンシャルを設定"""
        print("🔐 JRDBクレデンシャルをセキュアに設定します")
        print("（入力した情報はシステムキーチェーンに暗号化保存されます）")
        
        username = input("JRDBユーザー名: ").strip()
        if not username:
            print("❌ ユーザー名が入力されていません")
            return False
        
        password = getpass.getpass("JRDBパスワード: ").strip()
        if not password:
            print("❌ パスワードが入力されていません")
            return False
        
        # 確認
        print(f"ユーザー名: {username}")
        confirm = input("この情報でキーチェーンに保存しますか？ (y/N): ").strip().lower()
        
        if confirm == 'y':
            success = self.set_jrdb_credentials(username, password)
            if success:
                print("✅ JRDBクレデンシャルを安全に保存しました")
                return True
            else:
                print("❌ 保存に失敗しました")
                return False
        else:
            print("❌ 保存をキャンセルしました")
            return False
    
    def generate_encryption_key(self) -> bytes:
        """暗号化キーを生成"""
        key_path = self.config_dir / ".encryption_key"
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            # 新しいキー生成
            key = Fernet.generate_key()
            
            # キーを安全に保存（600パーミッション）
            with open(key_path, 'wb') as f:
                f.write(key)
            os.chmod(key_path, 0o600)
            
            logger.info("新しい暗号化キーを生成しました")
            return key
    
    def encrypt_config(self, config_data: Dict[str, Any]) -> bool:
        """設定データを暗号化して保存"""
        try:
            key = self.generate_encryption_key()
            fernet = Fernet(key)
            
            # JSON → バイト → 暗号化
            json_data = json.dumps(config_data).encode()
            encrypted_data = fernet.encrypt(json_data)
            
            # 暗号化データを保存
            with open(self.encrypted_config_path, 'wb') as f:
                f.write(encrypted_data)
            
            # ファイルパーミッション設定（所有者のみ読み書き）
            os.chmod(self.encrypted_config_path, 0o600)
            
            logger.info("設定データを暗号化して保存しました")
            return True
            
        except Exception as e:
            logger.error(f"暗号化エラー: {e}")
            return False
    
    def decrypt_config(self) -> Optional[Dict[str, Any]]:
        """暗号化された設定データを復号化"""
        try:
            if not self.encrypted_config_path.exists():
                return None
            
            key = self.generate_encryption_key()
            fernet = Fernet(key)
            
            # 暗号化データを読み込み
            with open(self.encrypted_config_path, 'rb') as f:
                encrypted_data = f.read()
            
            # 復号化 → JSON
            decrypted_data = fernet.decrypt(encrypted_data)
            config_data = json.loads(decrypted_data.decode())
            
            return config_data
            
        except Exception as e:
            logger.error(f"復号化エラー: {e}")
            return None
    
    def set_api_credentials(self, claude_api_key: str, cf_sync_token: str):
        """APIクレデンシャルを安全に保存"""
        try:
            keyring.set_password(self.service_name, "claude_api_key", claude_api_key)
            keyring.set_password(self.service_name, "cf_sync_token", cf_sync_token)
            logger.info("✅ APIクレデンシャルを安全に保存しました")
            return True
        except Exception as e:
            logger.error(f"API認証情報保存エラー: {e}")
            return False
    
    def get_api_credentials(self) -> Optional[Dict[str, str]]:
        """APIクレデンシャルを取得"""
        try:
            claude_key = keyring.get_password(self.service_name, "claude_api_key")
            cf_token = keyring.get_password(self.service_name, "cf_sync_token")
            
            if claude_key and cf_token:
                return {
                    "claude_api_key": claude_key,
                    "cf_sync_token": cf_token
                }
            else:
                return None
        except Exception as e:
            logger.error(f"API認証情報取得エラー: {e}")
            return None
    
    def setup_all_credentials_interactive(self):
        """全ての認証情報を対話式で設定"""
        print("🔐 競馬予測システム - セキュア設定")
        print("="*50)
        
        # Claude API Key
        claude_key = getpass.getpass("Claude API Key: ").strip()
        if not claude_key:
            print("❌ Claude API Keyが必要です")
            return False
        
        # Cloudflare Sync Token
        cf_token = getpass.getpass("Cloudflare Sync Token: ").strip()
        if not cf_token:
            print("❌ Cloudflare Sync Tokenが必要です")
            return False
        
        # JRDB認証情報
        print("\nJRDB認証情報:")
        jrdb_user = input("JRDB Username: ").strip()
        jrdb_pass = getpass.getpass("JRDB Password: ").strip()
        
        # 確認・保存
        print("\n設定内容:")
        print(f"Claude API Key: {claude_key[:10]}...")
        print(f"CF Sync Token: {cf_token[:10]}...")
        print(f"JRDB Username: {jrdb_user}")
        
        confirm = input("\nこの情報をキーチェーンに保存しますか？ (y/N): ").strip().lower()
        
        if confirm == 'y':
            # API認証情報保存
            api_success = self.set_api_credentials(claude_key, cf_token)
            
            # JRDB認証情報保存
            jrdb_success = True
            if jrdb_user and jrdb_pass:
                jrdb_success = self.set_jrdb_credentials(jrdb_user, jrdb_pass)
            
            if api_success and jrdb_success:
                print("✅ 全ての認証情報を安全に保存しました")
                return True
            else:
                print("❌ 一部の保存に失敗しました")
                return False
        else:
            print("❌ 保存をキャンセルしました")
            return False
    
    def clean_credentials(self):
        """保存された認証情報をクリア"""
        try:
            keyring.delete_password(self.service_name, "claude_api_key")
            keyring.delete_password(self.service_name, "cf_sync_token")
            keyring.delete_password(self.service_name, "jrdb_username")
            keyring.delete_password(self.service_name, "jrdb_password")
            
            if self.encrypted_config_path.exists():
                self.encrypted_config_path.unlink()
            
            logger.info("✅ 保存された認証情報をクリアしました")
            return True
        except Exception as e:
            logger.error(f"認証情報クリアエラー: {e}")
            return False

def setup_secure_credentials():
    """セキュア認証情報設定のメイン関数"""
    manager = SecureConfigManager()
    return manager.setup_all_credentials_interactive()

if __name__ == "__main__":
    # 認証情報設定スクリプトとして実行
    setup_secure_credentials()