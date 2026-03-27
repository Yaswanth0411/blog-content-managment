"""
blog/models.py

Models define the database tables and their structure.
Each class = one database table.
Each class attribute = one column in that table.

Tables we create:
  1. Category   — Blog categories (Technology, Travel, etc.)
  2. Post        — The main blog post
  3. Comment     — Comments on each blog post
  4. UserProfile — Extra info for each user (bio, avatar)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


# ─────────────────────────────────────────────
# 1. CATEGORY MODEL
# ─────────────────────────────────────────────
class Category(models.Model):
    """
    Represents a blog category (e.g., Technology, Lifestyle, Travel).
    Each Post belongs to ONE category (ForeignKey relationship).
    """

    # name: The category title shown to users (max 100 characters)
    name = models.CharField(max_length=100, unique=True)

    # slug: URL-friendly version of name.
    # e.g., "Web Development" → "web-development"
    # Used in URLs like: /category/web-development/
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    # description: Optional short description of the category
    description = models.TextField(blank=True, null=True)

    # color: Hex color for visual distinction in the UI
    # e.g., "#FF5733" for orange badges
    color = models.CharField(max_length=7, default='#3498db')

    class Meta:
        verbose_name_plural = "Categories"  # Fix plural name in admin
        ordering = ['name']                 # Always sorted A→Z

    def save(self, *args, **kwargs):
        """
        Override save() to auto-generate the slug from the name.
        This runs BEFORE actually saving to the database.
        e.g., if name="Web Dev Tips" → slug="web-dev-tips"
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the URL to view all posts in this category."""
        return reverse('category_detail', kwargs={'slug': self.slug})

    def __str__(self):
        """How the Category object appears as text (in admin, shell, etc.)"""
        return self.name


# ─────────────────────────────────────────────
# 2. POST MODEL
# ─────────────────────────────────────────────
class Post(models.Model):
    """
    The main blog post model.
    This is the heart of the CMS — each row = one blog article.
    """

    # STATUS CHOICES: A post is either a Draft (not visible) or Published
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # ── Basic Info ──────────────────────────────
    # title: The blog post headline
    title = models.CharField(max_length=300)

    # slug: URL-friendly title. e.g., "My First Post" → "my-first-post"
    # Used in: /post/my-first-post/
    slug = models.SlugField(max_length=300, unique=True, blank=True)

    # excerpt: Short summary shown on listing pages (optional)
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short summary shown on post cards. Auto-generated if left blank."
    )

    # ── Relationships ───────────────────────────
    # author: Links to Django's built-in User model
    # on_delete=CASCADE means: if the user is deleted, their posts are also deleted
    # related_name='posts' lets us do: user.posts.all() to get all posts by a user
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    # category: Each post belongs to one category (optional)
    # on_delete=SET_NULL means: if category deleted, post's category becomes null
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )

    # tags: Many-to-many relationship using django-taggit
    # A post can have many tags, a tag can belong to many posts
    tags = TaggableManager(blank=True)

    # ── Content ─────────────────────────────────
    # content: The main body of the post — uses CKEditor (rich text)
    # RichTextUploadingField allows images to be uploaded inside the editor
    content = RichTextUploadingField()

    # ── Media ───────────────────────────────────
    # thumbnail: Featured image for the post (stored in media/thumbnails/)
    # blank=True, null=True means it's optional
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        blank=True,
        null=True
    )

    # ── Status & Timestamps ──────────────────────
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )

    # created_at: Automatically set to NOW when the post is created
    created_at = models.DateTimeField(auto_now_add=True)

    # updated_at: Automatically updates to NOW every time the post is saved
    updated_at = models.DateTimeField(auto_now=True)

    # published_at: Manually set when the post goes live
    published_at = models.DateTimeField(null=True, blank=True)

    # ── Engagement ──────────────────────────────
    # views: Count of how many times this post has been viewed
    views = models.PositiveIntegerField(default=0)

    # featured: Mark a post as "featured" to highlight it on homepage
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']  # Newest posts first
        indexes = [
            models.Index(fields=['slug']),    # Fast slug lookups
            models.Index(fields=['status']),  # Fast status filtering
        ]

    def save(self, *args, **kwargs):
        """
        Auto-generate slug from title before saving.
        Also auto-generate excerpt from content if not provided.
        """
        # Generate slug from title
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure slug is unique by appending a number if needed
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Auto-generate excerpt from content (strip HTML tags, take first 200 chars)
        if not self.excerpt and self.content:
            import re
            clean = re.sub(r'<[^>]+>', '', self.content)  # Remove HTML tags
            self.excerpt = clean[:200].strip() + '...' if len(clean) > 200 else clean

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the URL for this specific post."""
        return reverse('post_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────
# 3. COMMENT MODEL
# ─────────────────────────────────────────────
class Comment(models.Model):
    """
    Represents a comment left by a user on a blog post.
    Each comment belongs to ONE post and ONE user.
    Supports replies (parent comment system).
    """

    # post: Which post this comment belongs to
    # on_delete=CASCADE: if post is deleted, all its comments are too
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'   # Access via: post.comments.all()
    )

    # author: The user who wrote the comment
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    # parent: For threaded replies — links to another comment
    # null=True means it can be a top-level comment (no parent)
    parent = models.ForeignKey(
        'self',                    # Self-referential: points to another Comment
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'    # Access replies via: comment.replies.all()
    )

    # body: The actual comment text
    body = models.TextField()

    # is_approved: Admin can moderate comments before they show
    is_approved = models.BooleanField(default=True)

    # created_at: When the comment was posted
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # Oldest comments first (natural reading order)

    def __str__(self):
        return f"Comment by {self.author.username} on '{self.post.title}'"


# ─────────────────────────────────────────────
# 4. USER PROFILE MODEL
# ─────────────────────────────────────────────
class UserProfile(models.Model):
    """
    Extends Django's built-in User model with extra fields.
    This is a "One-to-One" relationship: each User has exactly ONE profile.
    """

    # user: Link to Django's User. OneToOneField means 1 profile per user.
    # on_delete=CASCADE: if user deleted, profile is deleted too
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'   # Access via: user.profile
    )

    # avatar: Profile picture (optional)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    # bio: Short author biography shown on posts
    bio = models.TextField(blank=True, null=True, max_length=500)

    # website: Personal/portfolio website link
    website = models.URLField(blank=True, null=True)

    # twitter/linkedin: Social media handles
    twitter = models.CharField(max_length=100, blank=True, null=True)
    linkedin = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
