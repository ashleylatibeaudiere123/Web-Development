from django.contrib import admin
from .models import User, Auction_listing,  Bid, Comment, Watchlist

# Register your models here.
admin.site.register(User)
admin.site.register(Auction_listing)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)
