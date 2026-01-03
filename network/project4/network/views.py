from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import datetime
from django import forms
import json

# cs50ai and chatgpt used to decode problems
# Django reference used for pagination

from .models import User, Post

# Create a form for the new post
class newPost(forms.Form):
    newpost = forms.CharField(widget = forms.Textarea(attrs={"rows":"3", "cols":"170"}), label='')

def pages(request, posts, number):
    # Group posts into 10 and arrange into pages
        paginator = Paginator(posts, number)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj

# Display new post form and posts present on website
def index(request):
    # Obtain information submitted in form and post it to the server
    if request.method =="POST":
        form = newPost(request.POST)
        posts = Post.objects.all().order_by('-date_time')
        # Group posts into 10 and arrange into pages
        page_obj = pages(request, posts, 10)
        if form.is_valid():
            post = form.cleaned_data["newpost"]
            user= request.user
            date_time = datetime.now()
            new_post = Post(user= request.user, post= post, likes= 0, date_time = date_time)
            new_post.save()
            return render(request, "network/index.html",{
                "form":newPost(),
                "page_obj": page_obj
            })
        else:
            # If data is not valid, prompt them to submit again
            return render(request, "network/index.html", {
                "message": "Invalid submission. Try again.",
                "form": newPost(),
                "page_obj": page_obj
            })
    else:
    # Obtain all posts on the website
        posts = Post.objects.all().order_by('-date_time')

        page_obj = pages(request, posts, 10)

    # Load form

        return render(request, "network/index.html",{
                "form": newPost(),
                "page_obj": page_obj,

            })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

# Generate profile page for single user
def profile(request, name):
    # Query database for user's info and posts for profiled user
    userobject = User.objects.get(username = name)
    posts = Post.objects.filter(user = userobject).order_by('-date_time')
    page_obj = pages(request, posts, 10)

    # Allow users to follow each other except themselves
    if request.method == "POST":

        # Create new follower and update user followers total
        if request.POST.get("followbutton") == "follow":
            userobject.followers.add(request.user)
            userobject.num_followers = userobject.followers.count()
            userobject.save()

        # Also update the logged in user's following number
            logged_in_user = User.objects.get(username = request.user.username)
            logged_in_user.num_following = logged_in_user.following.count()
            logged_in_user.save()

            return render(request, "network/profile.html",{
                "userobject": userobject,
                "page_obj": page_obj,
                "foundfollower": 1,
                })

        # Delete follower, change marker for follower and reduce posters total
        elif request.POST.get("followbutton") =="unfollow":
            f = userobject.followers.get(username = request.user.username)
            userobject.followers.remove(f)
            userobject.num_followers = userobject.followers.count()
            userobject.save()

            # Update logged in user's count
            logged_in_user = User.objects.get(username= request.user.username)
            logged_in_user.num_following = logged_in_user.following.count()
            logged_in_user.save()
            return render(request, "network/profile.html",{
                "userobject": userobject,
                "page_obj": page_obj,
                "foundfollower": 0
                })
        else:
        # Update tag for whether the user is a follower or not
            f = userobject.followers.get(username= request.user.username)
            if f:
                foundfollower = 1
            else:
                foundfollower = 0

            return render(request, "network/profile.html",{
                "userobject": userobject,
                "page_obj": page_obj,
                "foundfollower": foundfollower
                })

    else:

        # Find if user is requesting their own profile
        if userobject == request.user:
            foundfollower = -1
        else:
            # Determine if logged in user is following current profile

            f = userobject.followers.filter(username = request.user.username)
            if f:
                foundfollower = 1
            else:
                foundfollower = 0

        # Return template for profile
        return render(request, "network/profile.html",{
                "userobject": userobject,
                "page_obj": page_obj,
                "foundfollower": foundfollower
            })

def following(request, id):
    # Get logged in user's object
    userobject = User.objects.get(id = id)

    # Get users who the logged in users follows
    following_list = userobject.following.all()

    # Get posts of users
    following_posts = []
    for user in following_list:
        user_posts = Post.objects.filter(user = user)
        for u_post in user_posts:
            following_posts.append(u_post)

    page_obj = pages(request, following_posts, 10)
    return render(request,"network/following.html",{
        "page_obj": page_obj
    })

def edit(request, id):

    # Get logged in user
    logged_in_user = User.objects.get(username= request.user.username)

    # Get post from id
    post = Post.objects.get(id = id )

    # Get user whose post will be edited
    poster = post.user

    # Return error if user tries to edit someone else's post
    if logged_in_user != poster:
        return JsonResponse({
            "error": "You cannot edit someone else's post.",
            "post": post.post
        }, status=403)

    # Get updated post contents through json
    data = json.loads(request.body)
    edited_post = data.get("post")

    #Update contents of post
    post.post = edited_post
    post.save()
    print(post.post)

    # Send back JSON response
    return JsonResponse({
        "message": "Post updated",
        "post": edited_post
    }, status=201)


def likes(request, id):
    # Get submitted data
    data = json.loads(request.body)
    liked_button_pressed = data.get("liked_button_pressed")

    # Get post
    post = Post.objects.get(id = id )

    # Determine if user has already liked the post
    try:
        already_liked_post = post.liked_by.get(username = request.user.username)

    except User.DoesNotExist:
        already_liked_post = None

    if already_liked_post:
        # If the post is already liked, unlike post
        post.liked_by.remove(request.user)
        post.likes -= 1

    else:
        # If not, then like post.
        post.liked_by.add(request.user)
        post.likes += 1
    post.save()

    return JsonResponse({
        "likes": post.likes,
          }, status = 201)
