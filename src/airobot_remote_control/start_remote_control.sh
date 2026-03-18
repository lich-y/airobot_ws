#!/bin/bash

# 机器人遥控器启动脚本
# 用法: ./start_remote_control.sh [选项]
# 选项:
#   -b, --build    只构建包，不启动
#   -r, --run      构建并启动服务
#   -h, --help     显示帮助信息

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 包名
PACKAGE_NAME="airobot_remote_control"

# 打印彩色信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助
show_help() {
    echo "机器人遥控器启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -b, --build    只构建包，不启动"
    echo "  -r, --run      构建并启动服务 (默认)"
    echo "  -h, --help     显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 构建并启动服务"
    echo "  $0 --build      # 仅构建包"
}

# 获取工作空间根目录
get_workspace_dir() {
    echo "/data/code/airobot_ws"
}

# 构建包
build_package() {
    print_info "正在构建包: $PACKAGE_NAME"
    
    WORKSPACE_DIR="/data/code/airobot_ws"
    cd "$WORKSPACE_DIR"
    print_info "工作目录: $WORKSPACE_DIR"
    
    # 使用 colcon 构建
    if colcon build --packages-select "$PACKAGE_NAME"; then
        print_success "包构建成功"
        return 0
    else
        print_error "包构建失败"
        return 1
    fi
}

# 启动服务
start_service() {
    print_info "正在启动机器人遥控器服务..."
    
    WORKSPACE_DIR="/data/code/airobot_ws"
    print_info "工作目录: $WORKSPACE_DIR"
    
    # 加载 ROS2 环境
    source /opt/ros/humble/setup.bash 2>/dev/null || source /opt/ros/foxy/setup.bash 2>/dev/null || true
    source "$WORKSPACE_DIR/install/setup.bash" 2>/dev/null || true
    
    # 设置 PYTHONPATH
    export PYTHONPATH="$WORKSPACE_DIR/install/airobot_remote_control/lib/python3.10/site-packages:$PYTHONPATH"
    
    # 直接运行HTTP服务器
    "$WORKSPACE_DIR/install/airobot_remote_control/bin/remote_control_http"
}

# 主程序
main() {
    case "${1:-}" in
        -b|--build)
            build_package
            ;;
        -r|--run)
            build_package && start_service
            ;;
        -h|--help)
            show_help
            ;;
        "")
            # 默认：构建并启动
            build_package && start_service
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
