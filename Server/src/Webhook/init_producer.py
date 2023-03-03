from flask import Flask

app = Flask(__name__)

app.secret_key = app.config['SECRETS_KEY']
app.config.from_object("config")