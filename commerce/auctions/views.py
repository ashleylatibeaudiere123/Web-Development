from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from datetime import datetime

from .models import User, Auction_listing,  Bid, Comment, Watchlist

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Description")
    start_bid = forms.DecimalField(max_digits=10, decimal_places = 2, label="Starting bid")
    category = forms.ChoiceField(label = "Category", choices = Auction_listing.category.field.choices, required= False)
    url = forms.URLField(label= "URL", required = False)


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Auction_listing.objects.filter(activity="Active")
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



@login_required(login_url= "login")
def create(request):
    if request.method == "POST":
        # Save info submitted as a form
        newlisting = NewListingForm(request.POST)
        # Check if form is valid before saving to the database
        if newlisting.is_valid():
            title = newlisting.cleaned_data["title"].capitalize()
            description = newlisting.cleaned_data["description"]
            start_bid = newlisting.cleaned_data["start_bid"]
            category = newlisting.cleaned_data["category"]
            url = newlisting.cleaned_data["url"]
            username = request.user.username
            date_time = datetime.now()

            listing = Auction_listing(title = title, description = description, start_bid= start_bid, highest_bid = start_bid, category = category, url = url, seller = username, date_time = date_time, activity ="Active")
            listing.save()

            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create.html",
        { "form" : NewListingForm()
        })

@login_required(login_url = "login")
def show_listing(request, id):
    # Load page when accessed by GET
    if request.method == "GET":

        # Get auction listing
        a_id = Auction_listing.objects.get(id = id)

        # Determine if user is the same as the seller and give them option to close listing
        user = request.user.username
        if user == a_id.seller:
            show_button = True

        else:
            show_button = False

        # Render page and determine if specific item is in watchlist
        try:
            watchlist_query = Watchlist.objects.get(listing_id = id, user = request.user)
        except Watchlist.DoesNotExist:
            watchlist_query = None

        return render(request, "auctions/listing.html",
                    {
                        "listing": a_id,
                        "watchlist_query": watchlist_query,
                        "show_end_button": show_button,
                        "close_listing": a_id.activity,
                         "comment": Comment.objects.filter(listing_id = id)

                    })
    else:
        # After submitting any part of the form
        user = request.user.username
        a_id = Auction_listing.objects.get(id = id)
        request.POST.get("button_type")
        if user == a_id.seller:
            show_button = True

        else:
            show_button = False

        watchlist_query = None
    # If form is submitted by post, determine if user is signed in and whether add/ remove button was pressed
        if request.POST.get("button_type") == "add":
            # To add the listing to the watchlist, need to first get Auction_object because id in Watchlist is a foreign key

            watchlist_query = Watchlist(listing_id = a_id, user = request.user)
            watchlist_query.save()
            return render(request, "auctions/listing.html",
                          {
                              "listing": a_id,
                              "watchlist_query": watchlist_query,
                              "show_end_button": show_button,
                              "comment": Comment.objects.filter(listing_id = id),
                              "close_listing": a_id.activity
                          })
        elif request.POST.get("button_type")=="remove":
            Watchlist.objects.get(listing_id = id, user = request.user).delete()
            watchlist_query = None
            return render(request, "auctions/listing.html", {
                "listing": a_id,
                "watchlist_query": watchlist_query,
                "show_end_button": show_button,
                "comment": Comment.objects.filter(listing_id = id),
                "close_listing": a_id.activity
            })
        # Change bid when place bid button is clicked
        if request.POST.get("button_type") == "Place Bid":
            bid = float(request.POST["bid"])
            try:
                watchlist_query = Watchlist.objects.get(listing_id = id, user = request.user)
            except Watchlist.DoesNotExist:
                watchlist_query = None

            # if bid is higher than start and highest bid, update bid
            if bid > a_id.start_bid and bid > a_id.highest_bid:
                a_id.highest_bid = bid
                a_id.save()
                new_bid = Bid(listing_id= a_id, bid = bid, user = request.user.username)
                new_bid.save()
                return render(request, "auctions/listing.html", {
                    "listing": a_id,
                    "watchlist_query": watchlist_query,
                    "show_end_button": show_button,
                    "comment": Comment.objects.filter(listing_id = id),
                    "close_listing": a_id.activity

                })
            else:
                return render(request, "auctions/listing.html", {
                    "listing": a_id,
                    "watchlist_query": watchlist_query,
                    "message": " Error: Bid must be higher than starting and current bid",
                    "show_end_button": show_button,
                    "comment": Comment.objects.filter(listing_id = id),
                    "close_listing": a_id.activity,
                })

        # Post comment
        if request.POST.get("button_type")== "Post Comment":
            text = request.POST.get("new_comment")
            new_comment = Comment(listing_id = Auction_listing.objects.get(id = id), comment = text, user = request.user.username)
            new_comment.save()
            try:
                watchlist_query = Watchlist.objects.get(listing_id = id, user= request.user)
            except Watchlist.DoesNotExist:
                watchlist_query = None

            return render(request, "auctions/listing.html", {
                    "listing": Auction_listing.objects.get(id = id),
                    "watchlist_query": watchlist_query,
                    "show_end_button": show_button,
                    "comment": Comment.objects.filter(listing_id = id),
                    "close_listing": a_id.activity,
            })

        # Close bid if close bid is button is pressed
        if request.POST.get("button_type") == "Close Bid":
            # Find auction listing object

            a_id = Auction_listing.objects.get(id = id)

            # Find all bids of the listing and select the max one
            list_of_bids = Bid.objects.filter(listing_id = id)
            if not list_of_bids.exists():
                a_id.winner = a_id.seller
            else:
                max_bid = list_of_bids.order_by('-bid')[0]
                # find user with max bid
                max_bid_user = max_bid.user
                # Updated winner in database, move listing to closed listings and delete bids
                a_id.winner = max_bid_user
            a_id.activity = "Inactive"
            a_id.save()
            list_of_bids.delete()
            show_button = False

            return render(request, "auctions/listing.html",{
                "listing": a_id,
                "watchlist_query": watchlist_query,
                "close_listing": a_id.activity,
                "user": request.user,
                "comment": Comment.objects.filter(listing_id = id),
                "show_end_button": show_button,
            } )

def categories(request):
    values =[]
    for key, value in Auction_listing.category.field.choices[1:]:
        values.append(value)

    return render(request, "auctions/categories.html", {
        "categories": values
    })

def show_category(request, category):

    return render(request, "auctions/category.html", {
        "category_listings": Auction_listing.objects.filter(activity="Active").filter(category=category),
        "category": category
    })

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": Watchlist.objects.filter(user = request.user)
    })
