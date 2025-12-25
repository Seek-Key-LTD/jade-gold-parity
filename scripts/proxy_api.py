#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按需代理 Web API
提供 RESTful API 来管理代理服务
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from flask import Flask, jsonify, request
from threading import Thread
import time

app = Flask(__name__)

# 配置
PROXY_HOST = "192.168.31.147"
PROXY_PORT = 1083
HEALTH_CHECK_URL = f"http://{PROXY_HOST}:{PROXY_PORT}"

class ProxyManager:
    def __init__(self):
        self.status = {
            "active": False,
            "last_check": None,
            "start_time": None,
            "stop_time": None,
            "health_status": "unknown"
        }
    
    def check_health(self):
        """检查代理健康状态"""
        try:
            response = requests.get(HEALTH_CHECK_URL, timeout=5)
            self.status["health_status"] = "healthy"
            self.status["active"] = True
            return True
        except:
            self.status["health_status"] = "unhealthy"
            self.status["active"] = False
            return False
    
    def execute_command(self, action):
        """执行代理管理命令"""
        try:
            result = subprocess.run(
                ['./scripts/on_demand_proxy.sh', action],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "命令执行超时"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }

proxy_manager = ProxyManager()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查 API"""
    is_healthy = proxy_manager.check_health()
    proxy_manager.status["last_check"] = datetime.now().isoformat()
    
    return jsonify({
        "status": "ok" if is_healthy else "error",
        "proxy": proxy_manager.status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/proxy/start', methods=['POST'])
def start_proxy():
    """启动代理服务"""
    if proxy_manager.status["active"]:
        return jsonify({
            "success": False,
            "message": "代理服务已在运行"
        })
    
    result = proxy_manager.execute_command("start")
    if result["success"]:
        time.sleep(3)  # 等待启动
        proxy_manager.check_health()
        proxy_manager.status["start_time"] = datetime.now().isoformat()
    
    return jsonify({
        "success": result["success"],
        "message": "代理服务启动" + ("成功" if result["success"] else "失败"),
        "output": result["output"],
        "error": result["error"]
    })

@app.route('/api/proxy/stop', methods=['POST'])
def stop_proxy():
    """停止代理服务"""
    if not proxy_manager.status["active"]:
        return jsonify({
            "success": False,
            "message": "代理服务未运行"
        })
    
    result = proxy_manager.execute_command("stop")
    if result["success"]:
        proxy_manager.status["active"] = False
        proxy_manager.status["health_status"] = "stopped"
        proxy_manager.status["stop_time"] = datetime.now().isoformat()
    
    return jsonify({
        "success": result["success"],
        "message": "代理服务停止" + ("成功" if result["success"] else "失败"),
        "output": result["output"],
        "error": result["error"]
    })

@app.route('/api/proxy/status', methods=['GET'])
def get_status():
    """获取代理状态"""
    proxy_manager.check_health()
    
    return jsonify({
        "proxy": proxy_manager.status,
        "config": {
            "host": PROXY_HOST,
            "port": PROXY_PORT,
            "url": HEALTH_CHECK_URL
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/proxy/restart', methods=['POST'])
def restart_proxy():
    """重启代理服务"""
    stop_result = proxy_manager.execute_command("stop")
    time.sleep(2)
    start_result = proxy_manager.execute_command("start")
    
    if start_result["success"]:
        time.sleep(3)
        proxy_manager.check_health()
        proxy_manager.status["start_time"] = datetime.now().isoformat()
    
    return jsonify({
        "success": start_result["success"],
        "message": "代理服务重启" + ("成功" if start_result["success"] else "失败"),
        "stop_result": stop_result["success"],
        "start_result": start_result["success"]
    })

@app.route('/api/proxy/test', methods=['POST'])
def test_proxy():
    """测试代理功能"""
    proxy_manager.check_health()
    
    test_results = {
        "health_check": proxy_manager.status["active"],
        "connection_test": False,
        "proxy_test": False,
        "timestamp": datetime.now().isoformat()
    }
    
    # 连接测试
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=10)
        test_results["connection_test"] = True
        test_results["response_code"] = response.status_code
    except Exception as e:
        test_results["connection_error"] = str(e)
    
    # 可以添加更多测试...
    
    return jsonify(test_results)

@app.route('/', methods=['GET'])
def index():
    """Web 管理界面"""
    return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>按需代理管理</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; }
        .card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
        .status { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; }
        .active { color: #28a745; }
        .inactive { color: #dc3545; }
        .btn { background: #007bff; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; margin-right: 0.5rem; }
        .btn:hover { background: #0056b3; }
        .btn:disabled { background: #6c757d; cursor: not-allowed; }
        .btn.stop { background: #dc3545; }
        .btn.stop:hover { background: #c82333; }
        .log { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 1rem; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>按需代理管理</h1>
    
    <div class="card">
        <div class="status" id="status">检查中...</div>
        <button class="btn" onclick="startProxy()">启动代理</button>
        <button class="btn stop" onclick="stopProxy()">停止代理</button>
        <button class="btn" onclick="restartProxy()">重启代理</button>
        <button class="btn" onclick="testProxy()">测试连接</button>
    </div>
    
    <div class="card">
        <h3>配置信息</h3>
        <p><strong>代理地址:</strong> 192.168.31.147:1083</p>
        <p><strong>健康检查:</strong> <span id="health">检查中...</span></p>
        <p><strong>最后更新:</strong> <span id="lastUpdate">-</span></p>
    </div>
    
    <div class="card">
        <h3>操作日志</h3>
        <div class="log" id="log">等待操作...</div>
    </div>

    <script>
        function log(message) {
            const logEl = document.getElementById('log');
            const timestamp = new Date().toLocaleString();
            logEl.textContent = `[${timestamp}] ${message}\\n` + logEl.textContent;
        }
        
        function updateStatus(data) {
            const statusEl = document.getElementById('status');
            const healthEl = document.getElementById('health');
            const lastUpdateEl = document.getElementById('lastUpdate');
            
            if (data.proxy.active) {
                statusEl.textContent = '🟢 代理服务运行中';
                statusEl.className = 'status active';
                healthEl.textContent = '健康';
            } else {
                statusEl.textContent = '🔴 代理服务已停止';
                statusEl.className = 'status inactive';
                healthEl.textContent = '离线';
            }
            
            lastUpdateEl.textContent = new Date(data.timestamp).toLocaleString();
        }
        
        async function apiCall(url, data = {}) {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (error) {
                log(`API 错误: ${error.message}`);
                return { success: false, error: error.message };
            }
        }
        
        async function startProxy() {
            log('启动代理服务...');
            const result = await apiCall('/api/proxy/start');
            if (result.success) {
                log('✅ 代理服务启动成功');
            } else {
                log(`❌ 启动失败: ${result.message}`);
            }
            checkStatus();
        }
        
        async function stopProxy() {
            log('停止代理服务...');
            const result = await apiCall('/api/proxy/stop');
            if (result.success) {
                log('✅ 代理服务停止成功');
            } else {
                log(`❌ 停止失败: ${result.message}`);
            }
            checkStatus();
        }
        
        async function restartProxy() {
            log('重启代理服务...');
            const result = await apiCall('/api/proxy/restart');
            if (result.success) {
                log('✅ 代理服务重启成功');
            } else {
                log(`❌ 重启失败: ${result.message}`);
            }
            checkStatus();
        }
        
        async function testProxy() {
            log('测试代理连接...');
            const result = await apiCall('/api/proxy/test');
            if (result.connection_test) {
                log('✅ 连接测试成功');
            } else {
                log(`❌ 连接测试失败: ${result.connection_error || '未知错误'}`);
            }
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/proxy/status');
                const data = await response.json();
                updateStatus(data);
            } catch (error) {
                log(`状态检查失败: ${error.message}`);
            }
        }
        
        // 定期状态检查
        checkStatus();
        setInterval(checkStatus, 10000);
        
        // 清理日志
        setInterval(() => {
            const logEl = document.getElementById('log');
            const lines = logEl.textContent.split('\\n');
            if (lines.length > 50) {
                logEl.textContent = lines.slice(-30).join('\\n');
            }
        }, 30000);
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    # 启动 Web API 服务
    print("按需代理 Web API 服务")
    print("访问 http://localhost:5000 管理代理服务")
    print("API 端点:")
    print("  GET  /api/health      - 健康检查")
    print("  POST /api/proxy/start  - 启动代理")
    print("  POST /api/proxy/stop   - 停止代理")
    print("  POST /api/proxy/restart - 重启代理")
    print("  GET  /api/proxy/status - 查看状态")
    print("  POST /api/proxy/test   - 测试代理")
    
    app.run(host='0.0.0.0', port=5000, debug=False)