import socket
import os
import time
import json
from cachetools import TTLCache

MOTD_CACHE_DURATION = int(os.getenv("MOTD_CACHE_DURATION", 60))
MOTD_SERVER_HOST = os.getenv("MOTD_SERVER_HOST", "172.17.0.1")
MOTD_SERVER_PORT = int(os.getenv("MOTD_SERVER_PORT", 25589))

cache = TTLCache(maxsize=1, ttl=MOTD_CACHE_DURATION)

def get_motd():
    if 'motd' in cache:
        return cache['motd']
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((MOTD_SERVER_HOST, MOTD_SERVER_PORT))
            s.send(b"\xFE\x01")
            response = s.recv(1024)
            motd = parse_motd(response)
            cache['motd'] = motd
            return motd
    except Exception as e:
        return "Error retrieving MOTD"

def parse_motd(response):
    motd = response[3:].decode('utf-8', errors='ignore')
    return motd.split('\x00')[0]

if __name__ == "__main__":
    while True:
        motd = get_motd()
        print(f"Current MOTD: {motd}")
        time.sleep(MOTD_CACHE_DURATION)
