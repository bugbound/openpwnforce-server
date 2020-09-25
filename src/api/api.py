# Copyright 2020 Bugbound

from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager

app = Flask(__name__)

app.config.from_object('settings')
app.url_map.strict_slashes = False

db = SQLAlchemy(app)

class UrlStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(600), unique=True)
    
class DnsStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(300), unique=True)

class FleetStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    ship_type = db.Column(db.String(20))
    capt_user_name = db.Column(db.String(30), unique=True)
    current_zector_id = db.Column(db.Integer)
    
class ZectorStore(db.Model):
    zector_id = db.Column(db.Integer, primary_key=True)
    zector_supplied_scope_id = db.Column(db.Integer)
    zector_name = db.Column(db.String(30), unique=True)
    zector_access_code = db.Column(db.String(10), unique=True)
    zector_disabled = db.Column(db.Boolean)

class SuppliedScopeStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bounty_name = db.Column(db.String(30))
    bounty_url = db.Column(db.String(300))
    in_scope_supplied = db.Column(db.String(300))
    out_scope_supplied = db.Column(db.String(300))
    disabled = db.Column(db.Boolean)

class UserStore(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30))
    user_access_code = db.Column(db.String(10))
    user_disabled  = db.Column(db.Boolean)
    
db.create_all()

# Create the Flask-Restless API manager.
manager = APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(UrlStore, methods=['POST', 'GET'])
manager.create_api(DnsStore, methods=['POST', 'GET'])
manager.create_api(FleetStore, methods=['POST', 'GET'])
manager.create_api(ZectorStore, methods=['POST', 'GET'])
manager.create_api(SuppliedScopeStore, methods=['POST', 'GET'])
manager.create_api(UserStore, methods=['POST', 'GET'])



@app.route('/')
def hello():
  return "<h1>OPEN PWN FORCE API</h1>"
  
@app.route("/clearall")
def clear_all_dbs():
  numrows = db.session.query(UrlStore).delete()
  numrows = db.session.query(DnsStore).delete()
  numrows = db.session.query(FleetStore).delete()
  numrows = db.session.query(ZectorStore).delete()
  numrows = db.session.query(SuppliedScopeStore).delete()
  #lets not remove users
  #numrows = db.session.query(UserStore).delete()
  
  db.session.commit()
  return "<h1 style='color:blue'>All Databases Have Been Wiped!</h1>"

@app.route("/stream/http_urls_by_hostname")
def stream_http_urls():
    hostname = request.args.get('hostname')
    
    def generate(hostname):
        for p in UrlStore.query.filter(UrlStore.url.startswith('http://%s'%hostname)).yield_per(10).enable_eagerloads(False):
            yield "%s\n"%p.url
        for q in UrlStore.query.filter(UrlStore.url.startswith('https://%s'%hostname)).yield_per(10).enable_eagerloads(False):
            yield "%s\n"%q.url
    return Response(generate(hostname), mimetype='text/plain')
    
@app.route("/stream/domains_from_wildcard")
def stream_domains_from_wildcard():
    raw_wildcard = request.args.get('wildcard')
    wildcard = raw_wildcard.replace('*', '%')
    
    
    def generatedomains(wildcard):
        for p in DnsStore.query.filter(DnsStore.domain.ilike(wildcard)).yield_per(10).enable_eagerloads(False):
            yield "%s\n"%p.domain
    return Response(generatedomains(wildcard), mimetype='text/plain')
    

