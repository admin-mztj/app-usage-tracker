# 应用使用时间追踪器

一个基于 Python + Electron 架构的桌面应用，用于追踪和统计用户在各应用程序上的使用时间。

## ✨ 功能特性

- 📊 实时追踪前台应用使用时间
- 📈 按今日/本周/本月查看统计数据
- 🎨 动漫主题紫色渐变玻璃拟态界面
- 📱 应用使用时间分布饼图
- 📉 24小时/周/月使用时段直方图
- 🎯 点击查看应用使用详情

## 🛠️ 技术栈

- **后端**: Python + Flask + SQLite
- **前端**: HTML + CSS + JavaScript + Chart.js
- **窗口追踪**: Win32 API (pywin32)
- **API**: RESTful API (端口 5000)

## 📁 项目结构

```
app-tracker/
├── backend/              # 后端服务
│   ├── api_server.py     # Flask API服务
│   ├── window_tracker.py # 窗口监控服务
│   ├── database.py       # 数据库操作
│   ├── start.py          # 一键启动脚本
│   └── requirements.txt  # Python依赖
├── frontend/             # 前端界面
│   └── index.html        # 主页面
└── README.md             # 说明文档
```

## 🚀 快速开始

### 环境要求

- Windows 10/11
- Python 3.6+

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 启动服务

**方式一（推荐）**:
```bash
cd backend
python start.py
```

**方式二**:
```bash
# 终端1 - 启动API服务
cd backend
python api_server.py

# 终端2 - 启动窗口监控
cd backend
python window_tracker.py
```

### 打开前端

在浏览器中打开 `frontend/index.html`

## 📖 使用说明

1. 启动服务后，应用会自动追踪前台窗口
2. 在前端界面查看统计数据
3. 点击应用查看详情和时段分布
4. 通过顶部标签切换查看不同时间段的数据

## 📝 数据更新

- 应用列表: 5秒自动刷新
- 饼图数据: 5分钟自动更新

## 📄 许可证

MIT License
