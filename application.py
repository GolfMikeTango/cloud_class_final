#application.py
import sys
from waitress import serve
from flaskapp import db, create_app

application = create_app()

db.create_all(app=create_app())

serve(application, port=80)