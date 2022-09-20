import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output
import pages.create_manuscripts_map, pages.create_manuscripts_graph, pages.create_prints_map, pages.create_prints_graph
from pages.create_manuscripts_df import manuscripts_all_map
from pages.create_prints_df import prints_all_map
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout =(html.Div([

    # welcome page



    html.Section([




                html.Div([
                    dcc.Markdown("""
       ## __The Seven Sages of Rome in the world__ \n
       _Inventory and visualisations_ \n
       Scroll down or go directly to the [manuscripts map](#anchor-1), the [manuscripts language graph](#anchor-2),
       the [prints map](#anchor-3), or the [prints language graph](#anchor-4). \n
       Access bibliographical information [here](#anchor-6)
       """),
                ], className='card'),


    ], className='section'),

    # manuscripts map
    html.Section([
        html.A(id='anchor-1'),
        pages.create_manuscripts_map.layout
    ], className='section'),

    # manuscripts graph
    html.Section([
        html.A(id='anchor-2'),
        html.Div([
            pages.create_manuscripts_graph.layout
        ]),
    ], className='section'),

    # prints map
    html.Section([
        html.A(id='anchor-3'),
            html.Div(
                pages.create_prints_map.layout
            ),
    ], className='section'),

    # prints graph
    html.Section([
        html.A(id='anchor-4'),
        html.Div([
            pages.create_prints_graph.layout
        ]),
    ], className='section'),

    # graph maker
    html.Section([
        html.A(id='anchor-5'),
        html.Div([
           # html.A(html.Button("Upload Excel sheet and create your own print visualisations", id="btn_print"), href='/printsgraphmaker'),

        ], className='card'),
        #graph_maker.layout

    ], className='section'),

    # end page
    html.Section([
        html.A(id='anchor-6'),
        html.Div([
            dcc.Markdown("""
                ## __Bibliographical information__ \n
                The information presented on this website was gathered from :  \n
                * Campbell, Killis and University of California Libraries. _The Seven Sages of Rome_. Boston, Ginn and company, 1907.
                * Runte, Hans Rainer, et al. _The Seven Sages of Rome and the Book of Sindbad : an Analytical Bibliography_. Garland, 1984. (Prints reference)
                * Runte, Hans Rainer. _Li Ystoire de la male marastre : version M of the Roman des sept sages de Rome : a critical edition with an introd., notes, a glossary, five appendices, and a bibliography_. M. Niemeyer, 1974.
                * Runte, Hans R., and Laurent Brun. “Les Sept Sages de Rome.” [Arlima - Archives de Littérature Du Moyen Âge](<https://www.arlima.net/qt/sept_sages_de_rome.html>), 12 Nov. 2021.
                            """, link_target="_blank"),
        ], className='card'),
    ], className='section'),

], className='container')
)


# -----------


# button to download manuscripts file
@callback(
    Output("download-dataframe-xlsx-manuscripts", "data"),
    Input("btn_xlsx-man", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(manuscripts_all_map.to_excel, "sevensages_manuscripts.xlsx")


# button to download prints file
@callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(prints_all_map.to_excel, "sevensages_prints.xlsx")



