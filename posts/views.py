from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import Post, Like, Comment, Bookmark, Tag, CATEGORY_CHOICES
from .forms import PostForm, CommentForm
from users.models import Follow


def feed_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Show posts from followed users + own posts
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).select_related('author__profile').prefetch_related('tags', 'likes', 'comments').order_by('-created_at')

    # Annotate liked/bookmarked status for current user
    liked_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    comment_form = CommentForm()

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'liked_ids': liked_ids,
        'bookmarked_ids': bookmarked_ids,
        'comment_form': comment_form,
    })


def explore_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    category = request.GET.get('category', '').strip()
    tag = request.GET.get('tag', '').strip()

    posts = Post.objects.select_related('author__profile').prefetch_related('tags', 'likes')

    if query:
        posts = posts.filter(
            Q(description__icontains=query) |
            Q(author__username__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(location__icontains=query)
        ).distinct()
    if location:
        posts = posts.filter(location__icontains=location)
    if category:
        posts = posts.filter(category=category)
    if tag:
        posts = posts.filter(tags__name__iexact=tag)

    if not any([query, location, category, tag]):
        posts = posts.annotate(likes_count=Count('likes')).order_by('-created_at')
    else:
        posts = posts.order_by('-created_at')

    liked_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    bookmarked_ids = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
    popular_tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]

    return render(request, 'posts/explore.html', {
        'posts': posts,
        'liked_ids': liked_ids,
        'bookmarked_ids': bookmarked_ids,
        'query': query,
        'location': location,
        'category': category,
        'tag': tag,
        'categories': CATEGORY_CHOICES,
        'popular_tags': popular_tags,
    })


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save()  # Save tags
            messages.success(request, 'Post shared successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('user__profile').order_by('created_at')
    comment_form = CommentForm()
    is_liked = Like.objects.filter(user=request.user, post=post).exists()
    is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=pk)

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'is_bookmarked': is_bookmarked,
    })


@login_required
def edit_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated.')
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('profile', username=request.user.username)
    return render(request, 'posts/delete_post.html', {'post': post})


@login_required
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)


@login_required
def like_toggle_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True

    likes_count = post.likes.count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_liked': is_liked, 'likes_count': likes_count})
    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def bookmark_toggle_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_bookmarked': is_bookmarked})
    return redirect(request.META.get('HTTP_REFERER', 'feed'))


def tag_view(request, tag_name):
    if not request.user.is_authenticated:
        return redirect('login')
    tag = get_object_or_404(Tag, name=tag_name.lower())
    posts = Post.objects.filter(tags=tag).select_related('author__profile').prefetch_related('likes')
    liked_ids = set(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    return render(request, 'posts/tag.html', {
        'tag': tag,
        'posts': posts,
        'liked_ids': liked_ids,
    })