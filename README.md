# RiskChain

RiskChain is a full-stack prototype for supply chain risk monitoring. The project combines a Django backend, a Next.js frontend, and a multi-agent AI orchestration layer to identify geopolitical, logistics, and weather-related disruptions across supply chain nodes and transport edges.

The repository is well suited as a portfolio project because it brings together three relevant engineering areas in one system:

- graph-based supply chain modelling
- REST API design with Django REST Framework
- AI-assisted risk analysis using specialized agents and Azure OpenAI

## What the project does

RiskChain models a supply chain as a graph of nodes and edges:

- nodes represent locations such as suppliers, ports, hubs, or destinations
- edges represent transport links between those locations
- risks can be attached to both nodes and edges

The platform is designed to support questions such as:

- Which parts of a supply chain are currently exposed to disruption?
- Which transport legs are most vulnerable to delays?
- Which external events should be surfaced for operational decision-making?

## Architecture

### Frontend

- Next.js 15 with React 19 and TypeScript
- dashboard-style UI for browsing supply chain scenarios
- component-based structure with reusable UI primitives

### Backend

- Django 5 and Django REST Framework
- domain model for countries, cities, nodes, edges, risks, and supply chains
- endpoints for querying supply chain data and triggering risk updates

### AI layer

- supervisor-based orchestration with LangGraph
- specialized agents for geopolitical risk, weather and natural disasters, and logistics monitoring
- Azure OpenAI integration for LLM-driven coordination

## Repository structure

```text
frontend/   Next.js application for the dashboard and process views
backend/    Python dependencies and Django project
backend/riskchain/agents/        AI agents and supervisor orchestration
backend/riskchain/supplychains/  domain models, serializers, and API views
backend/riskchain/create_data/   helper scripts for generating demo data
backend/riskchain/predict_delivery/  experiments for delay prediction models
```

## Local setup

### Frontend

Requirements:

- Node.js 20+
- npm

Start the frontend:

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

The app will usually be available at `http://localhost:3000`.

### Backend

Requirements:

- Python 3.11+

Set up the backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd riskchain
python manage.py runserver
```

The Django app will usually be available at `http://localhost:8000`.

Useful endpoints:

- admin panel: `http://localhost:8000/admin`
- all supply chains: `http://localhost:8000/supplychains/supplychain`
- supply chain by id: `http://localhost:8000/supplychains/supplychain/1/`

To create an admin user:

```bash
python manage.py createsuperuser
```

## Environment variables

To enable the AI agents, create a `.env` file in `backend/riskchain/` next to `manage.py`.

```env
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
```

The backend loads these values via `python-dotenv`, which keeps secrets out of the codebase and git history.

## Trigger the AI orchestrator manually

From a Django shell, the orchestrator can be run directly on stored nodes or edges:

```python
from agents.orchestrator_agent import process_node_with_supervisor, process_edge_with_supervisor
from supplychains.models import Node, Edge

node = Node.objects.first()
node_trace = process_node_with_supervisor(node)

edge = Edge.objects.first()
edge_trace = process_edge_with_supervisor(edge)
```

This is useful for debugging agent behaviour and inspecting the generated trace output.

## Quality checks

Python linting example:

```bash
pylint supplychains
```

To refresh backend dependencies after package changes:

```bash
pip freeze > requirements.txt
```

## Current status

This repository is currently a strong prototype with three clear strengths:

- a coherent end-to-end product idea
- an ambitious AI orchestration layer connected to a real domain model
- a frontend that can be used to present the concept visually

The most natural next steps would be tighter frontend-backend integration, automated tests around the API and agent flows, and deployment-ready environment configuration.