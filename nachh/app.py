# -*- coding: utf-8 -*-

from flask import *
from flask.ext.sqlalchemy import *
from flaskext.markdown import *
import random
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_pyfile("config.py")

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
db = SQLAlchemy(app)
md = Markdown(app)

class item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    text = db.Column(db.String(80))
    category = db.Column(db.String(80))
    picture_description = db.Column(db.String(80))
    picture_path = db.Column(db.String(80))
    
    def __init__(self, title, text, category, picture_description, picture_path):
        self.title=title
        self.text=text
        self.category=category
        self.picture_description=picture_description
        self.picture_path=picture_path
    
    def update(self, title, text, category, picture_description, picture_path):
        self.__init__(title, text, category, picture_description, picture_path)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = str(random.randint(1,9)) + secure_filename(file.filename) 
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return False

@app.route('/')
@app.route('/items')
@app.route('/items/')
def index():
    return render_template('index.html',items=item.query.all())

@app.route('/admin')
@app.route('/admin/')
def admin():
    return render_template('admin.html',items=item.query.all())

@app.route('/items/<itemid>')
def view_item(itemid=0):
    return render_template('index.html',items=[item.query.filter_by(id=itemid).first()])

    
@app.route('/items/add', methods=['POST', 'GET'])
def add_item():
    if request.method != 'POST':
        return render_template('additem.html')
    else:
            filename = upload_file()
            if filename:
                newitem = item(request.form['title'], request.form['text'], request.form['category'], request.form['picture_description'], filename)
                db.session.add(newitem)
                db.session.commit()
                flash('Item added')
                return redirect(url_for('index'))
        

@app.route('/items/edit/<itemid>', methods=['POST','GET'])
def edit_item(itemid=0):
    if request.method!='POST':
        return render_template('edititem.html', Item=item.query.filter_by(id=itemid).first())
    elif request.method=='POST':
        item_old = item.query.filter_by(id=itemid).first()
        filename = upload_file()
        if filename:
            item_old.update(request.form['title'], request.form['text'], request.form['category'], request.form['picture_description'], filename)
        else:
            item_old.update(request.form['title'], request.form['text'], request.form['category'], request.form['picture_description'], item_old.picture_path)
        db.session.commit()
        flash('Item updated')

        return redirect(url_for('index'))


@app.route('/items/delete/<itemid>', methods=['POST','GET'])
def delete_item(itemid=0):
    if request.method!='POST':
        return render_template('deleteitem.html')
    else:
        db.session.delete(item.query.filter_by(id=itemid).first())
        db.session.commit()
        flash('Item deleted')
        return redirect(url_for('index'))

db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0')