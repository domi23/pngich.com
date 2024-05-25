from flask import Flask, render_template, request, redirect, url_for, session
import os
import sqlite3
import datetime
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'C:\\Users\\konon\\OneDrive\\Рабочий стол\\Site\\static\\user_avatars\\'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'aff12443sfgfdfs'

DB_PATH = 'users.db'

def create_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comments
             (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, user_id INTEGER, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(post_id) REFERENCES posts(id), FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT, avatar TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, image_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, subscriber_id INTEGER, user_id INTEGER, FOREIGN KEY(subscriber_id) REFERENCES users(id), FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT posts.content, users.username, users.avatar, posts.image_path FROM posts JOIN users ON posts.user_id = users.id")
    posts = [{'content': row[0], 'username': row[1], 'avatar': row[2], 'image_path': row[3]} for row in c.fetchall()]

    subscribed_users = []
    if 'logged_in' in session:
        user_id = session.get('user_id')
        c.execute("SELECT users.username, users.avatar, users.id as user_id FROM subscriptions JOIN users ON subscriptions.user_id = users.id WHERE subscriber_id = ?", (user_id,))
        subscribed_users = [{'username': row[0], 'avatar': row[1], 'user_id': row[2]} for row in c.fetchall()]

    conn.close()
    return render_template('punter.html', posts=posts, subscribed_users=subscribed_users)

@app.route('/post_image')
def post_image():
    return render_template('post_image.html')

@app.route('/register-page')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return render_template('register.html', register_error="Пароли не совпадают. Пожалуйста, попробуйте еще раз.")

    if len(username) > 15 or len(email) > 25 or len(password) > 10:
        return render_template('register.html', register_error="Некоторые поля превышают допустимые значения.")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = c.fetchone()
    if existing_user:
        conn.close()
        return render_template('register.html', register_error="Этот email уже зарегистрирован. Пожалуйста, используйте другой.")

    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    user_id = c.lastrowid
    conn.close()

    # Log the user in
    session['logged_in'] = True
    session['user_id'] = user_id
    session['email'] = email
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].lower()
    password = request.form['password']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE LOWER(email) = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['logged_in'] = True
        session['user_id'] = user[0]
        session['email'] = user[2]
        return redirect(url_for('index'))
    else:
        return render_template('register.html', login_error="Неправильный email или пароль. Пожалуйста, попробуйте еще раз.")



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'logged_in' in session:
        try:
            username = request.form['username']
            password = request.form['password']

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            if 'avatar' in request.files and request.files['avatar'].filename != '':
                avatar = request.files['avatar']
                file_extension = avatar.filename.split('.')[-1]
                file_name = session['email'].split('@')[0] + '.' + file_extension
                avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                avatar.save(avatar_path)
                c.execute("UPDATE users SET username = ?, password = ?, avatar = ? WHERE email = ?", (username, password, file_name, session['email']))
            else:
                c.execute("UPDATE users SET username = ?, password = ? WHERE email = ?", (username, password, session['email']))

            conn.commit()
            conn.close()

            return redirect(url_for('profile'))
        except Exception as e:
            return str(e)
    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'logged_in' in session:
        if 'email' in session:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (session['email'],))
            user = c.fetchone()
            c.execute("SELECT content, image_path FROM posts WHERE user_id = ?", (user[0],))
            posts = [{'content': row[0], 'image_path': row[1]} for row in c.fetchall()]
            c.execute("SELECT COUNT(*) FROM subscriptions WHERE user_id = ?", (user[0],))
            num_followers = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM subscriptions WHERE subscriber_id = ?", (user[0],))
            num_following = c.fetchone()[0]
            is_subscribed = False
            if 'user_id' in session:
                c.execute("SELECT COUNT(*) FROM subscriptions WHERE subscriber_id = ? AND user_id = ?", (session['user_id'], user[0]))
                is_subscribed = c.fetchone()[0] > 0
            conn.close()

            if user:
                user_info = {
                    'user_id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'avatar': user[4] if user[4] else 'default-avatar.jpg'
                }
                return render_template('profile.html', user_info=user_info, user_posts=posts, is_owner=True, num_followers=num_followers, num_following=num_following, is_subscribed=is_subscribed)
            else:
                return "User not found."
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query')
    if query:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username, email, IFNULL(avatar, 'default-avatar.png') FROM users WHERE username LIKE ?", ('%' + query + '%',))
        results = c.fetchall()
        conn.close()
        return render_template('search_results.html', results=results, query=query)
    else:
        return "No search query provided."

@app.route('/view_profile/<int:user_id>')
def view_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    if not user:
        conn.close()
        return "Пользователь не найден."

    c.execute("SELECT content, image_path FROM posts WHERE user_id = ?", (user[0],))
    posts = [{'content': row[0], 'image_path': row[1]} for row in c.fetchall()]
    c.execute("SELECT COUNT(*) FROM subscriptions WHERE user_id = ?", (user[0],))
    num_followers = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM subscriptions WHERE subscriber_id = ?", (user[0],))
    num_following = c.fetchone()[0]
    
    is_owner = 'email' in session and session['email'] == user[2]
    
    is_subscribed = False
    if 'user_id' in session:
        c.execute("SELECT COUNT(*) FROM subscriptions WHERE subscriber_id = ? AND user_id = ?", (session['user_id'], user[0]))
        is_subscribed = c.fetchone()[0] > 0

    conn.close()

    user_info = {
        'user_id': user[0],
        'username': user[1],
        'email': user[2],
        'avatar': user[4] if user[4] else 'default-avatar.jpg'
    }

    return render_template('profile.html', user_info=user_info, user_posts=posts, is_owner=is_owner, num_followers=num_followers, num_following=num_following, is_subscribed=is_subscribed)

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'logged_in' in session:
        try:
            content = request.form['content']
            post_image = request.files['post_image']

            if post_image and post_image.filename != '':
                if not allowed_file(post_image.filename):
                    return render_template('post_image.html', error="Неправильный формат файла. Допустимы только jpg, jpeg, png.")

                user_email_prefix = session['email'].split('@')[0]

                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM posts WHERE user_id = ?", (session['user_id'],))
                count = c.fetchone()[0]
                conn.close()

                image_filename = f"Post{count + 1}_{user_email_prefix}.{post_image.filename.rsplit('.', 1)[1].lower()}"
                image_path = os.path.join('C:\\Users\\konon\\OneDrive\\Рабочий стол\\Site\\static\\user_posts', image_filename)
                post_image.save(image_path)
            else:
                image_filename = None

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO posts (user_id, content, image_path, created_at) VALUES (?, ?, ?, ?)", 
                      (session['user_id'], content, image_filename, datetime.datetime.now()))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except Exception as e:
            return str(e)
    else:
        return redirect(url_for('login'))

@app.route('/subscribe/<int:user_id>')
def subscribe(user_id):
    if 'logged_in' in session:
        subscriber_id = session.get('user_id')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO subscriptions (subscriber_id, user_id) VALUES (?, ?)", (subscriber_id, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_profile', user_id=user_id))
    else:
        return redirect(url_for('login'))

@app.route('/unsubscribe/<int:user_id>')
def unsubscribe(user_id):
    if 'logged_in' in session:
        subscriber_id = session.get('user_id')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM subscriptions WHERE subscriber_id = ? AND user_id = ?", (subscriber_id, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_profile', user_id=user_id))
    else:
        return redirect(url_for('login'))
    
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
