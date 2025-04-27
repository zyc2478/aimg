# AIGC Platform Backend

这是一个基于 FastAPI 和 Stable Diffusion 的 AI 图像生成平台后端。

## 功能特点

- 基于 Stable Diffusion 的图像生成
- RESTful API 接口
- PostgreSQL 数据库存储
- Redis 缓存支持
- Docker 容器化部署
- 完整的测试覆盖

## 技术栈

- Python 3.9+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Stable Diffusion
- Docker
- pytest

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/aigc-platform.git
cd aigc-platform/backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

4. 启动服务：
```bash
# 使用 Docker
docker-compose up -d

# 或者直接运行
uvicorn app.main:app --reload
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

运行测试：
```bash
pytest
```

## 部署

1. 构建 Docker 镜像：
```bash
docker-compose build
```

2. 启动服务：
```bash
docker-compose up -d
```

## 目录结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── api.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── image.py
│   ├── schemas/
│   │   └── image.py
│   ├── services/
│   │   └── image_generation.py
│   ├── database.py
│   └── main.py
├── tests/
│   └── test_image_generation.py
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 贡献

欢迎提交 Pull Request 或创建 Issue。

## 许可证

MIT 