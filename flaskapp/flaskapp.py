from flask import (
    Flask,
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    make_response,
    send_file
)
from flask_login import login_required, current_user
from collections import Counter
import re
import pyodbc
import os


flaskapp = Blueprint("flaskapp", __name__)

def init_azure_db():
    azure_pw = os.getenv("AZURE_PW")
    server = 'sql-compute.database.windows.net'
    database = 'kroger-data'
    username = os.getenv("AZURE_USER")
    driver= '{ODBC Driver 18 for SQL Server}'
    db_conn = 'DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ azure_pw
    return db_conn

azure_db = pyodbc.connect(init_azure_db())
    
@flaskapp.route("/")
def index():
    return render_template("index.html")

@flaskapp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@flaskapp.route("/datapage", methods=["GET", "POST"])
@login_required
def datapage():

    with azure_db.cursor() as cur:
        header_columns = [col.column_name for col in cur.columns('joined_data')]
    """
    need to render the following:
    DEFAULT ONE TABLE TO HSHD_NUM = 10 ON LOAD
    0. make a dashboard at the top and the searchable table next for readability, cause thats a lotta rows
    1. display a table of all columns where HSHD_NUM = 10
        order by HSHD_NUM, BASKET_NUM, PURCHASE_DATE, PRODUCT_NUM, DEPARTMENT, COMMODITY
    2. let user enter a new id into text box and refresh data table with fancy ajax
    """
    if request.method == 'POST':
        household_id = request.form.get('query_id')
        if not household_id.isdigit():
            flash("Wrong data type, use an integer")
            return redirect(url_for('flaskapp.datapage'))
        return render_template("data_central.html", user=current_user, headers=header_columns, hs_num=household_id)
    return render_template("data_central.html", user=current_user, headers=header_columns)

@flaskapp.route("/datapage/get-ajax-data", methods=["GET"])
@login_required
def get_ajax_data():
    with azure_db.cursor() as cur:
        results = []
        header_columns = [col.column_name for col in cur.columns('joined_data')]
        hs_num = 10 if request.args.get('hs_num') == '' else request.args.get('hs_num')
        cur.execute("select * from joined_data where HSHD_NUM = {} order by HSHD_NUM, BASKET_NUM, PURCHASE_DATE, PRODUCT_NUM, DEPARTMENT, COMMODITY".format(hs_num))
        row = cur.fetchall()

    for r in row:
        results.append(dict(zip(header_columns, r)))
    return {'data': results}

def wordcount(text):
    text = text.decode().lower().replace("\n", " ")
    text = re.sub("[^\w ]", "", text)
    text = text.split(" ")
    words = Counter(text)
    return dict(words)