/**
 * BuyerShowTool 前端逻辑
 */

class BuyerShowTool {
    constructor() {
        this.currentTaskId = null;
        this.eventSource = null;
        this.isConfigured = false;
        
        // DOM 元素
        this.configAlert = document.getElementById('configAlert');
        this.configAlertText = document.getElementById('configAlertText');
        
        // DeepSeek 配置
        this.deepseekUrl = document.getElementById('deepseekUrl');
        this.deepseekKey = document.getElementById('deepseekKey');
        this.deepseekModel = document.getElementById('deepseekModel');
        this.deepseekCount = document.getElementById('deepseekCount');
        
        // 通义配置
        this.tongyiKey = document.getElementById('tongyiKey');
        this.tongyiModel = document.getElementById('tongyiModel');
        this.tongyiCount = document.getElementById('tongyiCount');
        
        // 任务区域
        this.targetDirInput = document.getElementById('targetDir');
        this.runBtn = document.getElementById('runBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.clearLogBtn = document.getElementById('clearLogBtn');
        this.logContainer = document.getElementById('logContainer');
        this.reviewCountSpan = document.getElementById('reviewCount');
        this.imageCountSpan = document.getElementById('imageCount');
        
        this.init();
    }
    
    init() {
        // 绑定配置按钮事件
        document.getElementById('saveConfigBtn').addEventListener('click', () => this.saveConfig());
        document.getElementById('resetConfigBtn').addEventListener('click', () => this.resetConfig());
        
        // 绑定任务按钮事件
        this.runBtn.addEventListener('click', () => this.startTask());
        this.stopBtn.addEventListener('click', () => this.stopTask());
        this.clearLogBtn.addEventListener('click', () => this.clearLog());
        
        // 绑定浏览按钮事件
        document.getElementById('browseBtn').addEventListener('click', () => this.browseFolder());
        
        // 加载配置
        this.loadConfig();
    }
    
    browseFolder() {
        // 使用 input[type="file"] 方式选择文件夹
        const input = document.createElement('input');
        input.type = 'file';
        input.webkitdirectory = true;
        input.multiple = false;
        
        input.onchange = (e) => {
            const files = e.target.files;
            if (files.length > 0) {
                // 获取选中的文件夹路径
                // webkitRelativePath 包含类似 "folderName/" 的路径
                const path = files[0].webkitRelativePath;
                const folderPath = path.substring(0, path.indexOf('/'));
                
                // 对于浏览器安全限制，我们只能获取到相对路径
                // 但用户手动输入完整路径时，浏览器会允许访问
                // 这里我们提示用户如果需要浏览文件夹，可以直接拖拽文件夹到输入框
                this.appendLog('info', '提示: 由于浏览器安全限制，无法直接获取文件夹完整路径。');
                this.appendLog('info', '请直接在输入框中输入目标目录的完整路径，例如: C:\\example\\folder');
            }
        };
        
        input.click();
    }
    
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.configured && data.config) {
                // 已配置，加载配置到表单
                this.isConfigured = true;
                this.hideConfigAlert();
                
                // DeepSeek 配置
                this.deepseekUrl.value = data.config.deepseek.url || '';
                this.deepseekModel.value = data.config.deepseek.model || '';
                this.deepseekCount.value = data.config.deepseek.reviewCount || 4;
                
                // 通义配置
                this.tongyiModel.value = data.config.tongyi.model || '';
                this.tongyiCount.value = data.config.tongyi.imageCount || 4;
                
                // 更新任务信息
                this.reviewCountSpan.textContent = this.deepseekCount.value;
                this.imageCountSpan.textContent = this.tongyiCount.value;
                
                // 启用运行按钮
                this.runBtn.disabled = false;
            } else {
                // 未配置，显示警告
                this.isConfigured = false;
                this.showConfigAlert(data.message || '请先配置 API 密钥');
                this.runBtn.disabled = true;
                
                // 设置默认值
                this.setDefaultConfig();
            }
        } catch (error) {
            console.error('加载配置失败:', error);
            this.showConfigAlert('加载配置失败，请检查网络连接');
            this.runBtn.disabled = true;
        }
    }
    
    setDefaultConfig() {
        // 设置默认配置值
        this.deepseekUrl.value = 'https://api.deepseek.com/v1/chat/completions';
        this.deepseekModel.value = 'deepseek-chat';
        this.deepseekCount.value = 4;
        
        this.tongyiModel.value = 'wan2.7-image';
        this.tongyiCount.value = 4;
    }
    
    showConfigAlert(message) {
        this.configAlert.style.display = 'flex';
        this.configAlertText.textContent = message;
    }
    
    hideConfigAlert() {
        this.configAlert.style.display = 'none';
    }
    
    async saveConfig() {
        const configData = {
            deepseek: {
                url: this.deepseekUrl.value.trim(),
                apiKey: this.deepseekKey.value.trim(),
                model: this.deepseekModel.value.trim(),
                reviewCount: parseInt(this.deepseekCount.value) || 4
            },
            tongyi: {
                apiKey: this.tongyiKey.value.trim(),
                model: this.tongyiModel.value.trim(),
                imageCount: parseInt(this.tongyiCount.value) || 4
            }
        };
        
        // 验证必填字段
        if (!configData.deepseek.apiKey) {
            alert('请输入 DeepSeek API 密钥');
            return;
        }
        if (!configData.tongyi.apiKey) {
            alert('请输入通义万相 API 密钥');
            return;
        }
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('配置保存成功！');
                this.isConfigured = true;
                this.hideConfigAlert();
                this.runBtn.disabled = false;
                
                // 清空密钥输入框（安全考虑）
                this.deepseekKey.value = '';
                this.tongyiKey.value = '';
                
                // 更新任务信息
                this.reviewCountSpan.textContent = configData.deepseek.reviewCount;
                this.imageCountSpan.textContent = configData.tongyi.imageCount;
            } else {
                alert('配置保存失败: ' + (data.error || '未知错误'));
            }
        } catch (error) {
            alert('保存配置失败: ' + error.message);
        }
    }
    
    resetConfig() {
        this.setDefaultConfig();
        this.deepseekKey.value = '';
        this.tongyiKey.value = '';
    }
    
    async startTask() {
        if (!this.isConfigured) {
            alert('请先配置 API 密钥');
            return;
        }
        
        const targetDir = this.targetDirInput.value.trim();
        
        if (!targetDir) {
            alert('请输入目标目录路径');
            return;
        }
        
        // 清空日志
        this.clearLog();
        this.appendLog('info', '正在启动任务...');
        
        // 禁用开始按钮
        this.runBtn.disabled = true;
        this.stopBtn.disabled = false;
        
        try {
            const response = await fetch('/api/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ targetDir })
            });
            
            const data = await response.json();
            
            if (data.taskId) {
                this.currentTaskId = data.taskId;
                this.appendLog('info', `任务已启动，ID: ${data.taskId}`);
                this.connectSSE(data.taskId);
            } else {
                this.appendLog('error', `启动失败: ${data.error}`);
                this.resetButtons();
            }
        } catch (error) {
            this.appendLog('error', `请求失败: ${error.message}`);
            this.resetButtons();
        }
    }
    
    connectSSE(taskId) {
        // 关闭之前的连接
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // 创建 SSE 连接
        this.eventSource = new EventSource(`/api/logs/${taskId}`);
        
        this.eventSource.addEventListener('log', (event) => {
            const data = JSON.parse(event.data);
            this.appendLog(data.type, data.message);
        });
        
        this.eventSource.addEventListener('complete', (event) => {
            const data = JSON.parse(event.data);
            if (data.success) {
                this.appendLog('success', '✅ 任务完成！');
            } else {
                this.appendLog('error', `❌ 任务失败: ${data.message}`);
            }
            this.resetButtons();
            this.eventSource.close();
        });
        
        this.eventSource.onerror = (error) => {
            console.error('SSE 错误:', error);
            this.appendLog('error', '连接断开');
            this.resetButtons();
        };
    }
    
    stopTask() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        this.appendLog('warning', '任务已停止');
        this.resetButtons();
    }
    
    resetButtons() {
        this.runBtn.disabled = !this.isConfigured;
        this.stopBtn.disabled = true;
    }
    
    appendLog(type, message) {
        // 移除 placeholder
        const placeholder = this.logContainer.querySelector('.log-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        
        const now = new Date();
        const timestamp = now.toLocaleTimeString('zh-CN', { hour12: false });
        
        const typeLabels = {
            info: 'INFO',
            success: 'SUCCESS',
            warning: 'WARNING',
            error: 'ERROR',
            complete: 'COMPLETE'
        };
        
        entry.innerHTML = `
            <span class="timestamp">[${timestamp}]</span>
            <span class="type">[${typeLabels[type] || type.toUpperCase()}]</span>
            <span class="message">${this.escapeHtml(message)}</span>
        `;
        
        this.logContainer.appendChild(entry);
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
    }
    
    clearLog() {
        this.logContainer.innerHTML = '<div class="log-placeholder">点击"开始生成"后，日志将显示在这里...</div>';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new BuyerShowTool();
});