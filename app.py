from database import DB
from dash_app import App
print("Hello world")

db_client = DB()
app = App(db_client)
server = app.app.server 

if __name__=="__main__":
	app.app.run_server(debug=True, host='0.0.0.0')


