from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Profile, Follow
from .forms import RegisterForm, LoginForm, ProfileEditForm, UserEditForm
from posts.models import Post, Bookmark


def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to travelshare, {user.username}!')
            return redirect('feed')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'feed')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    followers = Follow.objects.filter(following=profile_user)
    following = Follow.objects.filter(follower=profile_user)
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    is_own_profile = request.user == profile_user

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'followers_count': followers.count(),
        'following_count': following.count(),
        'is_following': is_following,
        'is_own_profile': is_own_profile,
        'posts_count': posts.count(),
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'users/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('login')
    return render(request, 'users/delete_account.html')


@login_required
def follow_toggle_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow.delete()
        is_following = False
    else:
        is_following = True

    followers_count = Follow.objects.filter(following=target_user).count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_following': is_following, 'followers_count': followers_count})
    return redirect('profile', username=username)


@login_required
def followers_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=profile_user).select_related('follower__profile')
    return render(request, 'users/followers.html', {
        'profile_user': profile_user,
        'follows': followers,
        'tab': 'followers'
    })


@login_required
def following_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=profile_user).select_related('following__profile')
    return render(request, 'users/followers.html', {
        'profile_user': profile_user,
        'follows': following,
        'tab': 'following'
    })


@login_required
def bookmarks_view(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post__author').order_by('-created_at')
    return render(request, 'users/bookmarks.html', {'bookmarks': bookmarks})