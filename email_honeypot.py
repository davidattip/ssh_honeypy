# Import libraries
import asyncio
import os
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

# === Load environment variables ===
base_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=base_dir / '.env')
HONEYPY_HOST = os.getenv('HONEYPY_HOST', '127.0.0.1')  # fallback localhost

# === Logging configuration ===
log_file = base_dir / 'ssh_honeypy' / 'log_files' / 'email_audits.log'

logger = logging.getLogger('EmailHoneypot')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=2000, backupCount=5)
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# === Honeypot SMTP Handler ===
class HoneypotHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        client_ip = session.peer[0]
        mail_from = envelope.mail_from
        rcpt_tos = ', '.join(envelope.rcpt_tos)
        data = envelope.content.decode('utf8', errors='replace')

        log_entry = (
            f"=== New Email ===\n"
            f"IP: {client_ip}\n"
            f"MAIL FROM: {mail_from}\n"
            f"RCPT TO: {rcpt_tos}\n"
            f"DATA:\n{data}\n"
            f"=================\n"
        )

        logger.info(log_entry)

        return '250 Message accepted for delivery'

# === Main function ===
if __name__ == "__main__":
    handler = HoneypotHandler()
    controller = Controller(handler, hostname=HONEYPY_HOST, port=2525)
    print(f"[+] Email honeypot running on {HONEYPY_HOST}:2525 ...")
    controller.start()

    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
