import webbrowser

from waitress import serve
from app import server
from threading import Timer

def open_browser():
      webbrowser.open_new('http://127.0.0.1:8082/')

Timer(1, open_browser).start()
serve(server, port=8082, host='127.0.0.1')