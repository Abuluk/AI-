#!/usr/bin/env python3
# generate_ssl.py
# 生成自签名SSL证书（仅用于开发环境）

import os
import subprocess
from pathlib import Path

def generate_ssl_cert():
    """生成自签名SSL证书"""
    ssl_dir = Path(__file__).parent / "ssl"
    ssl_dir.mkdir(exist_ok=True)
    
    cert_file = ssl_dir / "cert.pem"
    key_file = ssl_dir / "key.pem"
    
    if cert_file.exists() and key_file.exists():
        print("SSL证书已存在，跳过生成")
        return
    
    print("正在生成自签名SSL证书...")
    
    try:
        # 使用OpenSSL生成证书
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", str(key_file), "-out", str(cert_file),
            "-days", "365", "-nodes", "-subj",
            "/C=CN/ST=Beijing/L=Beijing/O=Dev/OU=Dev/CN=localhost"
        ]
        
        subprocess.run(cmd, check=True)
        print("SSL证书生成成功！")
        print(f"证书文件: {cert_file}")
        print(f"私钥文件: {key_file}")
        
    except subprocess.CalledProcessError:
        print("OpenSSL命令执行失败，请确保已安装OpenSSL")
        print("或者手动生成证书文件")
    except FileNotFoundError:
        print("未找到OpenSSL，请先安装OpenSSL")
        print("Windows: 下载并安装OpenSSL")
        print("macOS: brew install openssl")
        print("Ubuntu: sudo apt-get install openssl")

if __name__ == "__main__":
    generate_ssl_cert()

