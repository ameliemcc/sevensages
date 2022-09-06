import json
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from pages.create_manuscripts_df import manuscripts_all

import numpy as np

# make a copy of the full dataframe, just in case we need it again
manuscripts_all_graph = manuscripts_all

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
manuscripts_all_graph['date_end'] = pd.to_numeric(manuscripts_all_graph['date_end']).fillna(manuscripts_all_graph['date_start']).astype(int)
manuscripts_all_graph['date_end'] = (manuscripts_all_graph['date_end']).astype(int)
manuscripts_all_graph['date_start'] = (manuscripts_all_graph['date_start']).astype(int)
# calculate a date mean
manuscripts_all_graph['new_mean'] = (manuscripts_all_graph['date_start'] + manuscripts_all_graph['date_end']) / 2

# create graph visualisation of repartition of languages amongst manuscripts

config={'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom', 'pan',  "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d",
                               "zoomOut2d", "autoScale2d",  "hoverClosestCartesian",
                               "hoverCompareCartesian", "zoom3d", "pan3d",
                               "resetCameraLastSave3d", "hoverClosest3d", "orbitRotation", "tableRotation", "zoomInGeo",
                               "zoomOutGeo",  "hoverClosestGeo",  "sendDataToCloud", "hoverClosestGl2d",
                               "hoverClosestPie", "toggleHover",  "toggleSpikelines", "resetScale2d"]
    , 'toImageButtonOptions': {
        'format': 'jpeg',  # one of png, svg, jpeg, webp
        'filename': 'sevensages_manuscripts_graph',
        'height': 1000,
        'width': 1200,
        'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
    }
        }


fig_mans_graph = px.histogram(
    manuscripts_all_graph,
    #range_x = [1300, 1650],
    x="new_mean",
    nbins=12,
    color='language',
    hover_data={'language': True, 'new_mean': True},
    labels={"language": "Language", "new_mean": "Dates", "count": "Count"},
    color_discrete_map = {
        "Dutch": '#c5abb5',
        "English": '#abb5c5',
        'French': '#a1797f',
        "High German": '#86562f',
        'Hungarian' : '#762e21',
        'Italian': '#7fa179',
        'Polish':'#335537',
        'Latin':'#565f73',
        'Spanish': '#685794',
        'Occitan': '#c4a599',
        'Catalan' : '#797fa1',
        'Scots' : '#335537',
        },
    )


layout = html.Div([
    html.Div([
        html.H2('Manuscripts'),
        dcc.Markdown('''
        This graph illustrates the languages in which manuscripts of *The Seven Sages of Rome* were written according to 
        date. Click on the graph to view information about the selected manuscripts. 
        '''),
    ], className='graph_text_style'),

    html.Div(dcc.Graph(figure=fig_mans_graph, config=config, id='basic-interactions-man-graph'), className='graph_style'
             ),

    html.Div([
        html.H3(['Selected manuscripts'], style={"display": "block"}),
        dcc.Markdown(id='list_all-man-graph', style={"word-wrap": "break-word"}, link_target="_blank")
    ], className='text_container'),
    ], className='graph_container')


graph_pr = dcc.Graph(figure=fig_mans_graph, config=config, id='basic-interactions' , className='graph_style'),

scroll = html.Div([
    dcc.Markdown(id='list_all', style={"word-wrap": "break-word"})
    ], className='text_container')


@callback(Output(component_id='list_all-man-graph', component_property='children'),
              [Input('basic-interactions-man-graph', 'clickData')])
def update_table(clickData):
    # rank in list of dates
    ptnbm = clickData["points"][0]["pointNumbers"]
    # show info of curve
    idx = clickData["points"][0]["curveNumber"]
    # show more info
    clicked = fig_mans_graph.data[idx]
    # list of dates for curve
    dates = clicked['x']
    # select rows which have the same date mean
    slctd = manuscripts_all_graph.loc[manuscripts_all_graph['new_mean'].isin(dates[ptnbm])]
    # select rows which have the same language
    slctd = slctd.loc[slctd['language'] == (clicked['legendgroup'])]
    aut = slctd['author'].values.tolist()
    tit1 = slctd['title_1'].values.tolist()
    tit2 = slctd['title_2'].values.tolist()
    tit3 = slctd['title_3'].values.tolist()
    tit4 = slctd['title_4'].values.tolist()
    tit5 = slctd['title_5'].values.tolist()
    tit6 = slctd['title_6'].values.tolist()
    tit7 = slctd['title_7'].values.tolist()
    bib = slctd['bibl'].values.tolist()
    dat_s = slctd['date_start'].values.tolist()
    dat_e = slctd['date_end'].values.tolist()
    add_i = slctd['add_inf'].values.tolist()

    # format link
    for i in range(len(add_i)):
        if (pd.isnull(add_i[i])) == False:
            link = str(add_i[i])
            link = ("[online information](<"+link+">)" )
            add_i[i] = link


    def italicize_titles(all_titles):
        for a_title in all_titles:
            for i in range(len(a_title)):
                if (pd.isnull(a_title[i])) == False:
                    title = str(a_title[i])
                    title = title.strip()
                    title = ("*" + title + "*")
                    a_title[i] = title

    italicize_titles([tit1, tit2, tit3, tit4, tit5, tit6, tit7])

    all_info = list(zip(aut, tit1, tit2, tit3, tit4, tit5, tit6, tit7, bib, dat_s, dat_e, add_i))


# https://dash.plotly.com/dash-core-components/markdown
    def write(*arguments):
        my_string = ""
        for number in arguments[:-2]:
            my_string += str(number)
            my_string += ", "
        my_string += str(arguments[-2])
        my_string += ". "
        my_string += str(arguments[-1])
        my_string += ". \n"
        return my_string

    formated_all = []
    info_to_write = []
    for entry in all_info:
        info_to_write = [item for item in entry if not (pd.isnull(item)) == True]
        formated = write(*info_to_write)
        formated_all.append(str(formated))

    return formated_all


fig_mans_graph.update_layout(
    clickmode='event+select',
    dragmode = False,
  #  title=dict(text = 'Repartiton of languages in The Seven Sages of Rome prints', pad_b = 20, pad_t = 20, yanchor = 'middle', xanchor = 'auto'),
    autosize=True,
    paper_bgcolor='#797fa1',
    font_family="Helvetica",
    font_size=15,
    legend=dict(font_size=15, itemclick=False, itemdoubleclick="toggleothers", tracegroupgap=4, title='Language'),
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
