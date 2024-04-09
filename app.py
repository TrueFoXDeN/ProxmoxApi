import time

from flask import Flask
from flask_cors import CORS

from api.auth import encode_token, token_required
from api.exceptions import exception_handler
from api import response_generator as r
from wakeonlan import send_magic_packet
from proxmoxer import ProxmoxAPI

from util.ping import ping

app = Flask(__name__)
cors = CORS(app)

is_online = [False, False, False]
is_online[0] = ping('192.168.140.17')
print(f'Server is online: {is_online[0]}')
is_online[1] = ping('192.168.140.12')
print(f'Windows VM is online: {is_online[1]}')
is_online[2] = ping('192.168.140.11')
print(f'Linux VM is online: {is_online[2]}')


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


@app.route('/status', methods=["GET"])
@exception_handler("status")
@token_required
def status(uid):
    is_online[0] = ping('192.168.140.17')
    is_online[1] = ping('192.168.140.12')
    is_online[2] = ping('192.168.140.11')
    return r.respond({"status": is_online})


@app.route('/toggle/<node>', methods=["POST"])
@exception_handler("toggle node")
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
                    return r.respond({"status": "server shutdown complete"})
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

                    return r.respond({"status": "server wakeup complete"})

            case 1:
                # windows start / shutdown
                proxmox = ProxmoxAPI(
                    "192.168.140.17", user="root@pam", password="Mastermind1324!-proxmox.,-", verify_ssl=False
                )

                if is_online[1]:
                    proxmox.nodes('pve').qemu('101').status.shutdown.post()
                    while is_online[1]:
                        if ping('192.168.140.12'):
                            is_online[1] = False
                        else:
                            time.sleep(1)
                    return r.respond({"status": "windows vm shutdown complete"})
                else:
                    proxmox.nodes('pve').qemu('101').status.start.post()
                    while not is_online[1]:
                        if ping('192.168.140.12'):
                            is_online[1] = True
                        else:
                            time.sleep(1)
                    return r.respond({"status": "windows vm wakeup complete"})
            case 2:
                # linux start / shutdown
                proxmox = ProxmoxAPI(
                    "192.168.140.17", user="root@pam", password="Mastermind1324!-proxmox.,-", verify_ssl=False
                )

                if is_online[2]:
                    proxmox.nodes('pve').qemu('100').status.shutdown.post()
                    while is_online[2]:
                        if ping('192.168.140.11'):
                            is_online[2] = False
                        else:
                            time.sleep(1)
                    return r.respond({"status": "linux vm shutdown complete"})
                else:
                    proxmox.nodes('pve').qemu('100').status.start.post()
                    while not is_online[2]:
                        if ping('192.168.140.11'):
                            is_online[2] = True
                        else:
                            time.sleep(1)
                    return r.respond({"status": "linux vm wakeup complete"})

    return r.respond({"status": f"no valid node found for id={node}"}, status=400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
