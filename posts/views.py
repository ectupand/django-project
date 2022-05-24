from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from users.models import Follow
from .forms import PostForm, CommentForm
from .models import Post, Group, User
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects. order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, 'paginator': paginator, "index": True}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, "page": page, "paginator": paginator})


@login_required
def new_post(request):
    if request.user not in User.objects.all():
        return redirect('index')
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form, 'title': 'Новый пост'})
    form = PostForm()
    return render(request, 'new_post.html',
                  {
                      'form': form,
                      'title': 'Новый пост',
                      'action': reverse('new_post')
                  })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user).order_by('-pub_date')
    name = user.first_name + ' ' + user.last_name

    number_of_user_posts = user_posts.count()
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    following=False
    if user != request.user:
        follow = Follow.objects.filter(author=user, user=request.user)
        if follow:
            following = True
        else:
            following = False

    try:
        last_post = user_posts[0]
    except IndexError:
        return render(request, 'profile.html', {'name': name, 'username': username, 'number_of_user_posts': 0})

    return render(
        request,
        'profile.html',
        {"following": following, 'name': name, 'username': username, 'number_of_user_posts': number_of_user_posts,
         'page': page, "paginator": paginator, 'last_post': last_post, 'last_post.pub_date': last_post.pub_date}
    )


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user, id=post_id)
    name = user.first_name + ' ' + user.last_name
    post = user_posts[0]
    form = CommentForm()
    items = post.comments.all()
    return render(
        request,
        'post.html',
        {'name': name, 'username': username, 'post': post, 'last_post.pub_date': post.pub_date,
         'last_post.id': post.id, 'number_of_user_posts': Post.objects.filter(author=user).count(),
         'form': form, 'items': items})


@login_required
def post_edit(request, username, post_id):
    user = User.objects.filter(username=username).first()
    if user.id != request.user.id:
        return HttpResponse('Unauthorized', status=401)

    post = Post.objects.filter(id=post_id, author=user).first()

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.POST and form.is_valid():
        form.instance.author = user
        form.save()
        return redirect('post', username, post_id)

    if post:
        return render(
            request,
            'new_post.html',
            {
                'form': form,
                'post': post,
                'title': 'Редактировать пост',
                'action': reverse('post_edit', args=(username, post_id)),
                'edit': 'Редактировать'
            })
    return HttpResponse('Unauthorized', status=401)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request, "post.html", {"form": form})


@login_required
def follow_index(request):
    following = User.objects.get(pk=request.user.id).follower.all().values_list('author')
    post_list = Post.objects.filter(author__in=following).order_by('-pub_date')
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"index": False, "follow_index": True, "page": page, "paginator": paginator})

@login_required
def profile_follow(request, username):
    #if request.method != 'POST':
    #    return redirect('profile', username=username)
    tofollowUser = get_object_or_404(User, username=username)
    follower = Follow.objects.create(author=tofollowUser, user=request.user)
    follower.save()
    return redirect('profile', username=username)

@login_required
def profile_unfollow(request, username):
    #if request.method != 'POST':
    #    return redirect('profile', username=username)
    tofollowUser = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(author=tofollowUser, user=request.user)
    follower.delete()
    return redirect('profile', username=username)