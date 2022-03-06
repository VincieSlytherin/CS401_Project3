from dash import Dash, html, dcc
from plotly.subplots import make_subplots
import plotly.express as px

import pandas as pd
import redis
import json
from dash.dependencies import Input, Output


app = Dash(__name__)
app.layout =  html.Div(
    html.Div([
        html.H4('Information',style={'textAlign': 'center','fontSize':'30px'}),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Graph(id='live-update-graph1'),
        dcc.Interval(
            id='interval-component',
            interval=5*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))



def update_table(n):
    r = redis.Redis(host='152.3.65.126', port=6379)
    metrics = r.get('rj133-proj3-output')
    metrics_str = metrics.decode("utf-8")
    metrics_json = json.loads(metrics_str)
    style = {'padding': '5px', 'fontSize': '16px'}
    return [html.Span("number of 5sec: "+str(metrics_json["number of 5sec"])),
            html.Br(),
            html.Span("input-timestamp: "+str(metrics_json["input-timestamp"])),
            html.Br(),
            html.Span("approximate_run_time(hour:min:sec): "+str(metrics_json["approximate_run_time(hour:min:sec)"])),
            html.Br(),
        html.Table(
            style={'textAlign':'center','width':'1000px','height':'300px'},
        className='formCenter',
        children=[
            
            html.Thead(
                html.Tr([
                    html.Th('Time Metrics'),html.Th('CPU1'),html.Th('CPU2'),html.Th('CPU3'),html.Th('CPU4')
                    ])
            
            ),
            html.Tbody([
             html.Tr([
                     html.Td(key),
                     html.Td(metrics_json["avg-util-cpu0-"+key]),
                     html.Td(metrics_json["avg-util-cpu1-"+key]),
                     html.Td(metrics_json["avg-util-cpu2-"+key]),
                     html.Td(metrics_json["avg-util-cpu3-"+key])
                     ]) for key in ["60sec","60min"]
                ])
            ])]
           
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    r = redis.Redis(host='152.3.65.126', port=6379)
    metrics = r.get('rj133-proj3-output')
    metrics_str = metrics.decode("utf-8")
    metrics_json = json.loads(metrics_str)
    
    fig = make_subplots(rows=2, cols=1)
    fig=px.histogram(y=[metrics_json[f"avg-util-cpu{i}-60sec"] for i in range(4)],x = ["cpu1","cpu2","cpu3","cpu4"],
                    title="avg-util-60sec",labels={"x":"cpu","y":"utilization"},histfunc="avg")
#     fig=px.histogram(y=[metrics_json[f"avg-util-cpu{i}-60min"] for i in range(4)],x = ["cpu1","cpu2","cpu3","cpu4"],
#                     title="avg-util-60min",labels={"x":"cpu","y":"utilization"},histfunc="avg")
#     fig.append_trace(trace0, 1, 1)
#     fig.append_trace(trace1, 2, 1)
           
    return fig

    
    
if __name__ == '__main__':
    app.run_server(debug=True,port=5105)