import dash
from dash import html, dcc, callback, Input, Output
import base64
import io
import dash
from dash.dependencies import Input, Output, State
from pages.create_prints_map import config_map
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

    html.Div([
        html.Div(id='output-datatable-m'),
        html.Div(id='output-div-m-map'),
        html.Div([
            html.Div(id='output-div-m')], className='container-print-graph')
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
            manuscripts_all_map = manuscripts_all_map.set_index('language', drop=False)
            manuscripts_all_map.index.names = ['index']

            # replace empty date spaces with nan
            manuscripts_all_map['date_start'].replace(' ', np.nan, inplace=True)
            manuscripts_all_map['date_end'].replace(' ', np.nan, inplace=True)
            manuscripts_all_map['language'].replace(' ', np.nan, inplace=True)

            # remove whitespaces where necessary
            manuscripts_all_map['iso-3'].str.strip()
            manuscripts_all_map['language'].str.strip()


            # drop rows which don't have a value for date_start
            manuscripts_all_map.dropna(subset=['date_start'], inplace=True)

            #manuscripts_all_map.dropna(subset=['iso-3'], inplace=True)

            # if no value for date_end, give it the same as date_start
            manuscripts_all_map['date_end'] = pd.to_numeric(manuscripts_all_map['date_end']).fillna(
                manuscripts_all_map['date_start']).astype(float)

            # calculate a date mean
            manuscripts_all_map['new_mean'] = (manuscripts_all_map['date_start'] + manuscripts_all_map['date_end']) / 2

            # deduce the century of production of the manuscript
            rx = r'^(\d\d)'
            manuscripts_all_map['date_mean_str'] = manuscripts_all_map['new_mean'].astype(str)
            manuscripts_all_map['cent'] = manuscripts_all_map['date_mean_str'].str.extract(rx)
            manuscripts_all_map['cent'] = pd.to_numeric(manuscripts_all_map['cent']).astype(float) + 1

            # make a new dataframe in which the languages are counted by century
            df_manuscripts = (manuscripts_all_map.groupby(['cent', 'language'])
                              .size().reset_index(name='count')
                              )

            df_manuscripts = df_manuscripts.set_index('language', drop=False)
            df_manuscripts.index.names = ['index']
           # df_manuscripts['cent'] = pd.to_numeric(df_manuscripts['cent']).astype(float)
            print(df_manuscripts)
            # latitude column
            df_manuscripts = df_manuscripts.assign(lati=0)
            df_manuscripts = df_manuscripts.assign(longi=0)


            # get latitude from prints_all_map and add it to new df_prints
            for index in df_manuscripts['language']:
                seriess = (manuscripts_all_map.loc[index, 'lat'])
                results = []
                try:
                    for y in seriess:
                        results.append(y)
                except TypeError:
                    results.append(seriess)
                df_manuscripts['lati'].loc[index] = results[0]
                # get longitude from prints_all_map and add it to new df_prints

            for index in df_manuscripts['language']:
                seriess = (manuscripts_all_map.loc[index, 'lon'])
                results = []
                try:
                    for y in seriess:
                        results.append(y)
                except TypeError:
                    results.append(seriess)
                df_manuscripts['longi'].loc[index] = results[0]

            df_manuscripts['cent'] = pd.to_numeric(df_manuscripts['cent']).astype(float)

            df_manuscripts = df_manuscripts.reset_index()

            print('before:')
            print(df_manuscripts)

            def check(cent, language):
                if not df_manuscripts[(df_manuscripts['cent'] == cent) & (df_manuscripts['language'] == language)].index.tolist():
                    df_manuscripts.loc[len(df_manuscripts.index)] = [len(df_manuscripts.index), cent, language, 0, 0, 0]
                else:
                    pass

            for x in range(13, 19):
                check(x, 'Catalan')
                check(x, 'Spanish')
                check(x, 'French')
                check(x, 'Latin')
                check(x, 'High German')
                check(x, 'Occitan')
                check(x, 'English')
                check(x, 'Italian')
                check(x, 'Scots')

            print('after:')
            print(df_manuscripts)




    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.Button(id="submit-button", children="Create Graph", className='button-4'),
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

# graph maker
@callback(Output('output-div-m', 'children'),
              Input('submit-button', 'n_clicks'),
              State('stored-data', 'data'))
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
        mans_graph_fig.update_layout(
            clickmode='event+select',
            dragmode=False,
            #  title=dict(text = 'Repartiton of languages in The Seven Sages of Rome prints', pad_b = 20, pad_t = 20, yanchor = 'middle', xanchor = 'auto'),
            autosize=True,
            paper_bgcolor='#797fa1',
            font_family="Helvetica",
            font_size=15,
            legend=dict(font_size=15, itemclick=False, itemdoubleclick="toggleothers", tracegroupgap=4,
                        title='Language'),
            margin_b=20,
            margin_l=15,
            margin_r=15,
            margin_t=10,
            plot_bgcolor='#797fa1',
            hoverlabel=dict(bordercolor='rgba(0,0,0,0)', font_color='white', font_family='Helvetica, Arial, sans-serif',
                            font_size=12),
            xaxis_title="Date of creation of the manuscript",
            yaxis_title="Number of existing manuscripts",
        )

        # print(data)
        return dcc.Graph(figure=mans_graph_fig, config=config)


# map maker

@callback(Output('output-div-m-map', 'children'),
              Input('submit-button-map','n_clicks'),
              State('stored-data-map','data')
          )
def make_maps(n, data):
    if n is None:
        return dash.no_update
    else:
        return html.Div([
            html.Div(
                dcc.Graph(id='graph-with-slider-map-m', config=config_map, className='create-map-style')),
            html.Div(dcc.Slider(
                min=13,
                max=18,
                step=None,
                verticalHeight=50,
                value=13,
                id='year-slider',
                className='slider',
                marks={
                    13: {'label': '13th century', 'style': {'color': '#333f44', 'font-size': '20px'}},
                    14: {'label': '14th century', 'style': {'color': '#333f44', 'font-size': '20px'}},
                    15: {'label': '15th century', 'style': {'color': '#333f44', 'font-size': '20px'}},
                    16: {'label': '16th century', 'style': {'color': '#333f44', 'font-size': '20px'}},
                    17: {'label': '17th century', 'style': {'color': '#333f44', 'font-size': '20px'}},
                    18: {'label': '18th century', 'style': {'color': '#333f44', 'font-size': '20px'}}
                },
            ), className='create-map-style-slider-m'),
        ], className='container-create-map'),



@callback(
    Output('graph-with-slider-map-m', 'figure'),
    Input('year-slider', 'value'),
    State('stored-data-map', 'data'))
def update_figure(selected_year, data):
    #filtered_df = (data.loc[data['century'] == selected_year])
    pd_df = pd.DataFrame.from_dict(data)
    filtered_df = (pd_df.loc[pd_df['cent'] == selected_year])

    # create a scale column for the bubbles
    all_data_diffq = (filtered_df["count"].max() - filtered_df["count"].min()) / 27
    filtered_df["scale"] = (filtered_df["count"] - filtered_df["count"].min()) / all_data_diffq

    fig = px.scatter_geo(
        filtered_df,
        lat=filtered_df['lati'],
        lon=filtered_df['longi'],
        size=filtered_df["scale"],
        size_max=max((filtered_df['count'])*2),
        projection='equirectangular',
        hover_data={'scale': False, 'count': True},
        color_discrete_sequence = ['#a1797f'],
        labels={"count": "Count"},
        text=filtered_df['language']
     )

    fig.update_traces(textposition="top center",
                      mode='markers+text',
                      textfont_size=15)

    lat_foc = 46.20222
    lon_foc = 6.14569

    fig.update_layout(legend_title_text=' ',
                      margin=dict(l=0, r=0, t=0, b=0),
                      autosize=True,
                      paper_bgcolor="#797fa1",
                      font_family='Helvetica, Arial, sans-serif',
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


