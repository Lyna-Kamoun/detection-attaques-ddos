# ─────────────────────────────────────────
# Détection d'attaques DDoS par IA
# Entraînement sur trafic simulé
# ─────────────────────────────────────────

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# ── Chargement du trafic simulé ───────────
df = pd.read_csv("../data/trafic_simule.csv")
print(f"Dataset simulé chargé : {len(df)} flux")
print(df['label'].value_counts())

# ── Encodage : BENIGN=0, tout le reste=1 ──
df['label_encode'] = df['label'].apply(lambda x: 0 if x == 'BENIGN' else 1)

# ── Features / cible ──────────────────────
X = df.drop(columns=['label', 'label_encode'])
y = df['label_encode']

X = X.replace([np.inf, -np.inf], np.nan)
X = X.fillna(X.median())

# ── Split 80/20 ───────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Normalisation ─────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ── Entraînement ──────────────────────────
print("\nEntraînement en cours...")
modele = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
modele.fit(X_train_sc, y_train)
print("✅ Modèle entraîné !")

# ── Évaluation ────────────────────────────
y_pred = modele.predict(X_test_sc)

print(f"\n── Accuracy : {accuracy_score(y_test, y_pred)*100:.2f}%")
print("\n── Rapport de classification ──────────")
print(classification_report(y_test, y_pred, target_names=["BENIGN", "ATTAQUE"]))

# ── Matrice de confusion ──────────────────
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=["BENIGN", "ATTAQUE"],
            yticklabels=["BENIGN", "ATTAQUE"])
plt.title("Matrice de confusion — Trafic simulé")
plt.xlabel("Prédit")
plt.ylabel("Réel")
plt.tight_layout()
plt.savefig("../data/matrice_confusion.png")
plt.show()

# ── Feature importance ────────────────────
importances = pd.Series(
    modele.feature_importances_, index=X.columns
).sort_values(ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(x=importances.values, y=importances.index, palette="viridis",
            hue=importances.index, legend=False)
plt.title("Importance des features")
plt.xlabel("Score d'importance")
plt.tight_layout()
plt.savefig("../data/feature_importance.png")
plt.show()

# ── Sauvegarde du modèle ──────────────────
joblib.dump(modele, "../models/random_forest.pkl")
joblib.dump(scaler, "../models/scaler.pkl")
print("\n✅ Modèle sauvegardé dans models/")