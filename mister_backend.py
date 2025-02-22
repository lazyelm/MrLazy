from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import paramiko
import threading
import time

from flask_cors import CORS

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Enable CORS
CORS(app)

MISTER_IP = "192.168.7.222"
MISTER_USER = "root"
MISTER_PASS = "1"

def ssh_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(MISTER_IP, username=MISTER_USER, password=MISTER_PASS)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    ssh.close()
    return output

@app.route("/consoles")
def list_consoles():
    output = ssh_command("ls /media/fat/_Console | grep .rbf")
    cores = [c.strip() for c in output.split("\n") if c]
    
    # Debugging line to check the output
    print(f"Consoles: {cores}")  # Log consoles for debugging

    return jsonify(cores)

@app.route("/games/<console>")
def list_games(console):
    output = ssh_command(f"ls /media/fat/games/{console}")
    games = [g.strip() for g in output.split("\n") if g]
    
    # Debugging line to check the output
    print(f"Games for {console}: {games}")  # Log games for debugging

    return jsonify(games)

@app.route("/launch", methods=["POST"])
def launch_game():
    data = request.json
    core = data["core"]
    game = data["game"]
    command = f"/media/fat/Scripts/mister -core /media/fat/_Console/{core}.rbf -rom /media/fat/games/{core}/{game}"
    ssh_command(command)
    socketio.emit("status", {"running": True, "core": core, "game": game})
    return jsonify({"status": "Game Launched"})

@app.route("/terminate")
def terminate_game():
    ssh_command("killall MiSTer")
    socketio.emit("status", {"running": False})
    return jsonify({"status": "Game Terminated"})

def check_status():
    """Background thread to monitor MiSTer status."""
    last_status = None
    while True:
        output = ssh_command("ps aux | grep MiSTer | grep -v grep")
        is_running = bool(output.strip())
        if is_running != last_status:
            socketio.emit("status", {"running": is_running})
            last_status = is_running
        time.sleep(5)

# Start monitoring thread
threading.Thread(target=check_status, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=2121)
