"""
blog/views.py

Views are the "controllers" in Django's MVT (Model-View-Template) pattern.
Each view function receives an HTTP request and returns an HTTP response.

Views in this file:
  1.  home              — Homepage with featured & recent posts
  2.  post_detail       — Single post page with comments
  3.  post_create       — Create a new blog post (auth required)
  4.  post_edit         — Edit an existing post (auth required)
  5.  post_delete       — Delete a post (auth required)
  6.  category_detail   — All posts in a category
  7.  tag_detail        — All posts with a specific tag
  8.  search            — Search posts by keyword
  9.  register          — User registration
  10. profile           — User profile & their posts
  11. add_comment       — Submit a comment (AJAX or normal form)
  12. delete_comment    — Delete a comment
  13. dashboard         — Author's personal dashboard
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST

from .models import Post, Category, Comment, UserProfile
from .forms import (
    PostForm, CommentForm, UserRegistrationForm,
    UserProfileForm, UserUpdateForm
)


# ─────────────────────────────────────────────
# 1. HOME VIEW
# ─────────────────────────────────────────────
def home(request):
    """
    Homepage: Shows featured posts, recent posts, categories, and popular tags.

    Query logic:
    - Only show 'published' posts (not drafts)
    - featured_posts: Posts marked as featured (max 3)
    - recent_posts: Latest published posts paginated (6 per page)
    """
    # Get all published posts
    all_published = Post.objects.filter(status='published').select_related('author', 'category')

    # Featured posts (limited to 3 for the hero section)
    featured_posts = all_published.filter(featured=True)[:3]

    # Recent posts (for the main grid) — paginated
    recent_qs = all_published.order_by('-published_at', '-created_at')
    paginator = Paginator(recent_qs, 6)  # 6 posts per page
    page_number = request.GET.get('page')
    recent_posts = paginator.get_page(page_number)

    # Sidebar: All categories with post count
    # annotate() adds an extra calculated field (post_count) to each category
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    )

    # Sidebar: Popular tags (using taggit)
    from taggit.models import Tag
    popular_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]  # Top 10 tags

    context = {
        'featured_posts': featured_posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'popular_tags': popular_tags,
    }
    return render(request, 'blog/home.html', context)


# ─────────────────────────────────────────────
# 2. POST DETAIL VIEW
# ─────────────────────────────────────────────
def post_detail(request, slug):
    """
    Displays a single blog post with its comments.

    - get_object_or_404: Returns 404 if post not found or not published
    - Increments view count on each visit
    - Loads approved comments and comment form
    - Shows "related posts" (same category, different post)
    """
    # Fetch the post or show 404 if not found / not published
    post = get_object_or_404(Post, slug=slug, status='published')

    # Increment view counter every time the page loads
    Post.objects.filter(pk=post.pk).update(views=post.views + 1)

    # Get all approved top-level comments (no parent) for this post
    # prefetch_related('replies') loads replies in one extra query (efficient)
    comments = post.comments.filter(
        is_approved=True,
        parent=None   # Only top-level (not replies)
    ).select_related('author', 'author__profile').prefetch_related('replies__author')

    # Comment form — empty for GET, populated for POST
    comment_form = CommentForm()

    # Related posts: same category, excluding current post (max 3)
    related_posts = Post.objects.filter(
        status='published',
        category=post.category
    ).exclude(pk=post.pk).order_by('-created_at')[:3]

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


# ─────────────────────────────────────────────
# 3. CREATE POST VIEW
# ─────────────────────────────────────────────
@login_required  # Decorator: if not logged in, redirect to /login/
def post_create(request):
    """
    Handles creating a new blog post.

    GET  → Show empty form
    POST → Validate and save form data
    """
    if request.method == 'POST':
        # request.FILES handles the uploaded thumbnail image
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # commit=False means: create the object but DON'T save to DB yet
            # We need to set the author first
            post = form.save(commit=False)
            post.author = request.user  # Set the logged-in user as author

            # If status is being set to 'published', record the publish time
            if post.status == 'published':
                post.published_at = timezone.now()

            post.save()

            # Required after save() when using TaggableManager (ManyToMany)
            form.save_m2m()

            messages.success(request, f'Post "{post.title}" created successfully! 🎉')
            # `post_detail` shows only published posts (status='published').
            # If the user saved as draft, redirect to the edit page instead.
            if post.status == 'draft':
                return redirect('post_edit', slug=post.slug)
            return redirect('post_detail', slug=post.slug)
    else:
        # GET request: show empty form
        form = PostForm()

    return render(request, 'blog/post_form.html', {
        'form': form,
        'action': 'Create',  # Used in template: "Create Post" vs "Edit Post"
    })


# ─────────────────────────────────────────────
# 4. EDIT POST VIEW
# ─────────────────────────────────────────────
@login_required
def post_edit(request, slug):
    """
    Handles editing an existing post.
    Only the post's author can edit it.
    """
    # Fetch the post — must belong to the logged-in user
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        # instance=post tells the form to UPDATE this post, not create a new one
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)

            # If changing to published and no published_at date yet
            if updated_post.status == 'published' and not updated_post.published_at:
                updated_post.published_at = timezone.now()

            updated_post.save()
            form.save_m2m()

            messages.success(request, f'Post "{updated_post.title}" updated successfully! ✏️')
            # Keep drafts inside the author's edit flow.
            if updated_post.status == 'draft':
                return redirect('post_edit', slug=updated_post.slug)
            return redirect('post_detail', slug=updated_post.slug)
    else:
        # Pre-fill the form with existing post data
        form = PostForm(instance=post)

    return render(request, 'blog/post_form.html', {
        'form': form,
        'post': post,
        'action': 'Edit',
    })


# ─────────────────────────────────────────────
# 5. DELETE POST VIEW
# ─────────────────────────────────────────────
@login_required
def post_delete(request, slug):
    """
    Deletes a blog post.
    Shows a confirmation page on GET, performs delete on POST.
    """
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        title = post.title
        post.delete()  # This permanently removes the row from the database
        messages.success(request, f'Post "{title}" has been deleted.')
        return redirect('dashboard')

    # GET: show confirmation page
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


# ─────────────────────────────────────────────
# 6. CATEGORY DETAIL VIEW
# ─────────────────────────────────────────────
def category_detail(request, slug):
    """Shows all published posts belonging to a specific category."""
    category = get_object_or_404(Category, slug=slug)

    # Get posts in this category, paginated
    posts_qs = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author').order_by('-created_at')

    paginator = Paginator(posts_qs, 8)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    # All categories for sidebar
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    )

    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts,
        'categories': categories,
    })


# ─────────────────────────────────────────────
# 7. TAG DETAIL VIEW
# ─────────────────────────────────────────────
def tag_detail(request, slug):
    """Shows all published posts with a specific tag."""
    from taggit.models import Tag
    tag = get_object_or_404(Tag, slug=slug)

    # taggit provides .filter(tags__slug=slug) to query by tag
    posts_qs = Post.objects.filter(
        tags__slug=slug,
        status='published'
    ).order_by('-created_at')

    paginator = Paginator(posts_qs, 8)
    posts = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/tag_detail.html', {
        'tag': tag,
        'posts': posts,
    })


# ─────────────────────────────────────────────
# 8. SEARCH VIEW
# ─────────────────────────────────────────────
def search(request):
    """
    Full-text search across post titles, excerpts, and content.
    Uses Django Q objects for OR queries.
    """
    query = request.GET.get('q', '').strip()  # Get search term from URL ?q=...
    posts = Post.objects.none()               # Start with empty queryset

    if query:
        # Q objects allow OR conditions:
        # Filter posts where title OR excerpt OR content contains the query
        posts_qs = Post.objects.filter(
            Q(title__icontains=query) |       # Case-insensitive title search
            Q(excerpt__icontains=query) |     # Case-insensitive excerpt search
            Q(content__icontains=query),      # Case-insensitive content search
            status='published'
        ).distinct().order_by('-created_at')  # .distinct() avoids duplicate results

        paginator = Paginator(posts_qs, 8)
        posts = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/search.html', {
        'query': query,
        'posts': posts,
    })


# ─────────────────────────────────────────────
# 9. REGISTER VIEW
# ─────────────────────────────────────────────
def register(request):
    """
    Handles new user registration.
    GET  → Show registration form
    POST → Create user & auto-login
    """
    # If already logged in, redirect to home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # form.save() creates the User object in the database
            user = form.save()

            # UserProfile is auto-created by the `post_save` signal.
            # Use get_or_create() to stay safe if it already exists.
            UserProfile.objects.get_or_create(user=user)

            # Log the user in automatically after registration
            login(request, user)

            messages.success(request, f'Welcome to BlogCMS, {user.username}! 🎉')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'blog/register.html', {'form': form})


# ─────────────────────────────────────────────
# 10. PROFILE VIEW
# ─────────────────────────────────────────────
@login_required
def profile(request):
    """
    Shows and allows editing of the user's profile.
    Uses two forms simultaneously: one for User, one for UserProfile.
    """
    # Get or create the UserProfile (safety net if it wasn't created at registration)
    profile_obj, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Two forms: one for User fields (first_name, last_name, email)
        #            one for UserProfile fields (bio, avatar, website, etc.)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully! ✅')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile_obj)

    # Show this user's post stats on the profile page
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    published_count = user_posts.filter(status='published').count()
    draft_count = user_posts.filter(status='draft').count()

    return render(request, 'blog/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_posts': user_posts[:5],  # Last 5 posts shown on profile
        'published_count': published_count,
        'draft_count': draft_count,
    })


# ─────────────────────────────────────────────
# 11. ADD COMMENT VIEW
# ─────────────────────────────────────────────
@login_required
@require_POST  # Only accept POST requests (not GET)
def add_comment(request, post_slug):
    """
    Handles posting a new comment or reply.
    @require_POST: Ensures this can only be called via form submission, not URL visit.
    """
    post = get_object_or_404(Post, slug=post_slug, status='published')
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user

        # Check if this is a reply (parent_id submitted in hidden field)
        parent_id = request.POST.get('parent_id')
        if parent_id:
            try:
                # Link this comment to its parent comment
                comment.parent = Comment.objects.get(id=parent_id)
            except Comment.DoesNotExist:
                pass  # If parent doesn't exist, treat as top-level comment

        comment.save()
        messages.success(request, 'Comment posted! 💬')

    return redirect('post_detail', slug=post_slug)


# ─────────────────────────────────────────────
# 12. DELETE COMMENT VIEW
# ─────────────────────────────────────────────
@login_required
def delete_comment(request, comment_id):
    """
    Deletes a comment.
    Only the comment author or an admin can delete.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug

    # Authorization check: only author or superuser can delete
    if comment.author == request.user or request.user.is_superuser:
        comment.delete()
        messages.success(request, 'Comment deleted.')
    else:
        messages.error(request, 'You are not authorized to delete this comment.')

    return redirect('post_detail', slug=post_slug)


# ─────────────────────────────────────────────
# 13. DASHBOARD VIEW
# ─────────────────────────────────────────────
@login_required
def dashboard(request):
    """
    Author's personal dashboard showing:
    - Their posts (published and drafts)
    - Statistics (total views, comments)
    """
    user_posts = Post.objects.filter(
        author=request.user
    ).select_related('category').annotate(
        comment_count=Count('comments')  # Add comment count to each post
    ).order_by('-created_at')

    # Summary stats
    total_posts = user_posts.count()
    published_posts = user_posts.filter(status='published').count()
    draft_posts = user_posts.filter(status='draft').count()
    total_views = sum(p.views for p in user_posts)
    total_comments = Comment.objects.filter(post__author=request.user).count()

    return render(request, 'blog/dashboard.html', {
        'posts': user_posts,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_views': total_views,
        'total_comments': total_comments,
    })
