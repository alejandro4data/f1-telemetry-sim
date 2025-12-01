import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import sys
import os

# Importar módulos propios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.telemetry.receiver import TelemetryReceiver

# --- CONFIGURACIÓN ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# OPTIMIZACIÓN 1: BUFFER REDUCIDO
# 60 puntos es suficiente para ver la tendencia de los últimos segundos sin saturar el DOM
receiver = TelemetryReceiver(buffer_size=60) 
receiver.connect()

graph_card_style = {
    'border': '1px solid #333',
    'borderRadius': '5px',
    'padding': '5px',
    'backgroundColor': 'rgba(0,0,0,0.2)'
}

# --- LAYOUT ---
app.layout = html.Div(style={'padding': '20px', 'maxWidth': '100%', 'overflowX': 'hidden'}, children=[
    
    # TITULO
    dbc.Row([
        dbc.Col(html.H2("🏎️ F1 TELEMETRY CONTROL", style={'color': '#ff3838', 'fontWeight': 'bold'}), width=8),
        dbc.Col(html.H5("VIRTUAL_SILVERSTONE | LIVE", style={'textAlign': 'right', 'color': '#666', 'marginTop': '10px'}), width=4),
    ], style={'marginBottom': '10px'}),
    
    html.Hr(style={'borderColor': '#444'}),

    # KPIs
    dbc.Row([
        dbc.Col(html.Div([html.H6("SPEED", style={'color':'#00ff00'}), html.H1("0", id='val-speed')]), width=3, style={'textAlign': 'center'}),
        dbc.Col(html.Div([html.H6("RPM", style={'color':'#ffffff'}), html.H1("0", id='val-rpm')]), width=3, style={'textAlign': 'center'}),
        dbc.Col(html.Div([html.H6("BRAKE TEMP", style={'color':'#ffaa00'}), html.H1("0", id='val-brake')]), width=3, style={'textAlign': 'center'}),
        dbc.Col(html.Div([html.H6("TYRE PRESS", style={'color':'#00aaff'}), html.H1("0", id='val-tyre')]), width=3, style={'textAlign': 'center'}),
    ], style={'marginBottom': '20px'}),

    # GRÁFICOS
    dbc.Row([
        dbc.Col(html.Div([
            dcc.Graph(id='chart-speed', config={'displayModeBar': False, 'staticPlot': False}, style={'height': '250px'})
        ], style=graph_card_style), width=6),
        
        dbc.Col(html.Div([
            dcc.Graph(id='chart-rpm', config={'displayModeBar': False, 'staticPlot': False}, style={'height': '250px'})
        ], style=graph_card_style), width=6),
    ], style={'marginBottom': '15px'}),

    dbc.Row([
        dbc.Col(html.Div([
            dcc.Graph(id='chart-brake', config={'displayModeBar': False, 'staticPlot': False}, style={'height': '250px'})
        ], style=graph_card_style), width=6),
        
        dbc.Col(html.Div([
            dcc.Graph(id='chart-tyre', config={'displayModeBar': False, 'staticPlot': False}, style={'height': '250px'})
        ], style=graph_card_style), width=6),
    ]),

    # OPTIMIZACIÓN 2: TIMING RELAJADO
    # Intervalo de 150ms (aprox 6-7 Hz). Da tiempo al navegador a respirar.
    dcc.Interval(id='interval-update', interval=150, n_intervals=0)
])

def create_trace_figure(df, column, title, color_hex, y_range):
    fig = go.Figure()
    
    x_vals = list(range(len(df))) if not df.empty else [0]
    y_vals = df[column] if not df.empty else [0]

    h = color_hex.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    fill_color_rgba = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)"

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines',
        line=dict(color=color_hex, width=2),
        fill='tozeroy', 
        fillcolor=fill_color_rgba,
        # OPTIMIZACIÓN 3: SIMPLIFICACIÓN DE RENDERIZADO
        hoverinfo='skip' # Desactivar tooltips mejora rendimiento
    ))

    # Configuración de transición con "Breathing Room"
    # Transición de 100ms dentro de un ciclo de 150ms = 50ms de descanso para la CPU
    tx_config = {'duration': 100, 'easing': 'linear'}

    fig.update_layout(
        title={'text': title, 'font': {'size': 12, 'color': '#aaa'}, 'x': 0.05, 'y': 0.9},
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=10, t=20, b=20),
        xaxis=dict(showgrid=False, visible=False, fixedrange=True),
        yaxis=dict(
            range=y_range, 
            showgrid=True, 
            gridcolor='#333', 
            fixedrange=True,
            zeroline=False
        ),
        uirevision='constant',
        transition=tx_config
    )
    return fig

@app.callback(
    [Output('val-speed', 'children'), Output('chart-speed', 'figure'),
     Output('val-rpm', 'children'),   Output('chart-rpm', 'figure'),
     Output('val-brake', 'children'), Output('chart-brake', 'figure'),
     Output('val-tyre', 'children'),  Output('chart-tyre', 'figure')],
    [Input('interval-update', 'n_intervals')]
)
def update_dashboard(n):
    # 1. Fetch eficiente
    receiver.fetch_latest_data()
    df = receiver.get_dataframe()
    
    if df.empty:
        s, r, b, t = 0, 0, 0, 0
    else:
        last = df.iloc[-1]
        s = int(last['speed'])
        r = int(last['rpm'])
        b = int(last['brake_temp_fl'])
        t = last['tyre_pressure_fl']

    fig_speed = create_trace_figure(df, 'speed', "VELOCITY (km/h)", '#00ff00', [0, 360])
    fig_rpm = create_trace_figure(df, 'rpm', "ENGINE (RPM)", '#ffffff', [0, 13500])
    fig_brake = create_trace_figure(df, 'brake_temp_fl', "BRAKE TEMP (°C)", '#ffaa00', [0, 1000])
    # Ajuste fino para ver mejor la variación de presión
    fig_tyre = create_trace_figure(df, 'tyre_pressure_fl', "TYRE PRESS (PSI)", '#00aaff', [20, 35])

    return (
        f"{s}", fig_speed,
        f"{r}", fig_rpm,
        f"{b}°C", fig_brake,
        f"{t:.2f}", fig_tyre
    )

if __name__ == '__main__':
    print("🚀 Telemetry Server running...")
    app.run(debug=False, port=8050)