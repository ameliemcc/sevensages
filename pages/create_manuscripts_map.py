from dash import dcc
from pages.create_manuscripts_df import df_manuscripts
from dash import html, callback
from dash.dependencies import Input, Output
import plotly.express as px



config_map={'displaylogo': False, 'scrollZoom': False, 'modeBarButtonsToRemove': ['scrollZoom', 'zoom', 'pan',
                                                             "zoom2d", "pan2d", "select2d", "lasso2d", 'resetScale2d',
                                                             "zoomIn2d", "zoomOut2d", "zoomInGeo","zoomOutGeo",
                                                             "autoScale2d", "hoverClosestCartesian",
                                                             "hoverCompareCartesian", "zoom3d", "pan3d", 'resetGeo',
                                                             "resetCameraDefault3d", "resetCameraLastSave3d",
                                                             "hoverClosest3d", "orbitRotation", "tableRotation",
                                                             "hoverClosestGeo",  "sendDataToCloud", "hoverClosestGl2d",
                                                             "hoverClosestPie", "toggleHover", "toggleSpikelines",
                                                             "resetViewMapbox", ],
                 'toImageButtonOptions': {
                     'format': 'jpeg',  # one of png, svg, jpeg, webp
                     'filename': 'sevensages_manuscripts_map',
                     'height': 1000,
                    'width': 1200,
                     'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
                 }
                 }

layout =html.Div([
            html.Div(

    html.Div([
            html.Div(
                dcc.Graph(id='graph-with-slider-man', config=config_map),
                className='map_style'),
            html.Div(
            dcc.Slider(
                df_manuscripts['cent'].min(),
                df_manuscripts['cent'].max(),
                step=None,
                verticalHeight=50,
                value=13,
                id='year-slider-man',
                className='slider',
                marks={
                    13: {'label': '13th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                    14: {'label': '14th century','style': {'color': '#333f44', 'font-size':'20px'}},
                    15: {'label': '15th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                    16: {'label': '16th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                    17: {'label': '17th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                    18: {'label': '18th century', 'style': {'color': '#333f44', 'font-size':'20px'}}
                },
            ), className='slider_style'),
]),
    ),
            html.Div([
                html.Div([
html.H2('Manuscripts'),
                dcc.Markdown("""
                This map illustrates the location in which manuscripts of *The Seven Sages of Rome* are inferred to have 
                been produced per century, as well as their number.\n
                The regions of origin of the manuscripts were deduced according to the language in which the manuscript 
                was written. Note that this method is not failsafe as manuscripts written in some languages (e.g. 
                French) may have been produced or used at locations now lying beyond their modern borders. Latin copies 
                of the *Seven Sages* might potentially have been written or used anywhere within the medieval West. 
"""
                             )], className='map_text_style'),


                html.Div([
                    html.Button("Download manuscript information", id="btn_xlsx-man", className='button'),
                    dcc.Download(id="download-dataframe-xlsx-manuscripts"),
                    html.A(html.Button("Make your own visualisations of manuscript data", id="btn_manu",className='button'
                                      ), href='/mansgraphmaker'),
                ], className='btn-group'),
],  className='buttons_style')

        ], className='graph_container')



@callback(
    Output('graph-with-slider-man', 'figure'),
    Input('year-slider-man', 'value'))
def update_figure(selected_year):
    filtered_df = (df_manuscripts.loc[df_manuscripts['cent'] == selected_year])

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
                      paper_bgcolor="#c4a599",
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




