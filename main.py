from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'thx1138'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password != password:
            session['username'] = username
            flash("This isn't the correct password")
            return render_template('login.html', username=username)
        if user and user.password == password:
            session['username'] = username
            flash("Log in successful!")
            #TODO pass username into newpost route
            return redirect('/newpost')
        else:
            flash("Username does not exist")
            return render_template('login.html')




@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        #TODO validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            #TODO pass username into /newpost route
            return redirect('/newpost', username=username)

        else:
            #TODO user error message
            pass




@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    id = request.args.get('id')
    username = session['username']

    if not id:
        return render_template('blog.html', blogs=blogs)

    else: 
        blog = Blog.query.get(id)
        title = blog.title
        body = blog.body
        username = session['username']
        return render_template('entry.html', blog_title=title, blog_body=body, username=username)




@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error = "Please give your blog a title"
    body_error = "Please write some stuff"


    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        
        if (not blog_title) or (blog_title.strip() == ""):
            if (not blog_body) or (blog_body.strip() == ""):
                return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error, body_error=body_error)  
            else:
                return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error)

        if (not blog_body) or (blog_body.strip() == ""):
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, body_error=body_error)

        if (not blog_title) or (blog_title.strip() == "") and (not blog_body) or (blog_body.strip() == ""): 
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body, title_error=title_error, body_error=body_error)  
        
        else: 
            #session['username'] = username
            #user = User.query.filter_by(username=username).first()
            #owner = user.id
            blog_owner = User.query.filter_by(username=session['username']).first()
            new_post = Blog(blog_title, blog_body, blog_owner) # user.id
            db.session.add(new_post)
            db.session.commit()
            just_posted = db.session.query(Blog).order_by(Blog.id.desc()).first()
            id = str(just_posted.id)
            #blog_author = just_posted.owner_id
            return redirect('/blog?id=' + id)



@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')




@app.route('/', methods=['POST', 'GET'])
def index():
    allusers = User.query.all()
    return render_template('index.html', users=allusers)


if __name__ == '__main__':
    app.run()