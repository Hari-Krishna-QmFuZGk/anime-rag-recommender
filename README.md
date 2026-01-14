# Anime RAG Recommender

A **production-style Retrieval-Augmented Generation (RAG) system** that delivers semantic anime recommendations using **LLMs + vector search**.
Designed to demonstrate **ML system design, scalable deployment, and observability**, not just model inference.

---

## Problem Statement

Traditional anime recommendation systems rely on keyword matching or collaborative filtering, which:

* Fail on natural-language queries (e.g., *“dark psychological anime like Death Note”*)
* Do not generalize well to sparse or new users
* Lack explainability in recommendations

---

## Solution Overview

This system implements a **RAG-based recommendation pipeline**:

* Converts anime metadata into semantic embeddings
* Retrieves contextually relevant anime using vector similarity
* Uses an LLM to reason over retrieved context and generate recommendations

The result is a **flexible, explainable, natural-language–driven recommender system**.

---

## Key Engineering Highlights

* End-to-end **RAG pipeline** (ingestion → embeddings → retrieval → generation)
* Decoupled **retrieval and generation layers**
* Low-latency LLM inference using **Groq**
* Containerized and deployed on **Kubernetes**
* Cloud-hosted infrastructure with **production monitoring**

---

## System Architecture

### 1. Data Ingestion

* Anime metadata is ingested from CSV and transformed into structured documents
* Preprocessing ensures consistent schema and chunking strategy

### 2. Embedding & Vector Storage

* **HuggingFace embedding models** generate dense vector representations
* Embeddings are stored in **ChromaDB** for efficient similarity search
* Enables semantic retrieval beyond keyword matching

### 3. Retrieval-Augmented Generation

* Top-K relevant anime documents are retrieved via vector similarity
* Retrieved context is injected into the LLM prompt
* Improves factual grounding and reduces hallucinations

### 4. LLM Orchestration

* **LangChain** manages retrieval, prompt templates, and response generation
* **Groq** provides low-latency inference suitable for interactive workloads

### 5. Deployment & Observability

* Dockerized services deployed on **Kubernetes (Minikube)**
* Hosted on a **Google Cloud VM**
* **Grafana Cloud** monitors cluster health and application metrics

---

## Tech Stack

* **LLM**: Groq
* **Embeddings**: HuggingFace
* **RAG Framework**: LangChain
* **Vector Store**: ChromaDB
* **Frontend**: Streamlit
* **Containerization**: Docker
* **Orchestration**: Kubernetes (Minikube)
* **Cloud**: Google Cloud VM
* **Monitoring**: Grafana Cloud

---

## Local Development

```bash
git clone https://github.com/<your-username>/anime-rag-recommender.git
cd anime-rag-recommender
```

```bash
docker build -t anime-rag-recommender .
docker run -p 8501:8501 anime-rag-recommender
```

Access UI at: `http://localhost:8501`

---

## Kubernetes Deployment

```bash
minikube start
kubectl apply -f k8s/
kubectl get pods
```

```bash
kubectl port-forward service/anime-rag-service 8501:8501
```

---

## Design Decisions & Trade-offs

* **RAG vs Collaborative Filtering**
  Chosen to support cold-start users and natural-language queries.

* **ChromaDB (Local) vs Managed Vector DB**
  Selected for simplicity and local experimentation; easily replaceable with Pinecone/Weaviate in production.

* **Groq for Inference**
  Optimized for low latency and fast iteration in interactive systems.

* **Kubernetes Deployment**
  Demonstrates scalability, isolation, and production-grade deployment patterns.

---

## Future Work

* Hybrid recommendation (semantic + behavioral signals)
* User personalization and feedback loops
* Managed vector databases and autoscaling
* CI/CD pipeline and automated model evaluation
* Advanced observability (tracing, prompt metrics)

---

## Why This Project Matters

This project showcases:

* **ML system design thinking**
* **LLM + retrieval integration**
* **Cloud-native deployment**
* **Production observability**

Designed to reflect the kind of **end-to-end ownership expected in FAANG-level ML/SWE roles**.
