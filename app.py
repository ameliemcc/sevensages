from dash import Dash


app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True,
			meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1, maximum-scale=1, '
			'minimum-scale=1, user-scalable=no,'}])
# initial-scale=1 -> nice size
# user-scalable=1.0,
server = app.server

if __name__ == '__main__':
	app.run_server(debug=True)
