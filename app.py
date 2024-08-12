from functools import wraps
import sqlite3
from flask import Flask, request, render_template, session, redirect, url_for
from flask_cors import CORS
from middleware.dbMiddleware import CreateCollection, TableCollection

app = Flask(__name__, template_folder='content/templates', static_folder='content/static')

app.secret_key = 'your_secret_key'

CORS(app)

DATABASE = "./database/app.db"

def connectDB():
    return sqlite3.connect(DATABASE)

def dbCollection(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        value = kwargs.get("collectionName")
        if value is not None:
            collect = TableCollection(connectDB,value)
            if collect.valid:
                request.collection = collect
            else:
                request.collection = False
        else:
            request.collection = False
        return f(*args,**kwargs)
    return decorated_function

@app.before_request
def initialize():
    CreateCollection(connector= connectDB, table_name="users", columns= [
    'id INTEGER PRIMARY KEY AUTOINCREMENT',
    'name TEXT NOT NULL',
    'age INTEGER', 
    'gender INTEGER', 
    ])

@app.route('/collection/<string:collectionName>', methods=['GET'])
@dbCollection
def collection_route_getAll(collectionName):
    if request.collection:
        return {"msg":request.collection.getAll(),"mode":True}
    return {"msg":f'table {collectionName} - was not found',"mode":False}

@app.route('/collection/<string:collectionName>', methods=['POST'])
@dbCollection
def collection_route_insert(collectionName):
    if request.collection:
        return {"msg": request.collection.insertOne(request.get_json()), "mode": True}
    return {"msg":f'table {collectionName} - was not found',"mode":False}

@app.route('/collection/<string:collectionName>', methods=['PUT'])
@dbCollection
def collection_route_update(collectionName):
    if request.collection:
        req_json = request.get_json()
        return {"msg": request.collection.updateOne(req_json["query"],req_json["data"]), "mode": True}
    return {"msg":f'table {collectionName} - was not found',"mode":False}

@app.route('/collection/<string:collectionName>', methods=['DELETE'])
@dbCollection
def collection_route_delete(collectionName):
    if request.collection:
        return {"msg": request.collection.deleteOne(request.get_json()), "mode": True}
    return {"msg":f'table {collectionName} - was not found',"mode":False}

@app.route('/search/collection/<string:collectionName>', methods=['POST'])
@dbCollection
def collection_route_search(collectionName):
    if request.collection:
        return {"msg": request.collection.getMany(request.get_json()), "mode": True}
    return {"msg":f'table {collectionName} - was not found',"mode":False}


@app.route("/",methods=["GET"])
def index():
    # if 'user_id' in session:
    #     user = TableCollection(connectDB,"users").getMany({"id":session['user_id']})
    #     if len(user) > 0:
    #         session['isadmin'] = user[0]["isadmin"]
    #         return render_template("index.html",session=session)
    return render_template('index.html',session=None)





