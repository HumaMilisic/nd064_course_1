import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


no_connections = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    app.logger.debug("get db connection")
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global  no_connections
    no_connections = no_connections+1
    return connection



# Function to get a post using its ID
def get_post(post_id):
    app.logger.debug("get post")
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    app.logger.info("index loading")
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    # title = post['title']
    if post is None:
        app.logger.info('no article')
        return render_template('404.html'), 404
    else:
        app.logger.info("article title "+post['title'])
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('about page')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    app.logger.debug("create "+request.method)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            app.logger.info("article title "+title)
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    return response


def get_db_connection_count():
    return no_connections


def get_post_count():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    count = len(posts)
    connection.close()
    return count


@app.route('/metrics')
def metrics():
    db_connection_count = get_db_connection_count()
    post_count = get_post_count()
    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count, "post_count": post_count}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Metrics request successfull')
    return response

# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,datefmt='%Y-%m-%d %H:%M:%S')
    app.run(host='0.0.0.0', port='3111')
    app.logger.info('application started')
