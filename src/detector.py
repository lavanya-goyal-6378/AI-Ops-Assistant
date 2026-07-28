
import joblib
import pandas as pd
 
FEATURE_COLS = [
    'flow_duration','fwd_pkt_count','bwd_pkt_count',
    'mean_pkt_size','iat_mean','pps',
    'flood_score','mac_fill','new_mac_rate','syn_count'
]
 
ALERT_THRESHOLD = 0.6   
 
class AnomalyDetector:
    def __init__(self):
        self.model = joblib.load('models/rf_model.pkl')
        self.le    = joblib.load('models/label_encoder.pkl')
        print('Model loaded:', self.model.__class__.__name__)
 
    def predict(self, telemetry: dict) -> dict:
        row = pd.DataFrame(
            [[telemetry[f] for f in FEATURE_COLS]],
            columns=FEATURE_COLS
        )
        label_id   = self.model.predict(row)[0]
        proba      = self.model.predict_proba(row)[0]
        confidence = round(float(proba.max()), 4)
        label      = self.le.inverse_transform([label_id])[0]
 
        return {
            'label':      label,
            'confidence': confidence,
            'is_alert':   label != 'BENIGN' and confidence > ALERT_THRESHOLD,
            'switch_id':  telemetry.get('switch_id', 'unknown'),
            'timestamp':  telemetry.get('timestamp'),
        }
 
if __name__ == '__main__':
    from telemetry import simulate_attack
    d = AnomalyDetector()

    for t in ['ddos','portscan','camoverflow']:
        print(t, '->', d.predict(simulate_attack(t)))