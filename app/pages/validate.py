import base64
import io
import dash
import Mixture
import multiprocessing

import numpy as np
import pandas as pd

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from flask import send_file
import plotly.graph_objects as go

from app import app

signature = ''
filename_signature = ''
dataFrameSignature = ''

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
            print(len(dataFrameSignature.columns))
            
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
            max=len(dataFrameSignature.columns),
            step=1,
            # marks={i: '{}'.format(i) for i in range(len(dataFrameSignature.columns)+1)},
            marks={
              1: '1',
              round(len(dataFrameSignature.columns)/2): str(round(len(dataFrameSignature.columns)/2)),
              len(dataFrameSignature.columns): str(len(dataFrameSignature.columns))
            },
            value=[round(len(dataFrameSignature.columns)*0.2), round(len(dataFrameSignature.columns)*0.75)]
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
def update_output(n_clicks, lines, cpu):
   
    global signature, result, pValues, tableMetrics, urlLm22, urlTil10
    
    if n_clicks is not None:

        X = dataFrameSignature

        Y = dataFrameSignature
        
        #if __name__ == '__main__':            
        #if __name__ == 'app':
        if True:
            result, pValues = Mixture.Mixture(X, Y , cpu, 0, '')
            
            metrics = result.Subjects[0].ACCmetrix[0].reset_index()

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
    if tab == 'tab4-3':
        return html.Div([
            dcc.Tabs(id='tabs5', value='tab5-1', children=[
                dcc.Tab(label='Breal - Bsim', value='tab5-1'),
                dcc.Tab(label='Breal vs Bsim', value='tab5-2'),
                dcc.Tab(label='Heatmaps', value='tab5-3'),
                dcc.Tab(label='BoxPlot', value='tab5-4'),
            ]),
            html.Div(id='tabs-content')
        ]) 