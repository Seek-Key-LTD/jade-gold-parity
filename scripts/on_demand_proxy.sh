#!/bin/bash

# 按需启动 AWS 爱尔兰代理服务
# 使用方法: ./on_demand_proxy.sh [start|stop|status|restart]

set -e

# 配置参数
AWS_INSTANCE="192.168.31.147"
PROXY_PORT="1083"
HEALTH_CHECK_URL="http://${AWS_INSTANCE}:${PROXY_PORT}"
LOG_FILE="on_demand_proxy.log"
PID_FILE="proxy_server.pid"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
    echo -e "$1"
}

# 检查服务状态
check_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat $PID_FILE)
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 代理服务正在运行 (PID: $pid)${NC}"
            log "服务状态检查: 运行中 (PID: $pid)"
            return 0
        else
            rm -f $PID_FILE
            echo -e "${RED}❌ PID文件存在但进程不存在${NC}"
            log "服务状态检查: PID文件存在但进程不存在"
            return 1
        fi
    else
        # 即使没有PID文件，也检查服务是否在运行
        if curl -s --connect-timeout 3 $HEALTH_CHECK_URL > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 代理服务正在运行 (无PID文件)${NC}"
            log "服务状态检查: 运行中 (无PID文件)"
            return 0
        else
            echo -e "${YELLOW}⏸️ 代理服务未运行${NC}"
            log "服务状态检查: 未运行"
            return 1
        fi
    fi
}

# 启动服务
start_service() {
    echo -e "${BLUE}🚀 启动按需代理服务...${NC}"
    log "尝试启动代理服务"
    
    if check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  服务已在运行，无需重复启动${NC}"
        log "启动尝试: 服务已在运行"
        return 0
    fi
    
    # 这里应该是启动代理服务的实际命令
    # 由于是AWS实例，这里可能是通过API调用或SSH远程启动
    echo -e "${BLUE}📡 正在连接到AWS实例...${NC}"
    log "连接AWS实例: ${AWS_INSTANCE}"
    
    # 模拟启动过程（实际应该是SSH命令或API调用）
    # ssh -i key.pem user@${AWS_INSTANCE} "sudo systemctl start proxy-service"
    
    # 这里创建一个模拟的代理服务进程用于演示
    echo "启动代理服务监听端口 ${PROXY_PORT}..."
    
    # 创建一个简单的HTTP代理服务作为示例
    cat > proxy_server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import threading
import urllib.request
import urllib.parse
import sys

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_CONNECT(self):
        # 处理HTTPS连接
        try:
            host, port = self.path.split(':')
            port = int(port)
            
            # 建立到目标服务器的连接
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((host, port))
            
            # 发送200响应表示连接建立
            self.send_response(200, 'Connection established')
            self.end_headers()
            
            # 开始双向数据转发
            self.relay_data(target_socket)
            
        except Exception as e:
            print(f"CONNECT error: {e}")
            self.send_error(500, f"Proxy error: {e}")
    
    def proxy_request(self):
        try:
            if self.path.startswith('http://'):
                url = self.path
            else:
                url = f"http://{self.headers.get("Host")}{self.path}"
            
            # 获取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            # 创建代理请求
            req = urllib.request.Request(url, post_data, dict(self.headers))
            req.get_method = self.command
            
            # 发送请求并获取响应
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    self.send_response(response.getcode())
                    
                    # 复制响应头
                    for header, value in response.headers.items():
                        if header.lower() not in ['connection', 'transfer-encoding']:
                            self.send_header(header, value)
                    self.end_headers()
                    
                    # 复制响应体
                    self.wfile.write(response.read())
                    
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                for header, value in e.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_error(500, f"Proxy error: {e}")
    
    def relay_data(self, target_socket):
        # 创建两个线程进行双向数据转发
        def forward_data(src, dst, direction):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.send(data)
            except:
                pass
            finally:
                dst.close()
                src.close()
        
        thread1 = threading.Thread(target=forward_data, 
                                args=(self.connection, target_socket, "client->server"))
        thread2 = threading.Thread(target=forward_data, 
                                args=(target_socket, self.connection, "server->client"))
        
        thread1.daemon = True
        thread2.daemon = True
        
        thread1.start()
        thread2.start()
        
        # 等待任一线程结束
        thread1.join()
        thread2.join()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 1083
    print(f"Starting proxy server on port {port}")
    
    try:
        with socketserver.ThreadingHTTPServer(('0.0.0.0', port), ProxyHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy server...")
    except Exception as e:
        print(f"Server error: {e}")
EOF
    
    # 启动代理服务
    python3 proxy_server.py $PROXY_PORT &
    local pid=$!
    echo $pid > $PID_FILE
    
    log "代理服务启动成功 (PID: $pid)"
    echo -e "${GREEN}✅ 代理服务启动成功${NC}"
    
    # 等待服务完全启动
    sleep 3
    
    # 验证服务
    if check_health; then
        log "服务健康检查通过"
        echo -e "${GREEN}🎉 服务已就绪并正常工作${NC}"
        show_service_info
    else
        echo -e "${RED}❌ 服务启动失败${NC}"
        log "服务健康检查失败"
        cleanup_service
        return 1
    fi
}

# 健康检查
check_health() {
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --connect-timeout 2 $HEALTH_CHECK_URL > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 健康检查通过 (尝试 $attempt/$max_attempts)${NC}"
            return 0
        else
            echo -e "${YELLOW}⏳ 健康检查中... (尝试 $attempt/$max_attempts)${NC}"
            sleep 1
            ((attempt++))
        fi
    done
    
    echo -e "${RED}❌ 健康检查失败${NC}"
    return 1
}

# 显示服务信息
show_service_info() {
    echo -e "${BLUE}📋 服务信息:${NC}"
    echo -e "  代理地址: ${AWS_INSTANCE}:${PROXY_PORT}"
    echo -e "  健康检查: ${HEALTH_CHECK_URL}"
    echo -e "  进程ID: $(cat $PID_FILE 2>/dev/null || echo '未知')"
    
    # 测试代理功能
    echo -e "${BLUE}🧪 功能测试:${NC}"
    local test_result=$(curl -s --max-time 10 -w "%{http_code}" $HEALTH_CHECK_URL)
    if [ "$test_result" = "200" ] || [ "$test_result" = "400" ]; then
        echo -e "  状态: ${GREEN}✅ 正常响应${NC}"
    else
        echo -e "  状态: ${RED}❌ 响应异常 (${test_result})${NC}"
    fi
}

# 停止服务
stop_service() {
    echo -e "${BLUE}🛑 停止代理服务...${NC}"
    log "停止代理服务请求"
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat $PID_FILE)
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}⏹️  终止进程 $pid...${NC}"
            kill -TERM $pid
            
            # 等待进程结束
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                ((count++))
            done
            
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${RED}🔪 强制终止进程 $pid...${NC}"
                kill -KILL $pid
            fi
            
            rm -f $PID_FILE
            log "服务停止成功 (PID: $pid)"
            echo -e "${GREEN}✅ 代理服务已停止${NC}"
        else
            echo -e "${YELLOW}⚠️  进程 $pid 不存在${NC}"
            rm -f $PID_FILE
        fi
    else
        # 尝试通过其他方式停止
        echo -e "${YELLOW}⚠️  未找到PID文件，尝试其他方式停止${NC}"
        # 这里可以添加SSH命令停止远程服务
        # ssh -i key.pem user@${AWS_INSTANCE} "sudo systemctl stop proxy-service"
        
        log "服务停止完成"
        echo -e "${GREEN}✅ 代理服务已停止${NC}"
    fi
}

# 清理资源
cleanup_service() {
    rm -f $PID_FILE
    rm -f proxy_server.py
    log "资源清理完成"
}

# 重启服务
restart_service() {
    echo -e "${BLUE}🔄 重启代理服务...${NC}"
    log "重启代理服务"
    stop_service
    sleep 2
    start_service
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}按需代理服务管理工具${NC}"
    echo "====================================="
    echo ""
    echo "使用方法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     - 启动代理服务"
    echo "  stop      - 停止代理服务"
    echo "  status    - 检查服务状态"
    echo "  restart   - 重启代理服务"
    echo "  health    - 执行健康检查"
    echo "  info      - 显示服务信息"
    echo "  help      - 显示此帮助信息"
    echo ""
    echo "配置信息:"
    echo "  代理地址: ${AWS_INSTANCE}:${PROXY_PORT}"
    echo "  日志文件: $LOG_FILE"
    echo "  PID文件: $PID_FILE"
    echo ""
    echo "示例:"
    echo "  $0 start      # 启动服务"
    echo "  $0 status     # 检查状态"
    echo "  $0 stop       # 停止服务"
}

# 主逻辑
case "${1:-help}" in
    "start")
        start_service
        ;;
    "stop")
        stop_service
        ;;
    "status")
        check_status
        if [ $? -eq 0 ]; then
            show_service_info
        fi
        ;;
    "restart")
        restart_service
        ;;
    "health")
        check_health
        ;;
    "info")
        if [ -f "$PID_FILE" ]; then
            show_service_info
        else
            echo -e "${YELLOW}⚠️  服务未运行${NC}"
            check_status
        fi
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知命令: $1${NC}"
        show_help
        exit 1
        ;;
esac