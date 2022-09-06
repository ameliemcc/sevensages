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
            'Drag and drop or ',
            html.A('select Excel spreadsheet')
        ]),
        # Allow multiple files to be uploaded
        multiple=True,
        className='upload-button'
    ),
    html.Div([
        'Download the manuscripts data file, modify it according to your needs, making no changes in column titles and '
        'completing the information for each column before saving it and uploading it above. '
    ], className='text-maker'),
    # output graph
    #future
    html.Div([
        html.Div(id='output-datatable-m'),
        html.Div(id='output-div-m-map'),
        html.Div([
            html.Div(id='output-div-m')], className='container-man-graph')
    ]),

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

            # for the map
            # make a copy of the full dataframe, just in case we need it again
            manuscripts_all_map = df

            # replace empty date spaces with nan
            manuscripts_all_map['date_start'].replace(' ', np.nan, inplace=True)
            manuscripts_all_map['date_end'].replace(' ', np.nan, inplace=True)
            manuscripts_all_map['iso-3'].replace(' ', np.nan, inplace=True)

            # remove whitespaces where necessary
            manuscripts_all_map['iso-3'].str.strip()

            # drop rows which don't have a value for date_start
            manuscripts_all_map.dropna(subset=['date_start'], inplace=True)

            manuscripts_all_map.dropna(subset=['iso-3'], inplace=True)

            # if no value for date_end, give it the same as date_start
            manuscripts_all_map['date_end'] = pd.to_numeric(manuscripts_all_map['date_end']).fillna(
                manuscripts_all_map['date_start']).astype(float)

            # calculate a date mean
            manuscripts_all_map['new_mean'] = (manuscripts_all_map['date_start'] + manuscripts_all_map['date_end']) / 2

            # deduce the century of production of the print
            rx = r'^(\d\d)'
            manuscripts_all_map['date_mean_str'] = manuscripts_all_map['new_mean'].astype(str)
            manuscripts_all_map['cent'] = manuscripts_all_map['date_mean_str'].str.extract(rx)
            manuscripts_all_map['cent'] = pd.to_numeric(manuscripts_all_map['cent']).astype(float) + 1

            # make a new dataframe in which the towns are counted by century
            df_manuscripts = (manuscripts_all_map['iso-3'].groupby(manuscripts_all_map['cent'])
                              .value_counts()
                              .reset_index(name='count'))

            df_manuscripts['language'] = manuscripts_all_map['language']

            df_manuscripts['cent'] = pd.to_numeric(df_manuscripts['cent']).astype(float)

            df_manuscripts = df_manuscripts.reset_index()

            def check(cent, label):
                if not df_manuscripts[
                    (df_manuscripts['cent'] == cent) & (df_manuscripts['iso-3'] == label)].index.tolist():
                    df_manuscripts.loc[len(df_manuscripts.index)] = [len(df_manuscripts.index), cent, label, 0, 'lang']
                else:
                    pass

            for x in range(13, 19):
                check(x, 'ITA')
                check(x, 'FRA')
                check(x, 'ESP')
                check(x, 'GBR')
                check(x, 'DEU')






    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Button(id="submit-button", children="Create Graph", className='button-2'),
        dcc.Store(id='stored-data', data=manuscripts_all_graph.to_dict('records')),
        html.Button(id="submit-button-map", children="Create map", className='button-4'),
        dcc.Store(id='stored-data-map', data=df_manuscripts.to_dict('records')),
    ], className='buttons-center')


@callback(Output('output-datatable-m', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@callback(Output('output-div-m', 'children'),
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

