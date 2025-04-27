# PegaAI

PegaAI是一个强大的AI图像生成和管理平台，支持多种AI引擎，提供作品分享和社区功能。

## 功能特点

- 支持多种AI引擎（Stable Diffusion、Midjourney等）
- 作品库管理
- 作品分享功能
- 社区互动
- RESTful API

## 技术栈

- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pytest

## 快速开始

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/pegaai.git
cd pegaai
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

5. 初始化数据库：
```bash
alembic upgrade head
```

6. 运行应用：
```bash
python app/main.py
```

7. 访问API文档：
```
http://localhost:8000/docs
```

## 项目结构

```
pegaai/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── db/
│   ├── models/
│   └── schemas/
├── tests/
├── alembic/
├── alembic.ini
├── requirements.txt
└── README.md
```

## API文档

API文档使用Swagger UI，可在以下地址访问：
```
http://localhost:8000/docs
```

主要API端点：
- `/api/v1/auth/*` - 认证相关
- `/api/v1/ai/*` - AI引擎相关
- `/api/v1/works/*` - 作品管理相关

## 测试

运行测试：
```bash
pytest
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情
