# src/telemetry.py
import time
import random
import json
import numpy as np

try:
    import redis
    _r = redis.Redis(host='172.22.159.198', port=6379, decode_responses=True)
    _r.ping()
    REDIS_AVAILABLE = True
    print('[telemetry] Connected to Redis — live engine data available')
except Exception:
    REDIS_AVAILABLE = False
    print('[telemetry] Redis not found — using simulated data')


def get_live_telemetry() -> dict:
    if not REDIS_AVAILABLE:
        raise RuntimeError("Redis is not available")

    switch = 'g0_s0'
    raw = _r.get(f'telemetry:{switch}')

    if raw:
        data = json.loads(raw)

        print(
            f"[REDIS READ] switch={switch} "
            f"pps={data.get('pps')} "
            f"timestamp={data.get('timestamp')}"
        )

        return data

    raise RuntimeError(
        f"No live Redis telemetry for {switch}"
    )


def _simulated() -> dict:
    return {
        'flow_duration':  round(random.uniform(0.01, 10.0), 3),
        'fwd_pkt_count':  random.randint(1, 5000),
        'bwd_pkt_count':  random.randint(0, 2000),
        'mean_pkt_size':  round(random.uniform(40, 1500), 1),
        'iat_mean':       round(random.uniform(0.0001, 2.0), 5),
        'pps':            round(random.uniform(1, 10000), 2),
        'flood_score':    round(random.uniform(0, 1), 3),
        'mac_fill':       round(random.uniform(0, 1), 3),
        'new_mac_rate':   round(random.uniform(0, 50), 2),
        'syn_count':      random.randint(0, 500),
        'switch_id':      random.choice(['g0s0','g0s1','g1s0',
                                         'g1s1','g2s0','g2s1']),
        'timestamp':      time.time(),
    }


def simulate_attack(attack_type='ddos') -> dict:
    base = get_live_telemetry()

    if attack_type == 'ddos':
        base.update({
            'pps':           float(np.random.uniform(5000, 10000)),
            'fwd_pkt_count': int(np.random.randint(3000, 6000)),
            'bwd_pkt_count': int(np.random.randint(0, 100)),
            'mean_pkt_size': float(np.random.uniform(40, 100)),
            'iat_mean':      float(np.random.uniform(0.00001, 0.001)),
            'flood_score':   float(np.random.uniform(0.7, 1.0)),
            'mac_fill':      float(np.random.uniform(0.3, 0.8)),
            'new_mac_rate':  float(np.random.uniform(5, 30)),
            'syn_count':     int(np.random.randint(0, 100)),
        })
    elif attack_type == 'portscan':
        base.update({
            'flow_duration': float(np.random.uniform(0.001, 0.05)),
            'fwd_pkt_count': int(np.random.randint(1, 10)),
            'mean_pkt_size': float(np.random.uniform(40, 80)),
            'iat_mean':      float(np.random.uniform(0.0001, 0.01)),
            'pps':           float(np.random.uniform(100, 1000)),
            'flood_score':   float(np.random.uniform(0.1, 0.4)),
            'syn_count':     int(np.random.randint(300, 500)),
        })
    elif attack_type == 'camoverflow':
        base.update({
            'mac_fill':      float(np.random.uniform(0.85, 1.0)),
            'new_mac_rate':  float(np.random.uniform(30, 50)),
            'flood_score':   float(np.random.uniform(0.7, 0.95)),
            'pps':           float(np.random.uniform(2000, 6000)),
        })
    elif attack_type == 'dos':
        base.update({
            'pps':           float(np.random.uniform(1000, 5000)),
            'fwd_pkt_count': int(np.random.randint(500, 3000)),
            'iat_mean':      float(np.random.uniform(0.0001, 0.01)),
            'flood_score':   float(np.random.uniform(0.4, 0.8)),
            'syn_count':     int(np.random.randint(100, 500)),
        })

    return base