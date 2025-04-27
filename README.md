# AI Image Generation Project

基于 Stable Diffusion 的 AI 图像生成项目，提供简单易用的 Web 界面。

## 功能特点

- 文本到图像生成
- 图像到图像转换
- 简单易用的 Web 界面
- RESTful API 支持
- 支持多种模型和参数配置

## 技术栈

- 后端：Python, FastAPI, Gradio
- 前端：React, TypeScript
- AI 模型：Stable Diffusion

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/zyc2478/aimg.git
cd aimg
```

2. 安装后端依赖
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

## 运行项目

1. 启动后端服务
```bash
cd backend
python app/main.py
```

2. 启动前端服务
```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 即可使用 Web 界面。

## API 文档

API 文档可在 http://localhost:8000/docs 查看。

## 许可证

MIT License

## 新增功能：作品库

- 所有通过"文生图"或"图生图"生成的图片，都会自动保存到 `backend/gallery` 目录，文件名为时间戳。
- Web 界面顶部菜单新增"作品库"Tab，可浏览所有已生成图片，支持点击"刷新"实时查看新作品。
- 作品库图片按生成时间倒序排列。
