import base64
import datetime
import io
import Mixture

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from flask import send_file

import pandas as pd

expression = ''
filename_expression = ''
result = ''
pValues = ''

cores = 4
output = ''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.Div([
      html.H2('MIXTURE'),
      html.H5('an improved algorithm for immune tumor microenvironment estimation based on gene expression data')
    ]),
    html.Div([        
        html.P('Expression file:'),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select File', style={
                    'color': 'blue'
                })
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
        html.P('Population quantity:', style={
            'margin-top': '10px'
        }),
        dcc.Input(
            id='population-input',
            placeholder='Enter a value...',
            type='number',
            min='1',
            value=''
        ),
        html.Button('Submit', id='button', style = {
            'margin-top': '10px'
        }),
        html.Div(id='output-processing'),
        dcc.Loading(id="loading-2", children=[html.Div(id="loading-output-2")], type="default")
    ], style={
            'margin': '0px',
            'width': '30%',
            'background-color': '#F7F7F7',
            'padding': '20px',
            'border-radius': '15px',
            'display': '-webkit-flex',
            '-webkit-flex-direction': 'column',
            'display': 'flex',
            'flex-direction': 'column',
    })
], style = {
        'width':'100%',
        'display': '-webkit-flex',
        '-webkit-flex-direction': 'column',
        'display': 'flex',
        'flex-direction': 'column',
        'margin': '0px',
        'padding': '0px',
})


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
        html.H5('Expressions File:' + filename),
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
    dash.dependencies.State('population-input', 'value')])
def update_output(n_clicks, signature, population):
   
    global expression, result, pValues
    
    if n_clicks is not None:
        
        if signature == 'LM22':
            X = pd.read_excel('data/LM22Signature.xlsx', sheet_name = 0)
        elif signature == 'TIL10':
            X = pd.read_excel('data/TIL10_signature.xlsx', sheet_name = 0)
        
        Y = pd.read_excel(expression, sheet_name = 0) 
        
        if __name__ == '__main__':
            
            result, pValues = Mixture.Mixture(X, Y , 4, population, '')            
                      
                      
        children = [
            html.H4('Finish Processing'),
            html.A('Download result', href='/download_result/')
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
            html.P('Processing data...', style = {
                'margin-top': '10px'
            }),
            html.P('Signature: ' + str(signature), style = {
                'margin-top': '10px'
            }),
            html.P('Population based : ' + str(population), style = {
                'margin-top': '10px'
            })
        ]
        return children

if __name__ == '__main__':
    app.run_server(debug=True)