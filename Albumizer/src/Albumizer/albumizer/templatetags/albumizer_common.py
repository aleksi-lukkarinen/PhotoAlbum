# This Python file uses the following encoding: utf-8

import hashlib
from datetime import datetime
from django import template
from django.contrib.auth.models import User
from Albumizer.albumizer.models import UserProfile, FacebookProfile, Album, Page, PageContent, \
        Country, State, Address, Order, SPSPayment, OrderStatus, OrderItem




register = template.Library()


@register.inclusion_tag("custom-tags/form_errors.html")
def form_error_list(forms):
    errors=[]
    nonfielderrors=[]
    
    for form in forms:
        for (field, err) in form.field_errors().items():
            errors.append([form.fields[field].label, err])
        for err in form.non_field_errors():
            nonfielderrors.append(err)

    return {"field_errors":errors, "non_field_errors":nonfielderrors}

def new_pseudo_unique_id():
    """ Creates an id, which most likely is unique in the context of a single html page. """
    dt_str = unicode(datetime.now())
    return hashlib.sha224(dt_str.encode("ascii", "backslashreplace")).hexdigest()




@register.inclusion_tag("custom-tags/random_picks_album_list.html", takes_context = True)
def random_picks_album_list(context, number_of_random_picks = 4):
    """ Outputs HTML and JavaScript code needed to render the Random Picks list of albums. """
    random_picks = Album.pseudo_random_public_ones(number_of_random_picks)

    if random_picks:
        number_of_random_picks = len(random_picks)

    if number_of_random_picks < 3:
        number_of_random_picks = 0
        random_picks = None
    elif number_of_random_picks > 4:
        number_of_random_picks = (number_of_random_picks / 4) * 4
        random_picks = random_picks[0:number_of_random_picks]

    return {
        "id": new_pseudo_unique_id(),
        "random_pick_albums": random_picks,
        "number_of_random_picks": number_of_random_picks,
        "site_domain": context.get("site_domain")
    }




@register.inclusion_tag("custom-tags/twitter-show-tweet.html", takes_context = True)
def show_twitter_tweet(context):
    """ Outputs HTML and JavaScript code needed to render a twitter tweet. """
    return {
        "id": new_pseudo_unique_id(),
        "site_name": context.get("site_name"),
        "site_domain": context.get("site_domain"),
        "twitter_account": context.get("twitter_account"),
        "twitter_hashtag": context.get("twitter_hashtag")
    }




@register.inclusion_tag("custom-tags/twitter-tweet-button-album.html", takes_context = True)
def twitter_tweet_button_album(context, album):
    """ Outputs HTML and JavaScript code needed to render a tweet button for an album. """
    return {
        "id": new_pseudo_unique_id(),
        "album": album,
        "site_domain": context.get("site_domain"),
        "twitter_account": context.get("twitter_account"),
        "twitter_hashtag": context.get("twitter_hashtag")
    }




@register.inclusion_tag("custom-tags/twitter-follow-button.html", takes_context = True)
def twitter_follow_button(context):
    """ Outputs HTML and JavaScript code needed to render a follow button for Albumizer's Twitter account. """
    return {
        "id": new_pseudo_unique_id(),
        "twitter_account": context.get("twitter_account")
    }




@register.inclusion_tag("custom-tags/usage-notice.html")
def albumizer_usage_notice():
    """ Outputs HTML and JavaScript code needed to render a usage notice describing number of users and albums. """
    return {
        "id": new_pseudo_unique_id(),
        'album_count': Album.objects.count(),
        'user_count': User.objects.count()
    }




@register.inclusion_tag("custom-tags/show-messages.html", takes_context = True)
def show_messages(context):
    """ Outputs HTML and JavaScript code needed to render any messages stored in the Django's message facility. """
    return {
        "messages": context.get("messages")
    }


