import os
import requests
import json

from flask import Blueprint, redirect, render_template, session, url_for, request, Response, flash, Flask, jsonify, abort

# Google Sign-In
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

from database import Field, Form, User, Manager

def getenv(name):
    return os.environ.get(name) if name in os.environ else {i.strip().split('=')[0]:i.strip().split('=')[1] for i in open('.env').readlines()}[name]

app = Flask(__name__)
app.secret_key = getenv("flask_app_secret")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = getenv('GOOGLE_CLIENT_ID')
flow = Flow.from_client_config(
    client_config=requests.get(getenv('deta_fileserver_url')+"/google_client_secret.json",headers={'Authorization':getenv('deta_api_key')}).json(),
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/afoirm/callback"
)
manager = Manager()

fields1 = [Field(type="text",name="Have you collected logistics?"),Field(type="text",name="Enter package ID")]
fields2 = [Field(type="text",name="Enter Food Requirements"),Field(type="text",name="Enter Hright Requirements")]
user_forms = [Form(author='Joel',name='Collection of Logistics',fields=fields1),Form(author='Jirael',name='Member Wellbeing',fields=fields2)]

def login_required(function):
    def _wrapper(*args, **kwargs):
        if "google_id" not in session:
            return redirect(url_for('/')) # Authorization required
        else:
            return function()
    # Renaming the function name:
    _wrapper.__name__ = function.__name__
    return _wrapper

@app.route('/')
def index():
    return render_template('index.html'),200

@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/dashboard')
@login_required
def dashboard():
    user = Manager.get_user(session["google_id"])
    return render_template('dashboard.html',user_forms=user_forms),200

@app.route('/view_foirms/<form_id>/<field_id>',methods=['GET','POST'])
# @login_required
def view_foirms(form_id,field_id):
    field_id = int(field_id) if field_id == "None" else None
    if request.method == 'GET':
        if field_id is None:
            tar = None
            for i in manager.forms:
                if i.form_id == form_id:
                    tar = i 
                    break
            return render_template('view_foirms.html',form=tar),200
        elif isinstance(field_id,int) and field_id >= 0:
            tar = None
            for i in manager.forms:
                if i.form_id == form_id:
                    tar = i 
                    break
            if tar is None:
                return abort(404)
            
            return render_template('view_foirms_field.html',field=tar),200

    elif request.method == 'POST':
        form_data = request.form
        if 'ocassion' in form_data:
            if form_data['ocassion'] == 'delete_field':
                field_id = int(form_data['field_id'])
                form = manager.get_form(form_data['form_id']) 
                manager.delete_field(session['google_id'],form.id,field_id)

@app.route("/afoirm/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        return Response("Not Authorized. Request Re-Login", status=401, mimetype='application/json') # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    # session["name"] = id_info.get("name")
    # session["email"] = id_info.get("email")
    # session["picture_url"] = id_info.get("picture")

    return redirect("/dashboard")

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
