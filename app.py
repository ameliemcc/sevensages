from dash import Dash


app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

server = app.server

if __name__ == '__main__':
	app.run_server(debug=True)