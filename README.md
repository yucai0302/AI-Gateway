<div align="center">🛡️ VibeGuardThe Missing Security Layer for AI Agents / AI Agent 的隐形安全防线"Don't let your Agents vibe-code their way into a data breach.""别让你的 Agent 在'凭感觉编程'中裸奔。"English | 中文文档</div><a name="english"></a>🇬🇧 EnglishVibeGuard is an open-source Agent Gateway designed to solve the critical security flaws exposed by incidents like the Moltbook data leak. It acts as a protective proxy between your Agents and LLM providers (OpenAI, Anthropic, DeepSeek).🚧 Status: Beta / Production-Ready Skeleton📉 Why Now? The Security CrisisThe rise of "Vibe Coding" (coding by feel with AI) has democratized development but exponentially increased security risks.1. The Moltbook Incident (Wake-up Call)Recently, Moltbook, a popular "Reddit for Agents," suffered a major security lapse where 1.5 million Agent API keys were reportedly exposed due to missing Row Level Security (RLS).2. The Explosion of Hardcoded SecretsAccording to recent security reports (e.g., GitGuardian), the number of hardcoded secrets leaked in public repositories is sky-rocketing as more non-engineers build AI apps.(Visual representation of the rising trend in secret leaks)🚨 The ProblemKey Leakage: If your Agent is hacked, your API Key (and credit card) is gone.Data Exposure: Agents might accidentally send users' PII (emails, phones) to public LLMs.Zero Observability: You have no idea what your Agent is actually saying or doing in the wild.💡 The SolutionVibeGuard sits in the middle. Your Agent talks to VibeGuard; VibeGuard talks to the LLM.Key Features🔑 Keyless Architecture (Identity Management)Agents use ephemeral, revocable tokens (agent-token-123).The real OPENAI_API_KEY is stored securely in the VibeGuard env, never exposed to the client code.🕵️‍♂️ Invisible Security Companion (PII Scrubbing)Automatically detects and redacts sensitive data (Email, Phone) before it leaves your infrastructure.📼 The Black Box (Audit Trail)Records every interaction via SQLite. Who asked what? How much did it cost? Did it violate policy?🛑 Injection Defense & Rate LimitingBlocks malicious prompts and enforces RPM (Requests Per Minute) limits to prevent budget drainage.🚀 Quick Start1. Installation# Clone the repo
git clone [https://github.com/yourusername/vibeguard.git](https://github.com/yourusername/vibeguard.git)
cd vibeguard

# Install dependencies
pip install -r requirements.txt
2. Run the Gateway# Run in Mock Mode (No OpenAI Key needed for testing)
export USE_MOCK_LLM=True
python main.py
Server will start at http://localhost:8000. Check console for the ADMIN_SECRET.3. Create an Agent (Admin Only)curl -X POST "http://localhost:8000/admin/agents" \
     -H "Authorization: Bearer <ADMIN_SECRET_FROM_CONSOLE>" \
     -H "Content-Type: application/json" \
     -d '{"name": "TestBot", "budget_limit": 50.0, "rate_limit_rpm": 60}'
4. Test Chatcurl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Authorization: Bearer <NEW_AGENT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
           "model": "gpt-3.5-turbo",
           "messages": [{"role": "user", "content": "My email is test@example.com, tell me a joke."}]
         }'
<a name="中文文档"></a>🇨🇳 中文文档VibeGuard 是一个开源的 AI Agent 安全网关，旨在解决由 Moltbook 数据泄露等事件暴露出的严重安全缺陷。它作为您的 Agent 和大模型提供商（OpenAI, Anthropic, DeepSeek）之间的保护性代理层。📉 项目背景与市场痛点"Vibe Coding"（凭感觉编程/AI辅助编程）的兴起让开发变得触手可及，但也导致了安全风险的指数级扩散。1. Moltbook 事件（行业分水岭）近期，备受欢迎的 Agent 社区 Moltbook 遭遇严重安全危机。由于缺乏行级安全（RLS）配置，据报道有 150 万个 Agent 的 API 密钥 暴露在公网。这证明了在 AGI 时代，传统的安全机制已无法应对 "人人都是开发者" 的现状。2. 裸奔的敏感数据在缺乏安全边界评估的情况下，大量由 Vibe Coding 生成的 Agent 正在公网“裸奔”。(示意图：随着 Agent 数量激增，由于配置错误导致的安全漏洞呈上升趋势)🚨 核心问题密钥泄露 (Key Leakage): 开发者习惯将 Key 硬编码在 Agent 中，一旦被黑客获取，不仅造成资金损失，更可能被用于恶意攻击。隐私暴露 (Data Exposure): Agent 可能会无意中将用户的 PII（邮箱、手机号）发送给公共大模型用于训练。不可观测 (Zero Observability): 很多 Vibe Coder 根本不知道自己的 Agent 在后台到底说了什么、做了什么。💡 解决方案VibeGuard 部署在中间层。您的 Agent 与 VibeGuard 对话，再由 VibeGuard 与大模型对话。核心功能🔑 无密钥架构 (Keyless Architecture)Agent 仅持有临时的、可撤销的令牌 (agent-token-123)。真实的 OPENAI_API_KEY 安全地存储在 VibeGuard 的环境变量中，绝不暴露给客户端代码。🕵️‍♂️ 隐形安全伴侣 (PII Scrubbing)隐私清洗：在数据离开您的基础设施之前，自动检测并掩盖敏感数据（如邮箱、手机号）。📼 黑匣子审计 (Audit Trail)基于 SQLite 记录每一次交互。谁问了什么？花了多少钱？是否违反了安全策略？🛑 注入防御与限流拦截恶意 Prompt，并实施 RPM (每分钟请求数) 限制，防止预算被刷爆。🚀 快速开始1. 安装# 克隆仓库
git clone [https://github.com/yourusername/vibeguard.git](https://github.com/yourusername/vibeguard.git)
cd vibeguard

# 安装依赖
pip install -r requirements.txt
2. 运行网关# 运行模拟模式 (测试无需 OpenAI Key)
export USE_MOCK_LLM=True
python main.py
服务将启动于 http://localhost:8000。请在控制台查看打印出的 ADMIN_SECRET。3. 创建 Agent (管理员)curl -X POST "http://localhost:8000/admin/agents" \
     -H "Authorization: Bearer <控制台显示的ADMIN_SECRET>" \
     -H "Content-Type: application/json" \
     -d '{"name": "TestBot", "budget_limit": 50.0, "rate_limit_rpm": 60}'
4. 测试对话curl -X POST "http://localhost:8000/v1/chat/completions" \
     -H "Authorization: Bearer <新生成的AGENT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
           "model": "gpt-3.5-turbo",
           "messages": [{"role": "user", "content": "我的邮箱是 test@example.com，讲个笑话。"}]
         }'
🤝 贡献为 Post-AGI 时代构建。欢迎提交 PR。
