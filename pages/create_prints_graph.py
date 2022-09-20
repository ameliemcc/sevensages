

import json
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from pages.create_prints_df import prints_all_map


# create graph visualisation of repartition of languages amongst prints

config={'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom', 'pan', "resetViewMapbox", "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d",
                               "zoomOut2d", "autoScale2d", "resetScale2d", "hoverClosestCartesian",
                               "hoverCompareCartesian", "zoom3d", "pan3d", "resetCameraDefault3d",
                               "resetCameraLastSave3d", "hoverClosest3d", "orbitRotation", "tableRotation", "zoomInGeo",
                               "zoomOutGeo", "resetGeo", "hoverClosestGeo",  "sendDataToCloud", "hoverClosestGl2d",
                               "hoverClosestPie", "toggleHover", "resetViews", "toggleSpikelines", "resetViewMapbox"]
        , 'toImageButtonOptions': {
                     'format': 'jpeg',  # one of png, svg, jpeg, webp
                     'filename': 'sevensages_prints_graph',
                     'height': 1000,
                    'width': 1200,
                     'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
                 }}

fig_prints_graph = px.histogram(
    prints_all_map,
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
    labels={"language": "Language", "date_mean": "Dates", "Count": "Count"}
)


layout = html.Div([
    html.Div([
        html.H2('Prints'),
        dcc.Markdown('''
        This graph illustrates the languages in which prints of *The Seven Sages of Rome* were written according to 
        date. Click on the graph to view additional information about the selected prints. 
        '''),
    ], className='graph_text_style'),

    html.Div(dcc.Graph(figure=fig_prints_graph, config=config, id='basic-interactions' )
             , className='graph_style'),

    html.Div([
        html.H4('Selected prints', style={"display": "block"}),
        dcc.Markdown(id='list_all', style={"word-wrap": "break-word"})
    ], className='text_container'),
    ], className='graph_container')


graph_pr = dcc.Graph(figure=fig_prints_graph, config=config, id='basic-interactions' , className='graph_style'),

scroll = html.Div([
        dcc.Markdown(id='list_all', style={"word-wrap": "break-word"})
    ], className='text_container')

@callback(Output(component_id='list_all', component_property='children'),
              [Input('basic-interactions', 'clickData')])
def update_table(clickData):
    # rank in list of dates
    ptnbm = clickData["points"][0]["pointNumbers"]
    # show info of curve
    idx = clickData["points"][0]["curveNumber"]
    # show more info
    clicked = fig_prints_graph.data[idx]
    # list of dates for curve
    dates = clicked['x']
    # select rows which have the same date mean
    slctd = prints_all_map.loc[prints_all_map['date_mean'].isin(dates[ptnbm])]
    # select rows which have the same language
    slctd = slctd.loc[slctd['language'] == (clicked['legendgroup'])]
    aut = slctd['author'].values.tolist()
    tit = slctd['title'].values.tolist()
    pri = slctd['print_town'].values.tolist()
    pub = slctd['publisher'].values.tolist()
    dat = slctd['date_mean'].values.tolist()
    bib = slctd['bibl'].values.tolist()
    dates = []
    for date in dat:
        dates.append(int(date))
    titles = []
    for title in tit:
        title = title.strip()
        if title != "nan":
            title = str(title)
            title = title.strip()
            title = ("*" + title + "*")
            titles.append(title)
    all_info = list(zip(aut, titles, pri, pub, dates, bib))
# https://dash.plotly.com/dash-core-components/markdown
    def write(*arguments):
        my_string = ""
        for number in arguments[:-2]:
            my_string += str(number)
            my_string += ", "
        my_string += str(arguments[-2])
        my_string += ". From "
        my_string += str(arguments[-1])
        my_string += ". \n"
        return my_string
    formated_all = []
    for entry in all_info:
        info_to_write = [item for item in entry if not (pd.isnull(item)) == True]
        formated = write(*info_to_write)
        formated_all.append(str(formated))
    return formated_all

fig_prints_graph.update_layout(
    clickmode='event+select',
    dragmode = False,
    autosize=True,
    paper_bgcolor="#797fa1",
    font_family="Helvetica",
    font_size=15,
    legend=dict(font_size=15, itemclick = False, itemdoubleclick = "toggleothers", tracegroupgap = 4, title = 'Language',
    ),
    margin_b = 20,
    margin_l = 15,
    margin_r = 15,
    margin_t = 10,
    plot_bgcolor = '#797fa1',
    hoverlabel=dict(bordercolor = 'rgba(0,0,0,0)', font_color = 'white', font_family = 'Helvetica, Arial, sans-serif', font_size = 12),
    xaxis_title="Date of edition of the print",
    yaxis_title="Number of existing prints",
    )


