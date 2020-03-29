import sys
import os

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from pages import index, validate

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

server = app.server
app.config['suppress_callback_exceptions'] = True
app.css.config.serve_locally = True

urlCss = 'assets/css/main.css'
urlLogo = 'assets/img/logo.svg'

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)

styleSheetFile =open(find_data_file(urlCss), "r")
logoFile = open(find_data_file(urlLogo), "r")

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
        ''' + str(styleSheetFile.read()) + '''
        </style>
    </head>
    <body>
        <header>
            ''' + str(logoFile.read()) + '''
            <nav role="menu">  
                <ul class="navigation">
                    <li><a href="/">Mixture</a></li>
                    <li><a href="/validate">Validate MS</a></li>
                </ul>
            </nav>
        </header>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.title = 'MixturePy'


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return index.layout
    elif pathname == '/validate':
        return validate.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)