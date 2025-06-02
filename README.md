# 🦾 AI Cost Optimization Advisor Agent

> **Enterprise AI Workflow & Cost Optimization – Powered by Lyzr Studio & Gemini API**

---

## 🚀 Overview

This project is a multi-agent AI Cost Optimization Advisor built for enterprises to analyze, recommend, and optimize the cost and architecture of AI agent deployments.  
It guides teams through a structured workflow—identifying automation opportunities, estimating ROI, mapping tasks to AI solutions, and generating actionable reports.

- **Platform:** Lyzr Studio (no AWS Bedrock or Amazon Nova used)
- **LLM:** Google Gemini API (via Lyzr; note: Gemini credits may be required; fallback logic included)
- **Interface:** API-first, with chat-based Q&A on workflow reports

> **Note:** While Gemini via Lyzr was the main LLM used, in some runs Gemini credits were exhausted and fallback/manual logic was used.

---

## ✨ Key Features

- **7-Step Modular Workflow:** From business context capture to monitoring and change management
- **LLM-Powered Reasoning:** Uses Gemini for AI task inference, bottleneck analysis, cost/ROI estimation, and solution mapping
- **Automated Cost & ROI Analysis:** Calculates direct/indirect savings, investment, payback period, and scaling projections
- **RAG Pipeline:** Retrieval-Augmented Generation for contextual, explainable recommendations and agent matching
- **Comprehensive Reports:** Generates both executive summaries and technical deep-dives
- **Chatbot Interface:** Ask questions about your AI report and get instant, context-aware answers
- **API Server:** Exposes endpoints for workflow execution and chatbot queries

---

## 🏗️ Architecture & Workflow

graph TD
A[Input JSON or User] --> B(main.py - 7-Step Workflow)
B --> C[Workflow Summary JSON]
C --> D[RAG Pipeline (rag_implementation.py)]
D --> E[Agent Matching, Cost Calculation, Implementation Plan]
E --> F[Formal Report Generation]
F --> G[Chatbot Q&A (qanda.py)]
G --> H[API Server (server.py)]


---

## 📂 Project Structure

| File/Folder              | Description                                                  |
|--------------------------|--------------------------------------------------------------|
| `main.py`                | Orchestrates the 7-step workflow, outputs summary JSON       |
| `server.py`              | Flask API server for workflow & chatbot endpoints            |
| `inputs.py`              | Input data model and sample enterprise context               |
| `rag_implementation.py`  | RAG pipeline: agent matching, cost calculation, planning     |
| `qanda.py`               | Chatbot logic using Gemini, handles report-based Q&A         |
| `generate_summary.py`    | Generates executive and workflow summaries in JSON           |
| `step1.py`–`step7.py`    | Modular workflow steps: context, tasks, bottlenecks, etc.    |
| `data/`                  | Agent database, FAISS index, and related data               |
| `reports/`               | Output directory for generated reports                       |
| `summaries/`             | Stores workflow summary JSONs                                |
| `logs/`                  | Logs for API calls and monitoring                           |

---

## ⚡ Installation

**Requirements:**
- Python 3.9+
- pip
- Google Gemini API key (get from Google AI Studio)
- [Optional] Lyzr Studio account for workflow management

git clone https://github.com/your-org/ai-cost-optimization-advisor.git

cd ai-cost-optimization-advisor

pip install -r requirements.

cp .env.example .env # Fill in your GEMINI_API_KEY



---

## 🏁 Quick Start

### 1. Run the API Server

python server.py

### 2. Run Workflow via API

Send a POST request to `/run-workflow` with your enterprise context as JSON.

curl -X POST http://localhost:5000/run-workflow
-H "Content-Type: application/json"
-d @sample_input.json

### 3. Chat with the Advisor

Ask follow-up questions about the generated report:

curl -X POST http://localhost:5000/ask-chatbot
-H "Content-Type: application/json"
-d '{"question": "How can I reduce LLM inference costs?", "include_report_context": true}'

---

## 🛠️ Usage & Customization

- **Input:** Use the provided `inputs.py` or send a custom JSON via API.
- **Workflow:** The main agent (`main.py`) processes the 7 steps and outputs a summary JSON.
- **RAG Pipeline:** `rag_implementation.py` takes the summary, matches agents, calculates costs, and generates implementation plans.
- **Reporting:** Reports are saved in `/reports` and summaries in `/summaries`.
- **Chatbot:** `qanda.py` provides a Q&A interface over the generated report using Gemini (if credits available).

---

## 📝 Notes

- **No AWS Bedrock or Amazon Nova:** This repo does not use AWS Bedrock or Amazon Nova models. All LLM tasks are handled via Gemini API.
- **Gemini Credits:** If Gemini API credits are exhausted, some steps may require manual fallback or will prompt for manual input.
- **Extensibility:** Add new agents to the `data/agents.db` and update RAG logic as needed.

---

## 🤝 Contributing

We welcome contributions!  
- Fork the repo, create a feature branch, and submit a pull request.
- See `CONTRIBUTING.md` for guidelines.

---

## 📄 License

MIT © Your Organization

---

> **Built with ❤️ by the AI Cost Optimization Advisor Team**  
> Empowering enterprises to deploy AI efficiently and cost-effectively!

---

**Questions?**  
Open an issue or use the `/ask-chatbot` API to get instant answers from your own AI cost architect.
