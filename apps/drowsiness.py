from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import plotly.express as px
from app import app
from DrowsinessMonitor import States, DrowsinessMonitor

colors = {
    'background': 'rgba(0,0,0,0)',
    'text': '#ffffff'
}

monitor = DrowsinessMonitor.instance()


def getLeftEyeFigure():
    figure = px.line(
        monitor.leftEyeAggregation,
        x="timestamp",
        y="count",
        labels={
            "date": "Datum",
            "illuminance": "Anzahl"
        },
        color_discrete_sequence=px.colors.qualitative.Light24
    )
    return figure

def getRightEyeFigure():
    figure = px.line(
        monitor.rightEyeAggregation,
        x="timestamp",
        y="count",
        labels={
            "date": "Datum",
            "illuminance": "Anzahl"
        },
        color_discrete_sequence=px.colors.qualitative.Light24
    )
    return figure

def getMouthFigure():
    figure = px.line(
        monitor.mouthAggregation,
        x="timestamp",
        y="count",
        labels={
            "date": "Datum",
            "illuminance": "Anzahl"
        },
        color_discrete_sequence=px.colors.qualitative.Light24
    )
    return figure


def getStatus():
    if monitor.isSleeping():
        return 'Am Schlafen'
    elif monitor.isTired():
        return 'Müde'
    else:
        return 'Nicht müde'

def getBody():
    return [
                    html.Div(
                        className='container-info',
                        children=[
                            html.Div(
                                className='small-container',
                                children=[
                                    html.H3('Linkes Auge'),
                                    html.H2('Offen' if monitor.leftEyeState == States.OPEN else 'Geschlossen')
                                ]
                            ),
                            html.Div(
                                className='small-container',
                                children=[
                                    html.H3('Rechtes Auge'),
                                    html.H2('Offen' if monitor.rightEyeState == States.OPEN else 'Geschlossen')
                                ]
                            ),
                            html.Div(
                                className='small-container',
                                id='small-container-co2',
                                children=[
                                    html.H3('Mund'),
                                    html.H2('Offen' if monitor.mouthState == States.OPEN else 'Geschlossen')
                                ]
                            ),
                            html.Div(
                                className='small-container',
                                id='small-container-co2',
                                children=[
                                    html.H3('Status'),
                                    html.H2(getStatus())
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        className='container-wrapper',
                        children=[
                            html.Div(
                                className='medium-container',
                                children=[
                                    html.H2('Linkes Auge'),
                                    dcc.Graph(
                                        id='left-eye-graph',
                                        figure=getLeftEyeFigure(),
                                        style={'width': '95%', 'height': '80%', 'margin': '0% 2.5%'}
                                    )
                                ]
                            ),
                            html.Div(
                                className='medium-container',
                                children=[
                                    html.H2('Rechtes Auge'),
                                    dcc.Graph(
                                        id='right-eye-graph',
                                        figure=getRightEyeFigure(),
                                        style={'width': '95%', 'height': '80%', 'margin': '0% 2.5%'}
                                    )
                                ]
                            ),
                            html.Div(
                                className='medium-container',
                                children=[
                                    html.H2('Mund'),
                                    dcc.Graph(
                                        id='mouth-graph',
                                        figure=getMouthFigure(),
                                        style={'width': '95%', 'height': '80%', 'margin': '0% 2.5%'}
                                    )
                                ]
                            )
                        ]
                    )
                ]

def serveLayout():
    layout = html.Div(
        children=[
            html.Div(
                className='header',
                children=[
                    html.Div(
                        className='title',
                        children=[
                            html.H2('Drowsiness Dashboard'),
                            html.Span('LIVE'),
                        ]
                    ),
                    html.Div(
                        id='fps',
                        children=[
                            html.H2(f'FPS: {monitor.fps}'),
                        ]
                    )
                ]
            ),
            html.Div(
                className='body',
                id='body',
                children=getBody()
            ),
            dcc.Interval(
                id='interval-component',
                interval=333,  # in milliseconds
                n_intervals=0
            )
        ]
    )
    return layout


@app.callback(Output('body', 'children'),
              Input('interval-component', 'n_intervals'))
def update_body(n):
    return getBody()

@app.callback(Output('fps', 'children'),
              Input('interval-component', 'n_intervals'))
def update_body(n):
    return [
        html.H2(f'FPS: {monitor.fps}'),
    ]
