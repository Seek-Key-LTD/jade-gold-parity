#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能按需代理监控系统
自动检测流量并按需启动/停止代理服务
"""

import os
import sys
import time
import json
import subprocess
import requests
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path

class SmartProxyMonitor:
    def __init__(self, config_file="proxy_config.json"):
        """初始化智能监控器"""
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.proxy_active = False
        self.last_activity = None
        self.activity_count = 0
        
    def load_config(self, config_file):
        """加载配置文件"""
        default_config = {
            "proxy_host": "192.168.31.147",
            "proxy_port": 1083,
            "startup_timeout": 60,  # 启动超时时间（秒）
            "idle_timeout": 300,   # 空闲超时时间（秒）
            "health_check_interval": 30,  # 健康检查间隔（秒）
            "activity_threshold": 5,  # 活动阈值（分钟）
            "auto_restart": True,    # 自动重启
            "log_retention_days": 7,  # 日志保留天数
            "monitoring_enabled": True
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    default_config.update(config)
            except Exception as e:
                print(f"配置文件加载失败，使用默认配置: {e}")
        
        # 创建配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    
    def setup_logging(self):
        """设置日志"""
        log_file = f"proxy_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def execute_script(self, action):
        """执行代理管理脚本"""
        try:
            script_path = "./scripts/on_demand_proxy.sh"
            result = subprocess.run(
                [script_path, action],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.logger.info(f"代理脚本执行成功: {action}")
                return True
            else:
                self.logger.error(f"代理脚本执行失败: {action}, 错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"代理脚本执行超时: {action}")
            return False
        except Exception as e:
            self.logger.error(f"代理脚本执行异常: {e}")
            return False
    
    def check_proxy_health(self):
        """检查代理健康状态"""
        try:
            proxy_url = f"http://{self.config['proxy_host']}:{self.config['proxy_port']}"
            response = requests.get(
                proxy_url,
                timeout=5,
                headers={'User-Agent': 'SmartProxyMonitor/1.0'}
            )
            
            # 任何响应都表示服务正常
            self.logger.debug(f"代理健康检查成功，状态码: {response.status_code}")
            return True
            
        except requests.exceptions.Timeout:
            self.logger.warning("代理健康检查超时")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.debug("代理服务未响应")
            return False
        except Exception as e:
            self.logger.error(f"代理健康检查异常: {e}")
            return False
    
    def get_proxy_activity(self):
        """获取代理活动统计"""
        # 这里可以集成实际的流量统计
        # 目前使用简单的活动检测
        if self.check_proxy_health():
            self.last_activity = datetime.now()
            return True
        return False
    
    def should_start_proxy(self):
        """判断是否应该启动代理"""
        if not self.config['monitoring_enabled']:
            return False
            
        # 如果已有活动记录且在阈值内
        if self.last_activity:
            time_since_activity = datetime.now() - self.last_activity
            if time_since_activity.total_seconds() < self.config['activity_threshold'] * 60:
                return True
        
        # 可以添加其他触发条件：
        # - 定时任务
        # - 特定时间段
        # - 流量阈值
        
        return False
    
    def should_stop_proxy(self):
        """判断是否应该停止代理"""
        if not self.proxy_active:
            return False
            
        if not self.config['monitoring_enabled']:
            return False
        
        # 检查空闲时间
        if self.last_activity:
            idle_time = datetime.now() - self.last_activity
            if idle_time.total_seconds() > self.config['idle_timeout']:
                return True
        
        return False
    
    def start_proxy_service(self):
        """启动代理服务"""
        self.logger.info("启动按需代理服务")
        
        if self.execute_script("start"):
            # 等待服务启动
            time.sleep(5)
            
            # 验证服务状态
            if self.check_proxy_health():
                self.proxy_active = True
                self.last_activity = datetime.now()
                self.activity_count += 1
                self.logger.info("代理服务启动成功")
                
                # 发送通知（可选）
                self.send_notification("代理服务已启动", "info")
                return True
            else:
                self.logger.error("代理服务启动失败")
                return False
        else:
            self.logger.error("代理服务启动命令执行失败")
            return False
    
    def stop_proxy_service(self):
        """停止代理服务"""
        self.logger.info("停止代理服务（空闲超时）")
        
        if self.execute_script("stop"):
            self.proxy_active = False
            self.logger.info("代理服务停止成功")
            
            # 发送通知（可选）
            self.send_notification("代理服务已停止", "warning")
            return True
        else:
            self.logger.error("代理服务停止失败")
            return False
    
    def send_notification(self, message, level="info"):
        """发送通知（可扩展）"""
        # 这里可以集成多种通知方式：
        # - 邮件通知
        # - Slack/微信通知
        # - 日志记录
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        
        if level == "error":
            self.logger.error(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def cleanup_old_logs(self):
        """清理旧日志"""
        try:
            current_date = datetime.now()
            log_files = list(Path('.').glob('proxy_monitor_*.log'))
            
            for log_file in log_files:
                # 从文件名提取日期
                date_str = log_file.stem.split('_')[-1]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                # 检查是否超过保留天数
                age = current_date - file_date
                if age.days > self.config['log_retention_days']:
                    log_file.unlink()
                    self.logger.info(f"清理旧日志文件: {log_file}")
                    
        except Exception as e:
            self.logger.error(f"日志清理失败: {e}")
    
    def run_monitoring_loop(self):
        """运行监控循环"""
        self.logger.info("启动智能代理监控")
        self.send_notification("智能代理监控已启动", "info")
        
        try:
            while True:
                # 检查当前状态
                is_active = self.check_proxy_health()
                
                # 状态变更处理
                if is_active and not self.proxy_active:
                    self.logger.info("检测到代理服务活跃（外部启动）")
                    self.proxy_active = True
                    self.last_activity = datetime.now()
                    
                elif not is_active and self.proxy_active:
                    self.logger.warning("代理服务意外停止")
                    if self.config['auto_restart']:
                        self.logger.info("自动重启代理服务")
                        if not self.start_proxy_service():
                            self.send_notification("自动重启失败", "error")
                    else:
                        self.proxy_active = False
                
                # 按需启动检查
                if not self.proxy_active and self.should_start_proxy():
                    self.start_proxy_service()
                
                # 按需停止检查
                elif self.proxy_active and self.should_stop_proxy():
                    self.stop_proxy_service()
                
                # 更新活动统计
                if is_active:
                    self.last_activity = datetime.now()
                
                # 定期清理
                if self.activity_count % 100 == 0:  # 每100次活动清理一次
                    self.cleanup_old_logs()
                
                # 等待下次检查
                time.sleep(self.config['health_check_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("收到停止信号，正在关闭监控...")
        except Exception as e:
            self.logger.error(f"监控循环异常: {e}")
            self.send_notification(f"监控异常: {e}", "error")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("智能代理监控已停止")
        
        # 可选择是否停止代理服务
        # if self.proxy_active:
        #     self.stop_proxy_service()
    
    def get_status_report(self):
        """获取状态报告"""
        status = {
            "proxy_active": self.proxy_active,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "activity_count": self.activity_count,
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
        
        return status

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("智能按需代理监控系统")
        print("========================")
        print("使用方法:")
        print("  python3 smart_monitor.py start     # 启动监控")
        print("  python3 smart_monitor.py stop      # 停止监控")
        print("  python3 smart_monitor.py status    # 查看状态")
        print("  python3 smart_monitor.py test      # 测试配置")
        print("  python3 smart_monitor.py config    # 生成配置文件")
        sys.exit(1)
    
    monitor = SmartProxyMonitor()
    command = sys.argv[1]
    
    if command == "start":
        monitor.run_monitoring_loop()
    elif command == "status":
        status = monitor.get_status_report()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif command == "stop":
        print("停止监控...")
        # 这里需要优雅停止，可以使用信号或文件标志
    elif command == "test":
        print("测试配置...")
        # 测试各种功能
    elif command == "config":
        print("配置文件已生成: proxy_config.json")
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()