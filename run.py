#!/usr/bin/env python3
"""
Nursing Research & Teaching Intelligent Agent
护理科研教学智能体启动脚本
"""

import os
import sys
import subprocess

def main():
    print("🧠 Nursing Research & Teaching Intelligent Agent")
    print("护理科研教学智能体")
    print("=" * 50)
    
    # 检查 Python 版本
    if sys.version_info < (3, 10):
        print("❌ 错误：需要 Python 3.10 或更高版本")
        print(f"当前版本：{sys.version}")
        return
    
    print(f"✅ Python 版本：{sys.version.split()[0]}")
    
    # 检查依赖是否已安装
    try:
        import fastapi
        import requests
        import neo4j
        print("✅ 依赖包已安装")
    except ImportError:
        print("📦 正在安装依赖包...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ 依赖包安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败，请手动运行：pip install -r requirements.txt")
            return
    
    # 启动服务
    print("\n🚀 启动服务...")
    print("📍 访问地址：http://localhost:8000")
    print("⏹️  按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动应用
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")

if __name__ == "__main__":
    main()
