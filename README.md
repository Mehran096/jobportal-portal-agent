# JobPortal AI Agents

AI agents to auto-generate jobs and blogs for JobPortal using Groq AI + MongoDB.

## Features
- Add single or multiple jobs automatically
- Add blogs with AI content
- Daily automatic blog posting (runs on Vercel Cron)
- Supports multiple companies and locations

## Folder Structure
- `agent.py` - Main job agent
- `agent1.py` / `agent2.py` / `agent3.py` - Company-wise job agents (ITBS, etc)
- `agent_blog.py` / `agent_blog1.py` - Blog agents
- `extra.py` / `fix.py` - Helper scripts
- `.env.example` - Environment template

## Setup

### 1. Install Python & Create venv
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1