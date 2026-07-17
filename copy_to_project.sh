#!/bin/bash

# RRG 项目迁移脚本
# 将 RRG 可视化复制到其他项目

set -e

# 检查参数
if [ $# -eq 0 ]; then
    echo "使用方法: $0 <目标目录>"
    echo ""
    echo "示例:"
    echo "  $0 /path/to/your/project"
    echo "  $0 ~/myproject/rrg"
    exit 1
fi

TARGET_DIR="$1"

echo "======================================"
echo "  RRG 项目迁移工具"
echo "======================================"
echo ""
echo "目标目录: $TARGET_DIR"
echo ""

# 1. 检查 dist 目录
if [ ! -d "dist" ]; then
    echo "❌ 错误: dist 目录不存在"
    echo "请先运行: npm run build"
    exit 1
fi

# 2. 创建目标目录
echo "📁 创建目标目录..."
mkdir -p "$TARGET_DIR"

# 3. 复制静态文件
echo "📦 复制静态文件..."
cp -r dist "$TARGET_DIR/"

# 4. 复制启动脚本
echo "🚀 复制启动脚本..."
cp serve.py "$TARGET_DIR/"

# 5. 复制数据更新脚本（可选）
if [ -d "scripts" ]; then
    echo "📝 复制数据更新脚本..."
    mkdir -p "$TARGET_DIR/scripts"
    cp scripts/update_rrg.py "$TARGET_DIR/scripts/"
    cp scripts/rrg_math.py "$TARGET_DIR/scripts/"
    
    # 创建 requirements.txt
    cat > "$TARGET_DIR/scripts/requirements.txt" << 'EOF'
yfinance
pandas
akshare
EOF
fi

# 6. 复制文档
echo "📄 复制文档..."
cp DEPLOY.md "$TARGET_DIR/README.md"

# 7. 创建启动脚本
echo "🔧 创建快速启动脚本..."

# Linux/Mac 启动脚本
cat > "$TARGET_DIR/start.sh" << 'EOF'
#!/bin/bash
echo "🚀 启动 RRG 可视化服务器..."
cd "$(dirname "$0")"
python3 serve.py 8000
EOF
chmod +x "$TARGET_DIR/start.sh"

# Windows 启动脚本
cat > "$TARGET_DIR/start.bat" << 'EOF'
@echo off
echo 启动 RRG 可视化服务器...
cd /d "%~dp0"
python serve.py 8000
pause
EOF

# 8. 创建数据更新脚本
cat > "$TARGET_DIR/update_data.sh" << 'EOF'
#!/bin/bash
echo "🔄 更新 RRG 数据..."
cd "$(dirname "$0")/scripts"
python3 update_rrg.py
cp public/*.json ../dist/
echo "✅ 数据更新完成"
EOF
chmod +x "$TARGET_DIR/update_data.sh"

echo ""
echo "======================================"
echo "✅ 迁移完成！"
echo "======================================"
echo ""
echo "📁 已复制到: $TARGET_DIR"
echo ""
echo "目录结构:"
echo "  $TARGET_DIR/"
echo "  ├── dist/              # 静态文件"
echo "  ├── serve.py           # Python 服务器"
echo "  ├── start.sh           # 启动脚本 (Linux/Mac)"
echo "  ├── start.bat          # 启动脚本 (Windows)"
echo "  ├── scripts/           # 数据更新脚本（可选）"
echo "  └── README.md          # 使用文档"
echo ""
echo "使用方法:"
echo "  cd $TARGET_DIR"
echo "  ./start.sh            # 或: python3 serve.py"
echo ""
echo "访问地址: http://localhost:8000"
echo "======================================"
