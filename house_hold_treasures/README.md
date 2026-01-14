# Household Treasures
#### Video Demo:  <https://youtu.be/50IirflhgTE>

![Household Treasures Screenshot](householdtreasures.png)

## Description:

#### Tech used: HTML, CSSS, Python, Javascript, Flask

Household Treasures is a web application that allows users to sell and buy items. Upon accessing the site, users are redirected to login using their username and password. If users do not have an account, they can register using the specified link. Missing or invalid data prompts an error message and reloading of the specific form. After registering, information such as their username and hash of their password is stored in the htreasures database.

Users are then redirected to the homepage, which shows all the items posted on the platform. They can search for an item by scrolling or using the search bar.  After clicking on the price, users are redirected to a specific item page, showing the item’s name, all pictures posted, its price and description. There is also a "message seller" button, which automatically sends an email to the seller asking for the availability of the item. 

![Listing](listing.png)

The web application further allows sellers to post items and keep track of all their active lisings.

![Sell form](sell.png)

![Seller's listing](seller_listings.png)


There are several files responsible for the design and workings of the web application. The layout.html provides the blueprint for the website, while the app.py file contains all the code that processes the data for each route. Helpers.py depict the code for the login-required function, while the requirements.txt file lists the required programming packages.

## How to run application

Use: flask run
