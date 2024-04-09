import time

from flask import Flask
from flask_cors import CORS

from api.auth import encode_token, token_required
from api.exceptions import exception_handler
from api import response_generator as r
from wakeonlan import send_magic_packet
import platform  # For getting the operating system name
import subprocess  # For executing a shell command
from proxmoxer import ProxmoxAPI

app = Flask(__name__)
cors = CORS(app)

is_online = [False, False, False]


@app.route('/', methods=["GET"])
@exception_handler("index")
def index():
    return r.respond({'hello': 'hello'})


@app.route('/token/admin', methods=["GET"])
@exception_handler("token admin")
def token_admin():
    token = encode_token({'uid': 'admin'})
    return r.respond({"token": token}, cookie=f"Authorization={token}")


@app.route('/token/user', methods=["GET"])
@exception_handler("token admin")
def token_user():
    token = encode_token({'uid': 'user'})
    return r.respond({"token": token}, cookie=f"Authorization={token}")


@app.route('/toggle/<node>', methods=["POST"])
@exception_handler("token admin")
@token_required
def toggle(uid, node):
    if uid == 'admin':
        match int(node):
            case 0:
                if is_online[0]:
                    # Shutdown
                    proxmox = ProxmoxAPI(
                        "192.168.140.17", user="root@pam", password="Mastermind1324!-proxmox.,-", verify_ssl=False
                    )

                    proxmox.nodes('pve').status.post(command='shutdown')
                    while is_online[0]:
                        if not ping('192.168.140.17'):
                            is_online[0] = False
                        else:
                            time.sleep(1)
                else:
                    # Wakeup
                    print('Starting wake on lan...')
                    send_magic_packet('10.7C.61.46.23.C2', ip_address='192.168.140.17')
                    while not is_online[0]:
                        if ping('192.168.140.17'):
                            is_online[0] = True
                        else:
                            time.sleep(1)
                    print('Finished.')

                pass
            case 1:
                # windows start / shutdown
                pass
            case 2:
                # windows start / shutdown
                pass

    return r.respond({"status": "ok"})


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
