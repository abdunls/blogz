from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hello123@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET']) # do I need "methods" here?
def index():
    if request.method == 'POST':
        blog_title = request.form['blog']
        new_blog = Blog(blog_title)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog!", blogs=blogs)


@app.route('/blogs', methods=['POST', 'GET'])
# shows all blogs that have been posted
def all_blogs():
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build a Blog!", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
# shows form where you can add a new blog post
def something():
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

        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit() 

        print("This is the new blog id: " + str(new_blog.id))

        return redirect('/blog?id=' + str(new_blog.id)) 
        
    return render_template('newpost.html', title="Add a new post", blog_title="", blog_body="")


@app.route('/blog', methods=['GET'])
def query_blog():
    post = Blog.query.filter_by(id=request.args.get("id"))
    return render_template('entry.html', blogs=post)



    #do I need to include this form in the main.py file?
# form """ 
# <!DOCTYPE html>
# <html>
#     <head>
#         <title>SignUp</title>
#         <style type="text/css">
#             .error {
#                 color: red;
#             }
#         </style>
#     </head>
#     <body>
        

#         <h1>Build a Blog</h1>
#         <form action="/newpost" id="form" method="POST">
#             <h1>Add a New Post</h1>
#             <label for="title">Title for your new blog:</label>
#             <input type="text" name="title" id="title" value="" >
            
#             <br></br>
            
#         </form>

#         <textarea name="new_blog" form="form">Your new blog:</textarea>
                
#         <button type="submit">Add a new post</button>
            
#     </body>
# </html>
# """


# Blog form that was showing up on main page -- previously in blog.html
# <form action="/newpost" id="form" method="POST">
#         <h2>Add a New Post</h2>
#         <label for="title">Title for your new blog:</label>
#         <br></br>
#         <input type="text" name="title" id="title" value="" >
        
#         <br></br>
        
#     </form>

# <p>Your new blog:</p>
# <textarea name="new_blog" form="form"></textarea>

# <br></br>

# <button type="submit">Add a new post</button>


if __name__ == '__main__':
    app.run()