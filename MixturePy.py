import base64
import datetime
import io
import Mixture
import multiprocessing

import numpy as np

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from flask import send_file
import plotly.graph_objects as go

import pandas as pd

expression = ''
filename_expression = ''
result = ''
pValues = ''
tableMetrics = ''

cores = 4
output = ''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__)
server = app.server
app.config['suppress_callback_exceptions'] = True
app.css.config.serve_locally = True

app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='/assets/css/main.css'
    ),
    html.Div([
      html.Img(src='assets/img/logo_mixture.png', style = {
          'width': '300px'
      }),
      #html.H2('MIXTURE'),
      html.H6('an improved algorithm for immune tumor microenvironment estimation based on gene expression data', style = {
          'margin-top': '-20px'
      })
    ]),
    html.Div([
    html.Div([        
        html.P('Expression file:'),
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
            min='1',
            value=''
        ),
        html.P('CPUs:', style={
            'margin-top': '10px'
        }),
        dcc.Slider(
            id='cpu-slider',
            min=1,
            max=multiprocessing.cpu_count(),
            step=1,
            marks={i: '{}'.format(i) for i in range(multiprocessing.cpu_count()+1)},
            value=multiprocessing.cpu_count()
        ),  
        html.Button('Submit', id='button', style = {
            'margin-top': '30px'
        })        
    ], style={
            '-webkit-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            '-moz-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'margin': '0px',
            'flex': '1',
            'height':'100%',
            'background-color': '#FFFFFF',
            'padding': '20px',
            'border-radius': '5px',
            'display': '-webkit-flex',
            '-webkit-flex-direction': 'column',
            'display': 'flex',
            'flex-direction': 'column',
    }),
    html.Div([
        html.Div(id='output-processing'),
        dcc.Loading(id='loading-2', children=[html.Div(id='loading-output-2')], type='default')        
    ], style={
            '-webkit-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            '-moz-box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'box-shadow': '1px 2px 3px 1px rgba(0,0,0,0.25)',
            'margin': '0px',
            'margin-left': '10px',
            'flex': '3',
            'height':'100%',
            'background-color': '#FFFFFF',
            'padding': '20px',
            'border-radius': '5px',
            'display': '-webkit-flex',
            '-webkit-flex-direction': 'column',
            'display': 'flex',
            'flex-direction': 'column',
    })
    ], style = {
        'width':'100%',
        'height':'100%',
        'display': '-webkit-flex',
        '-webkit-flex-direction': 'row',
        'display': 'flex',
        'flex-wrap': 'wrap',
        'flex-direction': 'row',
        'margin': '0px',
        'padding': '0px',
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
                        height=700
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
                        height=700
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
                        height=700
                    )
                )
            )
        ])

@app.callback(Output('tabs2-content', 'children'),
              [Input('tabs2', 'value')])
def render_content2(tab):
    if tab == 'tab2-1':
        return html.Div([
            html.H4('Finished Process'),
            html.A('Download result', href='/download_result/')
        ])
    elif tab == 'tab2-2':
        return html.Div([
            dcc.Tabs(id='tabs3', value='tab3-1', children=[
                dcc.Tab(label='Absolute', value='tab3-1'),
                dcc.Tab(label='Proportions', value='tab3-2'),
                dcc.Tab(label='Metrics', value='tab3-3'),
            ]),
            dt.DataTable(id='tabs3-content', style_table={'overflowX': 'scroll'})
        ])
    elif tab == 'tab2-3':
        return html.Div([
            dcc.Tabs(id='tabs', value='tab-1', children=[
                dcc.Tab(label='Bar Plot', value='tab-1'),
                dcc.Tab(label='Heatmaps', value='tab-2'),
                dcc.Tab(label='Immuno Content Score', value='tab-3'),
            ]),
            html.Div(id='tabs-content')
        ])     

@app.callback([Output('tabs3-content', 'data'), Output('tabs3-content', 'columns')],
              [Input('tabs3', 'value')])
def update_data(tab):
    global result
    absolute = result.Subjects[0].MIXabs[0].reset_index()
    proportions = result.Subjects[0].MIXprop[0].reset_index()
    metrics = result.Subjects[0].ACCmetrix[0].reset_index()
    if tab == 'tab3-1':
        return [absolute.to_dict('records'), [{"name": i, "id": i} for i in absolute.columns]]
    elif tab == 'tab3-2':
        return [proportions.to_dict('records'), [{"name": i, "id": i} for i in proportions.columns]]
    elif tab == 'tab3-3':
        return [metrics.to_dict('records'), [{"name": i, "id": i} for i in metrics.columns]]

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
            #df = pd.read_excel(io.BytesIO(decoded), sheet_name = 0)
            expression = io.BytesIO(decoded)
            
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    #df_expression = df
    
    filename_expression = filename
    
    return html.Div([
        html.P('Selected:' + filename),
        #html.H6(datetime.datetime.fromtimestamp(date)),

        #dash_table.DataTable(
        #    data=df.to_dict('records'),
        #    columns=[{'name': i, 'id': i} for i in df.columns]
        #),

        #html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        #html.Div('Raw Content'),
        #html.Pre(contents[0:200] + '...', style={
        #    'whiteSpace': 'pre-wrap',
        #    'wordBreak': 'break-all'
        #})
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
   
    global expression, result, pValues, tableMetrics
    
    if n_clicks is not None:
        
        if signature == 'LM22':
            X = pd.read_excel('data/LM22Signature.xlsx', sheet_name = 0)
        elif signature == 'TIL10':
            X = pd.read_excel('data/TIL10_signature.xlsx', sheet_name = 0)
        
        Y = pd.read_excel(expression, sheet_name = 0) 
        
        if __name__ == '__main__':            
            result, pValues = Mixture.Mixture(X, Y , cpu, population, '')
            
            metrics = result.Subjects[0].ACCmetrix[0].reset_index()
            
        children = [            
            dcc.Tabs(id='tabs2', value='tab2-1', children=[
                dcc.Tab(label='Download', value='tab2-1'),
                dcc.Tab(label='Tables', value='tab2-2'),
                dcc.Tab(label='Plots', value='tab2-3'),
            ]),
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
    pValues.to_excel(excel_writer, sheet_name='Pvalues')
    result.usedGenes[0].to_excel(excel_writer, sheet_name='UsedGenes', index=False)
    excel_writer.save()
    excel_data = strIO.getvalue()
    strIO.seek(0)  
    
    return send_file(strIO, attachment_filename='result_' + filename_expression, as_attachment=True)

#@app.callback(
#    dash.dependencies.Output('button', 'style'),
#    [dash.dependencies.Input('button', 'n_clicks'),
#    Input('upload-data', 'contents')])
#def update_output_hidden_button(n_clicks, contents):
#    if n_clicks is not None:
#        return {'display': 'none'}
#    if contents is not None:
#        return {'display': 'block'}

@app.callback(
    dash.dependencies.Output('output-processing', 'children'), 
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('signature-input', 'value'),
    dash.dependencies.State('population-input', 'value')])
def input_triggers_spinner_2(value, signature, population):
    if value is not None:
        children = [
            #html.P('Processing data...', style = {
            #    'margin-top': '10px'
            #}),
            #html.P('Signature: ' + str(signature), style = {
            #    'margin-top': '10px'
            #}),
            #html.P('Population based : ' + str(population), style = {
            #    'margin-top': '10px'
            #})
        ]
        #return children

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)