# -*- coding: utf-8 -*-

from flask import *
from flask.views import *
from flask.ext.sqlalchemy import *
from flaskext.markdown import *
from sqlalchemy import *
from flask.ext.wtf import Form, TextField, PasswordField, SubmitField, validators, validators
from flask.ext.wtf import *

app = Flask(__name__)
app.config.from_pyfile("config.py")

db = SQLAlchemy(app)
md = Markdown(app)

def login_required(f):
    """Checks whether user is logged in or raises error 401."""
    def decorator(*args, **kwargs):
        if not 'user_id' in session:
                return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorator

def logged_in():
    return 'user_id' in session

""" MODELS """

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))
    tasks = db.relationship('Task')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def checkPassword(self, password):
        return self.password == password

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    listid = db.Column(db.Integer, default=0)
    srnr = db.Column(db.String(80))
    title = db.Column(db.String(80))
    text = db.Column(db.String(80))
    category = db.Column(db.String(80))
    customer = db.Column(db.String(80))
    done = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer,default=0)
    private = db.Column(db.Boolean, default=True)
    information = db.Column(db.String(4000))

    user = db.relationship('User')
    
    def __init__(self, srnr, title, text, category, customer, done=0, pos=0, private=None):
        self.userid=session['user_id']
        self.srnr=srnr
        self.title=title
        self.text=text
        self.category=category
        self.customer=customer
        self.done=0
        pos = db.session.query(func.max(Task.position)).first()
        if pos[0] != None:
            self.position = pos[0]+1
        self.private=private.data

    def update(self, form):
        self.srnr=form.srnr.data
        self.title=form.title.data
        self.text=form.text.data
        self.category=form.category.data
        self.customer=form.customer.data
        self.private=form.private.data

""" FORMS """

class TaskForm(Form):
    srnr = TextField(label='Service Request', validators=[Required()])
    title = TextField(label='Title', validators=[Required()])
    text = TextField(label='Text')
    category = TextField(label='Category')
    customer = TextField(label='Customer')
    private = BooleanField(label='Private?', default=False)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.task = None

    def populate_form(self, taskid):
        task = Task.query.filter_by(id=taskid).first_or_404()
        self.srnr.data = task.srnr
        self.title.data = task.title
        self.text.data = task.text
        self.category.data = task.category
        self.customer.data = task.customer
        self.private.checked = task.private
        return True


class UserForm(Form):
    username = TextField(label='Username', validators=[Required()])
    password = PasswordField(label='Password', validators=[Required()])
    submit = SubmitField('Register')


class LoginForm(Form):
    username = TextField(label='Username', validators=[Required()])
    password = PasswordField(label='Password', validators=[Required()])
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def login_validate(self):
        rv = self.validate()
        if not rv:
            flash('validation error')
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            flash('no user found')
            return False

        if not user.checkPassword(self.password.data):
            flash('wrong pw')
            return False
        self.user = user
        return True


""" VIEWS """

class ListView(MethodView):
    decorators = [login_required]
    def get(self, taskid=None):
        if taskid is None:
            mycount = Task.query.filter_by(userid=session['user_id'], done=0).count()
            teamcount = Task.query.filter_by(private=False, done=0).count()
            myEmpty=False
            if mycount == 0:
                myEmpty=True
            if mycount > 1:
                myTasks=Task.query.filter_by(userid=session['user_id'], done=0).all()
            else:
                myTasks=Task.query.filter_by(userid=session['user_id'], done=0).first()
            teamEmpty=False
            if teamcount == 0:
                teamEmpty=True
            if teamcount > 1:
                teamTasks=Task.query.filter_by(private=False, done=0).all()
            else:
                teamTasks=Task.query.filter_by(private=False, done=0).first()
            return render_template('index.html', myTasks=myTasks, teamTasks=teamTasks, teamEmpty=teamEmpty, username=session['username'], myEmpty=myEmpty, userid=session['user_id'])  
        return render_template('index.html', myTasks=Task.query.filter_by(userid=session['user_id'],id=taskid, done=0).first_or_404(), username=session['username'])

class EditTaskView(MethodView):
    decorators = [login_required]
    def get(self, taskid):
        self.form = TaskForm()
        if (self.form.populate_form(taskid)):
            return render_template('task.html', title='Edit Task', form=self.form)
        else:
            return redirect(url_for('tasks'))

    def post(self, taskid):
        self.form = TaskForm()
        task = Task.query.filter_by(id=taskid).first_or_404()
        task.update(self.form)
        db.session.commit()
        flash('edited')
        return redirect(url_for('tasks'))



class TaskView(MethodView):
    decorators = [login_required]
    def __init__(self):
        self.form = TaskForm()
    def get(self):
        return render_template('task.html', title='Add Task', form = self.form)
    def post(self):
        if self.form.validate_on_submit():
            task = Task(self.form.srnr.data, self.form.title.data, self.form.text.data, self.form.category.data, self.form.customer.data, private=self.form.private)
            db.session.add(task)
            db.session.commit()
            flash('Task added')
        else:
            flash('error')

        return redirect(url_for('tasks'))



class LoginView(MethodView):

    def __init__(self):
        self.form=LoginForm()

    def get(self):
        return render_template('login.html', form=self.form)

    def post(self):
        if self.form.login_validate():
            flash('Logged in')
            session['user_id'] = self.form.user.id
            session['username'] = self.form.user.username
            return (redirect(url_for('index')))
        else:
            flash('Error')
            return render_template('login.html', form=self.form)


class RegisterView(MethodView):

    def __init__(self):
        self.form = UserForm()
    def get(self):
        return render_template('adduser.html', form=self.form)
    def post(self):
        if self.form.validate():
            user = User(self.form.username.data, self.form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('user added')
            return redirect(url_for('index'))
        else:
            flash('error')
            return render_template('adduser.html', form=self.form)

@login_required
@app.route('/tasks/<int:taskid>/done')
def done(taskid):
    task = Task.query.filter_by(id=taskid).first_or_404()
    task.done = 1
    db.session.commit()
    return redirect(url_for('tasks'))

@login_required
@app.route('/tasks/<int:taskid>/notdone')
def notdone(taskid):
    task = Task.query.filter_by(id=taskid).first_or_404()
    task.done = 0
    db.session.commit()
    return redirect(url_for('tasks'))

@login_required
@app.route('/tasks/done')
def listdone():
    count = Task.query.filter_by(userid=session['user_id'], done=1, private=True).count()
    if count == 0:
        return render_template('index.html', myEmpty=True, teamEmpty=True, username=session['username'])
    if count > 1:
        return render_template('index.html', myTasks=Task.query.filter_by(userid=session['user_id'], done=1).all(), username=session['username'], userid=session['user_id'], myEmpty=False, teamEmpty=True)
    else:
        return render_template('index.html', myTasks=Task.query.filter_by(userid=session['user_id'], done=1).first(), username=session['username'], userid=session['user_id'], myEmpty=False, teamEmpty=True)


@login_required
@app.route('/logout')
def log_out():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/register', view_func=RegisterView.as_view('register'))
app.add_url_rule('/tasks', view_func=ListView.as_view('tasks'))
app.add_url_rule('/tasks/<int:taskid>', view_func=ListView.as_view('tasks'))
app.add_url_rule('/tasks/add', view_func=TaskView.as_view('addtask'))
app.add_url_rule('/tasks/<int:taskid>/edit', view_func=EditTaskView.as_view('edittask'))


@app.route('/')
def index():
    if (logged_in()):
        return redirect(url_for('tasks'))
    else:
        return redirect(url_for('login'))

db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0')
