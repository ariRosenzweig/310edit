import flask
from flask import jsonify
from flask import Response
import Treecopy
import json


app = flask.Flask(__name__)

@app.route('/api/<first_name>/<last_name>')
@app.route('/api/<first_name>/<last_name>/<state_name>')
def stream(first_name, last_name, state_name=None):
    d = Treecopy.Proj()
    d.getSearch(first_name, last_name, state_name)
    d.getNew()  
    d.getApistats()  
    d.getLinks() 
    #d.extractText() 
    
    js = json.dumps(d.extractText(), indent=1)
    resp = Response(js, status=200, mimetype='application/json')
    return resp
    #print jsonify(d.extractText())
    #return flask.Response(  d.extractText(), mimetype= 'application/json' )

@app.route('/')
def default():
    return "To acess the api use the path /api followed by a combination of the below parameters.<br/>https://example.com/api/search?first_name={firstName}&last_name={lastName}&location={location}&pid={pid}&custom_string={custom_string}<br/>Documentation and endpoint tester coming soon."
if __name__ == "__main__":
    app.run(debug=True)