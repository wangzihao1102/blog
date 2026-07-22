"""Admin routes (login, dashboard, CRUD)."""
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, \
    url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, render_markdown
from app.models.post import Post
from app.models.tag import Tag
from app.models.user import User
from app.forms.auth import LoginForm
from app.forms.post import PostForm
from app.forms.tag import TagForm
from app.utils.markdown import generate_slug

admin_bp = Blueprint('admin', __name__)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('用户名或密码错误。', 'danger')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for('public.index'))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard with stats and recent posts."""
    total_posts = Post.query.count()
    published = Post.query.filter_by(is_published=True).count()
    drafts = total_posts - published
    recent = Post.query.order_by(Post.date_created.desc()).limit(5).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/dashboard.html',
                           total_posts=total_posts,
                           published=published,
                           drafts=drafts,
                           recent=recent,
                           tags=tags)


# ---------------------------------------------------------------------------
# Post CRUD
# ---------------------------------------------------------------------------

@admin_bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def post_create():
    """Create a new blog post."""
    form = PostForm()
    if form.validate_on_submit():
        slug_base = generate_slug(form.title.data)
        slug = slug_base
        counter = 1
        while Post.query.filter_by(slug=slug).first():
            slug = f'{slug_base}-{counter}'
            counter += 1
        post = Post(
            title=form.title.data,
            slug=slug,
            excerpt=form.excerpt.data or '',
            body=form.body.data,
            is_published=form.publish.data,
            author=current_user,
        )
        _process_tags(form, post)
        db.session.add(post)
        db.session.commit()
        flash('文章已创建！', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/post_edit.html', form=form, post=None)


@admin_bp.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def post_edit(id):
    """Edit an existing blog post."""
    post = db.session.get(Post, id) or abort(404)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        slug_base = generate_slug(form.title.data)
        slug = slug_base
        counter = 1
        while Post.query.filter_by(slug=slug).first() and slug != post.slug:
            slug = f'{slug_base}-{counter}'
            counter += 1
        post.slug = slug
        post.excerpt = form.excerpt.data or ''
        post.body = form.body.data
        post.is_published = form.publish.data
        _process_tags(form, post)
        db.session.commit()
        flash('文章已更新！', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/post_edit.html', form=form, post=post)


@admin_bp.route('/posts/<int:id>/delete', methods=['POST'])
@login_required
def post_delete(id):
    """Delete a blog post."""
    post = db.session.get(Post, id) or abort(404)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除。', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/posts/<int:id>/preview')
@login_required
def post_preview(id):
    """Preview a post by rendering its markdown."""
    post = db.session.get(Post, id) or abort(404)
    body_html = render_markdown(post.body)
    return render_template('public/post_detail.html', post=post,
                           body_html=body_html)


@admin_bp.route('/posts/preview-inline', methods=['POST'])
@login_required
def preview_inline():
    """Live preview of markdown content without saving."""
    body = request.form.get('body', '')
    title = request.form.get('title', '未命名文章')
    body_html = render_markdown(body)
    return render_template('public/post_detail.html',
                           post=type('Obj', (), {
                               'title': title,
                               'body_html': body_html,
                               'tags': [],
                               'date_created': datetime.utcnow(),
                               'author': current_user,
                           })())


# ---------------------------------------------------------------------------
# Tag Management
# ---------------------------------------------------------------------------

@admin_bp.route('/tags', methods=['GET', 'POST'])
@login_required
def tag_manage():
    """Manage tags."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            slug = generate_slug(name)
            existing = Tag.query.filter_by(slug=slug).first()
            if not existing:
                tag = Tag(name=name, slug=slug)
                db.session.add(tag)
                db.session.commit()
                flash(f'标签 "{name}" 已创建。', 'success')
            else:
                flash(f'标签 "{name}" 已存在。', 'warning')
        else:
            flash('标签名称不能为空。', 'danger')
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/tag_manage.html', tags=tags)


@admin_bp.route('/tags/<int:id>/delete', methods=['POST'])
@login_required
def tag_delete(id):
    """Delete a tag."""
    tag = db.session.get(Tag, id) or abort(404)
    db.session.delete(tag)
    db.session.commit()
    flash('标签已删除。', 'warning')
    return redirect(url_for('admin.tag_manage'))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _process_tags(form, post):
    """Parse comma-separated tags from form and assign to post."""
    tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
    tags = []
    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name, slug=generate_slug(name))
            db.session.add(tag)
            db.session.flush()  # Assign ID without committing
        tags.append(tag)
    post.tags = tags
