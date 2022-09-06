import dash
from dash import html, dcc, callback, Input, Output
import base64
import io
import dash
from dash.dependencies import Input, Output, State

import plotly.express as px
import numpy as np
import pandas as pd
from pages.create_manuscripts_graph import config

dash.register_page(__name__)

layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
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
    # output graph
    html.Div(id='output-div'),
    html.Div(id='output-datatable'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            manuscripts_all_graph = df
            # replace empty date spaces with nan
            manuscripts_all_graph['date_start'].replace(' ', np.nan, inplace=True)
            manuscripts_all_graph['date_end'].replace(' ', np.nan, inplace=True)

            # remove initial and trailing whitespaces
            for col in manuscripts_all_graph.columns:
                try:
                    manuscripts_all_graph[col] = manuscripts_all_graph[col].str.strip()
                except AttributeError:
                    pass

            # drop rows which don't have a value for date_start or language
            manuscripts_all_graph.dropna(subset=['date_start'], inplace=True)
            manuscripts_all_graph.dropna(subset=['language'], inplace=True)

            # if no value for date_end, give it the same as date_start
            manuscripts_all_graph['date_end'] = pd.to_numeric(manuscripts_all_graph['date_end']).fillna(
                manuscripts_all_graph['date_start']).astype(int)
            manuscripts_all_graph['date_end'] = (manuscripts_all_graph['date_end']).astype(int)
            manuscripts_all_graph['date_start'] = (manuscripts_all_graph['date_start']).astype(int)
            # calculate a date mean
            manuscripts_all_graph['new_mean'] = (manuscripts_all_graph['date_start'] + manuscripts_all_graph[
                'date_end']) / 2





    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Button(id="submit-button", children="Create Graph", className='button-2'),
        dcc.Store(id='stored-data', data=manuscripts_all_graph.to_dict('records')),
    ])


@callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@callback(Output('output-div', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'))
            #  State('xaxis-data','value'),
              #State('yaxis-data', 'value')
# )
def make_graphs(n, data):
    if n is None:
       return dash.no_update
    else:
        mans_graph_fig = px.histogram(
                data,
                # range_x = [1300, 1650],
                x="new_mean",
                nbins=12,
                color='language',
                hover_data={'language': True, 'new_mean': True},
                labels={"language": "Language", "new_mean": "Dates", "count": "Count"},
                color_discrete_map={
                    "Dutch": '#c5abb5',
                    "English": '#abb5c5',
                    'French': '#a1797f',
                    "High German": '#86562f',
                    'Hungarian': '#762e21',
                    'Italian': '#7fa179',
                    'Polish': '#335537',
                    'Latin': '#565f73',
                    'Spanish': '#685794',
                    'Occitan': '#c4a599',
                    'Catalan': '#797fa1',
                    'Scots': '#335537',
                },
            )

        # print(data)
        return dcc.Graph(figure=mans_graph_fig, config=config, className='graph_style')

