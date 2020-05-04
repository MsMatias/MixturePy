#! /usr/bin/env python3

import base64
import datetime
import io
import Mixture
import multiprocessing
import sys
import os
import webbrowser

import numpy as np

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from flask import send_file
import plotly.graph_objects as go

from threading import Timer

import pandas as pd

from app import app

expression = ''
filename_expression = ''
result = ''
pValues = ''
tableMetrics = ''

cores = 4
output = ''

urlTil10 = '../data/TIL10_signature.xlsx'
urlLm22 = '../data/LM22Signature.xlsx'

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)


layout = html.Div([
    html.Div([
    html.Div([        
        html.P('Expression file:'),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag & Drop or ',
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
        dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="default"),
        html.P('Signature Data:'),
        dcc.Dropdown(
            id='signature-input',
            options=[
                {'label': 'LM22', 'value': 'LM22'},
                {'label': 'TIL10', 'value': 'TIL10'},
            ],
            value='LM22'
        ),
        html.P('Number of permutation samples:', style={
            'margin-top': '10px'
        }),
        dcc.Input(
            id='population-input',
            placeholder='Enter a value...',
            type='number',
            min='0',
            value='0'
        ),
        html.P('CPUs:', style={
            'margin-top': '10px'
        }),
        dcc.Slider(
            id='cpu-slider',
            min=1,
            max=multiprocessing.cpu_count(),
            step=2,
            marks={i: '{}'.format(i) for i in range(1, multiprocessing.cpu_count()+2, 3)},
            value=multiprocessing.cpu_count()
        ),  
        html.Button('Submit', id='button', style = {
            'margin-top': '30px'
        })        
    ], style={
            '-webkit-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.05)',
            '-moz-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.05)',
            'box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.05)',
            'margin': '0px',
            'background-color': '#FFFFFF',
            'padding': '20px',
            'border-radius': '2px',
            'maxWidth': '20vw'
    }),
    html.Div([
        dcc.Loading(id='loading-2', children=[html.Div(id='loading-output-2')], type='default')        
    ], style={
            'margin': '0px',
            'margin-left': '5px',
            'width': '80vw',
            'maxWidth': '80vw'
    },id='output-processing')
    ], style = {
        'width':'100%',
        'height':'100%',
        'margin': '0px',
        'padding': '0px',
        'display': 'flex',
        'flex-direction': 'row'
},id='div-cont')
], style = {
        'width':'100%',
        'height':'100%',
        'display': '-webkit-flex',
        '-webkit-flex-direction': 'column',
        'display': 'flex',
        'flex-direction': 'column',
        'margin': '0px',
        'padding': '0px',
})

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content1(tab):
    global result
    count = len(result.Subjects[0].MIXprop[0])
    if tab == 'tab-1':
        xLabel = result.Subjects[0].MIXprop[0].index
        columns = result.Subjects[0].MIXprop[0].columns        
        return html.Div([
            html.H3('Bar Plot Subject-Proportions'),
            dcc.Graph(
                id='graph-1-tabs',
                figure=go.Figure(                    
                    data=[go.Bar(x=xLabel, y=[result.Subjects[0].MIXprop[0].iloc[j].values[i] for j in range(count)], name = columns[i]) for i in range(len(columns))],
                    layout=go.Layout(
                        barmode='relative',
                        title_text='Bar Plot',
                        height=700,
                        xaxis=dict(tickangle=-90, automargin= True)
                    )
                )
            )
        ])
    elif tab == 'tab-2':
        items = [result.Subjects[0].MIXprop[0].iloc[j].values for j in range(len(result.Subjects[0].MIXprop[0]))]        
        return html.Div([
            html.H3('Heatmaps of estimated cell-type proportion values'),
            dcc.Graph(
                id='graph-2',
                figure=go.Figure(data=go.Heatmap(
                    z=np.transpose(items),
                    x=result.Subjects[0].MIXprop[0].index,
                    y=result.Subjects[0].MIXprop[0].columns,
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
    elif tab == 'tab-3':
        mean = np.mean(result.Subjects[0].ACCmetrix[0].IscBySbj.values)
        std = np.std(result.Subjects[0].ACCmetrix[0].IscBySbj.values)
        return html.Div([
            html.H3('Immuno Content Score (Population Based)'),
            dcc.Graph(
                id='graph-2',
                figure=go.Figure(
                    data=[go.Scatter(
                        x=result.Subjects[0].ACCmetrix[0].index, 
                        y=result.Subjects[0].ACCmetrix[0].IscBySbj.values, 
                        mode='markers'
                    )],
                    layout=go.Layout(
                        shapes=[
                            go.layout.Shape(
                                type="line",
                                x0=-1,
                                y0=mean,
                                x1=count,
                                y1=mean,
                                line=dict(
                                    color="red",
                                    width=2,
                                    dash="dashdot",
                                ),
                            ),
                            go.layout.Shape(
                                type="line",
                                x0=-1,
                                y0=(mean+2*std),
                                x1=count,
                                y1=(mean+2*std),
                                line=dict(
                                    color="blue",
                                    width=2,
                                    dash="dashdot",
                                ),
                            ),
                            go.layout.Shape(
                                type="line",
                                x0=-1,
                                y0=(mean-2*std),
                                x1=count,
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

@app.callback(Output('tabs2-content', 'children'),
              [Input('tabs2', 'value')])
def render_content2(tab):

    ctx = dash.callback_context
    if not ctx.triggered[0]['value']:
        return no_update

    global result

    if tab == 'tab2-1':
        return html.Div([
            html.H4('Finished Process'),
            html.A('Download result', href='/download_result/')
        ])
    elif tab == 'tab2-2':
        absolute = result.Subjects[0].MIXabs[0].reset_index()
        proportions = result.Subjects[0].MIXprop[0].reset_index()
        metrics = result.Subjects[0].ACCmetrix[0].reset_index()
        return html.Div([
            #dcc.Tabs(id='tabs3', value='tab3-1', children=[
            #    dcc.Tab(label='Absolute', value='tab3-1'),
            #    dcc.Tab(label='Proportions', value='tab3-2'),
            #    dcc.Tab(label='Metrics', value='tab3-3'),
            #]),
            html.Div([
                html.H1(children='Absolute'),
                dt.DataTable(id='table-absolute', data=absolute.to_dict('records'), columns = [{"name": i, "id": i} for i in absolute.columns], style_table={'overflowX': 'scroll'})
            ]),
            html.Div([
                html.H1(children='Proportions'),
                dt.DataTable(id='table-proportions', data=proportions.to_dict('records'), columns = [{"name": i, "id": i} for i in proportions.columns], style_table={'overflowX': 'scroll'})
            ]),
            html.Div([
                html.H1(children='Metrics'),
                dt.DataTable(id='table-metrics', data=metrics.to_dict('records'), columns = [{"name": i, "id": i} for i in metrics.columns], style_table={'overflowX': 'scroll'})
            ])
        ])
    elif tab == 'tab2-3':
        count = len(result.Subjects[0].MIXprop[0])
        xLabel = result.Subjects[0].MIXprop[0].index
        columns = result.Subjects[0].MIXprop[0].columns 
        items = [result.Subjects[0].MIXprop[0].iloc[j].values for j in range(len(result.Subjects[0].MIXprop[0]))]
        mean = np.mean(result.Subjects[0].ACCmetrix[0].IscBySbj.values)
        std = np.std(result.Subjects[0].ACCmetrix[0].IscBySbj.values)
        return html.Div([
            #dcc.Tabs(id='tabs', value='tab-1', children=[
            #    dcc.Tab(label='Bar Plot', value='tab-1'),
            #    dcc.Tab(label='Heatmaps', value='tab-2'),
            #    dcc.Tab(label='Immuno Content Score', value='tab-3'),
            #]),
            #html.Div(id='tabs-content')
               
            html.Div([
                html.H3('Bar Plot Subject-Proportions'),
                dcc.Graph(
                    id='graph-1-tabs',
                    figure=go.Figure(                    
                        data=[go.Bar(x=xLabel, y=[result.Subjects[0].MIXprop[0].iloc[j].values[i] for j in range(count)], name = columns[i]) for i in range(len(columns))],
                        layout=go.Layout(
                            barmode='relative',
                            title_text='Bar Plot',
                            height=700,
                            xaxis=dict(tickangle=-90, automargin= True)
                        )
                    )
                )
            ]),
            html.Div([
                html.H3('Heatmaps of estimated cell-type proportion values'),
                dcc.Graph(
                    id='graph-2',
                    figure=go.Figure(data=go.Heatmap(
                        z=np.transpose(items),
                        x=result.Subjects[0].MIXprop[0].index,
                        y=result.Subjects[0].MIXprop[0].columns,
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
            ]),
            html.Div([
                html.H3('Immuno Content Score (Population Based)'),
                dcc.Graph(
                    id='graph-2',
                    figure=go.Figure(
                        data=[go.Scatter(
                            x=result.Subjects[0].ACCmetrix[0].index, 
                            y=result.Subjects[0].ACCmetrix[0].IscBySbj.values, 
                            mode='markers'
                        )],
                        layout=go.Layout(
                            shapes=[
                                go.layout.Shape(
                                    type="line",
                                    x0=-1,
                                    y0=mean,
                                    x1=count,
                                    y1=mean,
                                    line=dict(
                                        color="red",
                                        width=2,
                                        dash="dashdot",
                                    ),
                                ),
                                go.layout.Shape(
                                    type="line",
                                    x0=-1,
                                    y0=(mean+2*std),
                                    x1=count,
                                    y1=(mean+2*std),
                                    line=dict(
                                        color="blue",
                                        width=2,
                                        dash="dashdot",
                                    ),
                                ),
                                go.layout.Shape(
                                    type="line",
                                    x0=-1,
                                    y0=(mean-2*std),
                                    x1=count,
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
        ])     

#@app.callback([Output('tabs3-content', 'data'), Output('tabs3-content', 'columns')],
#              [Input('tabs3', 'value')])
#def update_data(tab):
#    global result
#    absolute = result.Subjects[0].MIXabs[0].reset_index()
#    proportions = result.Subjects[0].MIXprop[0].reset_index()
#    metrics = result.Subjects[0].ACCmetrix[0].reset_index()
#    if tab == 'tab3-1':
#        return [absolute.to_dict('records'), [{"name": i, "id": i} for i in absolute.columns]]
#    elif tab == 'tab3-2':
#        return [proportions.to_dict('records'), [{"name": i, "id": i} for i in proportions.columns]]
#    elif tab == 'tab3-3':
#        return [metrics.to_dict('records'), [{"name": i, "id": i} for i in metrics.columns]]
#
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    
    global expression, filename_expression

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            expression = io.BytesIO(decoded)
            
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    filename_expression = filename
    
    return html.Div([
        html.P('Selected:' + filename)
    ])


@app.callback(Output('loading-output-1', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(
        Output("loading-output-2", "children"),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('signature-input', 'value'),
     dash.dependencies.State('cpu-slider', 'value'),
     dash.dependencies.State('population-input', 'value')])
def update_output(n_clicks, signature, cpu, population):
   
    global expression, result, pValues, tableMetrics, urlLm22, urlTil10
    
    if n_clicks is not None:
        
        if signature == 'LM22':
            X = pd.read_excel(find_data_file(urlLm22), sheet_name = 0)
        elif signature == 'TIL10':
            X = pd.read_excel(find_data_file(urlTil10), sheet_name = 0)
        
        Y = pd.read_excel(expression, sheet_name = 0) 
        
        #if __name__ == '__main__':            
        #if __name__ == 'app':
        if True:
            result, pValues = Mixture.Mixture(X, Y , cpu, int(population), '')
            
            metrics = result.Subjects[0].ACCmetrix[0].reset_index()
            
        children = [
            html.A('Download', href='/download_result/', className='custom-tab-button'),   
            dcc.Tabs(id='tabs2', value='tab2-2', children=[
                #dcc.Tab(label='Download', value='tab2-1', 
                #className='custom-tab',
                #selected_className='custom-tab--selected'),
                dcc.Tab(label='Tables', value='tab2-2',
                className='custom-tab',
                selected_className='custom-tab--selected'),
                dcc.Tab(label='Plots', value='tab2-3',
                className='custom-tab',
                selected_className='custom-tab--selected'),
            ], parent_className='custom-tabs'),
            html.Div(id='tabs2-content')
        ]
        
        return children
    
@app.server.route('/download_result/')
def download_excel ():
    
    global result, pValues, filename_expression
    
    strIO = io.BytesIO()
    excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    result.Subjects[0].MIXabs[0].to_excel(excel_writer, sheet_name='Absolute')
    result.Subjects[0].MIXprop[0].to_excel(excel_writer, sheet_name='Proportions')
    result.Subjects[0].ACCmetrix[0].to_excel(excel_writer, sheet_name='Metrics')
    #if pValues is not None:
    #    pValues.to_excel(excel_writer, sheet_name='Pvalues')
    result.usedGenes[0].to_excel(excel_writer, sheet_name='UsedGenes', index=False)
    excel_writer.save()
    excel_data = strIO.getvalue()
    strIO.seek(0)  
    
    return send_file(strIO, attachment_filename='result_' + filename_expression, as_attachment=True)
