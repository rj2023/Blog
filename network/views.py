from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from project4 import settings
from .models import User, PostInteraction, Post, Comment, CommentLike
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import json
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from nltk.stem import PorterStemmer


porter_stemmer = PorterStemmer()



@csrf_exempt
def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            messages.info(request, "Passwords must match.")
            
            return render(request, "network/register.html")

        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
        except IntegrityError:
            messages.info(request, "Email already Exists.")
            return render(request, "network/register.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {"message": "Invalid username and/or password."})
    else:
        return render(request, "network/login.html")





@csrf_exempt
def index(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for post in page_obj:
        post.like_count = post.postinteraction_set.filter(interaction_type='like').count()

    return render(request, "network/index.html", {'data': page_obj})



def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    print(post.get_like_count())
    return render(request, 'network/post_detail.html', {'post': post})

def generate_trigrams(text):
    """Generate trigrams from the given text."""
    trigrams = set()
    text = text.lower()
    for i in range(len(text) - 2):
        trigrams.add(text[i:i+3])
    return trigrams




@login_required
def search_results(request):
    search_query = request.GET.get('search', '')  # Default to empty string if not found
    word_list = [word + ' ' for word in search_query.split()]

    # Initialize posts
    posts = Post.objects.all().order_by('-created_at')  # Default to all posts if no search query

    if search_query:
        # Handle tags and content search
        if search_query.startswith(('#', '@')):
            posts = Post.objects.filter(tags__name__icontains=search_query).distinct()
        else:
            stemmed_query = [porter_stemmer.stem(word) for word in word_list]

            query = Q()
            for stem in stemmed_query:
                query |= Q(content__icontains=stem)
          
            posts = posts.filter(query).distinct()
            query_trigrams = generate_trigrams(search_query)

            trigram_conditions = Q()
            for trigram in query_trigrams:
                trigram_conditions |= Q(content__icontains=trigram)

            # Combine the stemming and trigram matching
            posts = posts.filter(trigram_conditions).distinct()

            # Ranking the results based on the number of occurrences of the search query
            def count_occurrences(post):
                return sum(post.content.lower().count(stem) for stem in stemmed_query)

            posts = sorted(posts, key=count_occurrences, reverse=True)


    return render(request, "network/search_result.html", {
        'data': posts,
        'search_query': search_query
    })



@login_required
def add_comment(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment')
        post = get_object_or_404(Post, id=post_id)

        # Create the new comment
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=comment_text,
            created_at=now()
        )
        comment_count = CommentLike.objects.filter(comment=comment).count()
        return JsonResponse({
            'success': True,
            "id": comment.id,
            'comment': comment.content,
            'user': comment.user.username,
            'like_count': comment_count,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'success': False})

@login_required
def user_profile(request, id):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/user.html", {'data': page_obj})


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
@require_POST
def create_post(request):
    title = request.POST.get('title')
    content = request.POST.get('content')
    image = request.FILES.get('image')
    tags = request.POST.get('tags')  # Get tags from POST data

    # Create the post with the author field set to the current user
    post = Post.objects.create(
        author=request.user,
        title=title,
        content=content,
        image=image
    )
  
    if tags:
        # Split tags and check if they start with @ or #
        tag_list = [tag.strip() for tag in tags.split(',')]
        valid_tags = [tag for tag in tag_list if tag.startswith(('@', '#'))]

        # Add valid tags to the post
        post.tags.add(*valid_tags)
    return redirect('index')

@login_required
def create_post_page(request):
    return render(request, 'network/create_post.html')





def profile(request, id):
    profile_user = get_object_or_404(User, id=id)

    posts_list = Post.objects.filter(author=profile_user).order_by('-created_at')

    # Set up pagination
    paginator = Paginator(posts_list, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')  # Get the page number from the request
    try:
        posts = paginator.page(page_number)  # Get the posts for the requested page
    except PageNotAnInteger:
        posts = paginator.page(1)  # If the page number is not an integer, deliver first page
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # If the page number is out of range, deliver last page

    return render(request, 'network/profile.html', {
        'profile_user': profile_user,
        'data': posts,
    })


@login_required
def like_unlike_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        
        interaction, created = PostInteraction.objects.get_or_create(post=post, user=user)
        if created:
            interaction.interaction_type = 'like'
            interaction.save()
            liked = True
        else:
            interaction.delete()
            liked = False
        
        return JsonResponse({'liked': liked, 'likes_count': post.get_like_count()})


@login_required
def posts_by_tag(request, tag):
    posts = Post.objects.filter(tags__name=tag).order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Annotate posts with like count
    for post in page_obj:
        post.like_count = post.postinteraction_set.filter(interaction_type='like').count()

    return render(request, "network/tagged_posts.html", {'data': page_obj, 'tag': tag})

@login_required
@require_POST
def like_comment(request):
    comment_id = request.POST.get('comment_id')
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    # Check if the user has already liked the comment
    comment_like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
    
    if created:
        liked = True
    else:
        comment_like.delete()
        liked = False
    
    return JsonResponse({'liked': liked, 'like_count': comment.commentlike_set.count()})

@login_required
def share_post(request, post_id):
    if request.method == "POST":
        base_url = settings.BASE_URL
        post_url = f"{base_url}/post/{post_id}/"
        data = json.loads(request.body)
        recipient_email = data.get('email')
        
        post = get_object_or_404(Post, id=post_id)

        subject = f"Check out this post: {post.title}"
        message = f"Hi,\n\nI thought you might be interested in this post:\n\n{post.title}\n{post_url}\n\nBest,\n{request.user.username}"

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error sending email: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})