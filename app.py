from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests

import os
=======


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ollama API Configuration

OLLAMA_URL = "http://192.168.12.174:11434/api/generate"  # Ensure this is the correct host for your Ollama server
=======
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"  # Ensure this is the correct host for your Ollama server

MODEL_NAME = "gemma:2b"

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/writoria')
def writoria():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        post = Post(title=title, content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('write.html')

@app.route('/blog')
@login_required
def blog():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_detail(post_id):
    print(f"Received post_id: {post_id}")  # Debugging
    post = Post.query.get_or_404(post_id)
    return render_template('blog_detail.html', post=post)

@app.route('/write-blog', methods=['GET', 'POST'])
@login_required
def write_blog():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            post = Post(title=title, content=content, author=current_user)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('blog'))
            
    return render_template('write-blog.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("You are not authorized to edit this post.")
        return redirect(url_for('blog_detail', post_id=post.id))
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('blog_detail', post_id=post.id))

    return render_template('edit_blog.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_blog(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("You are not authorized to delete this post.")
        return redirect(url_for('blog_detail', post_id=post.id))
    
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully.")
    return redirect(url_for('blog'))

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    page_content = data.get("page_content", "")

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Prepare prompt with page content
    prompt = f"""
    You are a helpful assistant named Rick. The user is viewing a webpage with the following content:

    {page_content}

    The user asks: "{user_message}"
    
    Answer their question using information from the page. If the information is not available, let them know.
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=30
        )

        if response.status_code == 200:
            response_data = response.json()
            return jsonify({"response": response_data.get("response", "No response generated.")})
        else:
            return jsonify({"error": f"Ollama API error: {response.text}"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
