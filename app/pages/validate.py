import base64
import io
import dash
import Mixture
import multiprocessing

import numpy as np
import pandas as pd

from joblib import Parallel, delayed

from random import seed
from random import sample 
from random import randint

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from flask import send_file
import plotly.graph_objects as go

from app import app

signature = None
filename_signature = None
dataFrameSignature = None
result1 = None
pValues1 = None
tableMetrics1 = None
result2 = None
pValues2 = None
tableMetrics2 = None
subjects = None
betas = None
lines = None
estimate_lines = None
ids = None

seed(123)

layout = html.Div([
    html.Div([
    html.Div([        
        html.P('Molecular Signature file:'),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select File')
            ]), style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-msignature")], type="default"),
        dcc.Checklist(
            id="check_celllines",
            options=[
                {'label': 'Use Cellines', 'value': 'cellines'},
            ],
            value=['cellines']
        ),  
        html.P('CPUs:', style={
            'margin-top': '20px'
        }),
        dcc.Slider(
            id='cpu-slider',
            min=1,
            max=multiprocessing.cpu_count(),
            step=1,
            marks={i: '{}'.format(i) for i in range(multiprocessing.cpu_count()+1)},
            value=multiprocessing.cpu_count()
        ),  
        html.Button('Submit', id='button_validate', style = {
            'margin-top': '30px'
        })        
    ], style={
            '-webkit-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            '-moz-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'margin': '0px',
            'background-color': '#FFFFFF',
            'padding': '20px',
            'border-radius': '5px',
            'width': '20vw',
            'max-width': '20vw'
    }),
    html.Div([
        html.Div(id='output-processing'),
        dcc.Loading(id='loading-result', children=[html.Div(id='loading-output-result')], type='default')        
    ], style={
            '-webkit-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            '-moz-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'margin': '0px',
            'margin-left': '10px',
            'background-color': '#FFFFFF',
            'padding': '20px',
            'border-radius': '5px',
            'width': '80vw',
            'max-width': '80vw'
    })
    ], style = {
        'width':'100%',
        'height':'100%',
        'margin': '0px',
        'padding': '0px',
        'display': 'flex',
        'flex-direction': 'row'
})
], style = {
        'width':'100%',
        'height':'100%',
        'display': '-webkit-flex',
        '-webkit-flex-direction': 'column',
        'display': 'flex',
        'flex-direction': 'column',
        'margin': '0px',
        'padding': '0px',
        'background-color': '#F7F7F7',
})

def createBetas (X, a, b, n):

    ns = randint(a, b)
    r = np.random.uniform(1, 0.2, ns)
    rn = r/r.sum()
    id = sample(range(n-1), ns)
    betas = np.repeat(.0, n, axis=0)
    for index, i in enumerate(id, start = 0):
        betas[i] = rn[index]

    vector = X.to_numpy(copy=True)    
    vector = vector.flatten()
        
    A = np.dot(X, betas) + vector[sample(range(len(vector)), len(X.index))]

    return betas, id, A


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    
    global signature, filename_signature, dataFrameSignature

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            dataFrameSignature = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            signature = io.BytesIO(decoded)
            dataFrameSignature = pd.read_excel(signature, sheet_name = 0)
            
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    filename_signature = filename
    
    return html.Div([
        html.P('Selected: ' + filename),
        html.P('No se que label colocarle aca:', style={
            'margin-top': '10px'
        }),        
        dcc.RangeSlider(
            id='lines_slider',
            min=1,
            max=(len(dataFrameSignature.columns)-1),
            step=1,
            # marks={i: '{}'.format(i) for i in range(len(dataFrameSignature.columns)+1)},
            marks={
              1: '1',
              round((len(dataFrameSignature.columns)-1)/2): str(round((len(dataFrameSignature.columns)-1)/2)),
              (len(dataFrameSignature.columns)-1): str((len(dataFrameSignature.columns)-1))
            },
            value=[round((len(dataFrameSignature.columns)-1)*0.2), round((len(dataFrameSignature.columns)-1)*0.75)]
        ),
        html.P(id='lines_slider_output', style={
            'margin-top': '40px'
        })
    ])


@app.callback(Output('loading-output-msignature', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('lines_slider_output', 'children'),
              [Input('lines_slider', 'value')])
def update_lines(lines_slider):
    return 'Selected lines: from {} to {}'.format(lines_slider[0], lines_slider[1])

@app.callback(
    Output("loading-output-result", "children"),
    [dash.dependencies.Input('button_validate', 'n_clicks')],
    [dash.dependencies.State('lines_slider', 'value'),
     dash.dependencies.State('cpu-slider', 'value')])
def update_output(n_clicks, lines_slider, cpu):
   
    global signature, dataFrameSignature, result1, pValues1, tableMetrics1, result2, pValues2, tableMetrics2, subjects, betas, lines, estimate_lines, ids
    
    if n_clicks is not None:

        X = dataFrameSignature

        Y = dataFrameSignature
        
        #if __name__ == '__main__':            
        #if __name__ == 'app':
        if True:

            rango = 100

            lines = lines_slider

            # Escenario 1
            result1, pValues1 = Mixture.Mixture(X, Y , cpu, 1, '')            
            metrics1 = result1.Subjects[0].ACCmetrix[0].reset_index()

            # Escenario 2            
            X = dataFrameSignature.iloc[:, 1:]

            subjects = Parallel(n_jobs=cpu, backend='threading')(delayed(createBetas)(X = X, a = lines[0], b = lines[1], n = len(X.columns)) for i in range(rango))
            
            # Getting expression matrix
            vector = [x[2] for x in subjects]
            columns = ['V' + str(x+1) for x in range(len(subjects))]
            Y2 = pd.DataFrame(np.column_stack(vector), columns=columns)
            Y2.insert(0, 'Gene symbol', dataFrameSignature['Gene symbol'])

            # Getting Real Betas Matrix
            vector = [x[0] for x in subjects]
            columns = ['V' + str(x+1) for x in range(len(subjects))]
            betas = pd.DataFrame(np.column_stack(vector), columns=columns)

            X = dataFrameSignature

            result2, pValues2 = Mixture.Mixture(X, Y2 , cpu, 1, '') 
            betasSim = result2.Subjects[0].MIXprop[0].to_numpy(copy = True)           
            estimate_lines = pd.DataFrame([(betasSim[i] > 0).sum() for i in range(rango)])     
            metrics2 = result2.Subjects[0].ACCmetrix[0].reset_index()

            vector = [len(x[1]) for x in subjects]
            ids = pd.DataFrame(np.column_stack(vector))
            
        children = [            
            dcc.Tabs(id='tabs4', value='tab4-1', children=[
                dcc.Tab(label='Plots', value='tab4-1'),
            ]),
            html.Div(id='tabs4-content')
        ]
        
        return children

@app.callback(Output('tabs4-content', 'children'),
              [Input('tabs4', 'value')])
def render_content2(tab):
    if tab == 'tab4-1':
        return html.Div([
            dcc.Tabs(id='tabs5', value='tab5-3', children=[
                dcc.Tab(label='Breal - Bsim', value='tab5-1'),
                dcc.Tab(label='Breal vs Bsim', value='tab5-2'),
                dcc.Tab(label='Heatmaps', value='tab5-3'),
                dcc.Tab(label='BoxPlot', value='tab5-4'),
            ]),
            html.Div(id='tabs5-content')
        ])

@app.callback(Output('tabs5-content', 'children'),
              [Input('tabs5', 'value')])
def render_content1(tab):
    global result1, result2, betas, lines, estimate_lines, ids
    count = len(result2.Subjects[0].MIXprop[0])
    if tab == 'tab5-1':      
        betasSim = result2.Subjects[0].MIXprop[0].T.to_numpy(copy=True)
        betasSim = betasSim.flatten()
        betasHat = betas.to_numpy(copy=True)
        betasHat = betasHat.flatten()
        mean = np.mean(betasSim - betasHat)
        std = np.std(betasSim - betasHat)
        return html.Div([
            html.H3('Real betas - Simulated betas'),
            dcc.Graph(
                id='graph-3',
                figure=go.Figure(data=go.Scatter(
                    x = betasHat,
                    y = betasSim - betasHat,
                    mode='markers',
                    marker_color='rgba(0, 0, 0, .9)'
                ),
                layout=go.Layout(
                        shapes=[
                            go.layout.Shape(
                                type="line",
                                xref="paper",
                                x0=0,
                                y0=mean,
                                x1=1,
                                y1=mean,
                                line=dict(
                                    color="red",
                                    width=2,
                                    dash="dashdot",
                                ),
                            ),
                            go.layout.Shape(
                                type="line",
                                xref="paper",
                                x0=0,
                                y0=(mean+2*std),
                                x1=1,
                                y1=(mean+2*std),
                                line=dict(
                                    color="blue",
                                    width=2,
                                    dash="dashdot",
                                ),
                            ),
                            go.layout.Shape(
                                type="line",
                                xref="paper",
                                x0=0,
                                y0=(mean-2*std),
                                x1=1,
                                y1=(mean-2*std),
                                line=dict(
                                    color="blue",
                                    width=2,
                                    dash="dashdot",
                                ),
                            )
                        ],
                        height=700,
                        xaxis=dict(tickangle=-90, automargin= True)
                    )
                )
            )
        ])
    elif tab == 'tab5-2':      
        betasSim = result2.Subjects[0].MIXprop[0].T.to_numpy(copy=True)
        betasSim = betasSim.flatten()
        betasHat = betas.to_numpy(copy=True)
        betasHat = betasHat.flatten()
        return html.Div([
            html.H3('Real betas vs Simulated betas'),
            dcc.Graph(
                id='graph-3',
                figure=go.Figure(data=go.Scatter(
                    x = betasHat,
                    y = betasSim,
                    mode='markers',
                    marker_color='rgba(0, 0, 0, .9)'
                ),
                layout=go.Layout(
                        shapes=[
                            go.layout.Shape(
                                type="line",
                                x0=0,
                                y0=0,
                                x1=1,
                                y1=1,
                                line=dict(
                                    color="blue",
                                    width=2,
                                ),
                            )
                        ],
                        height=700,
                        xaxis=dict(tickangle=-90, automargin= True)
                    )
                )
            )
        ])
    elif tab == 'tab5-3':
        items = [result1.Subjects[0].MIXprop[0].iloc[j].values for j in range(len(result1.Subjects[0].MIXprop[0]))]        
        return html.Div([
            html.H3('Aca un titulo para el heatmap (o no)'),
            dcc.Graph(
                id='graph-3',
                figure=go.Figure(data=go.Heatmap(
                    z=np.transpose(items),
                    x=result1.Subjects[0].MIXprop[0].index,
                    y=result1.Subjects[0].MIXprop[0].columns,
                    colorscale= [
                        [0.0, 'rgb(255,255,255)'],
                        [1.0, 'rgb(255,0,0)']
                    ]
                ),
                    layout=go.Layout(
                        height=700,
                        xaxis=dict(tickangle=-90, automargin= True)
                    )
                )
            )
        ])
    elif tab == 'tab5-4':
        items = [go.Box(y=estimate_lines[(ids.values == j)[0]][0], name = str(j)) for j in range(lines[0],lines[1])]        
        return html.Div([
            html.H3('Aca titulo para el boxplot'),
            dcc.Graph(
                id='graph-3',
                figure=go.Figure(data=items,
                    layout=go.Layout(
                        height=700,
                        xaxis=dict(tickangle=0, automargin= True)
                    )
                )
            )
        ])