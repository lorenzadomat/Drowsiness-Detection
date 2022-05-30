from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from threading import Thread
from DrowsinessDetector import DrowsinessDetector

from apps import drowsiness

from app import app

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    return drowsiness.serveLayout()


if __name__ == '__main__':
    detector = DrowsinessDetector()
    thread1 = Thread(target=app.run_server)

    thread1.start()
    detector.runWithFaceMap()