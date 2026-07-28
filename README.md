#AIOps Incident Assitant
Intelligent system that monitors the Dragonfly SDN network in real time,
detects anomalies using Random Forest model, retrieves relevant
context via RAG, and generates human-readable incident reports.

Project Architecture:
+-----------------------------------------------------------------+
|                    STREAMLIT DASHBOARD                          |
|         Live telemetry  |  Active alerts  |  AI explanation     |
+------------------+----------------------------------------------+
                    |
+------------------v----------------------------------------------+
|              INCIDENT EXPLAINER  (RAG + LLM)                    |
|   ChromaDB retrieval  ->  LLaMA 3 prompt  ->  incident report   |
+------------------+----------------------------------------------+
                   |
+------------------v----------------------------------------------+
|              ANOMALY DETECTOR  (RF model)                       |
|   Flow features  ->  predict label + confidence score           |
+------------------+----------------------------------------------+
                   |
+------------------v----------------------------------------------+
|              TELEMETRY COLLECTOR                                 |
|   Polls Dragonfly simulation  ->  extracts flow features        |
+------------------+----------------------------------------------+
                   |
+------------------v----------------------------------------------+
|              KNOWLEDGE BASE  (ChromaDB vector store)            |
|   Dragonfly docs + runbooks + FloodScore formulas + attacks     |
+-----------------------------------------------------------------+

## Results
| Metric                 | Value      |
|------------------------|------------|
| Detection F1 (macro)   | 97.3%      |
| RAG retrieval precision| 85%        |
| End-to-end latency     | ~1.8s avg  |
 

Stack
Python / scikit-learn / LangChain / ChromaDB / Groq LLaMA 3 / Streamlit
