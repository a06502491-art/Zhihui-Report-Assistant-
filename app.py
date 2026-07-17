import os
import re
import sys
import io
import time

try:
    import streamlit as st
except Exception as e:
    print(f"[ERROR] 导入streamlit失败: {e}")
    sys.exit(1)

try:
    from PyPDF2 import PdfReader
except Exception as e:
    print(f"[ERROR] 导入PyPDF2失败: {e}")
    sys.exit(1)

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception as e:
    print(f"[ERROR] 导入langchain_text_splitters失败: {e}")
    sys.exit(1)

try:
    from langchain_community.embeddings import DashScopeEmbeddings
except Exception as e:
    print(f"[ERROR] 导入DashScopeEmbeddings失败: {e}")
    sys.exit(1)

try:
    from langchain_community.chat_models import ChatTongyi
except Exception as e:
    print(f"[ERROR] 导入ChatTongyi失败: {e}")
    sys.exit(1)

try:
    from langchain_chroma import Chroma
except Exception as e:
    print(f"[ERROR] 导入Chroma失败: {e}")
    sys.exit(1)

def clean_text(text):
    if not text:
        return None
    
    allowed_punctuation = "，。！？、；：""''（）《》【】,.!?;:'\"()<>{}"
    
    result = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            result.append(char)
        elif 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            result.append(char)
        elif '0' <= char <= '9':
            result.append(char)
        elif char in '\n\t ':
            result.append(char)
        elif char in allowed_punctuation:
            result.append(char)
    
    cleaned = ''.join(result)
    cleaned = ' '.join(cleaned.split())
    
    if len(cleaned.strip()) < 2:
        return None
    
    return cleaned

print("[DEBUG] === 程序启动 ===")

st.set_page_config(page_title="智汇研报助手", layout="wide")

print("[DEBUG] 页面配置完成")

st.markdown("""
<style>
    :root {
        --primary-color: #3b82f6;
        --primary-hover: #2563eb;
        --bg-light: #f8fafc;
        --bg-dark: #0f172a;
        --sidebar-bg-light: #ffffff;
        --sidebar-bg-dark: #1e293b;
        --text-light: #1e293b;
        --text-dark: #f1f5f9;
        --text-muted-light: #64748b;
        --text-muted-dark: #94a3b8;
        --card-bg-light: #ffffff;
        --card-bg-dark: #1e293b;
        --border-light: #e2e8f0;
        --border-dark: #334155;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --radius-sm: 6px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
    }

    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    body {
        background: var(--bg-light);
        color: var(--text-light);
        font-size: 15px;
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .dark body {
        background: var(--bg-dark);
        color: var(--text-dark);
    }

    .css-18e3th9 {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    .css-1d391kg {
        padding: 1rem;
    }

    .css-1l02zno {
        padding: 1rem;
    }

    .css-163ttbj {
        padding: 0;
    }

    .css-1q1n0ol {
        background: transparent;
        border: none;
        box-shadow: none;
    }

    .css-17eq0hr {
        background: var(--card-bg-light);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
        padding: 1.25rem;
    }

    .dark .css-17eq0hr {
        background: var(--card-bg-dark);
        border-color: var(--border-dark);
    }

    .stSidebar {
        background: var(--sidebar-bg-light);
        border-right: 1px solid var(--border-light);
        padding: 1.5rem;
        width: 320px !important;
        box-shadow: var(--shadow-md);
    }

    .dark .stSidebar {
        background: var(--sidebar-bg-dark);
        border-color: var(--border-dark);
    }

    .stSidebar .css-6qob1r {
        display: none;
    }

    .stSidebarTitle {
        font-size: 20px;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .stSidebarSubtitle {
        font-size: 13px;
        color: var(--text-muted-light);
        margin-bottom: 1.5rem;
    }

    .dark .stSidebarSubtitle {
        color: var(--text-muted-dark);
    }

    .stTextInput, .stFileUploader, .stButton {
        margin-bottom: 1rem;
    }

    .stTextInput > div > div {
        border-radius: var(--radius-md);
        border: 1.5px solid var(--border-light);
        transition: all 0.2s ease;
        background: var(--card-bg-light);
        padding: 0.75rem 1rem;
    }

    .dark .stTextInput > div > div {
        border-color: var(--border-dark);
        background: var(--card-bg-dark);
    }

    .stTextInput > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    .stButton > button {
        width: 100%;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
        border: none;
        color: white;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-md);
        font-size: 14px;
        letter-spacing: 0.3px;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, var(--primary-hover), #1d4ed8);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }

    .stFileUploader > div > div {
        border-radius: var(--radius-md);
        border: 2px dashed var(--border-light);
        background: var(--card-bg-light);
        transition: all 0.2s ease;
        padding: 1.5rem;
        min-height: 120px;
    }

    .dark .stFileUploader > div > div {
        border-color: var(--border-dark);
        background: var(--card-bg-dark);
    }

    .stFileUploader > div > div:hover {
        border-color: var(--primary-color);
        background: rgba(59, 130, 246, 0.05);
    }

    .dark .stFileUploader > div > div:hover {
        background: rgba(59, 130, 246, 0.1);
    }

    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }

    .chat-header {
        margin-bottom: 2rem;
        text-align: center;
    }

    .chat-header h1 {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-light);
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .dark .chat-header h1 {
        color: var(--text-dark);
    }

    .chat-header p {
        color: var(--text-muted-light);
        font-size: 14px;
    }

    .dark .chat-header p {
        color: var(--text-muted-dark);
    }

    .stChatMessage {
        padding: 0;
        margin-bottom: 1rem;
    }

    .stChatMessage > div {
        padding: 0;
        background: transparent !important;
    }

    .message-bubble {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: var(--radius-lg);
        font-size: 15px;
        line-height: 1.6;
        word-wrap: break-word;
    }

    .message-user {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
        color: white;
        border-bottom-right-radius: var(--radius-sm);
        margin-left: auto;
        box-shadow: var(--shadow-md);
    }

    .message-assistant {
        background: var(--card-bg-light);
        color: var(--text-light);
        border: 1px solid var(--border-light);
        border-bottom-left-radius: var(--radius-sm);
        box-shadow: var(--shadow-sm);
    }

    .dark .message-assistant {
        background: var(--card-bg-dark);
        color: var(--text-dark);
        border-color: var(--border-dark);
    }

    .message-label {
        font-size: 12px;
        font-weight: 500;
        margin-bottom: 4px;
        color: var(--text-muted-light);
    }

    .dark .message-label {
        color: var(--text-muted-dark);
    }

    .stChatInput > div > div {
        border-radius: var(--radius-xl);
        border: 1.5px solid var(--border-light);
        box-shadow: var(--shadow-md);
        transition: all 0.2s ease;
        background: var(--card-bg-light);
        padding: 0.5rem 1rem;
    }

    .dark .stChatInput > div > div {
        border-color: var(--border-dark);
        background: var(--card-bg-dark);
    }

    .stChatInput > div > div:focus-within {
        border-color: var(--primary-color);
        box-shadow: var(--shadow-lg);
    }

    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 12px 16px;
        background: var(--card-bg-light);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        border-bottom-left-radius: var(--radius-sm);
        color: var(--text-muted-light);
    }

    .dark .typing-indicator {
        background: var(--card-bg-dark);
        border-color: var(--border-dark);
        color: var(--text-muted-dark);
    }

    .typing-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--text-muted-light);
        animation: typing 1.4s infinite ease-in-out both;
    }

    .dark .typing-dot {
        background: var(--text-muted-dark);
    }

    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }

    .preset-buttons {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }

    .preset-btn {
        flex: 1;
        min-width: 180px;
        max-width: 250px;
        padding: 0.625rem 1rem;
        border-radius: var(--radius-md);
        background: var(--card-bg-light);
        border: 1px solid var(--border-light);
        color: var(--text-light);
        font-size: 13px;
        font-weight: 500;
        transition: all 0.2s ease;
        cursor: pointer;
        text-align: center;
        box-shadow: var(--shadow-sm);
    }

    .dark .preset-btn {
        background: var(--card-bg-dark);
        border-color: var(--border-dark);
        color: var(--text-dark);
    }

    .preset-btn:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .preset-btn:active {
        transform: translateY(0);
    }

    .highlighted-source {
        color: var(--primary-color);
        font-weight: 600;
    }

    .success-message {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        color: #16a34a;
        font-size: 14px;
        margin-bottom: 1rem;
    }

    .dark .success-message {
        background: rgba(34, 197, 94, 0.15);
        border-color: rgba(34, 197, 94, 0.3);
    }

    .error-message {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        color: #dc2626;
        font-size: 14px;
        margin-bottom: 1rem;
    }

    .dark .error-message {
        background: rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.3);
    }

    .divider {
        border: none;
        height: 1px;
        background: var(--border-light);
        margin: 1.5rem 0;
    }

    .dark .divider {
        background: var(--border-dark);
    }

    .streaming-text {
        white-space: pre-wrap;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    print("[DEBUG] 初始化chat_history")

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
    print("[DEBUG] 初始化vector_store为None")

def clear_history():
    st.session_state.chat_history = []
    st.session_state.vector_store = None
    print("[DEBUG] 已清空对话历史和向量库")

def build_prompt(user_input, context_with_sources):
    history = st.session_state.chat_history
    recent_history = history[-10:]
    
    history_text = ""
    if recent_history:
        history_text = "\n\n对话历史：\n"
        for msg in recent_history:
            role = "用户" if msg["role"] == "user" else "助手"
            history_text += f"{role}：{msg['content']}\n"
    
    prompt = f"""基于以下参考内容和对话历史回答用户问题：

参考内容：
{context_with_sources}

{history_text}

用户问题：{user_input}

重要要求：
1. 回答必须基于提供的参考内容，不要编造信息
2. 在回答的每个关键信息后，必须以 [第X页] 的格式标注引用来源
3. 如果引用了多个页码，可以标注为 [第X,Y页]
4. 如果没有相关参考内容，请明确说明"""
    return prompt

def stream_response(text, placeholder):
    highlighted_text = text.replace("[第", "<span class='highlighted-source'>[第").replace("页]", "页]</span>")
    full_text = ""
    for i in range(len(highlighted_text)):
        full_text = highlighted_text[:i+1]
        placeholder.markdown(full_text, unsafe_allow_html=True)
        time.sleep(0.02)
    return text

st.sidebar.markdown('<div class="stSidebarTitle">智汇研报助手 v1.0</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="stSidebarSubtitle">基于 RAG 技术的垂直领域问答系统</div>', unsafe_allow_html=True)
st.sidebar.markdown('<hr class="divider">', unsafe_allow_html=True)

st.sidebar.markdown("### 设置", unsafe_allow_html=True)
api_key = st.sidebar.text_input("请输入 DashScope API Key", type="password")
print(f"[DEBUG] 侧边栏输入的api_key值: {'有值' if api_key else '空'}")

if api_key:
    print(f"[DEBUG] 开始初始化组件，API Key前缀: {api_key[:5]}...")
    try:
        os.environ["DASHSCOPE_API_KEY"] = api_key
        print(f"[DEBUG] 环境变量设置成功")
        
        embeddings = DashScopeEmbeddings(model="text-embedding-v2", dashscope_api_key=api_key)
        print(f"[DEBUG] DashScopeEmbeddings初始化成功")
        
        st.session_state.vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings,
        )
        print(f"[DEBUG] Chroma向量库初始化成功")
        
        st.session_state.llm = ChatTongyi(model="qwen-plus", dashscope_api_key=api_key)
        print(f"[DEBUG] ChatTongyi初始化成功")
    except Exception as init_err:
        print(f"[ERROR] 组件初始化失败: {type(init_err).__name__}: {str(init_err)}")
        import traceback
        traceback.print_exc()
        st.error(f"组件初始化失败: {type(init_err).__name__}: {str(init_err)}")

st.sidebar.markdown('<hr class="divider">', unsafe_allow_html=True)
st.sidebar.markdown("### 文件上传", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("上传PDF文件", type=["pdf"], on_change=clear_history)
print(f"[DEBUG] 文件上传状态: {'已上传' if uploaded_file else '未上传'}")

st.sidebar.markdown('<hr class="divider">', unsafe_allow_html=True)
if st.sidebar.button("清空对话"):
    clear_history()

def process_pdf(uploaded_file):
    try:
        print(f"[DEBUG] === 开始处理PDF: {uploaded_file.name} ===")
        
        try:
            reader = PdfReader(uploaded_file)
            print(f"[DEBUG] PdfReader初始化成功，PDF页数: {len(reader.pages)}")
        except Exception as pdf_err:
            print(f"[ERROR] PdfReader初始化失败: {type(pdf_err).__name__}: {str(pdf_err)}")
            import traceback
            traceback.print_exc()
            st.error(f"PDF读取失败: {type(pdf_err).__name__}: {str(pdf_err)}")
            return
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        all_chunks = []
        all_metadatas = []
        
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                print(f"[DEBUG] 第{i+1}页提取文本长度: {len(page_text) if page_text else 0}")
                if page_text:
                    page_chunks = text_splitter.split_text(page_text)
                    for j, chunk in enumerate(page_chunks):
                        cleaned = clean_text(chunk)
                        if cleaned and len(cleaned.strip()) >= 2:
                            all_chunks.append(cleaned)
                            all_metadatas.append({
                                "source": uploaded_file.name,
                                "page_number": i + 1,
                                "chunk_id": j
                            })
            except Exception as extract_err:
                print(f"[ERROR] 第{i+1}页提取文本失败: {type(extract_err).__name__}: {str(extract_err)}")
                import traceback
                traceback.print_exc()
        
        print(f"[DEBUG] 总切片数量: {len(all_chunks)}")
        
        if not all_chunks:
            st.warning("PDF内容为空或清洗后无有效文本，请检查PDF文件")
            return
        
        print(f"[DEBUG] 准备存入向量库: {len(all_chunks)} 个片段，包含页码信息")
        
        try:
            st.session_state.vector_store.add_texts(texts=all_chunks, metadatas=all_metadatas)
            print(f"[DEBUG] 向量库存储成功")
            st.markdown('<div class="success-message">✅ 文件上传成功！已处理所有文本片段</div>', unsafe_allow_html=True)
        except Exception as chroma_err:
            print(f"[ERROR] 向量库存储失败: {type(chroma_err).__name__}: {str(chroma_err)}")
            import traceback
            traceback.print_exc()
            st.error(f"向量库存储失败: {type(chroma_err).__name__}: {str(chroma_err)}")
        
    except Exception as e:
        print(f"[ERROR] 处理PDF时顶层出错: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        st.error(f"处理PDF时出错: {type(e).__name__}: {str(e)}")

if uploaded_file is not None:
    if not api_key:
        st.markdown('<div class="error-message">❌ 请先在左侧输入 API Key</div>', unsafe_allow_html=True)
    else:
        process_pdf(uploaded_file)

st.markdown('<div class="chat-header"><h1>智汇研报助手</h1><p>基于 RAG 技术的智能问答系统</p></div>', unsafe_allow_html=True)

if api_key:
    st.markdown(f'<div style="text-align: center; margin-bottom: 1.5rem; font-size: 13px; color: var(--text-muted-light);">当前使用的Key前缀: {api_key[:5]}...</div>', unsafe_allow_html=True)

st.markdown("### 快速提问", unsafe_allow_html=True)

preset_questions = ["总结本文核心观点", "提取文中的财务数据", "列出文中提到的主要风险"]
st.markdown('<div class="preset-buttons">', unsafe_allow_html=True)
for i, question in enumerate(preset_questions):
    if st.button(question, key=f"preset_{i}", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        with st.chat_message("user"):
            st.markdown(f'<div class="message-bubble message-user">{question}</div>', unsafe_allow_html=True)
        
        with st.chat_message("assistant"):
            if not api_key:
                st.markdown('<div class="error-message">❌ 请先在左侧输入 API Key</div>', unsafe_allow_html=True)
            elif st.session_state.vector_store is None:
                st.markdown('<div class="error-message">❌ 请先在左侧输入 API Key</div>', unsafe_allow_html=True)
            else:
                docs = st.session_state.vector_store.similarity_search(question, k=3)
                
                if not docs:
                    st.markdown('<div style="color: var(--text-muted-light);">⚠️ 知识库为空，请先上传PDF文件</div>', unsafe_allow_html=True)
                else:
                    context_with_sources = "\n\n".join([
                        f"【第{doc.metadata.get('page_number', '?')}页】\n{doc.page_content}" 
                        for doc in docs
                    ])
                    prompt = build_prompt(question, context_with_sources)
                    
                    response = st.session_state.llm.invoke(prompt)
                    
                    placeholder = st.empty()
                    full_text = stream_response(response.content, placeholder)
                    st.session_state.chat_history.append({"role": "assistant", "content": full_text})
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("### 对话历史", unsafe_allow_html=True)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        role_label = "用户" if message["role"] == "user" else "智汇助手"
        bubble_class = "message-user" if message["role"] == "user" else "message-assistant"
        content = message["content"]
        if message["role"] == "assistant":
            content = content.replace("[第", "<span class='highlighted-source'>[第").replace("页]", "页]</span>")
        st.markdown(f'<div class="message-label">{role_label}</div><div class="message-bubble {bubble_class}">{content}</div>', unsafe_allow_html=True)

user_input = st.chat_input("请输入您的问题...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(f'<div class="message-bubble message-user">{user_input}</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        if not api_key:
            st.markdown('<div class="error-message">❌ 请先在左侧输入 API Key</div>', unsafe_allow_html=True)
        elif st.session_state.vector_store is None:
            st.markdown('<div class="error-message">❌ 请先在左侧输入 API Key</div>', unsafe_allow_html=True)
        else:
            docs = st.session_state.vector_store.similarity_search(user_input, k=3)
            
            if not docs:
                st.markdown('<div style="color: var(--text-muted-light);">⚠️ 知识库为空，请先上传PDF文件</div>', unsafe_allow_html=True)
            else:
                context_with_sources = "\n\n".join([
                    f"【第{doc.metadata.get('page_number', '?')}页】\n{doc.page_content}" 
                    for doc in docs
                ])
                prompt = build_prompt(user_input, context_with_sources)
                
                response = st.session_state.llm.invoke(prompt)
                
                placeholder = st.empty()
                full_text = stream_response(response.content, placeholder)
                st.session_state.chat_history.append({"role": "assistant", "content": full_text})