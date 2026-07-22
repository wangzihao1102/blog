"""Integration tests for the blog application."""
import re
import warnings
import sys

warnings.filterwarnings('ignore', category=UserWarning)

# Ensure the app directory is in the path
sys.path.insert(0, '.')

from app import create_app
from app.models.post import Post
from app.models.tag import Tag
from app.models.user import User
from app.extensions import db

app = create_app()
client = app.test_client()

passed = 0
failed = 0


def test(name, condition, detail=''):
    global passed, failed
    if condition:
        print(f'  PASS: {name}')
        passed += 1
    else:
        print(f'  FAIL: {name} - {detail}')
        failed += 1


def get_csrf(html):
    """Extract CSRF token from HTML."""
    m = re.search(r'csrf_token.*?value="([^"]+)"', html)
    return m.group(1) if m else None


def login_as_admin():
    """Login as admin and return the client session."""
    lr = client.get('/admin/login')
    csrf = get_csrf(lr.data.decode())
    return client.post('/admin/login', data={
        'csrf_token': csrf,
        'username': 'admin',
        'password': 'changeme',
        'submit': '登录'
    })


# ===========================================================================
# 1. Homepage
# ===========================================================================
print('=== 1. Homepage ===')
resp = client.get('/')
test('Returns 200', resp.status_code == 200)
test('Shows welcome', '欢迎' in resp.data.decode())

# ===========================================================================
# 2. Login
# ===========================================================================
print('\n=== 2. Login ===')
resp = login_as_admin()
resp = client.get('/admin/dashboard', follow_redirects=True)
test('Login redirects to dashboard', 'Dashboard' in resp.data.decode() or '仪表盘' in resp.data.decode())

# ===========================================================================
# 3. Dashboard
# ===========================================================================
print('\n=== 3. Dashboard ===')
resp = client.get('/admin/dashboard')
test('Dashboard returns 200', resp.status_code == 200)
test('Shows stats', '总文章数' in resp.data.decode())

# ===========================================================================
# 4. Create Published Post
# ===========================================================================
print('\n=== 4. Create Published Post ===')
er = client.get('/admin/posts/new')
csrf = get_csrf(er.data.decode())
resp = client.post('/admin/posts/new', data={
    'csrf_token': csrf,
    'title': 'Hello World',
    'excerpt': 'First post',
    'body': '# Hello World\n\nThis is my first blog post.\n\n```python\nprint("Hi")\n```',
    'tags': 'hello,test',
    'publish': 'on',
    'submit': '保存文章'
}, follow_redirects=True)
test('Post created', 'Hello World' in resp.data.decode())

# ===========================================================================
# 5. View Post
# ===========================================================================
print('\n=== 5. View Post ===')
resp = client.get('/post/hello-world')
test('Post page returns 200', resp.status_code == 200, f'got {resp.status_code}')
if resp.status_code == 200:
    test('Contains title', 'Hello World' in resp.data.decode())
    test('Contains rendered content', 'Hello World' in resp.data.decode())
    test('Contains code block', 'print' in resp.data.decode())

# ===========================================================================
# 6. Homepage Shows Post
# ===========================================================================
print('\n=== 6. Homepage Shows Post ===')
resp = client.get('/')
test('Post on homepage', 'Hello World' in resp.data.decode())
test('Excerpt on homepage', 'First post' in resp.data.decode())

# ===========================================================================
# 7. Search
# ===========================================================================
print('\n=== 7. Search ===')
resp = client.get('/search?q=Hello')
test('Search returns 200', resp.status_code == 200)
test('Search finds post', 'Hello World' in resp.data.decode())

# ===========================================================================
# 8. Categories
# ===========================================================================
print('\n=== 8. Categories ===')
resp = client.get('/categories')
test('Categories returns 200', resp.status_code == 200)

# ===========================================================================
# 9. Tag Page
# ===========================================================================
print('\n=== 9. Tag Page ===')
resp = client.get('/tag/hello')
test('Tag page returns 200', resp.status_code == 200)

# ===========================================================================
# 10. Logout
# ===========================================================================
print('\n=== 10. Logout ===')
resp = client.get('/admin/logout', follow_redirects=True)
test('Logout redirects to home', '欢迎' in resp.data.decode())

# ===========================================================================
# 11. Invalid Login
# ===========================================================================
print('\n=== 11. Invalid Login ===')
lr = client.get('/admin/login')
csrf = get_csrf(lr.data.decode())
resp = client.post('/admin/login', data={
    'csrf_token': csrf,
    'username': 'admin',
    'password': 'wrong',
    'submit': '登录'
})
test('Invalid login shows error', '错误' in resp.data.decode() or 'danger' in resp.data.decode())

# ===========================================================================
# 12. Protected Routes
# ===========================================================================
print('\n=== 12. Protected Routes ===')
resp = client.get('/admin/dashboard')
test('Redirects to login', resp.status_code == 302)

# ===========================================================================
# 13. Static Files
# ===========================================================================
print('\n=== 13. Static Files ===')
test('CSS served', client.get('/static/css/style.css').status_code == 200)
test('JS served', client.get('/static/js/preview.js').status_code == 200)

# ===========================================================================
# 14. Draft Post
# ===========================================================================
print('\n=== 14. Draft Post ===')
login_as_admin()
er = client.get('/admin/posts/new')
csrf = get_csrf(er.data.decode())
resp = client.post('/admin/posts/new', data={
    'csrf_token': csrf,
    'title': 'Draft Post',
    'excerpt': 'Not published',
    'body': '# Draft\n\nThis is a draft.',
    'tags': 'draft',
    'publish': '',
    'submit': '保存文章'
}, follow_redirects=True)
test('Draft created', 'Draft' in resp.data.decode())
resp = client.get('/post/draft-post')
test('Draft not visible publicly', resp.status_code == 404)

# ===========================================================================
# 15. Tag Management
# ===========================================================================
print('\n=== 15. Tag Management ===')
resp = client.get('/admin/tags')
test('Tag page loads', resp.status_code == 200)
tag_resp = client.post('/admin/tags', data={'name': 'NewTag', 'submit': '添加标签'})
test('Add tag works', '已创建' in tag_resp.data.decode() or 'NewTag' in tag_resp.data.decode())

# ===========================================================================
# 16. Post Preview
# ===========================================================================
print('\n=== 16. Post Preview ===')
dash = client.get('/admin/dashboard').data.decode()
m = re.search(r'/admin/posts/(\d+)/edit', dash)
if m:
    post_id = m.group(1)
    resp = client.get(f'/admin/posts/{post_id}/preview')
    test('Preview returns 200', resp.status_code == 200)
else:
    test('Found post in dashboard', False)

# ===========================================================================
# 17. Duplicate Slug Handling
# ===========================================================================
print('\n=== 17. Duplicate Slug Handling ===')
er = client.get('/admin/posts/new')
csrf = get_csrf(er.data.decode())
resp = client.post('/admin/posts/new', data={
    'csrf_token': csrf,
    'title': 'Hello World',
    'excerpt': 'Second post',
    'body': '# Second Hello World',
    'tags': 'hello',
    'publish': 'on',
    'submit': '保存文章'
}, follow_redirects=True)
test('Second post created with unique slug', '文章已创建' in resp.data.decode())
resp1 = client.get('/post/hello-world')
resp2 = client.get('/post/hello-world-1')
test('First post accessible', resp1.status_code == 200, f'got {resp1.status_code}')
test('Second post accessible', resp2.status_code == 200, f'got {resp2.status_code}')

# ===========================================================================
# 18. Edit Post
# ===========================================================================
print('\n=== 18. Edit Post ===')
er = client.get('/admin/posts/1/edit')
test('Edit page loads', er.status_code == 200)
if er.status_code == 200:
    csrf = get_csrf(er.data.decode())
    resp = client.post('/admin/posts/1/edit', data={
        'csrf_token': csrf,
        'title': 'Hello World Updated',
        'excerpt': 'Updated excerpt',
        'body': '# Updated\n\nThis content was edited.',
        'tags': 'hello,test,updated',
        'publish': 'on',
        'submit': '保存文章'
    }, follow_redirects=True)
    test('Edit saves successfully', 'Updated' in resp.data.decode())
    resp = client.get('/post/hello-world-updated')
    test('Edited post accessible', resp.status_code == 200, f'got {resp.status_code}')

# ===========================================================================
# Summary
# ===========================================================================
print()
print('=' * 50)
print(f'RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests')
print('=' * 50)
if failed > 0:
    sys.exit(1)
else:
    print('ALL TESTS PASSED!')
