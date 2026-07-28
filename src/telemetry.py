import time, random
 
# When we will  have live Mininet running, we replace the random values
# below with real values pulled from  engine.py
 
def get_live_telemetry():
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

#updating the attack specific features 
def simulate_attack(attack_type='ddos'):
    base = get_live_telemetry()
    if attack_type == 'ddos':
        base.update({'pps':9800,'fwd_pkt_count':4900,
                     'iat_mean':0.00005,'flood_score':0.92,
                     'mean_pkt_size':60})
    elif attack_type == 'portscan':
        base.update({'flow_duration':0.002,'fwd_pkt_count':2,
                     'mean_pkt_size':44,'syn_count':450})
    elif attack_type == 'camoverflow':
        base.update({'mac_fill':0.97,'new_mac_rate':48,
                     'flood_score':0.85})
    return base


