from dash import dcc
from pages.create_prints_df import df_prints
from dash import html, callback
from dash.dependencies import Input, Output
import plotly.express as px


config_map=dict({'displaylogo': False, 'scrollZoom': False, 'modeBarButtonsToRemove': ['scrollZoom', 'zoom', 'pan',  "zoom2d", "pan2d", "select2d", "lasso2d",
                                                             "zoomIn2d", "zoomOut2d",
                                                             "autoScale2d", "hoverClosestCartesian",
                                                             "hoverCompareCartesian", "zoom3d", "pan3d",
                                                             "resetCameraDefault3d", "resetCameraLastSave3d",
                                                             "hoverClosest3d", "orbitRotation", "tableRotation",
                                                             "hoverClosestGeo",  "sendDataToCloud", "hoverClosestGl2d",
                                                             "hoverClosestPie", "toggleHover", "toggleSpikelines",
                                                             "resetViewMapbox"]
                , 'toImageButtonOptions': {
    'format': 'jpeg',  # one of png, svg, jpeg, webp
    'filename': 'sevensages_prints_map',
    'height': 1000,
    'width': 1200,
    'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
}
})

layout = html.Div([
    html.Div([
            html.Div(
                dcc.Graph(id='graph-with-slider',config=config_map ),
                className='map_style'),
            html.Div(
            dcc.Slider(
                df_prints['century'].min(),
                df_prints['century'].max(),
                step=None,
                verticalHeight=50,
                value=15,
                id='year-slider',
                className = 'slider',
                marks={15: {'label': '15th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                       16: {'label': '16th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                       17: {'label': '17th century', 'style': {'color': '#333f44', 'font-size':'20px'}},
                       }
            ), className='slider_style'),
]),
  html.Div([
      html.Div([
          html.H2('Prints'),
          dcc.Markdown('This map illustrates the towns in which prints of *The Seven Sages of Rome* were produced per'
                       ' century, as well as their number.\n'),
      ], className='map_text_style'),

      html.Button("Download print information", id="btn_xlsx", className='button-2'),
      dcc.Download(id="download-dataframe-xlsx"),
      html.A(html.Button("Make your own visualisations of print data", id="btn_print",
                         className='button-3'), href='/printsgraphmaker'),
  ],  className='buttons_style')


        ], className='graph_container'),

all_data_diffq = (df_prints["Count"].max() - df_prints["Count"].min()) / 11 + 1
df_prints["scale"] = (df_prints["Count"] - df_prints["Count"].min()) + 1 / all_data_diffq


@callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = (df_prints.loc[df_prints['century'] == selected_year])
    # create a scale column for the bubbles
    #all_data_diffq = (filtered_df["Count"].max() - filtered_df["Count"].min()) / 11 + 1
    #filtered_df["scale"] = (filtered_df["Count"] - filtered_df["Count"].min()) + 1 / all_data_diffq
   # filtered_df["scale"] = df_prints["scale"]

    fig = px.scatter_geo(
        filtered_df,
        lat=filtered_df['lati'],
        lon=filtered_df['longi'],
        text=filtered_df['print_town'],
        size=filtered_df['scale'],
        size_max=11,
        projection='equirectangular',
        hover_data={'scale': False, 'print_town': False, 'lati': False, 'longi':False, 'Count':True},
        labels = {"Count" : "Count"},
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



