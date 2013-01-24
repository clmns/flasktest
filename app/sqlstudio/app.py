# -*- coding: utf-8 -*-

from flask import *
from flask.ext.sqlalchemy import *
from sqlalchemy import *

MAX_LENGTH=20
app = Flask(__name__)
app.config.from_pyfile("config.py")

db = SQLAlchemy(app)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    hostip = db.Column(db.String(80))
    #users = db.relationship('User', backref=db.backref('server', lazy='dynamic'))
    type = db.Column(db.String(80))
    customer = db.Column(db.String(80))
    default_db = db.Column(db.String(80))
    
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    
    def __init__(self, servername, serverip, servertype, customername, defaultdb, username, passwd, db_type):
        self.name=servername
        self.hostip=serverip
        self.type=servertype
        self.customer=customername
        self.default_db = defaultdb
        self.username = username
        self.passwd = passwd
        self.db_type_active = db_type
        
    db_type = {'MSSQL' : 'mssql+pyodbc://', 'SQLITE' : 'sqlite://'}
    db_type_active = db.Column(db.String(80))
    trusted_connection = db.Column(db.Integer)
    
    def return_engine_string(self):
        if self.db_type_active == 'MSSQL':
            return self.db_type[self.db_type_active] + self.username + ':' + self.password + '@' + self.hostip + '/' + self.default_db
        elif self.db_type_active == 'SQLITE':
            return self.db_type[self.db_type_active] + self.hostip
        

"""class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #server_id = db.Column(db.Integer, db.ForeignKey('Server.id'))
"""
    
@app.route('/')
def index():
    return render_template('index.html',servers=Server.query.all())
    
@app.route('/query', methods=["POST","GET"])
@app.route('/query/<sid>', methods=["POST","GET"])
def query(sid=0):
    if request.method == 'POST':
        if request.form['data'] != 0:
            eng_str = Server.query.filter_by(id=sid).first().return_engine_string()
            engine = create_engine(eng_str)
            i = 0
            result = []
            row = []
            header = []
            conn = engine.connect()
            sql = request.form['data']
            
            sql = sql.replace(u"\xa0", " ")
            res = conn.execute(sql)
            res_row = res.fetchone()
            while res_row is not None:
                new_val= ()
                row = []
                if (i==0):
                    header=res_row.keys()
                    i=1
                for val in res_row:
                    val = str(val)
                    if len(val) > MAX_LENGTH:
                        new_val = (val, val[:MAX_LENGTH])
                        row.append(new_val)
                    else:
                        new_val = (val,0)
                        row.append(new_val)
                res_row = res.fetchone()
                result.append(row)
                
        return render_template("result.html", header=header, entries=result)
    else:
        return render_template("index.html", id=sid, servers=Server.query.all())
            
        
@app.route('/servers/add', methods=['POST', 'GET'])
def add_server():
    if request.method != 'POST':
        return render_template('addserver.html', db_type=Server.db_type)
    else:
        newserver = Server(request.form['servername'], request.form['serverip'], request.form['type'], request.form['customername'], request.form['defaultdb'], request.form['username'], request.form['passwd'], request.form['db_type'])
        db.session.add(newserver)
        db.session.commit()
        return "server added"
        
@app.route('/servers/')
def list_server():
    return render_template("listserver.html", servers=Server.query.all())


@app.route('/servers/edit/<serverid>', methods=['POST','GET'])
def edit_server(serverid=0):
    if request.method!='POST':
        return render_template("editserver.html", server=Server.query.filter_by(id=serverid).first(), db_type=Server.db_type)


db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0')
