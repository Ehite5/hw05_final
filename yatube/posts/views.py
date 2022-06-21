from http.client import HTTPResponse

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

NUMBER_OF_POSTS = 10


def paginator_func(request, posts):
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@require_GET
def index(request):
    posts = Post.objects.select_related('author', 'group')
    text_main = 'Последние обновления на сайте'
    template = 'posts/index.html'
    keyword = request.GET.get("q", None)
    if keyword:
        posts = Post.objects.select_related('author', 'group').filter(
            text__icontains=keyword)
        if posts:
            text_main = 'Найдено:'
            posts = Post.objects.select_related('author', 'group').filter(
                text__icontains=keyword)
        else:
            text_main = 'По Вашему запросу ничего не найдено'
    context = {
        'text_main': text_main,
        'page_obj': paginator_func(request, posts),
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    text_groups = f'Записи сообщества "{group.title}"'
    posts = group.posts.select_related('author', 'group')
    context = {
        'text_groups': text_groups,
        'group': group,
        'page_obj': paginator_func(request, posts),
    }
    return render(request, template, context)


def profile(request, username):
    author_name = get_object_or_404(User, username=username)
    if author_name:
        posts = Post.objects.select_related('author',
                                            'group').filter(author=author_name)
        all_author_posts = author_name.posts.count()
        if (request.user.is_authenticated
            and Follow.objects.filter(user=request.user,
                                      author=author_name).exists()):
            following = True
        else:
            following = False
        context = {
            'author_name': author_name,
            'all_author_posts': all_author_posts,
            'page_obj': paginator_func(request, posts),
            'following': following
        }
        return render(request, 'posts/profile.html', context)
    return HTTPResponse('Ничего не найдено по запросу о данном авторе.')


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(), pk=post_id)
    all_author_posts = post.author.posts.count()
    title_30 = post.text[:30]
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'all_author_posts': all_author_posts,
        'title_30': title_30,
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form,
                                                          'is_edit': False})
    new_post = form.save(commit=False)
    new_post.author_id = request.user.id
    new_post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    if request.user.username != post.author.username:
        return redirect(f'/profile/{post.author.username}/')
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    if request.method != 'POST':
        context = {
            'form': form,
            'post': post,
            'is_edit': is_edit
        }
        return render(
            request,
            'posts/create_post.html',
            context
        )
    form = PostForm(request.POST, instance=post, files=request.FILES or None,)
    if not form.is_valid():
        context = {
            'form': form,
            'post': post,
            'is_edit': is_edit
        }
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comment = Comment.objects.filter(post=post)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_func(request, follow_list)
    follow = True
    context = {'follow': follow,
               'page_obj': page_obj
               }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (request.user != author
            and not Follow.objects.filter(user=request.user,
                                          author=author).exists()):
        Follow.objects.create(user=request.user,
                              author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user,
                             author=author):
        Follow.objects.filter(user=request.user,
                              author=author).delete()
    return redirect('posts:profile', author)
