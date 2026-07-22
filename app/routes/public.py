"""Public-facing routes."""
from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.extensions import db
from app.models.post import Post
from app.models.tag import Tag
from app.config import Config

pub_bp = Blueprint('public', __name__)


@pub_bp.route('/')
def index():
    """Homepage with paginated post list."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_published=True) \
        .order_by(Post.date_created.desc()) \
        .paginate(page=page, per_page=Config.POSTS_PER_PAGE, error_out=False)
    return render_template('public/index.html', posts=posts)


@pub_bp.route('/post/<slug>')
def post_detail(slug):
    """Individual post detail page."""
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    # Previous/next post navigation
    prev_post = Post.query.filter(
        Post.is_published == True,
        Post.date_created < post.date_created
    ).order_by(Post.date_created.desc()).first()
    next_post = Post.query.filter(
        Post.is_published == True,
        Post.date_created > post.date_created
    ).order_by(Post.date_created.asc()).first()
    return render_template('public/post_detail.html', post=post,
                           prev_post=prev_post, next_post=next_post)


@pub_bp.route('/tag/<slug>')
def by_tag(slug):
    """Posts filtered by tag."""
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(
        Post.is_published == True,
        Post.tags.any(Tag.slug == slug)
    ).order_by(Post.date_created.desc()) \
     .paginate(page=page, per_page=Config.POSTS_PER_PAGE, error_out=False)
    return render_template('public/tag_list.html', tag=tag, posts=posts)


@pub_bp.route('/search')
def search():
    """Full-text search by title or body."""
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('public.index'))
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(
        Post.is_published == True,
        (Post.title.contains(q) | Post.body.contains(q))
    ).order_by(Post.date_created.desc()) \
     .paginate(page=page, per_page=Config.POSTS_PER_PAGE, error_out=False)
    return render_template('public/search.html', query=q, posts=posts)


@pub_bp.route('/categories')
def categories():
    """Archive listing grouped by year."""
    from sqlalchemy import func, text
    years = db.session.query(func.extract('year', Post.date_created).label('yr')) \
        .filter(Post.is_published == True) \
        .distinct().order_by(text('yr desc')).all()
    year_list = [int(float(y.yr)) for y in years]
    return render_template('public/categories.html', years=year_list)


@pub_bp.route('/archive/<int:year>/<int:month>')
def archive(year, month):
    """Monthly archive listing."""
    from sqlalchemy import extract
    posts = Post.query.filter(
        Post.is_published == True,
        extract('year', Post.date_created) == year,
        extract('month', Post.date_created) == month
    ).order_by(Post.date_created.desc()).all()
    month_names = ['', '一月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '十一月', '十二月']
    title = f'{year}年{month_names[month]}'
    return render_template('public/index.html', posts=posts, title=title)
