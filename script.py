import os
import time
import socket
from flask import Flask, jsonify
from cachetools import TTLCache
from mcstatus import MinecraftServer

app = Flask(__name__)

MOTD_CACHE_DURATION = int(os.getenv("MOTD_CACHE_DURATION", 60))
MOTD_SERVER_HOST = os.getenv("MOTD_SERVER_HOST", "172.17.0.1")
MOTD_SERVER_PORT = int(os.getenv("MOTD_SERVER_PORT", 25589))

cache = TTLCache(maxsize=1, ttl=MOTD_CACHE_DURATION)
server_status = "up"

def check_server_status():
    global server_status
    try:
        server = MinecraftServer(MOTD_SERVER_HOST, MOTD_SERVER_PORT)
        server.status()
        server_status = "up"
    except Exception:
        server_status = "down"

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
    except Exception:
        return "Minecraft server is down"

def parse_motd(response):
    return response[3:].decode('utf-8', errors='ignore').split('\x00')[0]

@app.route("/motd", methods=["GET"])
def motd():
    check_server_status()
    return jsonify({"motd": get_motd(), "status": server_status})

def main():
    app.run(host=MOTD_SERVER_HOST, port=MOTD_SERVER_PORT)

if __name__ == "__main__":
    main()
