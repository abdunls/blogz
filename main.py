from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hello123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'makesomethingup'
db = SQLAlchemy(app)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'all_blogs', 'query_blog' 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
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


@app.route('/', methods=['POST', 'GET']) # do I need "methods" here?
def index():
    if request.method == 'POST':
        blog_title = request.form['blog']
        new_blog = Blog(blog_title)
        db.session.add(new_blog)
        db.session.commit()

    users = User.query.all()
    return render_template('index.html', users=users)

    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog!", blogs=blogs)


@app.route('/blogs', methods=['GET'])
# shows all blogs that have been posted
def all_blogs():
    if 'user' in request.args:
        user_id = request.args.getlist('user')
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', user_blogs=user_blogs)
    
    single_post = request.args.get('id')
    if single_post:
        blogs = Blog.query.get(single_post)
        return render_template('entry.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = ""
    password_error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # password_check = User.query.filter_by(password=password).first()
        
        if user and user.password == password:
            # remember that the user has logged in
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')

        if user.password != password:
            # correct username but incorrect password
            flash("Password incorrect")
            password_error = "Incorrect password"
            return render_template('login.html', username_error=username_error, password_error=password_error)
        
        if not username: 
            flash("Username incorrect or user does not exist")
            username_error = "User not found"
            return render_template('login.html', username_error=username_error, password_error=password_error)
        if not password:
            password_error = "Password needed"
            return render_template('login.html', username_error=username_error, password_error=password_error)
        else: 
            # explain why login failed 
            flash('User password incorrect or user does not exist', 'error')
            # inlcude a button that says "Create Account" 
            return "<input type='submit' value='Create Account'>"
            
    return render_template('login.html', username_error=username_error, password_error=password_error)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        usernameError = ""
        passwordError = ""
        password2Error = ""
        error = ""

        existing_user = User.query.filter_by(username=username).first()    
        if existing_user:
            usernameError = "Username already exists"
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            # remember the user
            session['username'] = username
            return redirect('/newpost')
        if not username or not password or not verify:
            error = "One or more fields are invalid"       
        if password != verify:
            password2Error = "Verify Password must match Password" 
        if len(password) < 3 or len(username) < 3: 
            passwordError = "Password must be more than 3 characters long"
            usernameError = "Username must be more than 3 characters long"
        else:
            # TODO user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')


@app.route('/newpost', methods=['POST', 'GET'])
# shows form where you can add a new blog post
# TODO think about what you'll need to do in your /newpost route handler function since there is a new parameter to consider when creating a blog entry
def something():
    
    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        title_error = ""
        body_error = ""

        if not blog_title:
            title_error = "Blog post needs a title"
        if not blog_body:
            body_error = "Blog post needs content"
        if title_error or body_error:
            return render_template('newpost.html', title=blog_title, title_error_render=title_error, body=blog_body, body_error_render=body_error)    

        if len(blog_title) > 3 and len(blog_body) > 3:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit() 
            id = str(new_blog.id)

        return redirect('/blog?id=' + id) 
        
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('newpost.html', title="Add a new post", blogs=blogs, blog_title="", blog_body="")


@app.route('/blog', methods=['POST', 'GET'])
def query_blog():
    
    if 'user' in request.args:
        user_id = request.args.getlist('user')
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', user_blogs=user_blogs)
    
    single_post = request.args.get('id')
    if single_post:
        blogs = Blog.query.get(single_post)
        post = Blog.query.filter_by(id=request.args.get("id"))
        return render_template('entry.html', blogs=post)

        # return render_template('entry.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)
    

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/')


if __name__ == '__main__':
    app.run()
