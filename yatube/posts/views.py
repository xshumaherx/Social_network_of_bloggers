from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def func_paginator(request, post_list):
    paginator = Paginator(post_list, settings.NUMBER_ENTRIES_FOR_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group')
    page_obj = func_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = group.posts.all()
    page_obj = func_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author', 'group')
    page_obj = func_paginator(request, post_list)
    following = Follow.objects.filter(
        user__username=request.user,
        author=author,
    )
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post_obj = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.all()
    context = {
        'post': post_obj,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
        return render(request, template, {'form': form})
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    context = {'form': form, 'post': post, 'is_edit': True}

    if request.user == post.author:
        if request.method == 'GET':
            return render(request, template, context)
        else:
            if form.is_valid():
                form.save()
            return redirect('posts:post_detail', post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    author_list = Post.objects.filter(author__following__user=request.user)
    page_obj = func_paginator(request, author_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """'Подписка на автора'"""
    author = get_object_or_404(User, username=username)
    if (
        author.following.filter(
            user=request.user,
            author=author)
            .exists() or request.user == author):
        return redirect(f'/profile/{username}/')
    Follow.objects.create(user=request.user, author=author)
    return redirect(f'/profile/{username}/')


@login_required
def profile_unfollow(request, username):
    """'Отписка от автора'"""
    template = 'posts:profile'
    follow = get_object_or_404(
        Follow, user=request.user, author__username=username)
    follow.delete()
    return redirect(template, username=username)
