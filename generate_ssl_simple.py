#!/usr/bin/env python3
# generate_ssl_simple.py
# 生成自签名SSL证书（简化版本，避免OpenSSL配置问题）

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
        # 使用更简单的OpenSSL命令，避免配置文件问题
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:2048", 
            "-keyout", str(key_file), "-out", str(cert_file),
            "-days", "365", "-nodes", "-subj",
            "/C=CN/ST=Beijing/L=Beijing/O=Dev/OU=Dev/CN=localhost",
            "-config", "NUL"  # 使用空配置文件
        ]
        
        # 在Windows上，使用环境变量跳过配置文件
        env = os.environ.copy()
        env['OPENSSL_CONF'] = 'NUL'
        
        subprocess.run(cmd, check=True, env=env)
        print("SSL证书生成成功！")
        print(f"证书文件: {cert_file}")
        print(f"私钥文件: {key_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"OpenSSL命令执行失败: {e}")
        print("尝试使用更简单的方法...")
        
        # 如果上面的方法失败，尝试使用更简单的命令
        try:
            cmd_simple = [
                "openssl", "req", "-x509", "-newkey", "rsa:2048", 
                "-keyout", str(key_file), "-out", str(cert_file),
                "-days", "365", "-nodes"
            ]
            
            # 交互式生成证书
            subprocess.run(cmd_simple, check=True, input=b"\n\n\n\n\n\n\n", env=env)
            print("SSL证书生成成功（交互式）！")
            
        except Exception as e2:
            print(f"简化方法也失败: {e2}")
            print("请手动生成SSL证书或使用HTTP模式")
            
    except FileNotFoundError:
        print("未找到OpenSSL，请先安装OpenSSL")
        print("Windows: 下载并安装OpenSSL")
        print("macOS: brew install openssl")
        print("Ubuntu: sudo apt-get install openssl")

if __name__ == "__main__":
    generate_ssl_cert()
