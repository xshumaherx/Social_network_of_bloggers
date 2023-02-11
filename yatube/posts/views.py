from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

PROFILE = 'posts:profile'
DETAIL = 'posts:post_detail'
HTML_INDEX = 'posts/index.html'
HTML_GROUP_LIST = 'posts/group_list.html'
HTML_PROFILE = 'posts/profile.html'
HTML_DETAIL = 'posts/post_detail.html'
HTML_EDIT_CREATE = 'posts/create_post.html'
HTML_FOLLOW = 'posts/follow.html'


def func_paginator(request, post_list):
    paginator = Paginator(post_list, settings.NUMBER_ENTRIES_FOR_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    template = HTML_INDEX
    post_list = Post.objects.select_related('author', 'group')
    page_obj = func_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = HTML_GROUP_LIST
    post_list = group.posts.all()
    page_obj = func_paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    template = HTML_PROFILE
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author', 'group')
    page_obj = func_paginator(request, post_list)
    following = Follow.objects.filter(
        user__username=request.user,
        author=author).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = HTML_DETAIL
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
    template = HTML_EDIT_CREATE
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(PROFILE, request.user.username)
        return render(request, template, {'form': form})
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = HTML_EDIT_CREATE
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
            return redirect(DETAIL, post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(DETAIL, post_id=post_id)


@login_required
def follow_index(request):
    template = HTML_FOLLOW
    author_list = Post.objects.filter(author__following__user=request.user)
    page_obj = func_paginator(request, author_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """'Подписка на автора'"""
    if request.user.username == username:
        return redirect(
            reverse(PROFILE, kwargs={'username': username}))
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(
        reverse(PROFILE, kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    """'Отписка от автора'"""
    template = PROFILE
    follow = get_object_or_404(
        Follow, user=request.user, author__username=username)
    follow.delete()
    return redirect(template, username=username)


def page_not_found(request, exception):
    return render(
        request,
        "core/404.html",
        {"path": request.path},
        status=404
    )
