from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:local@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

name = ''
content = ''

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(2000))

    def __init__(self, name, content):
        self.name = name
        self.content = content

@app.route('/', methods=['GET', 'POST'])
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
        if name == '' or content == '':
            return redirect('/newpost?unfilled=yes')
        new_blog = Blog(name, content)
        db.session.add(new_blog)
        db.session.commit()
        blog_id = str(new_blog.id)
        return redirect('/blog?id='+blog_id)
    elif request.args.get('id'):
        blog_id = request.args.get('id')
    else:
        blogs = Blog.query.all()
        return render_template('home.html', blogs = blogs)
    blog = Blog.query.get(blog_id)

    return render_template('blog-page.html', blog=blog)

@app.route('/newpost', methods=['GET', 'POST'])
def newblog():
    global name
    global content
    unfilled = request.args.get('unfilled')
    name = name
    content = content
    if unfilled != 'yes':
        name = ''
        content = ''
    return render_template('blog-add.html', unfilled=unfilled, content=content, name=name)
    

if __name__ == '__main__':
    app.run()