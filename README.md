# 智汇研报助手

基于 **RAG（Retrieval-Augmented Generation）** 技术构建的垂直领域智能问答系统，专为金融研报、行业报告等文档的深度分析与问答场景设计。

## 🎯 项目简介

智汇研报助手是一款基于 Streamlit 和 LangChain 的智能文档问答系统，支持上传 PDF 文件并基于文件内容进行精准问答。系统采用向量数据库存储文档语义信息，结合大语言模型实现上下文感知的智能回答，有效解决 AI 幻觉问题。

## ✨ 功能亮点

### � 核心能力
- **PDF 文档解析**：支持多页 PDF 文件的文本提取，自动处理特殊字符和编码问题
- **智能文本切片**：采用 `RecursiveCharacterTextSplitter` 进行语义感知的文本分块（chunk_size=1000, chunk_overlap=200）
- **向量存储**：使用 ChromaDB 进行本地持久化存储，支持高效的语义检索
- **智能问答**：基于阿里云通义千问 qwen-plus 模型，结合检索到的文档片段生成精准回答

### 🧠 高级特性
- **多轮对话记忆**：自动保存最近 5 轮对话历史，支持上下文关联的连续问答
- **引用溯源**：回答中自动标注引用来源页码 `[第X页]`，有效减少 AI 幻觉
- **预设问题**：提供"总结本文核心观点"、"提取文中的财务数据"、"列出文中提到的主要风险"三个常用分析维度
- **会话管理**：支持手动清空对话历史和向量库，上传新文件自动重置状态

### 🎨 界面体验
- **现代化 UI**：采用 Streamlit wide 布局，视觉层次清晰
- **Markdown 渲染**：支持加粗、列表、标题等格式的富文本展示
- **来源高亮**：页码引用以蓝色加粗显示，便于快速定位文档位置

## 🛠 技术栈

| 模块 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Streamlit | >= 1.30.0 |
| LLM 框架 | LangChain | >= 0.1.0 |
| 向量数据库 | ChromaDB | >= 0.4.0 |
| 嵌入模型 | DashScope Embeddings | text-embedding-v2 |
| 大语言模型 | 通义千问 | qwen-plus |
| PDF 解析 | PyPDF2 | >= 2.0.0 |
| 环境管理 | python-dotenv | >= 1.0.0 |

## 📦 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd zhihui-report-assistant
```

### 2. 创建虚拟环境（推荐）

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## ⚙️ 配置说明

### 方式一：使用 .env 文件（推荐）

1. 复制环境变量示例文件：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入您的阿里云 API Key：

```env
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 方式二：应用内输入

启动应用后，在侧边栏的密码输入框中输入 API Key。

## 🚀 运行应用

```bash
streamlit run app.py
```

启动成功后访问：
- **本地地址**：http://localhost:8501
- **网络地址**：http://192.168.xxx.xxx:8501

## 📖 使用指南

### 基础流程

1. **配置 API Key**：在侧边栏输入阿里云 DashScope API Key
2. **上传文档**：点击文件上传按钮，选择 PDF 文件
3. **等待处理**：系统自动进行文本提取、切片、向量化
4. **开始问答**：在聊天输入框中提问，或使用预设问题按钮

### 预设问题

| 按钮 | 功能 |
|------|------|
| 总结本文核心观点 | 自动生成文档内容概要 |
| 提取文中的财务数据 | 识别并整理关键财务指标 |
| 列出文中提到的主要风险 | 汇总风险提示信息 |

### 注意事项

- 支持可提取文本的 PDF 文件，扫描件需提前进行 OCR 处理
- 推荐文档大小不超过 50MB，页数不超过 200 页
- 首次上传文件会自动创建 `chroma_db` 目录
- 上传新文件会自动清空之前的对话历史和向量库

## 📁 项目结构

```
zhihui-report-assistant/
├── app.py                 # 主应用入口
├── requirements.txt       # Python 依赖列表
├── .env.example           # 环境变量示例
├── .env                   # 环境变量配置（需自行创建）
├── chroma_db/             # ChromaDB 向量存储目录（自动生成）
│   ├── chroma.sqlite3     # 数据库文件
│   └── embedding_function/
└── README.md              # 项目说明文档
```

## 🔑 API Key 获取

1. 登录阿里云控制台：https://dashscope.console.aliyun.com/
2. 进入 API Key 管理页面：https://dashscope.console.aliyun.com/apiKey
3. 点击"创建 API Key"，复制生成的 Key
4. 配置到 `.env` 文件中

## 🔒 安全说明

- API Key 请勿提交到代码仓库，已将 `.env` 添加到 `.gitignore`
- 建议定期轮换 API Key，确保账户安全
- 向量数据存储在本地，不会上传到第三方服务

## 📝 更新日志

### v1.0.0
- ✅ 基础 PDF 上传与解析功能
- ✅ 文本切片与向量存储
- ✅ 基于 ChromaDB 的语义检索
- ✅ 通义千问大模型集成
- ✅ 多轮对话记忆功能
- ✅ 引用溯源与页码标注
- ✅ 预设问题按钮
- ✅ 会话管理与清空功能

## 📞 联系方式

如有问题或建议，欢迎提交 Issue 或 PR。

---

**License**: MIT