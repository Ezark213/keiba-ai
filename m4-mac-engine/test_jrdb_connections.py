#!/usr/bin/env python3
"""
JRDB接続テストスクリプト
様々な接続方法を試す
"""
import ftplib
import requests
import socket
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))
from config import config

print("\n" + "="*60)
print("🔍 JRDB接続テスト開始")
print("="*60 + "\n")

# 認証情報確認
print(f"ユーザー名: {config.jrdb_username[:3]}***")
print(f"パスワード: {'*' * len(config.jrdb_password)}\n")

# テスト1: 様々なFTPサーバーアドレス
print("📡 FTP接続テスト...")
ftp_hosts = [
    "jrdb.com",
    "www.jrdb.com",
    "ftp.jrdb.com",
    "data.jrdb.com",
    "jrdb.jp",
    "www.jrdb.jp",
    "ftp.jrdb.jp",
    "data.jrdb.jp"
]

for host in ftp_hosts:
    try:
        print(f"\n試行: {host}")
        # DNS解決テスト
        try:
            ip = socket.gethostbyname(host)
            print(f"  ✓ DNS解決成功: {ip}")
        except:
            print(f"  ✗ DNS解決失敗")
            continue
            
        # FTP接続テスト
        ftp = ftplib.FTP()
        ftp.connect(host, 21, timeout=10)
        print(f"  ✓ FTP接続成功")
        
        # ログイン試行
        try:
            ftp.login(config.jrdb_username, config.jrdb_password)
            print(f"  ✓ ログイン成功！")
            
            # ディレクトリ一覧
            print("  ディレクトリ一覧:")
            files = []
            ftp.retrlines('LIST', files.append)
            for f in files[:5]:  # 最初の5件
                print(f"    {f}")
                
            ftp.quit()
            print(f"\n🎉 成功: {host} で接続可能です！")
            break
            
        except Exception as e:
            print(f"  ✗ ログイン失敗: {e}")
            ftp.quit()
            
    except Exception as e:
        print(f"  ✗ 接続失敗: {str(e)[:50]}...")

# テスト2: HTTP/HTTPS接続
print("\n\n🌐 HTTP/HTTPS接続テスト...")
http_urls = [
    "http://www.jrdb.com",
    "https://www.jrdb.com",
    "http://www.jrdb.jp",
    "https://www.jrdb.jp",
    "http://jrdb.com",
    "https://jrdb.com",
    "http://jrdb.jp",
    "https://jrdb.jp"
]

for url in http_urls:
    try:
        print(f"\n試行: {url}")
        response = requests.get(url, timeout=5, allow_redirects=True)
        print(f"  ✓ 接続成功: ステータス {response.status_code}")
        print(f"  最終URL: {response.url}")
        
        # ログインフォームを探す
        if 'login' in response.text.lower() or 'password' in response.text.lower():
            print("  📝 ログインフォームが見つかりました")
            
    except Exception as e:
        print(f"  ✗ 接続失敗: {str(e)[:50]}...")

print("\n" + "="*60)
print("テスト完了")
print("="*60)