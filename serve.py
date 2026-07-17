#!/usr/bin/env python3
"""
简单的 HTTP 服务器，用于提供 RRG 可视化静态文件
无需 Node.js/npm，只需要 Python 3

使用方法:
    python serve.py [端口号]
    
示例:
    python serve.py          # 默认端口 8000
    python serve.py 8080     # 使用端口 8080
"""

import http.server
import socketserver
import sys
import os
from pathlib import Path

# 默认端口
DEFAULT_PORT = 8000

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "dist"
PUBLIC_DIR = Path(__file__).parent / "public"


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义处理器，支持 SPA 路由"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)
    
    def end_headers(self):
        # 添加 CORS 头，允许跨域
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # 清理路径，移除查询参数
        path = self.path.split('?')[0]

        # 如果请求 JSON 文件，从 public 目录读取
        if path.endswith('.json'):
            json_file = PUBLIC_DIR / path.lstrip('/')
            if json_file.exists():
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                with open(json_file, 'rb') as f:
                    self.wfile.write(f.read())
                return

        # 其他静态文件从 dist 目录读取
        file_path = STATIC_DIR / path.lstrip('/')

        # 如果文件存在，直接返回
        if file_path.exists() and file_path.is_file():
            return super().do_GET()

        # 对于根路径或不存在的路径，返回 index.html (SPA 支持)
        if path == '/' or not file_path.exists():
            self.path = '/index.html'

        return super().do_GET()


def main():
    # 获取端口号
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"错误: 无效的端口号 '{sys.argv[1]}'")
            sys.exit(1)
    
    # 检查静态文件目录
    if not STATIC_DIR.exists():
        print(f"错误: 静态文件目录不存在: {STATIC_DIR}")
        print("请先运行 'npm run build' 构建项目")
        sys.exit(1)
    
    # 启动服务器
    Handler = MyHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print("=" * 60)
            print(f"🚀 RRG 可视化服务器已启动")
            print(f"📍 访问地址: http://localhost:{port}")
            print(f"📁 静态文件目录: {STATIC_DIR}")
            print("=" * 60)
            print("按 Ctrl+C 停止服务器")
            print()
            
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        sys.exit(0)
    
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"错误: 端口 {port} 已被占用")
            print(f"请尝试其他端口，例如: python serve.py {port + 1}")
        else:
            print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
