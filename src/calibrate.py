# ─────────────────────────────────────────
# Calibration : génère des features
# dans le même format que monitor.py
# ─────────────────────────────────────────

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

np.random.seed(42)
N = 500  # flux par classe

def faire_flux(n, proto, fwd_pps, bwd_pps,
               fwd_size, bwd_size, duree, label):
    rows = []
    for _ in range(n):
        d  = np.random.uniform(*duree)
        fp = np.random.uniform(*fwd_pps)
        bp = np.random.uniform(*bwd_pps)
        fs = np.random.uniform(*fwd_size)
        bs = np.random.uniform(*bwd_size)
        tf = int(fp * d)
        tb = int(bp * d)
        iat = (1 / max(fp + bp, 0.001)) * 1e6
        rows.append([
            np.random.choice(proto),  # protocol
            d * 1e6,                  # flow_duration (µs)
            tf,                       # total_forward_packets
            tb,                       # total_backward_packets
            tf * fs,                  # total_forward_packets_length
            tb * bs,                  # total_backward_packets_length
            fs,                       # forward_packet_length_mean
            bs,                       # backward_packet_length_mean
            fp,                       # forward_packets_per_second
            bp,                       # backward_packets_per_second
            iat,                      # forward_iat_mean
            iat,                      # backward_iat_mean
            iat,                      # flow_iat_mean
            fp + bp,                  # flow_packets_per_seconds
            (tf*fs + tb*bs) / max(d, 0.001),  # flow_bytes_per_seconds
            label
        ])
    return rows

colonnes = [
    'protocol','flow_duration','total_forward_packets',
    'total_backward_packets','total_forward_packets_length',
    'total_backward_packets_length','forward_packet_length_mean',
    'backward_packet_length_mean','forward_packets_per_second',
    'backward_packets_per_second','forward_iat_mean',
    'backward_iat_mean','flow_iat_mean',
    'flow_packets_per_seconds','flow_bytes_per_seconds','label'
]

# ── Génération des flux ───────────────────
print("Génération des flux d'entraînement...")

normal = faire_flux(N, [6,17],
    fwd_pps=(0.5,10), bwd_pps=(0.5,10),
    fwd_size=(50,500), bwd_size=(50,800),
    duree=(0.1,5), label=0)

syn = faire_flux(N, [6],
    fwd_pps=(200,2000), bwd_pps=(0,2),
    fwd_size=(40,60), bwd_size=(0,10),
    duree=(0.001,0.05), label=1)

udp = faire_flux(N, [17],
    fwd_pps=(500,5000), bwd_pps=(500,5000),
    fwd_size=(40,70), bwd_size=(40,70),
    duree=(0.001,0.01), label=1)

http = faire_flux(N, [6],
    fwd_pps=(100,500), bwd_pps=(100,500),
    fwd_size=(200,600), bwd_size=(400,1200),
    duree=(0.005,0.05), label=1)

df = pd.DataFrame(normal + syn + udp + http, columns=colonnes)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Total flux : {len(df)}")
print(df['label'].value_counts())

# ── Entraînement ──────────────────────────
X = df.drop(columns=['label'])
y = df['label']
X = X.replace([np.inf, -np.inf], np.nan)
X = X.fillna(X.median())

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

modele = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
modele.fit(X_train_sc, y_train)

y_pred = modele.predict(X_test_sc)
print(f"\nAccuracy : {accuracy_score(y_test, y_pred)*100:.2f}%")
print(classification_report(y_test, y_pred,
      target_names=["BENIGN", "ATTAQUE"]))

# ── Sauvegarde ────────────────────────────
joblib.dump(modele, "../models/random_forest.pkl")
joblib.dump(scaler, "../models/scaler.pkl")
print("✅ Modèle recalibré et sauvegardé !")
