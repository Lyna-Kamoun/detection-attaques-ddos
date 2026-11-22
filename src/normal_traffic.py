import socket
import time
import random

print("🟢 Génération de trafic normal...")

while True:
    try:
        # Simule des requêtes HTTP normales vers localhost
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(("127.0.0.1", 80))
        s.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        s.close()
    except:
        pass

    try:
        # Simule du trafic UDP normal
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(b"ping", ("127.0.0.1", random.randint(8000, 9000)))
        s.close()
    except:
        pass

    time.sleep(0.3)  # rythme lent = trafic normal

