from mikiui import MikiApp, Div

app = MikiApp(title="Demo App")

@app.route("/")
def home():
    return Div("Demo")
