import time, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from telemetry import get_live_telemetry, simulate_attack
from detector  import AnomalyDetector
from explainer import IncidentExplainer
 
POLL_INTERVAL  = 2   # seconds between reads
ALERT_COOLDOWN = 30  # seconds before same switch can re-alert
 
def run_pipeline(test_mode=False):
    detector  = AnomalyDetector()
    explainer = IncidentExplainer()
    last_alert = {}
    alerts     = []
    tick       = 0
    print('Pipeline running. Ctrl+C to stop.')
 
    while True:
        # 1. Get telemetry (or inject test attack)
        if test_mode and tick % 15 == 5:
            import random
            attack    = random.choice(['ddos','portscan','camoverflow'])
            telemetry = simulate_attack(attack)
            print(f'[TEST] Injecting {attack}')
        else:
            telemetry = get_live_telemetry()
 
        # 2. Detect
        result = detector.predict(telemetry)
 
        # 3. Check cooldown and fire alert
        switch     = result['switch_id']
        now        = time.time()
        in_cooldown = (switch in last_alert and
                       now - last_alert[switch] < ALERT_COOLDOWN)
 
        if result['is_alert'] and not in_cooldown:
            print(f'[ALERT] {result["label"]} on {switch}')
 
            # 4. RAG + LLM explanation
            report = explainer.explain(result, telemetry)
            print('[REPORT]', report[:200], '...')
 
            alerts.append({**result,'telemetry':telemetry,'report':report})
            last_alert[switch] = now
 
        tick += 1
        time.sleep(POLL_INTERVAL)
 
if __name__ == '__main__':
    run_pipeline(test_mode=True)
