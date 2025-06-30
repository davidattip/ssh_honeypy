#!/bin/bash

echo "=== 🚀 HONEYPY AUTO DEPLOY 🚀 ==="

# === CONFIG ===
REPO_URL="https://github.com/davidattip/ssh_honeypy.git"
INSTALL_DIR="/opt/honeypy"
USERNAME="ubuntu"

echo "[+] Mise à jour et installation des dépendances système..."
sudo apt update
sudo apt install -y python3-venv python3-pip git

echo "[+] Clonage du repo..."
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

echo "[+] Vérification/création des fichiers de logs..."
mkdir -p $INSTALL_DIR/ssh_honeypy/log_files
touch $INSTALL_DIR/ssh_honeypy/log_files/creds_audits.log
touch $INSTALL_DIR/ssh_honeypy/log_files/cmd_audits.log
touch $INSTALL_DIR/ssh_honeypy/log_files/email_audits.log
touch $INSTALL_DIR/ssh_honeypy/log_files/malware_audits.log

echo "[+] Création des services systemd..."

# === SSH Honeypot ===
cat <<EOF | sudo tee /etc/systemd/system/ssh_honeypy.service
[Unit]
Description=SSH Honeypot
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python honeypy.py -a 0.0.0.0 -p 2222 --ssh
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
