from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow


POST_PER_PAGE: int = 10


@cache_page(20, key_prefix='index_page')
def index(request):

    posts = Post.objects.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/index.html', {'page_obj': page_obj, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/group_list.html', {'group': group,
                                                     'page_obj': page_obj, })


def profile(request, username):

    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = Follow.objects.filter(author=author)

    return render(request, 'posts/profile.html', {'author': author,
                                                  'page_obj': page_obj,
                                                  'following': following, })


def post_detail(request, post_id):
    posts = get_object_or_404(Post, pk=post_id)
    title = posts.text[:30]
    comment = Comment.objects.filter(post=post_id)
    isauthor: bool = str(posts.author) == str(request.user)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/post_detail.html', {'posts': posts,
                                                          'title': title,
                                                          'isauthor': isauthor,
                                                          'form': form,
                                                          'comments': comment})
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def post_сreate(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form, })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'is_edit': 'True',
                                                          'form': form, })
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user)

    posts = Post.objects.filter(author__following__user=user)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/follow.html', {'page_obj': page_obj, })


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, username=username)
    if (request.user.username == username
            or Follow.objects.filter(user=user, author=author).exists()):
        return redirect('posts:profile', username)
    Follow.objects.create(user=user, author=author)

    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()

    return redirect('posts:profile', username)
