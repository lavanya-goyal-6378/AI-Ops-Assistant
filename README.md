#AIOps Incident Assitant
Intelligent system that monitors the Dragonfly SDN network in real time,
detects anomalies using Random Forest model, retrieves relevant
context via RAG, and generates human-readable incident reports.

## Project Architecture

```text
                     +-----------------------------+
                     | STREAMLIT DASHBOARD         |
                     | Live Telemetry | Alerts     |
                     | AI Explanation             |
                     +-------------+---------------+
                                   |
                                   v
                     +-----------------------------+
                     | INCIDENT EXPLAINER          |
                     | RAG + Groq LLM              |
                     | ChromaDB Retrieval          |
                     +-------------+---------------+
                                   |
                                   v
                     +-----------------------------+
                     | ANOMALY DETECTOR            |
                     | Random Forest Model         |
                     | Predict Label + Confidence  |
                     +-------------+---------------+
                                   |
                                   v
                     +-----------------------------+
                     | TELEMETRY COLLECTOR         |
                     | Dragonfly / Mininet         |
                     | Extract Flow Features       |
                     +-------------+---------------+
                                   |
                                   v
                     +-----------------------------+
                     | KNOWLEDGE BASE              |
                     | ChromaDB                    |
                     | Docs + Runbooks + Attacks   |
                     +-----------------------------+
```

## Results
| Metric                 | Value      |
|------------------------|------------|
| Detection F1 (macro)   | 97.3%      |
| RAG retrieval precision| 85%        |
| End-to-end latency     | ~1.8s avg  |
 

Stack
Python / scikit-learn / LangChain / ChromaDB / Groq LLaMA 3 / Streamlit
