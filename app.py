from dash import Dash, html, dcc
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

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

r = redis.Redis(host='152.3.65.126', port=6379)
metrics = r.get('rj133-proj3-output')
metrics_str = metrics.decode("utf-8")
app.metrics=json.loads(metrics_str)
app.min=[]
app.hour=[]
app.memory=[]


@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))



def update_table(n):
    r = redis.Redis(host='152.3.65.126', port=6379)
    metrics = r.get('rj133-proj3-output')
    metrics_str = metrics.decode("utf-8")
    metrics_json = json.loads(metrics_str)
    app.metrics=json.loads(metrics_str)
    style = {'padding': '5px', 'fontSize': '16px'}
    return [html.Span("number of 5sec: "+str(metrics_json["number of 5sec"])),
            html.Br(),
            html.Span("input-timestamp: "+str(metrics_json["input-timestamp"])),
            html.Br(),
            html.Span("approximate_run_time(hour:min:sec): "+str(metrics_json["approximate_run_time(hour:min:sec)"])),
            html.Br(),
            html.Span("vm_memory_pc_60sec: "+str(metrics_json["vm_memory_pc_60sec"])),
        html.Table(
            style={'textAlign':'center','width':'1000px','height':'100px'},
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

           
    return fig

@app.callback(Output('live-update-graph1', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live1(n):
    
    app.min.append([app.metrics[f'avg-util-cpu{i}-60sec'] for i in range(4)])
    app.hour.append([app.metrics[f'avg-util-cpu{i}-60min'] for i in range(4)])
    app.memory.append(app.metrics[f'vm_memory_pc_60sec'])
    if len(app.min)>360:
        app.min.pop(0)
        app.hour.pop(0)
        app.memory.pop(0)
        

    fig = make_subplots(rows = 3, cols = 1, subplot_titles=('utilization average 1min','utilization average 1hour',"memory percent 1min"))
    for i in range(4):
        fig.add_trace(go.Scatter(x=np.arange(len(app.min)), y=np.array(app.min)[:,i],name=f"cpu{i+1}_60sec"),row=1,col=1)
        fig.add_trace(go.Scatter(x=np.arange(len(app.hour)), y=np.array(app.hour)[:,i],name=f"cpu{i+1}_60min"),row=2,col=1)
    
    fig.add_trace(go.Scatter(x=np.arange(len(app.memory)), y=np.array(app.memory),name=f"memory_percent"),row=3,col=1)
    
    fig.update_xaxes(title_text = 'time')
    fig.update_yaxes(title_text = 'Utilization')
    fig.update_layout(
        # plot_bgcolor='white',
        width = 1200,
        height = 600
    )

    return fig

    
    
if __name__ == '__main__':
    app.run_server(host='0.0.0.0',port = 5105,debug=True)
