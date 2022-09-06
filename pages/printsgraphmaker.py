import dash
from dash import html, dcc, callback, Input, Output
import base64
import io
import dash
from dash.dependencies import Input, Output, State

import plotly.express as px
import numpy as np
import pandas as pd
from pages.create_prints_graph import config
from pages.create_prints_map import config_map


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
    # output graph
    html.Div(id='output-div-p'),
    html.Div(id='output-div-p-map'),
    html.Div(id='output-datatable-p'),
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
        df = df.drop(df.index[[0]])
        prints_all_map = df.set_index('print_town', drop=False)
        prints_all_map.index.names = ['index']

        # replace empty date spaces with nan
        prints_all_map['date_start'].replace(' ', np.nan, inplace=True)
        prints_all_map['date_end'].replace(' ', np.nan, inplace=True)
        prints_all_map['lat'].replace(' ', np.nan, inplace=True)

        # remove whitespaces where necessary
        prints_all_map['print_town'].str.strip()

        # drop rows which don't have a value for date_start
        prints_all_map.dropna(subset=['date_start'], inplace=True)

        prints_all_map.dropna(subset=['language'], inplace=True)

        # drop rows which don't have a value for lat
        # prints_all_map.dropna(subset=['lat'], inplace=True)

        # if no value for date_end, give it the same as date_start
        prints_all_map['date_end'] = pd.to_numeric(prints_all_map['date_end']).fillna(
            prints_all_map['date_start']).astype(float)

        # calculate a date mean
        prints_all_map['date_mean'] = (prints_all_map['date_start'] + prints_all_map['date_end']) / 2

        # deduce the century of production of the print
        rx = r'^(\d\d)'
        prints_all_map['date_mean_str'] = prints_all_map['date_mean'].astype(str)
        prints_all_map['century'] = prints_all_map['date_mean_str'].str.extract(rx)
        prints_all_map['century'] = pd.to_numeric(prints_all_map['century']).astype(float) + 1

        # make a new dataframe in which the towns are counted by century
        df_prints = (prints_all_map['print_town'].groupby(prints_all_map['century'])
                     .value_counts()
                     .reset_index(name='count'))

        df_prints = df_prints.set_index('print_town', drop=False)
        df_prints.index.names = ['index']

        # latitude column
        df_prints = df_prints.assign(lati=0)
        df_prints = df_prints.assign(longi=0)

        # get latitude from prints_all_map and add it to new df_prints
        for index in df_prints['print_town']:
            seriess = (prints_all_map.loc[index, 'lat'])
            results = []
            try:
                for y in seriess:
                    results.append(y)
            except TypeError:
                results.append(seriess)
            df_prints['lati'].loc[index] = results[0]

        # get longitude from prints_all_map and add it to new df_prints
        for index in df_prints['print_town']:
            seriess = (prints_all_map.loc[index, 'long'])
            results = []
            try:
                for y in seriess:
                    results.append(y)
            except TypeError:
                results.append(seriess)
            df_prints['longi'].loc[index] = results[0]

        df_prints['century'] = pd.to_numeric(df_prints['century']).astype(float)

        df_prints = df_prints.reset_index()
        all_data_diffq = (df_prints["count"].max() - df_prints["count"].min()) / 11 + 1
        df_prints["scale"] = ((df_prints["count"] - df_prints["count"].min()) + 1 / all_data_diffq).astype(int)


    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Button(id="submit-button", children="Create graph", className='button-4'),
        dcc.Store(id='stored-data', data=prints_all_map.to_dict('records')),
        html.Button(id="submit-button-map", children="Create map", className='button-4'),
        dcc.Store(id='stored-data-map', data=df_prints.to_dict('records')),

    ], className='buttons-center')



@callback(Output('output-datatable-p', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

# graph maker
@callback(Output('output-div-p', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data')
          )
            #  State('xaxis-data','valuƒhoe'),
              #State('yaxis-data', 'value')
# )
def make_graphs(n, data):
    if n is None:
       return dash.no_update
    else:
        print_graph_fig = px.histogram(
            data,
            range_x=[1400, 1650],
            x="date_mean",
            nbins=12,
            color='language',
            color_discrete_map={
                "Dutch": '#c5abb5',
                "English": '#abb5c5',
                'French': '#a1797f',
                "German": '#86562f',
                'Hungarian': '#762e21',
                'Italian': '#7fa179',
                'Polish': '#335537',
                'Latin': '#565f73',
                'Spanish': '#685794',
                'Occitan': '#c4a599'
            },
            hover_data={'language': True, 'date_mean': True},
            labels={"language": "Language", "date_mean": "Dates", "count": "Count"}
        )
        # print(data)
        return dcc.Graph(figure=print_graph_fig, config=config, className='graph_style')

# map maker




@callback(Output('output-div-p-map', 'children'),
              Input('submit-button-map','n_clicks'),
              State('stored-data-map','data')
          )
def make_maps(n, data):
    if n is None:
        return dash.no_update
    else:
        return html.Div([
            html.Div(
                dcc.Graph(id='graph-with-slider-map', config=config_map),
                className='create-map-style'),
            html.Div(
            dcc.Slider(
                min = 15,
                max = 17,
              #int(data['century']).min(),
               # int(data['century']).max(),
                step=None,
                verticalHeight=50,
                value=15,
                id='year-slider',
                className = 'slider',
                marks={15: {'label': '15th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                       16: {'label': '16th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                       17: {'label': '17th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                       }
            ), className='create-map-style-slider'),
]),



@callback(
    Output('graph-with-slider-map', 'figure'),
    Input('year-slider', 'value'),
    State('stored-data-map', 'data'))
def update_figure(selected_year, data):
    #filtered_df = (data.loc[data['century'] == selected_year])
    pd_df = pd.DataFrame.from_dict(data)
    filtered_df = (pd_df.loc[pd_df['century'] == selected_year])
    # create a scale column for the bubbles
    all_data_diffq = (filtered_df["count"].max() - filtered_df["count"].min()) / 11 + 1
    filtered_df["scale"] = (filtered_df["count"] - filtered_df["count"].min()) + 1 / all_data_diffq
#    filtered_df["scale"] = df_prints["scale"]

    fig = px.scatter_geo(
        filtered_df,
        lat=filtered_df['lati'],
        lon=filtered_df['longi'],
        text=filtered_df['print_town'],
        size=filtered_df['scale'],
        size_max=11,
        projection='equirectangular',
        hover_data={'scale': False, 'print_town': False, 'lati': False, 'longi':False, 'count':True},
        labels = {"count" : "Count"},
        color_discrete_sequence=['#a1797f'],
    )

    fig.update_traces(textposition="top center", mode='markers+text',
                      textfont_size = 10)

    lat_foc = 46.20222
    lon_foc = 6.14569

    fig.update_layout(legend_title_text=' ',
                      margin=dict(l=0, r=0, t=0, b=0),
                      autosize=True,
                      font_family='Helvetica, Arial, sans-serif',
                      paper_bgcolor="#c4a599",
                      hoverlabel=dict(bordercolor='rgba(0,0,0,0)', font_color='white',
                                      font_family='Helvetica, Arial, sans-serif', font_size=12),
                      transition_duration=500,
                      geo=dict(
                          projection_scale=7,  # this is kind of like zoom
                          center=dict(lat=lat_foc, lon=lon_foc),  # this will center on the point

                      ))

    fig.update_geos(
        showcoastlines=True,
        showcountries=False,
        showocean=True,
        landcolor="#abb5c5",
        oceancolor="#797fa1"
    )

    return fig
