#!/bin/bash

echo "=== 🧹 HONEYPY CLEANUP SCRIPT 🧹 ==="

INSTALL_DIR="/opt/ssh_honeypy"

echo "[+] Arrêt des services..."
sudo systemctl stop ssh_honeypy
sudo systemctl stop email_honeypy
sudo systemctl stop malware_honeypy
sudo systemctl stop honeypy_dashboard
sudo systemctl stop web_honeypy

echo "[+] Désactivation des services..."
sudo systemctl disable ssh_honeypy
sudo systemctl disable email_honeypy
sudo systemctl disable malware_honeypy
sudo systemctl disable honeypy_dashboard
sudo systemctl disable web_honeypy

echo "[+] Suppression des fichiers systemd..."
sudo rm -f /etc/systemd/system/ssh_honeypy.service
sudo rm -f /etc/systemd/system/email_honeypy.service
sudo rm -f /etc/systemd/system/malware_honeypy.service
sudo rm -f /etc/systemd/system/honeypy_dashboard.service
sudo rm -f /etc/systemd/system/web_honeypy.service

echo "[+] Nettoyage systemd..."
sudo systemctl daemon-reload

echo "[+] Suppression du répertoire Honeypy..."
sudo rm -rf $INSTALL_DIR

echo "✅ TOUT A ÉTÉ SUPPRIMÉ !"

echo "[+] Suppression du script deploy.sh et remove.sh..."
rm -f ~/deploy.sh
rm -f ~/remove.sh
