import os
from flask import (
    render_template, redirect, url_for, flash,
    request, abort, Blueprint, current_app, send_from_directory
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db
from app.models import (
    User, Post, Comment, Category, Tag, Notification, PostTags
)
from app.forms import (
    RegistrationForm, LoginForm, PostForm,
    CommentForm, CategoryForm, TagForm, ProfileUpdateForm
)

main = Blueprint('main', __name__)

# -------------------------------
# Helpers
# -------------------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# -------------------------------
# Home Page
# -------------------------------
@main.route('/')
def index():
    posts = Post.query.filter_by(status='published').order_by(Post.published_at.desc()).all()
    return render_template('index.html', posts=posts)

# -------------------------------
# Register
# -------------------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_pw,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

# -------------------------------
# Login
# -------------------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

# -------------------------------
# Logout
# -------------------------------
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('main.index'))

# -------------------------------
# Admin Dashboard
# -------------------------------
@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)

    users = User.query.all()
    posts = Post.query.all()
    comments = Comment.query.all()
    categories = Category.query.all()
    return render_template(
        'admin_dashboard.html',
        users=users,
        posts=posts,
        comments=comments,
        categories=categories
    )

# -------------------------------
# Author Dashboard
# -------------------------------
@main.route('/author/dashboard')
@login_required
def author_dashboard():
    if current_user.role != 'author':
        abort(403)

    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template(
        'author_dashboard.html',
        posts=posts
    )

# -------------------------------
# Create New Post
# -------------------------------
@main.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if current_user.role != 'author':
        abort(403)

    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    form.tags.choices = [(t.id, t.name) for t in Tag.query.all()]

    if form.validate_on_submit():
        filename = None
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(upload_path)

        post = Post(
            title=form.title.data,
            content=form.content.data,
            image_filename=filename,
            user_id=current_user.id,
            category_id=form.category.data if form.category.data else None,
            status='pending' if current_user.role == 'author' else 'published',
            scheduled_publish=form.scheduled_publish.data if form.scheduled_publish.data else None,
            published_at=datetime.utcnow() if not form.scheduled_publish.data else None
        )
        db.session.add(post)
        db.session.commit()

        # handle tags
        for tag_id in form.tags.data:
            post_tag = PostTags(post_id=post.id, tag_id=tag_id)
            db.session.add(post_tag)
        db.session.commit()

        flash('Post created.', 'success')
        return redirect(url_for('main.author_dashboard'))

    return render_template('create_post.html', form=form)
# -------------------------------
# Edit Post
# -------------------------------
@main.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Only the author or admin can edit
    if current_user.role != 'admin' and post.user_id != current_user.id:
        abort(403)

    form = PostForm(obj=post)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    form.tags.choices = [(t.id, t.name) for t in Tag.query.all()]

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category_id = form.category.data if form.category.data else None
        post.scheduled_publish = form.scheduled_publish.data if form.scheduled_publish.data else None
        if not post.scheduled_publish:
            post.published_at = datetime.utcnow()

        # handle image if new image uploaded
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(upload_path)
            post.image_filename = filename

        db.session.commit()

        # update tags
        PostTags.query.filter_by(post_id=post.id).delete()
        for tag_id in form.tags.data:
            db.session.add(PostTags(post_id=post.id, tag_id=tag_id))
        db.session.commit()

        flash('Post updated.', 'success')
        return redirect(url_for('main.author_dashboard'))

    return render_template('edit_post.html', form=form, post=post)

# -------------------------------
# View Single Post
# -------------------------------
@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    if post.status != 'published' and current_user.role != 'admin' and post.author != current_user:
        abort(403)

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            post_id=post.id,
            name=form.name.data,
            email=form.email.data,
            content=form.content.data,
        )
        db.session.add(comment)
        db.session.commit()

        # create notification
        if post.author != current_user:
            notif = Notification(
                user_id=post.author.id,
                message=f"New comment on your post: {post.title}"
            )
            db.session.add(notif)
            db.session.commit()

        flash('Comment added!', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))

    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).all()
    return render_template('post_detail.html', post=post, form=form, comments=comments)

# -------------------------------
# Search
# -------------------------------
@main.route('/search')
def search():
    query = request.args.get('q', '')
    posts = []
    if query:
        posts = Post.query.filter(
            Post.title.ilike(f"%{query}%")
        ).all()
    return render_template('search_results.html', posts=posts, query=query)

# -------------------------------
# Uploads (serve images)
# -------------------------------
@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename
    )

# -------------------------------
# General Dashboard
# -------------------------------
@main.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# -------------------------------
# Admin: Pending Posts
# -------------------------------
@main.route('/admin/posts/pending')
@login_required
def pending_posts():
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.index'))

    posts = Post.query.filter_by(status='pending').all()
    return render_template('admin_pending_posts.html', posts=posts)

@main.route('/admin/posts/approve/<int:post_id>')
@login_required
def approve_post(post_id):
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.index'))

    post = Post.query.get_or_404(post_id)
    post.status = 'published'
    post.published_at = datetime.utcnow()
    db.session.commit()
    flash("Post approved and published!", "success")
    return redirect(url_for('main.pending_posts'))

@main.route('/admin/posts/reject/<int:post_id>')
@login_required
def reject_post(post_id):
    if current_user.role != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('main.index'))

    post = Post.query.get_or_404(post_id)
    post.status = 'rejected'
    db.session.commit()
    flash("Post has been rejected.", "warning")
    return redirect(url_for('main.pending_posts'))
