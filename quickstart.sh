#!/bin/bash

# 快速启动脚本 - Hugo 牧月记三部曲部署

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 Hugo 是否安装
check_hugo() {
    if ! command -v hugo &> /dev/null; then
        echo -e "${RED}❌ Hugo 未安装${NC}"
        echo -e "${YELLOW}请先安装 Hugo：${NC}"
        echo "  macOS: brew install hugo"
        echo "  Ubuntu: sudo apt-get install hugo"
        echo "  或访问: https://gohugo.io/getting-started/installing/"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Hugo 已安装: $(hugo version)${NC}"
}

# 检查 Python（用于视频链接替换脚本）
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安装${NC}"
        echo "请先安装 Python3"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python3 已安装: $(python3 --version)${NC}"
}

# 创建目录结构
setup_directories() {
    echo -e "${BLUE}📁 创建目录结构...${NC}"
    
    mkdir -p static/videos/tian
    mkdir -p static/videos/di
    mkdir -p static/videos/ren
    mkdir -p scripts
    
    echo -e "${GREEN}✅ 目录结构创建完成${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "${BLUE}📦 检查依赖...${NC}"
    
    # 检查并安装 Python 依赖
    if [ ! -f "requirements.txt" ]; then
        echo "awscli>=1.0.0" > requirements.txt
    fi
    
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ 依赖检查完成${NC}"
}

# 初始化 Git 仓库（如果需要）
init_git() {
    if [ ! -d ".git" ]; then
        echo -e "${BLUE}🔧 初始化 Git 仓库...${NC}"
        git init
        git add .
        git commit -m "初始提交：Hugo 牧月记三部曲项目"
        echo -e "${GREEN}✅ Git 仓库初始化完成${NC}"
        echo -e "${YELLOW}💡 记得在 GitHub 上创建仓库并添加远程地址：${NC}"
        echo "   git remote add origin git@github.com:your-username/your-repo.git"
        echo "   git push -u origin main"
    fi
}

# 本地预览
start_server() {
    echo -e "${BLUE}🚀 启动本地服务器...${NC}"
    echo -e "${GREEN}🌐 网站地址: http://localhost:1313${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
    hugo server -D
}

# 显示帮助信息
show_help() {
    echo "Hugo 牧月记三部曲 - 快速启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  setup      - 设置项目结构和依赖"
    echo "  server     - 启动本地开发服务器"
    echo "  build      - 构建生产版本"
    echo "  help       - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 setup   # 初始化项目"
    echo "  $0 server  # 启动开发服务器"
    echo "  $0 build   # 构建生产版本到 public/ 目录"
    echo ""
    echo "部署步骤:"
    echo "  1. 运行 $0 setup"
    echo "  2. 将视频文件放入 static/videos/ 对应目录"
    echo "  3. 运行 $0 server 预览"
    echo "  4. 配置 GitHub Secrets"
    echo "  5. 推送到 GitHub 触发自动部署"
}

# 构建生产版本
build_production() {
    echo -e "${BLUE}🏗️  构建生产版本...${NC}"
    
    if [ ! -d "public" ]; then
        mkdir public
    fi
    
    hugo --minify
    
    echo -e "${GREEN}✅ 构建完成！${NC}"
    echo -e "${BLUE}📂 构建文件位于: public/ 目录${NC}"
    echo -e "${YELLOW}💡 可以直接将 public/ 目录部署到任何静态文件服务${NC}"
}

# 主逻辑
main() {
    echo -e "${BLUE}📚 Hugo 牧月记三部曲 - 快速启动${NC}"
    echo "======================================"
    
    case "${1:-setup}" in
        "setup")
            check_hugo
            check_python
            setup_directories
            install_dependencies
            init_git
            
            echo -e "${GREEN}🎉 项目设置完成！${NC}"
            echo ""
            echo -e "${BLUE}下一步操作:${NC}"
            echo "  1. 将视频文件放入 static/videos/ 目录"
            echo "  2. 运行 '$0 server' 启动开发服务器"
            echo "  3. 配置 GitHub Secrets 并推送代码以触发自动部署"
            echo ""
            echo -e "${YELLOW}📖 详细说明请查看 DEPLOYMENT_GUIDE.md${NC}"
            ;;
        "server")
            check_hugo
            start_server
            ;;
        "build")
            check_hugo
            build_production
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"