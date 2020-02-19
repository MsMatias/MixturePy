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
from plotly.subplots import make_subplots
from scipy import stats
from score import Score

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
result3 = None

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
        html.P('False discovery test', style={
            'border-top': '1px black solid',
            'margin-top': '20px'
        }),
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
        html.P('Max number of cell lines in the mixture simulated sample:', style={
            'margin-top': '10px'
        }),        
        dcc.RangeSlider(
            id='lines_slider',
            min=2,
            max=(len(dataFrameSignature.columns)-1),
            step=1,
            # marks={i: '{}'.format(i) for i in range(len(dataFrameSignature.columns)+1)},
            marks={
              2: '2',
              round((len(dataFrameSignature.columns)-1)/2): str(round((len(dataFrameSignature.columns)-1)/2)),
              (len(dataFrameSignature.columns)-1): str((len(dataFrameSignature.columns)-1))
            },
            value=[2, round((len(dataFrameSignature.columns)-1)*0.75)]
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
     dash.dependencies.State('cpu-slider', 'value'),
     dash.dependencies.State('check_celllines', 'value')])
def update_output(n_clicks, lines_slider, cpu, celllines):
   
    global signature, dataFrameSignature, result1, pValues1, tableMetrics1, result2, pValues2, tableMetrics2, subjects, betas, lines, estimate_lines, ids, result3
    
    if n_clicks is not None:

        X = dataFrameSignature

        Y = dataFrameSignature
        
        #if __name__ == '__main__':            
        #if __name__ == 'app':
        if True:

            rango = 1000

            lines = lines_slider

            # Escenario 1
            result1, pValues1 = Mixture.Mixture(X, Y , cpu, 1, '', method=Score)            
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

            result2, pValues2 = Mixture.Mixture(X, Y2 , cpu, 1, '', method=Score) 
            
            betasSim = result2.Subjects[0].MIXprop[0].to_numpy(copy = True)           
            estimate_lines = pd.DataFrame([(betasSim[i] > 0).sum() for i in range(rango)])     
            metrics2 = result2.Subjects[0].ACCmetrix[0].reset_index()

            vector = [len(x[1]) for x in subjects]
            ids = pd.DataFrame(np.column_stack(vector))   

            #Celllines analysis
            if len(celllines) == 1:
                Y3 = pd.read_excel(dataCelllines, sheet_name = 0)
                result3, pValues3 = Mixture.Mixture(X, Y3 , cpu, 1, '', method=Score)
                #cc = pd.read_excel('./data/outputCellines(2).xlsx', sheet_name = 0) 
                #cc.index = cc.iloc[:,0].astype(int)
                #cc.index.name = 'Subjects'
                #cc2 = pd.read_excel('./data/outputCellines(2).xlsx', sheet_name = 1)
                #cc2.index = cc2.iloc[:,0].astype(int)
                #cc2.index.name = 'Subjects'
                #result3 = [cc.iloc[:, 1:], cc2.iloc[:, 1:]]
                children_tabs = [
                    dcc.Tab(label='Similation Test', value='tab4-1', style={'padding': '0px'}, selected_style={'padding': '0px'}),
                    dcc.Tab(label='False Discovery Test', value='tab4-2', style={'padding': '0px'}, selected_style={'padding': '0px'})
                ]
            else:
                children_tabs = [
                    dcc.Tab(label='Similation Test', value='tab4-1', style={'padding': '0px'}, selected_style={'padding': '0px'})
                ]
            
        children = [            
            dcc.Tabs(id='tabs4', value='tab4-1', children=[
                dcc.Tab(label='Similation Test', value='tab4-1', style={'padding': '0px'}, selected_style={'padding': '0px'}),
                dcc.Tab(label='False Discovery Test', value='tab4-2', style={'padding': '0px'}, selected_style={'padding': '0px'})
            ], style={
                'height': '35px'
            }),
            html.Div(id='tabs4-content')
        ]

        children = []


        # Similation Test
        children.append(html.H1('Similation Test'))

        # Bland Altman analysis

        # Proportions
        children.append(blandAltmanGraph(result2.Subjects[0].MIXprop[0], 'pro'))

        # Absolute
        children.append(blandAltmanGraph(result2.Subjects[0].MIXprop[0], 'per'))
        
        # Correlation analysis
        children.append(correlationAnalysisGraph(result2.Subjects[0].MIXprop[0]))

        # Self Test
        children.append(selfTestGraph(result1.Subjects[0].MIXprop[0]))

        # Number of Cell Types
        children.append(numberOfCellTypeGraph(estimate_lines, ids))

        if len(celllines) == 1:

            # False Discovery Test
            children.append(html.H1('False Discovery Test'))

            # Number of Cell Types
            children.append(numberOfCellTypeFDTGraph(result3[1]))

            # Absolute Beta Estimation
            children.append(absoluteBetaEstimation(result3[0]))

        return children

def numberOfCellTypeGraph (data, ids):
    items = [go.Box(y=data[(ids.values == j)[0]][0], name = str(j)) for j in range(lines[0],lines[1])]        
    return html.Div([
        html.Hr(),
        dcc.Graph(
            id='graph-3',
            figure=go.Figure(data=items,
                layout=go.Layout(
                    title=go.layout.Title(
                        text= "Number of Cell Types",
                        font=dict(
                            family='Courier New, monospace',
                            size=20,
                            color='#000000'
                        ),
                        y=0.9,
                        x=0.5,
                        xanchor= 'center',
                        yanchor= 'top'
                    ),
                    xaxis=go.layout.XAxis(
                        title=go.layout.xaxis.Title(
                            text='True number of coefficients',
                            font=dict(
                                family='Courier New, monospace',
                                size=14,
                                color='#7f7f7f'
                            )
                        ),
                        tickangle=0,
                        automargin= True
                    ),
                    yaxis=go.layout.YAxis(
                        title=go.layout.yaxis.Title(
                            text='Estimated number of coefficients',
                            font=dict(
                                family='Courier New, monospace',
                                size=14,
                                color='#7f7f7f'
                            )
                        )
                    ),
                    height=700,
                )
            )
        )
    ])

def selfTestGraph (data):
    items = [data.iloc[j].values for j in range(len(data))]        
    return html.Div([
        html.Hr(),
        dcc.Graph(
            id='graph-3',
            figure=go.Figure(data=go.Heatmap(
                z=np.transpose(items),
                x=data.index,
                y=data.columns,
                colorscale= [
                    [0.0, 'rgb(255,255,255)'],
                    [1.0, 'rgb(255,0,0)']
                ]
            ),
                layout=go.Layout(
                    title=go.layout.Title(
                        text= "Self Test",
                        font=dict(
                            family='Courier New, monospace',
                            size=20,
                            color='#000000'
                        ),
                        y=0.9,
                        x=0.5,
                        xanchor= 'center',
                        yanchor= 'top'
                    ),
                    xaxis=go.layout.XAxis(
                        title=go.layout.xaxis.Title(
                            text='Estimated Immune Cell Types',
                            font=dict(
                                family='Courier New, monospace',
                                size=14,
                                color='#7f7f7f'
                            )
                        ),
                        tickangle=-90,
                        automargin= True
                    ),
                    yaxis=go.layout.YAxis(
                        title=go.layout.yaxis.Title(
                            text='True Immune Cell Types present in the Signature Matrix',
                            font=dict(
                                family='Courier New, monospace',
                                size=14,
                                color='#7f7f7f'
                            )
                        )
                    ),
                    height=700
                )
            )
        )
    ])

def correlationAnalysisGraph (data):
    betasSim = data.T.to_numpy(copy=True)
    betasSim = betasSim.flatten()
    betasHat = betas.to_numpy(copy=True)
    betasHat = betasHat.flatten()
    slope, intercept, r_value, p_value, std_err = stats.linregress(betasHat, betasSim)
    return html.Div([
        html.Hr(),
        dcc.Graph(
            id='graph-3',
            figure=go.Figure(data=[go.Scattergl(
                x = betasHat,
                y = betasSim,
                mode='markers',
                marker_color='rgba(0, 0, 0, .9)'
            ),
            go.Scatter(x=betasHat, y=intercept + slope*betasHat,
                mode='lines',
                name='lines')
            ],
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
                    title=go.layout.Title(
                        text= "Correlation Analysis",
                        font=dict(
                                family='Courier New, monospace',
                                size=20,
                                color='#000000'
                        ),
                        y=0.9,
                        x=0.5,
                        xanchor= 'center',
                        yanchor= 'top'
                    ),
                    xaxis=go.layout.XAxis(
                        title=go.layout.xaxis.Title(
                            text='True Simulated Coefficient',
                            font=dict(
                                family='Courier New, monospace',
                                size=14,
                                color='#7f7f7f'
                            )
                        ),
                        tickangle=-90,
                        automargin= True
                    ),
                    yaxis=go.layout.YAxis(
                        title=go.layout.yaxis.Title(
                            text='Estimated Coefficients',
                            font=dict(
                                family='Courier New, monospace',
                                size=14,
                                color='#7f7f7f'
                            )
                        )
                    ),
                    height=700
                )
            )
        )
    ])

def blandAltmanGraph (data, value):
    count = len(data)
    betasSim = data.T.to_numpy(copy=True)
    betasSim = betasSim.flatten()
    betasHat = betas.to_numpy(copy=True)
    betasHat = betasHat.flatten()
    mean = np.mean(betasSim - betasHat)
    std = np.std(betasSim - betasHat)
    if value == 'pro':                
        xx = betasHat
        yy = betasSim - betasHat
    elif value == 'per':        
        xx = betasHat
        m = (betasSim + betasHat)/2
        yy = (betasSim - betasHat)
        yy = 100 * np.divide(yy, m, out=np.zeros_like(yy), where=m!=0)

    slope, intercept, r_value, p_value, std_err = stats.linregress(xx, yy)

    fig = make_subplots(rows=1, cols=2, column_widths=[0.7, 0.3], shared_yaxes=True)
    fig.add_trace(go.Scattergl(
                x = xx,
                y = yy,
                mode='markers',
                marker_color='rgba(0, 0, 0, .9)'
                ),row=1, col=1)
    fig.add_trace(go.Scattergl(x=xx, y=intercept + slope*xx,
                    mode='lines',
                    name='lines'),row=1, col=1)
    fig.add_trace(go.Violin(y=yy, box_visible=True, line_color='black',
                               meanline_visible=True, fillcolor='blue', opacity=0.8,
                               x0='Violin'),row=1, col=2)

                               
    fig['layout'].update(
        title_text="Bland-Altman Analysis",
        title_font_family='Courier New, monospace',
        title_font_size=20,
        title_font_color='#000000',
        title_xanchor='center',
        title_yanchor = 'top',
        title_x = 0.5,
        title_y = 0.9,
        xaxis_title='Estimated Coefficients',
        yaxis_title='Error',
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#7f7f7f"
        ),
        height=700,
        shapes=[
        go.layout.Shape(
            type="line",
            xref="x1",
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
            xref="x1",
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
            xref="x1",
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
    ])

            
    return dcc.Graph(
        id='graph-3',
        figure=fig
        )

def numberOfCellTypeFDTGraph (data):
    dfSum = data.sum(axis=1)
    dfSum = dfSum.where(dfSum > 0).notna()
    lines = data[dfSum]
    items = [go.Violin(y=lines.iloc[:, j], name = lines.iloc[:, j].name) for j in range(len(lines.columns))]
    return html.Div([
        dcc.Graph(
            id='graph-abe',
            figure=go.Figure(data=items,
                layout=go.Layout(
                    height=700,
                    xaxis=dict(tickangle=-90, automargin= True)
                )
            )
        )
    ])

def absoluteBetaEstimation (data):
    items = go.Box(y=data.values.flatten(), name = 1)
        
    return html.Div([
        dcc.Graph(
            id='graph-abe',
            figure=go.Figure(data=items,
                layout=go.Layout(
                    height=700,
                    xaxis=dict(tickangle=-90, automargin= True)
                )
            )
        )
    ])

@app.callback(Output('tabs6-content', 'children'),
              [Input('tabs6', 'value')])
def render_content1(tab):
    global result3
    dfSum = result3[1].sum(axis=1)
    dfSum = dfSum.where(dfSum > 0).notna()
    lines = result3[1][dfSum]
    
    if tab == 'tab6-2':
        items = go.Box(y=result3[0].values.flatten(), name = 1)
        
        return html.Div([
            dcc.Graph(
                id='graph-abe',
                figure=go.Figure(data=items,
                    layout=go.Layout(
                        height=700,
                        xaxis=dict(tickangle=-90, automargin= True)
                    )
                )
            )
        ])
    elif tab == 'tab6-1':
        items = [go.Violin(y=lines.iloc[:, j], name = lines.iloc[:, j].name) for j in range(len(lines.columns))]
        return html.Div([
            dcc.Graph(
                id='graph-abe',
                figure=go.Figure(data=items,
                    layout=go.Layout(
                        height=700,
                        xaxis=dict(tickangle=-90, automargin= True)
                    )
                )
            )
        ])