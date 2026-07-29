import time
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from telemetry import simulate_attack
from detector import AnomalyDetector
from explainer import IncidentExplainer

det = AnomalyDetector()
exp = IncidentExplainer()

latencies = []

for i in range(10):
    t0 = time.time()

    telemetry = simulate_attack("ddos")
    result = det.predict(telemetry)
    report = exp.explain(result, telemetry)

    latency = (time.time() - t0) * 1000
    latencies.append(latency)
    
    print(f"Run {i+1}: {latency:.2f} ms")
    
telemetry = simulate_attack("ddos")

t1 = time.time()
result = det.predict(telemetry)
detector_time = (time.time()-t1)*1000

t2 = time.time()
report = exp.explain(result, telemetry)
llm_time = (time.time()-t2)*1000

print(f"Detector: {detector_time:.2f} ms")
print(f"LLM: {llm_time:.2f} ms")
print(f"Total: {detector_time+llm_time:.2f} ms")

print("\nBenchmark Results")
print(f"Mean latency : {np.mean(latencies):.2f} ms")
print(f"Min latency  : {np.min(latencies):.2f} ms")
print(f"Max latency  : {np.max(latencies):.2f} ms")
print(f"P95 latency  : {np.percentile(latencies,95):.2f} ms")