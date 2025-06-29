# Import library dependencies.
import pandas as pd
import re
import requests

# === EXISTANT ===
def parse_creds_audits_log(creds_audits_log_file):
    data = []
    with open(creds_audits_log_file, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            ip_address = parts[0]
            username = parts[1]
            password = parts[2]
            data.append([ip_address, username, password])
    df = pd.DataFrame(data, columns=["ip_address", "username", "password"])
    return df


def parse_cmd_audits_log(cmd_audits_log_file):
    data = []
    with open(cmd_audits_log_file, 'r') as file:
        for line in file:
            lines = line.strip().split('\n')
            pattern = re.compile(r"Command b'([^']*)'executed by (\d+\.\d+\.\d+\.\d+)")
            for line in lines:
                match = pattern.search(line)
                if match:
                    command, ip = match.groups()
                    data.append({'IP Address': ip, 'Command': command})
    df = pd.DataFrame(data)
    return df


# ✅ AJOUT : Parser pour le fichier Email Honeypot
def parse_email_audits_log(email_audits_log_file):
    data = []
    current_record = {}
    with open(email_audits_log_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("IP:"):
                current_record['IP'] = line.split(":")[1].strip()
            elif line.startswith("MAIL FROM:"):
                current_record['FROM'] = line.split(":", 1)[1].strip()
            elif line.startswith("RCPT TO:"):
                current_record['TO'] = line.split(":", 1)[1].strip()
            elif line.startswith("DATA:"):
                current_record['DATA'] = ''
            elif line.startswith("==="):
                if current_record:
                    data.append(current_record)
                    current_record = {}
            elif 'DATA' in current_record:
                current_record['DATA'] += line + "\n"

    df = pd.DataFrame(data)
    return df


def top_10_calculator(dataframe, column):
    if dataframe.empty or column not in dataframe.columns:
        return pd.DataFrame(columns=[column, "count"])
    top_10_df = dataframe[column].value_counts().reset_index().head(10)
    top_10_df.columns = [column, "count"]
    return top_10_df


def get_country_code(ip):
    data_list = []
    url = f"https://api.cleantalk.org/?method_name=ip_info&ip={ip}"
    try:
        response = requests.get(url)
        api_data = response.json()
        if response.status_code == 200:
            data = response.json()
            ip_data = data.get('data', {})
            country_info = ip_data.get(ip, {})
            data_list.append({'IP Address': ip, 'Country_Code': country_info.get('country_code')})
        elif response.status_code == 429:
            print(api_data["error_message"])
            print(f"[!] Rate limit exceeded.\n {response.status_code}")
        else:
            print(f"[!] Error: {response.status_code}")
    except requests.RequestException as e:
        print(f"[!] Request failed: {e}")

    return data_list


def ip_to_country_code(dataframe):
    data = []
    for ip in dataframe['ip_address']:
        get_country = get_country_code(ip)
        parse_get_country = get_country[0]["Country_Code"]
        data.append({"IP Address": ip, "Country_Code": parse_get_country})
    df = pd.DataFrame(data)
    return df

# ===========================================
# Parser pour le log du malware honeypot
# ===========================================

def parse_malware_audits_log(malware_audits_log_file):
    """
    Parse le fichier 'malware_audits.log' pour en extraire :
    - L'adresse IP
    - Le nom du fichier uploadé
    - La date/heure
    """
    import pandas as pd
    import re

    data = []

    with open(malware_audits_log_file, 'r') as file:
        for line in file:
            # Exemple de ligne :
            # 2025-06-29 23:58:01 IP: 127.0.0.1 uploaded file: test.php
            pattern = re.compile(r"IP:\s+([\d\.]+)\s+uploaded file:\s+(.*)")
            match = pattern.search(line)
            if match:
                ip_address, filename = match.groups()
                timestamp = line.split(' ')[0] + ' ' + line.split(' ')[1]
                data.append({
                    "timestamp": timestamp,
                    "ip_address": ip_address,
                    "filename": filename
                })

    df = pd.DataFrame(data, columns=["timestamp", "ip_address", "filename"])
    return df
