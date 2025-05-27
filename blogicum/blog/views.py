from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import Http404
from blog.utils import (
    annotate_comment_count,
    paginate, get_published_posts,
    get_published_posts_no_filter,
    is_post_visible_to_user
)

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserEditForm


def index(request):
    post_list = get_published_posts_no_filter(
        Post.objects
    ).order_by("-pub_date")
    page_obj = paginate(post_list, request)
    return render(request, "blog/index.html", {"page_obj": page_obj})

# from django.core.paginator import Paginator
# def index(request):
#     post_list = Post.objects.published().order_by("-pub_date")
#     paginator = Paginator(post_list, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)
#     return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.all(), pk=post_id)

    if not post.category.is_published and request.user != post.author:
        raise Http404("Category not published")

    if not is_post_visible_to_user(post, request.user):
        raise Http404("Post not found")

    form = CommentForm()
    return render(
        request,
        "blog/detail.html",
        {"post": post, "form": form, "comments": post.comments.all()},
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(is_published=True), slug=category_slug
    )
    post_list = get_published_posts_no_filter(
        Post.objects
    ).filter(category=category).order_by("-pub_date")
    page_obj = paginate(post_list, request)
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj}
    )


class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/registration_form.html"
    success_url = reverse_lazy("blog:index")


def profile(request, username):
    profile = get_object_or_404(get_user_model(), username=username)

    if profile == request.user:
        post_list = profile.posts.all()
    else:
        post_list = get_published_posts(profile.posts.all())

    post_list = annotate_comment_count(post_list).order_by("-pub_date")
    page_obj = paginate(post_list, request)
    return render(
        request, "blog/profile.html",
        {"profile": profile, "page_obj": page_obj}
    )


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)

    return render(request, "blog/user.html", {"form": form})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()
    return render(request, "blog/create.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, "blog/comment.html",
                  {"form": form, "comment": comment})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/create.html", {"form": None, "post": post})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)

    return render(request, "blog/comment.html",
                  {"comment": comment, "form": None})
