"""
blog/urls.py

URL patterns for the blog app.
These are included from the main blog_project/urls.py via include('blog.urls').

Pattern format: path('url/', view_function, name='url_name')
  - url/         → What appears in the browser address bar
  - view_function → Which view handles this URL
  - name=        → Unique name used in templates & redirects: {% url 'home' %}
"""

from django.urls import path
from . import views

urlpatterns = [
    # ─────────────────────────────────────────
    # MAIN PAGES
    # ─────────────────────────────────────────

    # Homepage: /
    path('', views.home, name='home'),

    # Search: /search/?q=your+query
    path('search/', views.search, name='search'),

    # ─────────────────────────────────────────
    # BLOG POSTS
    # ─────────────────────────────────────────

    # Create new post: /post/create/
    path('post/create/', views.post_create, name='post_create'),

    # View single post: /post/my-post-slug/
    # <slug:slug> captures the URL slug and passes it to the view
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),

    # Edit post: /post/my-post-slug/edit/
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),

    # Delete post: /post/my-post-slug/delete/
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),

    # ─────────────────────────────────────────
    # CATEGORIES & TAGS
    # ─────────────────────────────────────────

    # Category listing: /category/technology/
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),

    # Tag listing: /tag/python/
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),

    # ─────────────────────────────────────────
    # COMMENTS
    # ─────────────────────────────────────────

    # Add comment to a post: /post/my-post-slug/comment/
    path('post/<slug:post_slug>/comment/', views.add_comment, name='add_comment'),

    # Delete a comment: /comment/42/delete/
    # <int:comment_id> captures an integer (the comment's primary key)
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # ─────────────────────────────────────────
    # USER DASHBOARD
    # ─────────────────────────────────────────

    # Author's dashboard: /dashboard/
    path('dashboard/', views.dashboard, name='dashboard'),
]
