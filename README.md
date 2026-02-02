<div align="center">

🛡️ VibeGuard

The Missing Security Layer for AI Agents

AI Agent 的隐形安全防线

"Don't let your Agents vibe-code their way into a data breach."





"别让你的 Agent 在'凭感觉编程'中裸奔。"

<!-- Badges (Optional but recommended for style) -->

<p>
<a href="#-english">🇬🇧 English</a> •
<a href="#-中文文档">🇨🇳 中文文档</a>
</p>

</div>

<!-- English Section -->

<div id="-english"></div>

🇬🇧 English

VibeGuard is an open-source Agent Gateway designed to solve the critical security flaws exposed by incidents like the Moltbook data leak. It acts as a protective proxy between your Agents and LLM providers (OpenAI, Anthropic, DeepSeek).

🚧 Status: Beta / Production-Ready Skeleton

📉 Why Now? The Security Crisis

The rise of "Vibe Coding" (coding by feel with AI) has democratized development but exponentially increased security risks.

The Moltbook Incident (Wake-up Call): Recently, Moltbook, a popular "Reddit for Agents," suffered a major security lapse where 1.5 million Agent API keys were reportedly exposed due to missing Row Level Security (RLS).

The Explosion of Hardcoded Secrets: According to recent security reports (e.g., GitGuardian), the number of hardcoded secrets leaked in public repositories is sky-rocketing as more non-engineers build AI apps.

🚨 The Problem

❌ Key Leakage: If your Agent is hacked, your API Key (and credit card) is gone.

❌ Data Exposure: Agents might accidentally send users' PII (emails, phones) to public LLMs.

❌ Zero Observability: You have no idea what your Agent is actually saying or doing in the wild.

💡 The Solution

VibeGuard sits in the middle. Your Agent talks to VibeGuard; VibeGuard talks to the LLM.

Key Features

🔑 Keyless Architecture: Agents use ephemeral tokens; the real API Key is hidden in the backend.

🕵️‍♂️ PII Scrubbing: Automatically redacts emails and phone numbers before they leave your infra.

📼 Audit Trail: Records every interaction via SQLite for full accountability.

🛑 Injection Defense: Blocks common prompt injection patterns.

🚀 Quick Start

1. Installation

# Clone the repo
git clone [https://github.com/yourusername/vibeguard.git](https://github.com/yourusername/vibeguard.git)
cd vibeguard

# Install dependencies
pip install -r requirements.txt


2. Run the Gateway

export USE_MOCK_LLM=True
python main.py


<div align="right">
<a href="#-vibeguard">↑ Back to Top</a>
</div>

<!-- Chinese Section -->

<div id="-中文文档"></div>

🇨🇳 中文文档

VibeGuard 是一个开源的 AI Agent 安全网关，旨在解决由 Moltbook 数据泄露等事件暴露出的严重安全缺陷。它作为您的 Agent 和大模型提供商之间的保护层。

📉 项目背景

"Vibe Coding"（凭感觉编程）让开发变得触手可及，但也导致了安全风险的指数级扩散。

Moltbook 事件： 近期备受欢迎的 Agent 社区因配置错误暴露了 150 万个 API 密钥。

裸奔的敏感数据： 大量 Agent 在公网环境下缺乏基本的安全边界评估。

🚨 核心问题

❌ 密钥泄露: 硬编码在代码中的 Key 一旦丢失，后果不堪设想。

❌ 隐私暴露: Agent 可能会无意中将用户隐私发送给公共大模型。

❌ 不可观测: 开发者无法追踪 Agent 在后台的真实行为。

💡 解决方案

核心功能

🔑 无密钥架构: Agent 持有临时令牌，真实的 API Key 安全存储在服务端。

🕵️‍♂️ 隐私清洗: 在数据发出前，自动掩盖邮箱、手机号等敏感信息。

📼 黑匣子审计: 基于 SQLite 记录每一条对话，支持事后追溯。

🛑 注入防御: 拦截常见的恶意指令注入。

🚀 快速开始

1. 安装

git clone [https://github.com/yourusername/vibeguard.git](https://github.com/yourusername/vibeguard.git)
cd vibeguard
pip install -r requirements.txt


2. 启动服务

# 开启模拟模式进行测试
export USE_MOCK_LLM=True
python main.py


🤝 贡献

为 Post-AGI 时代构建。欢迎提交 PR。

<div align="right">
<a href="#-vibeguard">↑ 回到顶部</a>
</div>
