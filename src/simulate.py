import numpy as np
import pandas as pd

np.random.seed(42)

def simuler_trafic_normal(n=200):
    return pd.DataFrame({
        'protocol':                       np.random.choice([6, 17], n),
        'flow_duration':                  np.random.randint(100000, 5000000, n),
        'total_forward_packets':          np.random.randint(2, 20, n),
        'total_backward_packets':         np.random.randint(2, 20, n),
        'total_forward_packets_length':   np.random.randint(200, 5000, n),
        'total_backward_packets_length':  np.random.randint(200, 8000, n),
        'forward_packet_length_mean':     np.random.uniform(50, 500, n),
        'backward_packet_length_mean':    np.random.uniform(50, 800, n),
        'forward_packets_per_second':     np.random.uniform(0.5, 10, n),
        'backward_packets_per_second':    np.random.uniform(0.5, 10, n),
        'forward_iat_mean':               np.random.uniform(10000, 500000, n),
        'backward_iat_mean':              np.random.uniform(10000, 500000, n),
        'flow_iat_mean':                  np.random.uniform(10000, 500000, n),
        'flow_packets_per_seconds':       np.random.uniform(1, 20, n),
        'flow_bytes_per_seconds':         np.random.uniform(100, 5000, n),
        'label':                          'BENIGN'
    })

def simuler_syn_flood(n=200):
    return pd.DataFrame({
        'protocol':                       np.full(n, 6),
        'flow_duration':                  np.random.randint(100, 5000, n),
        'total_forward_packets':          np.random.randint(500, 2000, n),
        'total_backward_packets':         np.random.randint(0, 3, n),
        'total_forward_packets_length':   np.random.randint(20000, 80000, n),
        'total_backward_packets_length':  np.random.randint(0, 100, n),
        'forward_packet_length_mean':     np.random.uniform(40, 60, n),
        'backward_packet_length_mean':    np.random.uniform(0, 10, n),
        'forward_packets_per_second':     np.random.uniform(500, 2000, n),
        'backward_packets_per_second':    np.random.uniform(0, 2, n),
        'forward_iat_mean':               np.random.uniform(100, 1000, n),
        'backward_iat_mean':              np.random.uniform(0, 100, n),
        'flow_iat_mean':                  np.random.uniform(100, 1000, n),
        'flow_packets_per_seconds':       np.random.uniform(500, 2000, n),
        'flow_bytes_per_seconds':         np.random.uniform(20000, 80000, n),
        'label':                          'SYN_Flood'
    })

def simuler_udp_flood(n=200):
    return pd.DataFrame({
        'protocol':                       np.full(n, 17),
        'flow_duration':                  np.random.randint(1000, 10000, n),
        'total_forward_packets':          np.random.randint(1000, 5000, n),
        'total_backward_packets':         np.random.randint(1000, 5000, n),
        'total_forward_packets_length':   np.random.randint(50000, 200000, n),
        'total_backward_packets_length':  np.random.randint(50000, 200000, n),
        'forward_packet_length_mean':     np.random.uniform(40, 70, n),
        'backward_packet_length_mean':    np.random.uniform(40, 70, n),
        'forward_packets_per_second':     np.random.uniform(1000, 5000, n),
        'backward_packets_per_second':    np.random.uniform(1000, 5000, n),
        'forward_iat_mean':               np.random.uniform(50, 500, n),
        'backward_iat_mean':              np.random.uniform(50, 500, n),
        'flow_iat_mean':                  np.random.uniform(50, 500, n),
        'flow_packets_per_seconds':       np.random.uniform(2000, 10000, n),
        'flow_bytes_per_seconds':         np.random.uniform(100000, 400000, n),
        'label':                          'UDP_Flood'
    })

def simuler_http_flood(n=200):
    return pd.DataFrame({
        'protocol':                       np.full(n, 6),
        'flow_duration':                  np.random.randint(5000, 50000, n),
        'total_forward_packets':          np.random.randint(200, 800, n),
        'total_backward_packets':         np.random.randint(200, 800, n),
        'total_forward_packets_length':   np.random.randint(20000, 100000, n),
        'total_backward_packets_length':  np.random.randint(50000, 300000, n),
        'forward_packet_length_mean':     np.random.uniform(200, 600, n),
        'backward_packet_length_mean':    np.random.uniform(400, 1200, n),
        'forward_packets_per_second':     np.random.uniform(100, 500, n),
        'backward_packets_per_second':    np.random.uniform(100, 500, n),
        'forward_iat_mean':               np.random.uniform(500, 5000, n),
        'backward_iat_mean':              np.random.uniform(500, 5000, n),
        'flow_iat_mean':                  np.random.uniform(500, 5000, n),
        'flow_packets_per_seconds':       np.random.uniform(200, 1000, n),
        'flow_bytes_per_seconds':         np.random.uniform(10000, 100000, n),
        'label':                          'HTTP_Flood'
    })

normal = simuler_trafic_normal(200)
syn    = simuler_syn_flood(200)
udp    = simuler_udp_flood(200)
http   = simuler_http_flood(200)

simulation = pd.concat([normal, syn, udp, http], ignore_index=True)
simulation = simulation.sample(frac=1, random_state=42)
simulation.to_csv("../data/trafic_simule.csv", index=False)

print(f"✅ Dataset simulé : {len(simulation)} flux")
print(simulation['label'].value_counts())
