# === IMPORTS ===
from dash import Dash, html, dash_table, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
from pathlib import Path
from dotenv import load_dotenv
import os

# === PROJECT FILES ===
from dashboard_data_parser import *
from honeypy import *

# === CONSTANTS ===
base_dir = Path(__file__).parent.parent
creds_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'creds_audits.log'
cmd_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'cmd_audits.log'
email_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'email_audits.log'
malware_audits_log_local_file_path = base_dir / 'ssh_honeypy' / 'log_files' / 'malware_audits.log'

dotenv_path = Path('public.env')
load_dotenv(dotenv_path=dotenv_path)

# === LOAD LOG FILES ===
creds_audits_log_df = parse_creds_audits_log(creds_audits_log_local_file_path)
cmd_audits_log_df = parse_cmd_audits_log(cmd_audits_log_local_file_path)
email_audits_log_df = parse_email_audits_log(email_audits_log_local_file_path)
malware_audits_log_df = parse_malware_audits_log(malware_audits_log_local_file_path)

# === TOP 10 ===
top_ip_address = top_10_calculator(creds_audits_log_df, "ip_address")
top_usernames = top_10_calculator(creds_audits_log_df, "username")
top_passwords = top_10_calculator(creds_audits_log_df, "password")
top_cmds = top_10_calculator(cmd_audits_log_df, "Command")
top_email_ips = top_10_calculator(email_audits_log_df, "IP")
top_uploaded_files = top_10_calculator(malware_audits_log_df, "filename")

# === DASH THEME ===
load_figure_template(["cyborg"])
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css")

image = 'assets/images/honeypy-logo-white.png'

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, dbc_css])
app.title = "HONEYPY"
app._favicon = "../assets/images/honeypy-favicon.ico"

country = os.getenv('COUNTRY')
def country_lookup(country):
    if country == 'True':
        get_ip_to_country = ip_to_country_code(creds_audits_log_df)
        top_country = top_10_calculator(get_ip_to_country, "Country_Code")
        message = dbc.Col(dcc.Graph(figure=px.bar(top_country, x="Country_Code", y='count')),
                          style={'width': '33%', 'display': 'inline-block'})
    else:
        message = "No Country Panel Defined"
    return message

# === SSH TABLES ===
creds_tables = html.Div([
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                data=creds_audits_log_df.to_dict('records'),
                columns=[{"name": "IP Address", 'id': 'ip_address'}],
                style_table={'width': '100%', 'color': 'black'},
                style_cell={'textAlign': 'left', 'color': '#2a9fd6'},
                style_header={'fontWeight': 'bold'},
                page_size=10
            ),
        ),
        dbc.Col(
            dash_table.DataTable(
                data=creds_audits_log_df.to_dict('records'),
                columns=[{"name": "Usernames", 'id': 'username'}],
                style_table={'width': '100%'},
                style_cell={'textAlign': 'left', 'color': '#2a9fd6'},
                style_header={'fontWeight': 'bold'},
                page_size=10
            ),
        ),
        dbc.Col(
            dash_table.DataTable(
                data=creds_audits_log_df.to_dict('records'),
                columns=[{"name": "Passwords", 'id': 'password'}],
                style_table={'width': '100%','justifyContent': 'center'},
                style_cell={'textAlign': 'left', 'color': '#2a9fd6'},
                style_header={'fontWeight': 'bold'},
                page_size=10
            ),
        ),       
    ])
])

# === EMAIL TABLE ===
email_table = html.Div([
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                data=email_audits_log_df.to_dict('records'),
                columns=[
                    {"name": "IP", 'id': 'IP'},
                    {"name": "FROM", 'id': 'FROM'},
                    {"name": "TO", 'id': 'TO'},
                    {"name": "DATA", 'id': 'DATA'}
                ],
                style_table={'width': '100%'},
                style_cell={'textAlign': 'left', 'color': '#2a9fd6'},
                style_header={'fontWeight': 'bold'},
                page_size=10
            ),
        ),
    ])
])

# === MALWARE TABLE ===
malware_table = html.Div([
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                data=malware_audits_log_df.to_dict('records'),
                columns=[
                    {"name": "Timestamp", 'id': 'timestamp'},
                    {"name": "IP Address", 'id': 'ip_address'},
                    {"name": "Filename", 'id': 'filename'}
                ],
                style_table={'width': '100%'},
                style_cell={'textAlign': 'left', 'color': '#2a9fd6'},
                style_header={'fontWeight': 'bold'},
                page_size=10
            ),
        ),
    ])
])

# === THEMES ===
apply_creds_theme = html.Div([creds_tables], className="dbc")
apply_email_theme = html.Div([email_table], className="dbc")
apply_malware_theme = html.Div([malware_table], className="dbc")

# === LAYOUT ===
app.layout = dbc.Container([

    html.Div([html.Img(src=image, style={'height': '25%', 'width': '25%'})],
             style={'textAlign': 'center'}, className='dbc'),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=px.bar(top_ip_address, x="ip_address", y='count')), width=4),
        dbc.Col(dcc.Graph(figure=px.bar(top_usernames, x='username', y='count')), width=4),
        dbc.Col(dcc.Graph(figure=px.bar(top_passwords, x='password', y='count')), ),
    ], align='center', class_name='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=px.bar(top_cmds, x='Command', y='count')),
                style={'width': '33%', 'display': 'inline-block'}),
        dbc.Col(dcc.Graph(figure=px.bar(top_email_ips, x='IP', y='count')),
                style={'width': '33%', 'display': 'inline-block'}),
        dbc.Col(dcc.Graph(figure=px.bar(top_uploaded_files, x='filename', y='count')),
                style={'width': '33%', 'display': 'inline-block'}),
    ], align='center', class_name='mb-4'),

    country_lookup(country),

    html.Div([
        html.H3("SSH Intelligence Data",
                style={'textAlign': 'center', "font-family": 'Consolas, sans-serif', 'font-weight': 'bold'}),
    ]),
    apply_creds_theme,

    html.Div([
        html.H3("Email Honeypot Logs",
                style={'textAlign': 'center', "font-family": 'Consolas, sans-serif', 'font-weight': 'bold'}),
    ]),
    apply_email_theme,

    html.Div([
        html.H3("Malware Honeypot Logs",
                style={'textAlign': 'center', "font-family": 'Consolas, sans-serif', 'font-weight': 'bold'}),
    ]),
    apply_malware_theme

])

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1")
