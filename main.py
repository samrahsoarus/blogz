

from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


#---------------------------------------------------------------------------------- CLASSES --------------------------------------------------------------------------------


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    def __init__(self, title, body):
        self.title = title
        self.body = body


#---------------------------------------------------------------------------- ROUTES + HANDLERS ----------------------------------------------------------------------------


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def display_blogs():
    blog_posts = Blog.query.all()
    return render_template('home.html', page_title="Build A Blog", blogs=blog_posts)


@app.route('/new')
def display_blog_form():
    blog_title = ''
    blog_body = ''
    error_message = ''
    return render_template('new.html', page_title='Add a Blog Entry', error=error_message, title=blog_title, body=blog_body)


@app.route('/new', methods=['POST', 'GET'])
def create_new_blog():
    blog_title = request.form['title']
    blog_body = request.form['body']
    if blog_title != '' and blog_body != '':
        new_blog = Blog(title=blog_title, body=blog_body)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('post.html', page_title=blog_title, body=blog_body)
    else:
        error_message = "Blog title or body is blank! Please enter and resubmit."
        return render_template('new.html', error=error_message, page_title='Add a Blog Entry', title=blog_title, body=blog_body)


@app.route('/post', methods=['POST', 'GET'])
def display_post():
    blog_id = request.args.get('id')
    blog_to_display = Blog.query.filter_by(id=blog_id).first()
    blog_title = blog_to_display.title
    blog_body =  blog_to_display.body
    return render_template('post.html', page_title=blog_title, body=blog_body)


if __name__ == '__main__':
    app.run()