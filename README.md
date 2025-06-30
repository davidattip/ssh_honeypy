# 🐝 Honeypy – Multi-Honeypot Suite

Bienvenue sur **Honeypy**, une suite complète de faux services (honeypots) pour tromper, enregistrer et analyser les comportements des attaquants sur un serveur VPS.

---

## 📦 Composants inclus

- **SSH Honeypot** : Faux serveur SSH (port `2222`).
- **Email Honeypot** : Faux serveur SMTP (port `2525`).
- **Malware Honeypot** : Faux portail d’upload de fichiers (port `8080`).
- **Web Honeypot** : Fausse page WordPress login (port `5000`).
- **Dashboard** : Tableau de bord de visualisation interactive (port `8050`).

---

## 📂 Arborescence

```plaintext
/opt/ssh_honeypy/
│
├── honeypy.py
├── ssh_honeypot.py
├── email_honeypot.py
├── malware_honeypot.py
├── web_honeypot.py
├── web_app.py
├── dashboard_data_parser.py
├── requirements.txt
├── .env
├── deploy.sh
├── remove.sh
└── log_files/
    ├── creds_audits.log
    ├── cmd_audits.log
    ├── email_audits.log
    ├── malware_audits.log

⚙️ Prérequis
Un serveur VPS sous Ubuntu 22.04.

git, python3, python3-venv, pip, openssh-client installés.

🚀 Déploiement
1️⃣ Cloner le dépôt :

git clone https://github.com/davidattip/ssh_honeypy /opt/ssh_honeypy
cd /opt/ssh_honeypy

2️⃣ Configurer l’adresse IP dans .env :
Créer un fichier .env :

HONEYPY_HOST=0.0.0.0

3️⃣ Donner les droits et exécuter le script de déploiement :

chmod +x deploy.sh
./deploy.sh

4️⃣ Vérifier que les services sont actifs :

sudo systemctl status ssh_honeypy
sudo systemctl status email_honeypy
sudo systemctl status malware_honeypy
sudo systemctl status honeypy_dashboard
sudo systemctl status web_honeypy

 Accès aux services

| Composant        | URL                          |
| ---------------- | ---------------------------- |
| SSH Honeypot     | `ssh utilisateur@IP -p 2222` |
| Email Honeypot   | SMTP – Port `2525`           |
| Malware Honeypot | `http://<TON-IP>:8080/`      |
| Web Honeypot     | `http://<TON-IP>:5000/`      |
| Dashboard        | `http://<TON-IP>:8050/`      |


🧹 Désinstallation
Pour tout supprimer proprement :

chmod +x remove.sh
./remove.sh


 Notes
Les logs sont enregistrés dans le dossier log_files.

Les services sont gérés par systemd pour démarrer automatiquement au reboot.

Change le HONEYPY_HOST dans .env pour passer de localhost (127.0.0.1) à l’extérieur (0.0.0.0 ou IP publique).

Sécurité : N’utilise pas le serveur en production réelle — c’est un honeypot conçu pour attirer les attaquants.

👨‍💻 Auteur
Honeypy par David Attip