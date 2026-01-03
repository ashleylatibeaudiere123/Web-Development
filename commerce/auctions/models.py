from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    pass

class Auction_listing(models.Model):
    title = models.CharField(max_length = 64)
    description = models.CharField()
    start_bid = models.DecimalField(max_digits = 10, decimal_places = 2)
    highest_bid = models.DecimalField(max_digits = 10, decimal_places = 2)
    categories= {"":"","Fashion":"Fashion", "Home": "Home", "Toys":"Toys", "Electronics":"Electronics", "Furniture":"Furniture"}
    category = models.CharField(choices= categories)
    url = models.URLField()
    seller = models.CharField(null = False)
    date_time = models.DateTimeField(null = False)
    winner = models.CharField(null = True, blank= True)
    choices = {"Active": "Active", "Inactive": "Inactive"}
    activity = models.CharField(choices= choices)
    def __str__(self):
        return f"{self.id}: {self.title} by {self.seller} {self.activity}"

class Watchlist(models.Model):
    listing_id = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name= "wquery")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists", null=False, blank= True)
    def __str__(self):
        return f"{self.user} Watchlist: {self.listing_id.id}"

class Bid(models.Model):
    listing_id = models.ForeignKey(Auction_listing, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits= 10, decimal_places = 2)
    user = models.CharField(null=False)
    date_time = models.DateTimeField(auto_now_add= True)
    def __str__(self):
        return f"{self.listing_id.id}: Bid raised to {self.bid} by {self.user}"

class Comment(models.Model):
    listing_id = models.ForeignKey(Auction_listing, on_delete=models.CASCADE)
    comment = models.CharField()
    user = models.CharField()
    date_time = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f"{self.listing_id.id}. {self.user}: {self.comment}"


