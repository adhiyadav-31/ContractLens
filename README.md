# ContractLens

**AI-powered Business Contract Intelligence & Obligation Tracking Agent**

ContractLens transforms static business contracts into actionable, traceable information.

Instead of manually reading contracts to find important dates, obligations, payment terms, renewal conditions, and risks, ContractLens uses AI to extract and organize this information.

## What ContractLens Does

* 📄 Upload and analyze contracts
* 🧠 Extract important contract information
* 👤 Identify parties and their obligations
* 📅 Extract deadlines, renewal dates, and payment terms
* ⚠️ Flag clauses that may require human review
* 🔍 Answer natural-language questions about contracts
* 📚 Provide source references for AI-generated answers
* 🔄 Compare different versions of a contract
* 🏢 Perform counterparty due-diligence checks using available external information
* 🔔 Track upcoming contractual obligations and deadlines

## Core Idea

**Contract → Understanding → Obligations → Deadlines → Review → Action**

ContractLens is designed to assist businesses with contract review and management. It does not replace legal professionals or provide definitive legal advice.

## How It Works

```text
Contract PDF
     ↓
Text Extraction
     ↓
Contract Intelligence
     ↓
Structured Contract Data
     ↓
┌──────────────────────────────┐
│ Obligations                  │
│ Deadlines                    │
│ Risk / Review Flags          │
│ Counterparty Information     │
└──────────────────────────────┘
     ↓
RAG + Semantic Search
     ↓
AI Answers + Source Evidence
     ↓
Business Dashboard
```

## Tech Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* FastAPI

### AI / ML

* Gemini
* Embeddings
* Retrieval-Augmented Generation (RAG)

### Document Processing

* PyMuPDF

### Vector Database

* ChromaDB

### Database

* MongoDB Atlas

## Project Structure

```text
ContractLens/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── agents/
│   │   ├── services/
│   │   ├── models/
│   │   ├── database/
│   │   └── utils/
│   │
│   ├── uploads/
│   ├── .env
│   ├── .gitignore
│   └── requirements.txt
│
├── sample_contracts/
│   ├── contract_v1.pdf
│   └── contract_v2.pdf
│
├── .gitignore
└── README.md
```

## Agent Architecture

ContractLens uses an orchestrated agentic workflow consisting of specialized capabilities:

* **Contract Intelligence Agent** → understands and extracts contract information
* **Obligation Agent** → identifies who must do what and when
* **Risk & Review Agent** → identifies clauses requiring human attention
* **Counterparty Due Diligence Agent** → checks available information about the contracting party
* **Orchestrator** → coordinates the workflow and routes tasks to the appropriate capability

## RAG Pipeline

Contract documents are converted into text and divided into relevant chunks.

```text
PDF
 ↓
Text
 ↓
Chunks
 ↓
Embeddings
 ↓
ChromaDB
 ↓
Relevant Contract Sections
 ↓
Gemini
 ↓
Answer + Source Reference
```

This allows ContractLens to answer questions using evidence from the uploaded contract rather than relying only on the model's general knowledge.

## Running the Project

### Backend

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside `backend/` and add the required API keys and database connection details.

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

### Frontend

Open:

```text
frontend/index.html
```

or serve the frontend through a local development server.

## Demo Flow

```text
Upload Contract
      ↓
Extract Contract Information
      ↓
Identify Obligations
      ↓
Generate Timeline
      ↓
Show Review Flags
      ↓
Ask Questions
      ↓
Show Source Evidence
      ↓
Compare Contract Versions
```

## Disclaimer

ContractLens is an AI-assisted contract intelligence system. Its outputs are intended to support human review and decision-making and should not be treated as legal advice.
