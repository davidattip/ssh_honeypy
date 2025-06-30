#!/bin/bash

echo "=== 🚀 HONEYPY AUTO DEPLOY 🚀 ==="

# === CONFIG ===
REPO_URL="https://github.com/davidattip/ssh_honeypy.git"
INSTALL_DIR="/opt/ssh_honeypy"
USERNAME="ubuntu"

echo "[+] Mise à jour et installation des dépendances système..."
sudo apt update
sudo apt install -y python3-venv python3-pip git openssh-client

echo "[+] Clonage/Mise à jour du repo..."
sudo mkdir -p $INSTALL_DIR
sudo chown $USERNAME:$USERNAME $INSTALL_DIR

if [ ! -d "$INSTALL_DIR/.git" ]; then
  git clone $REPO_URL $INSTALL_DIR
else
  cd $INSTALL_DIR && git pull
fi

echo "[+] Création de l'environnement virtuel..."
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Assurer que aiosmtpd est installé pour le honeypot email
pip install aiosmtpd
grep -qxF 'aiosmtpd' requirements.txt || echo 'aiosmtpd' >> requirements.txt

echo "[+] Vérification/création des fichiers de logs..."
mkdir -p $INSTALL_DIR/ssh_honeypy/log_files
touch $INSTALL_DIR/ssh_honeypy/log_files/creds_audits.log
touch $INSTALL_DIR/ssh_honeypy/log_files/cmd_audits.log
touch $INSTALL_DIR/ssh_honeypy/log_files/email_audits.log
touch $INSTALL_DIR/ssh_honeypy/log_files/malware_audits.log

echo "[+] Vérification/génération de la clé RSA pour SSH Honeypot..."
KEY_PATH="$INSTALL_DIR/static/server.key"
mkdir -p $INSTALL_DIR/static

if [ ! -f "$KEY_PATH" ]; then
  echo "[*] Génération de la clé SSH server.key..."
  ssh-keygen -t rsa -b 2048 -f "$KEY_PATH" -N ""
else
  echo "[*] Clé SSH déjà existante : $KEY_PATH"
fi

# === Vérification/Création du fichier .env ===
ENV_FILE="$INSTALL_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "[+] Création du fichier .env par défaut..."
  echo "HONEYPY_HOST=0.0.0.0" > $ENV_FILE
  echo "[*] Modifie $ENV_FILE pour mettre ton IP publique si besoin !"
else
  echo "[*] Fichier .env déjà présent."
fi

echo "[+] Création des services systemd..."

# === SSH Honeypot ===
cat <<EOF | sudo tee /etc/systemd/system/ssh_honeypy.service
[Unit]
Description=SSH Honeypot
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$INSTALL_DIR/venv/bin/python honeypy.py -a \$HONEYPY_HOST -p 2222 --ssh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# === Email Honeypot ===
cat <<EOF | sudo tee /etc/systemd/system/email_honeypy.service
[Unit]
Description=Email Honeypot
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$INSTALL_DIR/venv/bin/python email_honeypot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# === Malware Honeypot ===
cat <<EOF | sudo tee /etc/systemd/system/malware_honeypy.service
[Unit]
Description=Malware Honeypot
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$INSTALL_DIR/venv/bin/python malware_honeypot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# === Dashboard ===
cat <<EOF | sudo tee /etc/systemd/system/honeypy_dashboard.service
[Unit]
Description=HONEYPY Dashboard
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$INSTALL_DIR/venv/bin/python web_app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "[+] Reload systemd..."
sudo systemctl daemon-reload

echo "[+] Activation des services au démarrage..."
sudo systemctl enable ssh_honeypy
sudo systemctl enable email_honeypy
sudo systemctl enable malware_honeypy
sudo systemctl enable honeypy_dashboard

echo "[+] Démarrage des services..."
sudo systemctl restart ssh_honeypy
sudo systemctl restart email_honeypy
sudo systemctl restart malware_honeypy
sudo systemctl restart honeypy_dashboard

echo "✅ DEPLOY TERMINÉ AVEC SUCCÈS !"
echo "➡️ VPS: vps-e67e2d48.vps.ovh.net (193.70.0.151)"
echo "➡️ Services actifs et persistants."

# === Web Honeypot ===
cat <<EOF | sudo tee /etc/systemd/system/web_honeypy.service
[Unit]
Description=Web Honeypot (WordPress Fake Login)
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/venv/bin/python honeypy.py -a \$HONEYPY_HOST -p 5000 --http
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable web_honeypy
sudo systemctl restart web_honeypy

sudo chown -R ubuntu:ubuntu $INSTALL_DIR/ssh_honeypy/log_files
sudo chmod -R 755 $INSTALL_DIR/ssh_honeypy/log_files
