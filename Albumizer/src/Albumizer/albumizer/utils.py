# This Python file uses the following encoding: utf-8

import hashlib
from django.conf import settings
from models import UserProfile, FacebookProfile, Album, Layout, Page, PageContent, Country, State, \
        Address, ShoppingCartItem, Order, SPSPayment, OrderStatus, OrderItem




def computeValidationHashForShoppingCart(request, exclude_addresses = True, extra_key = None):
    """ 
        Generates a hash which can be used to ensure that content
        of shopping cart does not change during checkout process.
    """
    hash_base = unicode(request.user.username) + request.META.get("REMOTE_ADDR") + \
                request.META.get("REMOTE_HOST") + request.META.get("HTTP_USER_AGENT") + \
                settings.SECRET_KEY

    if extra_key:
        hash_base += extra_key

    items = ShoppingCartItem.items_of_user(request.user)
    if exclude_addresses:
        for item in items:
            hash_base += unicode(item.album) + unicode(item.count)
    else:
        for item in items:
            hash_base += unicode(item.album) + unicode(item.count) + unicode(item.deliveryAddress)

    return hashlib.sha256(hash_base.encode("ascii", "backslashreplace")).hexdigest()




def validationHashForShoppingCartIsValid(request, exclude_addresses = True, extra_key = None):
    """ Validates hash returned by computeValidationHashForShoppingCart(). """
    if request.method == "GET":
        given_hash = request.GET.get("v")
    else:
        given_hash = request.POST.get("v")

    if not given_hash:
        return False

    our_hash = computeValidationHashForShoppingCart(request, exclude_addresses, extra_key)

    return our_hash == given_hash




def convert_money_into_two_decimal_string(amount):
    """ Returns the price of this album as a string with two decimal places. """
    amount_str = unicode(round(amount, 2))
    period_pos = amount_str.find(".")
    if period_pos == -1:
        amount_str += ".00"
    else:
        numbers_after_period = len(amount_str) - period_pos - 1
        if numbers_after_period == 1:
            amount_str += "0"
        elif numbers_after_period == 0:
            amount_str += "00"

    return amount_str




