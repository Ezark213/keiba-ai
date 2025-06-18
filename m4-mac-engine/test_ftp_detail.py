#!/usr/bin/env python3
"""
JRDB FTP接続詳細テスト
"""
import ftplib
import socket
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from config import config

print("\n" + "="*60)
print("🔍 JRDB FTP接続詳細テスト")
print("="*60 + "\n")

# 認証情報
username = config.jrdb_username
password = config.jrdb_password
print(f"ユーザー名: {username}")
print(f"パスワード: {'*' * len(password)}\n")

# テストするホスト
hosts = [
    "ftp.jrdb.com",
    "jrdb.com",
    "www.jrdb.com"
]

for host in hosts:
    print(f"\n{'='*40}")
    print(f"テスト対象: {host}")
    print('='*40)
    
    # 1. DNS解決
    try:
        ip = socket.gethostbyname(host)
        print(f"✓ DNS解決成功: {ip}")
    except Exception as e:
        print(f"✗ DNS解決失敗: {e}")
        continue
    
    # 2. ポートスキャン
    ports = [21, 20, 22, 80, 443]  # FTP, FTP-DATA, SSH, HTTP, HTTPS
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"✓ ポート {port} 開いています")
            
            # FTPポートが開いている場合、接続試行
            if port == 21:
                try:
                    print(f"\nFTP接続試行中...")
                    ftp = ftplib.FTP()
                    ftp.set_debuglevel(2)  # デバッグ出力ON
                    ftp.connect(host, 21, timeout=10)
                    print(f"✓ FTP接続成功")
                    
                    # ログイン試行
                    try:
                        ftp.login(username, password)
                        print(f"✓ ログイン成功！")
                        
                        # 現在のディレクトリ
                        print(f"\n現在のディレクトリ: {ftp.pwd()}")
                        
                        # ディレクトリ一覧
                        print("\nディレクトリ一覧:")
                        files = []
                        ftp.retrlines('LIST', files.append)
                        for f in files[:10]:
                            print(f"  {f}")
                            
                        ftp.quit()
                        print(f"\n🎉 成功: {host} で接続・ログイン可能です！")
                        sys.exit(0)
                        
                    except Exception as e:
                        print(f"✗ ログイン失敗: {e}")
                        
                except Exception as e:
                    print(f"✗ FTP接続失敗: {e}")
        else:
            print(f"✗ ポート {port} 閉じています")
        sock.close()

print("\n\n" + "="*60)
print("テスト完了")
print("="*60)