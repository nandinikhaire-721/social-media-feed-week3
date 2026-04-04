from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post
from .forms import PostForm


# ================= AUTH VIEWS =================

def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username=username, password=password)
        login(request, user)

        return redirect('profile', username=user.username)

    return render(request, 'accounts/signup.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('profile', username=user.username)
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ================= HOME =================

def home(request):
    return render(request, 'accounts/home.html')


# ================= PROFILE =================

@login_required
def profile_view(request, username):
    user_obj = get_object_or_404(User, username=username)

    is_following = False

    if user_obj != request.user:
        if user_obj in request.user.profile.following.all():
            is_following = True

    context = {
        'user_obj': user_obj,
        'is_following': is_following,
        'followers': user_obj.followers.all(),
        'following': user_obj.profile.following.all(),
    }

    return render(request, 'accounts/profile.html', context)


# ================= FOLLOW SYSTEM =================

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow != request.user:
        request.user.profile.following.add(user_to_follow)

    return redirect('profile', username=username)


@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)

    if user_to_unfollow != request.user:
        request.user.profile.following.remove(user_to_unfollow)

    return redirect('profile', username=username)


# ================= POST VIEWS =================

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'accounts/post_list.html', {'posts': posts})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'accounts/post_form.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = PostForm(instance=post)

    return render(request, 'accounts/post_form.html', {'form': form})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)

    if request.method == 'POST':
        post.delete()
        return redirect('post_list')

    return render(request, 'accounts/post_confirm_delete.html', {'post': post})