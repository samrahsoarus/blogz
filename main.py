
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


#---------------------------------------------------------------------------------- CLASSES --------------------------------------------------------------------------------


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    def __init__(self, title, body):
        self.email = title
        self.password = body  


#---------------------------------------------------------------------------- ROUTES + HANDLERS ----------------------------------------------------------------------------


@app.before_request
def require_login():
    allowed_routes = ['signup', 'login', 'display_users', 'display_blogs']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


# REDIRECT TO INDEX.HTML / HOME
@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/index.html')


# BLOG.HTML / BLOG
@app.route('/blog', methods=['POST', 'GET'])
def display_blogs():
    blog_posts = Blog.query.all()
    blog_users = User.query.all()
    return render_template('blog.html', page_title="Blogz", author='', blogs=blog_posts, users=blog_users)


# INDEX.HTML / HOME
@app.route('/home', methods=['POST', 'GET'])
def display_users():
    blog_users = User.query.all()
    return render_template('index.html', page_title="Blog Users", users=blog_users)


@app.route('/new')
def display_blog_form():
    blog_title = ''
    blog_body = ''
    error_message = ''
    return render_template('new.html', page_title='Add a Blog Entry', error=error_message, title=blog_title, body=blog_body)


@app.route('/post', methods=['POST', 'GET'])
def display_post():
    blog_author = ''
    # Get blog-id or user-id from the link user clicked on 'Blog' page
    blog_id = request.args.get('blog_id')
    user_id = request.args.get('user_id')
    # Page of posts using user id
    if user_id is not None:
        user = User.query.filter_by(id=user_id).first()
        blog_author = user.email
        blog_users = User.query.all()
        posts_to_display = Blog.query.filter_by(owner_id=user_id)
        return render_template('blog.html', page_title="Blogz", author=blog_author, blogs=posts_to_display, users=blog_users)
    # Post requested using blog id
    else:
        blog_to_display = Blog.query.filter_by(id=blog_id).first()
        blog_title = blog_to_display.title
        blog_body =  blog_to_display.body
        return render_template('post.html', page_title=blog_title, body=blog_body)


@app.route('/new', methods=['POST', 'GET'])
def create_new_blog():
    # Get blog title and body from the form
    blog_title = request.form['title']
    blog_body = request.form['body']
    # Get blog owner from login info
    owner_email = session['email']
    owner_id = User.query.filter_by(email=owner_email).first()
    # If the title or body is NOT blank then add that new blog into database and display it
    if blog_title != '' and blog_body != '':
        new_blog = Blog(title=blog_title, body=blog_body, owner=owner_id)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('post.html', page_title=blog_title, body=blog_body)
    # If the title or body is blank then display error and re-render the new post form
    else:
        error_message = "Blog title or body is blank! Please enter and resubmit."
        return render_template('new.html', error=error_message, page_title='Add a Blog Entry', title=blog_title, body=blog_body)


# REDIRECT TO INDEX.HTML / HOME
@app.route('/login', methods=['POST', 'GET'])
def login():
    # If the user entered login information
    if request.method == 'POST':
        # Grab user data
        email = request.form['email']
        password = request.form['password']
        # Look for username in the database
        user = User.query.filter_by(email=email).first()
        # If the user exists and the right password was entered
        if user and user.password == password:
            # Assign the session a key logging in the user 
            session['email'] = email
            flash("You are logged in as " + email, "error")
            # Send user to the new blog page
            return redirect('/new')
        return render_template('login.html', page_title="Log In", error = "Username does not exist or password incorrect!")
    return render_template('login.html', page_title="Log In", error = "")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    email = ''
    password = ''
    verify = ''
    message = ''
    # If the user entered data
    if request.method == 'POST':
        # Grab user data
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        # Check to see if the user already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        # Figure out if there are any errors
        message = check_entries(email, password, verify, existing_user)
        if not existing_user and message == '':
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/new')
    # Render the template w/ errors (if there are none, no message)
    return render_template('signup.html', page_title="Sign Up", error=message)


@app.route('/logout')
def logout():
    # Check is the user is logged in before logging out
    #if session.get('email') == True:
    del session['email']
    flash('You have been logged out!', 'error')
    return redirect('/blog')


#-------------------------------------------------------------------------------- FUNCTIONS ----------------------------------------------------------------------------------


def check_entries(email, password, verify, existing_user):
    message1 = ''
    message2 = ''
    message3 = ''
    message4 = ''
    if email == '' or password == '' or verify == '':
        message1 = "One or more fields are blank. "
    if existing_user:
        message2 = "Username already exists. "
    if password != verify:
        message3 = "Passwords don't match. "
    if email != '' and password != '' and verify != '' and len(password) < 3 or len(email) < 3 or len(verify) < 3:
        message4 = "Username and password must be at least 3 characters long. "
    if message1 == '' and message2 == '' and message3 == '' and message4 == '':
        return ''
    else:
        return message1 + message2 + message3 + message4


#--------------------------------------------------------------------------------- RUN APP -----------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run()