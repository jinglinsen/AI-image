# Amazon AIGC助手 - 后端服务

基于Flask + SQLite + Nano Banana API的智能图片生成后端服务。

## 🚀 功能特性

### 核心功能
- **多模态图片生成**：支持10张输入图片，生成7种类型的Amazon Listing图片
- **智能提示词构建**：基于模板和上下文自动生成高质量提示词
- **上下文记忆**：学习用户偏好，优化重新生成效果
- **批量处理**：支持多种图片类型的并发生成
- **成本控制**：API使用统计和成本估算

### 图片类型支持
1. **产品主图** - 纯白背景专业产品照
2. **信息图** - 功能特性可视化展示
3. **生活方式图** - 真实使用场景展示
4. **尺寸图** - 产品尺寸对比展示
5. **产品细节图** - 特写展示工艺细节
6. **多角度图** - 全方位产品展示
7. **使用说明图** - 步骤式操作指导
8. **对比图** - 与竞品优势对比
9. **包装图** - 产品包装展示

### 市场适配
- 🇺🇸 美国市场 - 功能性和家庭场景
- 🇬🇧 英国市场 - 经典优雅风格
- 🇩🇪 德国市场 - 品质工艺导向
- 🇯🇵 日本市场 - 精致简约美学
- 🇮🇳 印度市场 - 性价比实用性

## 📋 环境要求

- Python 3.8+
- SQLite 3
- OpenRouter API Key (用于访问Nano Banana)

## 🔧 安装配置

### 1. 克隆项目
```bash
git clone <project-url>
cd backend
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 环境配置
```bash
cp .env.example .env
# 编辑 .env 文件，配置API密钥等
```

### 4. 初始化数据库
```bash
python run.py
```

## 🚀 启动服务

### 开发模式
```bash
python run.py
```

### 生产模式
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📡 API接口

### 核心接口

#### 1. 生成图片
```http
POST /api/generate-images
Content-Type: application/json

{
  "productForm": {
    "targetMarket": "US",
    "title": "4件装 10英寸陶瓷餐盘套装",
    "sellingPoints": "微波炉适用，耐高温安全...",
    "dimensions": {"length": "25", "width": "25", "height": "3", "unit": "cm"}
  },
  "selectedImageTypes": ["main", "lifestyle", "detail"],
  "mainPrompt": "一套精美的白色陶瓷餐盘...",
  "productImages": [...],
  "referenceImages": [...],
  "competitors": [...]
}
```

#### 2. 查询任务状态
```http
GET /api/task-status/{task_id}
```

#### 3. 重新生成图片
```http
POST /api/regenerate-image
Content-Type: application/json

{
  "original_image_id": 123,
  "modifications": {
    "prompt_modifications": "调整光线更柔和..."
  },
  "reference_images": [...]
}
```

#### 4. 图片上传
```http
POST /api/upload-image
Content-Type: multipart/form-data

image: <file>
```

### 工具接口

#### 健康检查
```http
GET /api/health
```

#### 获取图片
```http
GET /api/image/{filename}
```

## 🗂️ 项目结构

```
backend/
├── app.py              # Flask应用主文件
├── models.py           # 数据库模型
├── config.py           # 配置管理
├── run.py              # 启动脚本
├── requirements.txt    # Python依赖
├── .env.example        # 环境变量模板
├── services/           # 业务服务层
│   ├── image_generator.py    # 图片生成服务
│   ├── prompt_builder.py     # 提示词构建服务
│   └── context_manager.py    # 上下文管理服务
├── utils/              # 工具类
│   └── image_processor.py    # 图片处理工具
├── uploads/            # 上传文件存储
├── generated_images/   # 生成图片存储
└── README.md          # 本文档
```

## 🛠️ 核心架构设计

### 1. 多图片输入处理
- **限制管理**：Nano Banana支持最多10张输入图片
- **优先级策略**：产品图片 > 参考图片
- **自动压缩**：图片自动调整到API适配尺寸
- **格式转换**：统一转换为base64格式

### 2. 多类型输出处理
- **并发生成**：每种图片类型独立生成
- **专用提示词**：每种类型有专门的提示词模板
- **错误隔离**：单个类型失败不影响其他类型
- **进度跟踪**：实时更新生成进度

### 3. 上下文记忆系统
- **用户偏好学习**：基于反馈学习用户喜好
- **成功元素提取**：记录生成成功的关键因素
- **失败避免**：记录失败案例避免重复
- **智能推荐**：基于历史生成个性化建议

## 🎯 最优解决方案

### 图片重新生成策略
1. **上下文继承**：保持原始任务的产品信息和市场定位
2. **渐进优化**：基于用户反馈逐步调整提示词
3. **元素组合**：结合成功元素和新需求
4. **A/B测试**：支持并行生成多个版本供选择

### 成本优化方案
1. **智能缓存**：相似请求复用结果
2. **批量处理**：合并同类型请求
3. **质量预检**：生成前验证提示词质量
4. **用量控制**：每日请求限制和成本告警

## 🔒 安全特性

- **输入验证**：严格的文件类型和大小检查
- **SQL注入防护**：使用ORM和参数化查询
- **XSS防护**：输出内容转义
- **CSRF保护**：API访问令牌验证
- **文件隔离**：上传文件和生成文件分离存储

## 📊 监控与日志

- **API使用统计**：记录每次调用的详细信息
- **性能监控**：响应时间和成功率统计
- **错误追踪**：详细的错误日志和堆栈跟踪
- **成本分析**：API调用成本实时统计

## 🚀 部署建议

### Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 环境变量配置
```bash
# 生产环境必需配置
OPENROUTER_API_KEY=your_production_api_key
FLASK_ENV=production
SECRET_KEY=your_strong_secret_key
DATABASE_URL=sqlite:///production.db
```

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
