import os
import re
import time
import json
import uuid
import httpx
import sqlite3
import logging
import secrets
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Header, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# --- 1. 配置与环境 (Configuration) ---

class Settings:
    # 基础配置
    APP_NAME: str = "VibeGuard Pro"
    VERSION: str = "1.0.0-beta"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # LLM 配置
    USE_MOCK_LLM: bool = os.getenv("USE_MOCK_LLM", "True").lower() == "true"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-placeholder-key")
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # 数据库配置 (使用 SQLite 文件持久化)
    DB_PATH: str = "vibeguard.db"
    
    # 管理员密钥 (用于创建 Agent，首次启动请查看控制台输出)
    ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", secrets.token_urlsafe(16))

settings = Settings()

# --- 2. 日志配置 (Logging) ---
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VibeGuard")

# --- 3. 数据库层 (Persistence Layer) ---

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 允许通过列名访问
    return conn

def init_db():
    """初始化数据库表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Agents 表：存储 Agent 身份、预算和限流策略
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        rate_limit_rpm INTEGER DEFAULT 60, -- 每分钟请求限制
        total_budget_usd REAL DEFAULT 10.0,
        current_usage_usd REAL DEFAULT 0.0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Audit Logs 表：审计日志
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        request_id TEXT PRIMARY KEY,
        agent_id TEXT,
        endpoint TEXT,
        model TEXT,
        input_sanitized TEXT,
        tokens_used INTEGER,
        latency_ms REAL,
        status TEXT,
        risk_flags TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(agent_id) REFERENCES agents(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")

# --- 4. 业务逻辑层 (Service Layer) ---

class RateLimiter:
    """
    简单的内存限流器 (生产环境建议使用 Redis)
    实现固定窗口算法
    """
    _usage_cache: Dict[str, List[float]] = {}
    
    @classmethod
    def check_limit(cls, agent_id: str, limit_rpm: int) -> bool:
        now = time.time()
        window_start = now - 60  # 1分钟窗口
        
        # 清理旧记录
        if agent_id not in cls._usage_cache:
            cls._usage_cache[agent_id] = []
        
        # 过滤掉窗口外的请求
        cls._usage_cache[agent_id] = [t for t in cls._usage_cache[agent_id] if t > window_start]
        
        # 检查是否超限
        if len(cls._usage_cache[agent_id]) >= limit_rpm:
            return False
            
        # 记录本次请求
        cls._usage_cache[agent_id].append(now)
        return True

class PIIEngine:
    """隐私清洗引擎"""
    
    PATTERNS = {
        "EMAIL": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "PHONE": r'\b1[3-9]\d{9}\b',
        # 简单的 Visa/MasterCard 格式 (仅供演示)
        "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b', 
        "IPV4": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    }

    RISK_KEYWORDS = [
        "ignore previous instructions", 
        "system prompt", 
        "忽略之前的指令",
        "drop table",
        "exec("
    ]

    @classmethod
    def sanitize(cls, text: str) -> Tuple[str, List[str]]:
        """
        清洗文本并返回：(清洗后的文本, 触发的规则列表)
        """
        triggered_rules = []
        sanitized_text = text

        for name, pattern in cls.PATTERNS.items():
            if re.search(pattern, sanitized_text):
                triggered_rules.append(name)
                sanitized_text = re.sub(pattern, f'[{name}_REDACTED]', sanitized_text)
        
        return sanitized_text, triggered_rules

    @classmethod
    def check_injection(cls, text: str) -> bool:
        """检测 Prompt 注入"""
        text_lower = text.lower()
        for keyword in cls.RISK_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

# --- 5. API 模型 (Pydantic Models) ---

class AgentCreate(BaseModel):
    name: str
    budget_limit: float = 10.0
    rate_limit_rpm: int = 60

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: List[ChatMessage]
    temperature: float = 0.7

# --- 6. FastAPI 应用构建 ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    init_db()
    logger.info(f"🔑 ADMIN SECRET KEY: {settings.ADMIN_SECRET}")
    logger.info("Save this key to manage agents via /admin endpoints.")
    yield
    # 关闭时逻辑 (如有)

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)
security = HTTPBearer()

# --- 7. 依赖注入与中间件逻辑 ---

async def get_current_agent(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证 Agent Token 并获取 Agent 信息"""
    token = credentials.credentials
    conn = get_db_connection()
    cursor = conn.cursor()
    
    agent = cursor.execute("SELECT * FROM agents WHERE token = ?", (token,)).fetchone()
    conn.close()
    
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid Agent Token")
    
    if not agent['is_active']:
        raise HTTPException(status_code=403, detail="Agent is suspended")
        
    if agent['current_usage_usd'] >= agent['total_budget_usd']:
        raise HTTPException(status_code=402, detail="Budget limit exceeded")

    return dict(agent)

async def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证管理员密钥"""
    if credentials.credentials != settings.ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Admin Secret")
    return True

# --- 8. 路由端点 (Endpoints) ---

# --- Admin API (新增) ---
@app.post("/admin/agents", tags=["Admin"])
def create_agent(agent_data: AgentCreate, _=Depends(verify_admin)):
    """创建新的 Agent 并颁发 Token"""
    token = f"vg-{secrets.token_urlsafe(16)}"
    agent_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO agents (id, name, token, rate_limit_rpm, total_budget_usd) VALUES (?, ?, ?, ?, ?)",
        (agent_id, agent_data.name, token, agent_data.rate_limit_rpm, agent_data.budget_limit)
    )
    conn.commit()
    conn.close()
    
    logger.info(f"Created new agent: {agent_data.name}")
    return {"agent_id": agent_id, "token": token, "note": "Store this token securely."}

@app.get("/admin/audit-logs", tags=["Admin"])
def view_audit_logs(_=Depends(verify_admin), limit: int = 50):
    """查看最近的审计日志"""
    conn = get_db_connection()
    logs = conn.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(log) for log in logs]

# --- Public Agent API ---
@app.post("/v1/chat/completions", tags=["Agent Gateway"])
async def chat_proxy(
    request: ChatRequest, 
    agent: dict = Depends(get_current_agent)
):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # 1. 限流检查 (Rate Limiting)
    if not RateLimiter.check_limit(agent['id'], agent['rate_limit_rpm']):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Slow down.")

    user_content = request.messages[-1].content
    
    # 2. 安全检查 (Security Gates)
    # A. 注入检测 (阻断)
    if PIIEngine.check_injection(user_content):
        # 记录恶意行为
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO audit_logs (request_id, agent_id, status, risk_flags) VALUES (?, ?, ?, ?)",
            (request_id, agent['id'], "BLOCKED", "PROMPT_INJECTION")
        )
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="Security Policy Violation: Malicious prompt detected.")
    
    # B. PII 清洗 (脱敏)
    sanitized_content, triggered_rules = PIIEngine.sanitize(user_content)
    
    # 替换请求内容
    request.messages[-1].content = sanitized_content
    
    # 3. LLM 转发 (Proxy)
    response_data = {}
    
    if settings.USE_MOCK_LLM:
        # Mock 响应
        await asyncio.sleep(0.5) # 模拟网络延迟
        response_data = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"[VibeGuard] Received sanitized: '{sanitized_content}'. Rules triggered: {triggered_rules}"
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        }
    else:
        # 真实转发
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{settings.OPENAI_BASE_URL}/chat/completions",
                    json=request.dict(),
                    headers=headers,
                    timeout=60.0
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=resp.status_code, detail="Upstream Provider Error")
                response_data = resp.json()
            except Exception as e:
                logger.error(f"Upstream Error: {e}")
                raise HTTPException(status_code=502, detail="Upstream Service Unavailable")

    # 4. 审计与计费 (Auditing)
    latency = (time.time() - start_time) * 1000
    total_tokens = response_data.get("usage", {}).get("total_tokens", 0)
    
    # 估算成本 (简化逻辑: $0.000002/token)
    cost_usd = total_tokens * 0.000002
    
    conn = get_db_connection()
    # 更新余额
    conn.execute(
        "UPDATE agents SET current_usage_usd = current_usage_usd + ? WHERE id = ?",
        (cost_usd, agent['id'])
    )
    # 写入详尽日志
    conn.execute(
        '''INSERT INTO audit_logs 
           (request_id, agent_id, endpoint, model, input_sanitized, tokens_used, latency_ms, status, risk_flags) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            request_id, 
            agent['id'], 
            "/chat/completions", 
            request.model, 
            sanitized_content, 
            total_tokens, 
            latency, 
            "SUCCESS", 
            ",".join(triggered_rules)
        )
    )
    conn.commit()
    conn.close()

    return response_data

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 {settings.APP_NAME} Starting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
