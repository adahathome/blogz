from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = 'itsasecret'

db = SQLAlchemy(app)

name = ''
content = ''

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(2000))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, name, content, user_id):
        self.name = name
        self.content = content
        self.user_id = user_id

@app.before_request
def require_login():
    allowed_routes = ['landing', 'login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        flash('You must be logged in to view that page')
        return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
def landing():
    users = User.query.all()

    return render_template('index.html', users = users)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        pword = request.form['password']
        pword_match = request.form['pass_match']
        email = request.form['user_email']
        if len(pword) < 3 or len(pword)>20:
            flash('Password must be between three and twenty characters')
        if pword != pword_match:
            flash('Passwords do not match')
        if email == "" or (('@' not in email) and ('.' not in email)):
            flash('Please enter a valid email')
        else:
            new_user = User(email, pword)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = new_user.email
            return redirect('/newpost')
        return render_template('signup.html')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['user_email']
        pword = request.form['password']
        if User.query.filter_by(email=email).first():
            check_user = User.query.filter_by(email=email).first()
            if check_user.password == pword:
                session['email'] = email
                return redirect('/newpost')
            else:
                flash('Password does not match password for ' + check_user.email)
        else:
            flash('User not found')

    return render_template('login.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    blogs = Blog.query.all()
    return render_template('home.html', blogs = blogs)

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    global name
    global content
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        user = request.form['creator_id']
        if name == '' or content == '':
            return redirect('/newpost?unfilled=yes')
        new_blog = Blog(name, content, user)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = str(new_blog.id)
        return redirect('/blog?id='+blog_id)
    elif request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('blog-page.html', blog=blog)
    elif request.args.get('user_id'):
        user_id = request.args.get('user_id')
        blogs = Blog.query.filter_by(user_id=user_id).all()
        return render_template('singleUser.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
    return render_template('home.html', blogs = blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    global name
    global content
    unfilled = request.args.get('unfilled')
    name = name
    content = content
    user_email = session['email']
    creator = User.query.filter_by(email=user_email).first()
    poster = creator.id
    if unfilled != 'yes':
        name = ''
        content = ''
    return render_template('blog-add.html', unfilled=unfilled, content=content, name=name, poster=poster)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run()