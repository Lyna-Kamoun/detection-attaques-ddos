import warnings
warnings.filterwarnings("ignore")

from scapy.all import *
import numpy as np
import joblib
import time
import threading
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from datetime import datetime

modele = joblib.load("../models/random_forest.pkl")
scaler = joblib.load("../models/scaler.pkl")

console = Console()

etat = {
    "statut":        "EN ATTENTE",
    "confiance":     0.0,
    "paquets":       0,
    "total_paquets": 0,
    "alertes":       0,
    "historique":    [],
    "derniere_maj":  datetime.now().strftime("%H:%M:%S"),
}

paquets_fenetre = []
debut_fenetre   = time.time()
FENETRE         = 2

def extraire_features(paquets):
    if len(paquets) == 0:
        return None
    total_fwd     = sum(1 for p in paquets if p['direction'] == 'fwd')
    total_bwd     = sum(1 for p in paquets if p['direction'] == 'bwd')
    total_fwd_len = sum(p['size'] for p in paquets if p['direction'] == 'fwd')
    total_bwd_len = sum(p['size'] for p in paquets if p['direction'] == 'bwd')
    duree         = max(time.time() - debut_fenetre, 0.001)
    fwd_pps       = total_fwd / duree
    bwd_pps       = total_bwd / duree
    tailles_fwd   = [p['size'] for p in paquets if p['direction'] == 'fwd']
    tailles_bwd   = [p['size'] for p in paquets if p['direction'] == 'bwd']
    fwd_mean      = np.mean(tailles_fwd) if tailles_fwd else 0
    bwd_mean      = np.mean(tailles_bwd) if tailles_bwd else 0
    protocoles    = [p['proto'] for p in paquets]
    proto         = max(set(protocoles), key=protocoles.count) if protocoles else 6
    temps         = [p['time'] for p in paquets]
    iats          = [temps[i+1]-temps[i] for i in range(len(temps)-1)]
    iat_mean      = np.mean(iats)*1e6 if iats else 0
    return [[
        proto, duree*1e6, total_fwd, total_bwd,
        total_fwd_len, total_bwd_len, fwd_mean, bwd_mean,
        fwd_pps, bwd_pps, iat_mean, iat_mean, iat_mean,
        (total_fwd+total_bwd)/duree,
        (total_fwd_len+total_bwd_len)/max(duree,0.001),
    ]]

def faire_dashboard():
    if etat["statut"] == "ATTAQUE DÉTECTÉE":
        couleur = "red"
        icone   = "🔴"
        barre   = "█" * int(etat["confiance"] / 5)
    elif etat["statut"] == "TRAFIC NORMAL":
        couleur = "green"
        icone   = "🟢"
        barre   = "█" * 10
    else:
        couleur = "yellow"
        icone   = "🟡"
        barre   = "░" * 10

    statut_panel = Panel(
        f"[bold {couleur}]{icone}  {etat['statut']}[/bold {couleur}]\n\n"
        f"[white]Confiance    :[/white] [{couleur}]{etat['confiance']:.1f}%[/{couleur}]\n"
        f"[white]Progression  :[/white] [{couleur}]{barre}[/{couleur}]\n"
        f"[white]Paquets/fen. :[/white] {etat['paquets']}\n"
        f"[white]Mise à jour  :[/white] {etat['derniere_maj']}",
        title="[bold]STATUT EN TEMPS RÉEL[/bold]",
        style=couleur,
        box=box.ROUNDED
    )

    stats_panel = Panel(
        f"[white]Total paquets :[/white] [cyan]{etat['total_paquets']}[/cyan]\n"
        f"[white]Total alertes :[/white] [red]{etat['alertes']}[/red]\n"
        f"[white]Fenêtre       :[/white] [cyan]{FENETRE}s[/cyan]\n"
        f"[white]Modèle        :[/white] [cyan]Random Forest[/cyan]\n"
        f"[white]Interface     :[/white] [cyan]lo (loopback)[/cyan]",
        title="[bold]STATISTIQUES[/bold]",
        style="blue",
        box=box.ROUNDED
    )

    table = Table(
        title="HISTORIQUE DES ATTAQUES DÉTECTÉES",
        box=box.SIMPLE,
        style="white",
        show_lines=True
    )
    table.add_column("Heure",     style="cyan",  width=10)
    table.add_column("Statut",    style="white", width=22)
    table.add_column("Confiance", style="white", width=12)
    table.add_column("Paquets",   style="white", width=10)

    if len(etat["historique"]) == 0:
        table.add_row(
            "--:--:--",
            "[dim]Aucune attaque détectée[/dim]",
            "--",
            "--"
        )
    else:
        for ligne in etat["historique"][-8:]:
            table.add_row(
                ligne[0],
                f"[red]{ligne[1]}[/red]",
                f"[red]{ligne[2]}[/red]",
                ligne[3]
            )

    return Panel(
        Columns([statut_panel, stats_panel]),
        title="[bold white] SYSTÈME DE DÉTECTION D'ATTAQUES DDoS PAR IA — Cybersécurité & Cryptographie[/bold white]",
        box=box.DOUBLE,
        style="blue"
    ), Panel(table, box=box.ROUNDED, style="blue")

def analyser_fenetre():
    global paquets_fenetre, debut_fenetre

    nb = len(paquets_fenetre)
    etat["total_paquets"] += nb
    etat["paquets"]        = nb
    etat["derniere_maj"]   = datetime.now().strftime("%H:%M:%S")

    if nb < 5:
        etat["statut"]    = "EN ATTENTE"
        etat["confiance"] = 0.0
        paquets_fenetre   = []
        debut_fenetre     = time.time()
        return

    features = extraire_features(paquets_fenetre)
    if features is None:
        return

    features_sc = scaler.transform(features)
    prediction  = modele.predict(features_sc)[0]
    proba       = modele.predict_proba(features_sc)[0][1] * 100

    if prediction == 1:
        etat["statut"]    = "ATTAQUE DÉTECTÉE"
        etat["confiance"] = proba
        etat["alertes"]  += 1
        etat["historique"].append([
            etat["derniere_maj"],
            "🔴 ATTAQUE DÉTECTÉE",
            f"{proba:.1f}%",
            str(nb)
        ])
    else:
        etat["statut"]    = "TRAFIC NORMAL"
        etat["confiance"] = 100 - proba

    paquets_fenetre = []
    debut_fenetre   = time.time()

def traiter_paquet(paquet):
    global paquets_fenetre, debut_fenetre
    if IP in paquet:
        paquets_fenetre.append({
            'direction': 'fwd' if paquet[IP].src == '127.0.0.1' else 'bwd',
            'size':      len(paquet),
            'proto':     paquet[IP].proto,
            'time':      time.time(),
        })
    if time.time() - debut_fenetre >= FENETRE:
        analyser_fenetre()

def lancer_capture():
    sniff(iface="lo", prn=traiter_paquet, store=False)

thread = threading.Thread(target=lancer_capture, daemon=True)
thread.start()

console.clear()
try:
    with Live(console=console, refresh_per_second=2) as live:
        while True:
            top, bottom = faire_dashboard()
            from rich.console import Group
            live.update(Group(top, bottom))
            time.sleep(0.5)
except KeyboardInterrupt:
    console.print("\n[bold red]🛑 Moniteur arrêté.[/bold red]")
