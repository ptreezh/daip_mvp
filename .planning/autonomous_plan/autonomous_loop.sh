#!/bin/bash
# DAIP-LIVE 自主执行循环
# 长时自动运行，无需人工干预

set -e  # 遇到错误退出

# 配置
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
PLAN_DIR="$PROJECT_ROOT/.planning/autonomous_plan"
STATE_FILE="$PLAN_DIR/STATE.md"
LOG_DIR="$PROJECT_ROOT/data/logs"
LOOP_LOG="$LOG_DIR/autonomous_loop.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOOP_LOG"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOOP_LOG"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOOP_LOG"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOOP_LOG"
}

# 创建日志目录
mkdir -p "$LOG_DIR"

log "=== DAIP-LIVE 自主执行循环启动 ==="

# 检查环境
check_environment() {
    log "检查环境..."

    # 检查是否在 git 仓库中
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "不在 git 仓库中"
        exit 1
    fi

    # 检查工作目录是否干净
    if ! git diff-index --quiet HEAD --; then
        log_warning "工作目录有未提交的变更"
        git status --short
    fi

    # 检查计划目录
    if [ ! -d "$PLAN_DIR" ]; then
        log_error "计划目录不存在: $PLAN_DIR"
        exit 1
    fi

    log_success "环境检查通过"
}

# 读取当前状态
read_current_phase() {
    if [ -f "$STATE_FILE" ]; then
        grep "当前状态" "$STATE_FILE" | head -1 || echo "unknown"
    else
        echo "unknown"
    fi
}

# 更新状态
update_state() {
    local phase="$1"
    local status="$2"
    local message="$3"

    log "更新状态: Phase $phase - $status - $message"

    # 更新 STATE.md
    if [ -f "$STATE_FILE" ]; then
        # 使用临时文件更新
        local temp_file="$STATE_FILE.tmp"
        cp "$STATE_FILE" "$temp_file"

        # 更新时间戳
        sed -i "s/\*\*最后更新\*\*: .*/\*\*最后更新\*\*: $(date +'%Y-%m-%d %H:%M:%S')/" "$temp_file"

        mv "$temp_file" "$STATE_FILE"
    fi
}

# 执行 Phase 0
execute_phase_0() {
    log "开始执行 Phase 0: 地基稳定"

    # 创建 worktree
    log "创建 phase-0 worktree..."
    if [ ! -d "../daip-live-phase-0" ]; then
        git worktree add ../daip-live-phase-0 -b phase-0
        log_success "Worktree 创建成功"
    else
        log_warning "Worktree 已存在，继续执行"
    fi

    cd ../daip-live-phase-0

    # 安装依赖
    log "安装依赖..."
    poetry install --no-interaction

    # 验证基线
    log "验证基线..."
    poetry run pytest --collect-only | tee -a "$LOOP_LOG"

    # P0-1: SQLAlchemy 兼容性
    log "执行 P0-1: SQLAlchemy 2.0 兼容性修复..."
    # 这里将由 AI Agent 执行具体任务

    # ... 更多任务

    cd "$PROJECT_ROOT"
}

# 执行 Phase 1
execute_phase_1() {
    log "开始执行 Phase 1: 辩论真实"
    # ...
}

# 主循环
main_loop() {
    log "进入主循环..."

    while true; do
        log "检查执行状态..."

        # 读取当前 Phase
        local current_phase=$(read_current_phase)
        log "当前 Phase: $current_phase"

        # 根据 Phase 执行任务
        case "$current_phase" in
            *"Phase 0"*|*"phase-0"*)
                execute_phase_0
                ;;
            *"Phase 1"*|*"phase-1"*)
                execute_phase_1
                ;;
            *"完成"*|*"completed"*)
                log_success "所有 Phase 已完成"
                break
                ;;
            *)
                log_warning "未知状态: $current_phase，启动 Phase 0"
                execute_phase_0
                ;;
        esac

        # 等待下一次循环 (30 分钟)
        log "等待 30 分钟后继续..."
        sleep 1800
    done
}

# 主函数
main() {
    log "启动 DAIP-LIVE 自主执行系统"

    check_environment
    main_loop

    log_success "自主执行完成"
}

# 执行
main "$@"
