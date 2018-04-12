from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
   

    def __init__(self, title, body):
        self.title = title
        self.body = body
        



@app.route('/blog', methods=['POST', 'GET'])
def blogstuff():
    blogs = Blog.query.all()
    clicked = request.args.get(Blog.id)
    #mainpage = request.form['mainblogpage']
    if (clicked):
        return render_template('entry.html')

    else:
        return render_template('blog.html', blogs=blogs)


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
            new_post = Blog(blog_title, blog_body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')


@app.route('/blog?id={{ blog.id }}', methods=['POST', 'GET'])
def entry():
    
    blog_title = request.args.get('{{ blog.title }}')
    blog_body = request.args.get('{{ blog.body }}')

    return render_template('entry.html', entry=entry, blog_title=blog_title, blog_body=blog_body)  



@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('blog.html')


if __name__ == '__main__':
    app.run()