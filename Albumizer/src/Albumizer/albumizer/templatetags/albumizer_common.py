# This Python file uses the following encoding: utf-8

import hashlib
from datetime import datetime
from django.template.base import FilterExpression, Library, Node, TemplateSyntaxError, resolve_variable
from django.template.defaulttags import token_kwargs
from django.template.loader import get_template
from django.contrib.auth.models import User
from Albumizer.albumizer.models import UserProfile, FacebookProfile, Album, Page, PageContent, \
        Country, State, Address, Order, SPSPayment, OrderStatus, OrderItem
from Albumizer.albumizer.utils import convert_money_into_two_decimal_string



register = Library()




def new_pseudo_unique_id():
    """ 
        Creates an id, which most likely is unique in the context of a single html page.
    """
    dt_str = unicode(datetime.now())
    return hashlib.sha224(dt_str.encode("ascii", "backslashreplace")).hexdigest()




@register.inclusion_tag("custom-tags/form_errors.html")
def form_error_list(forms):
    errors = []
    nonfielderrors = []

    for form in forms:
        for (field, err) in form.field_errors().items():
            errors.append([form.fields[field].label, err])
        for err in form.non_field_errors():
            nonfielderrors.append(err)

    return {
        "field_errors": errors,
        "non_field_errors": nonfielderrors
    }




@register.inclusion_tag("custom-tags/random-picks-album-list.html", takes_context = True)
def random_picks_album_list(context, number_of_random_picks = 4):
    """ 
        Outputs HTML and JavaScript code needed to render the Random Picks list of albums.
    """
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




@register.inclusion_tag("custom-tags/payment-services.html", takes_context = True)
def payment_services(context):
    """ Outputs HTML code needed to render a list of available payment services. """
    return {
        "debug": context.get("debug"),
        "sps_parameters": context.get("sps_parameters")
    }




class PaymentDetailsNode(Node):
    """
        Represents a template node for payment details.
    """
    def __init__(self, payment_info_reference, options):
        self._payment_info_reference = payment_info_reference
        self._options = options

    def render(self, context):
        payment_info = resolve_variable(self._payment_info_reference, context)

        container_style = ""
        if self._options.get("no_margins", False):
            container_style += "margin: 0em; "
        container_width = self._options.get("width", None)
        if container_width:
            container_style += "width: " + container_width + "; "

        template = get_template("custom-tags/payment-details.html")
        context.update({
            "payment_info": payment_info,
            "container_style": container_style.strip()
        })
        output = template.render(context)
        context.pop()

        return output

@register.tag
def payment_details(parser, token):
    """ 
        Outputs HTML code needed to render details of a payment.
    """
    token_parts = token.split_contents()
    if len(token_parts) < 2:
        raise TemplateSyntaxError("A payment detail dictionary is a mandatory parameter for %r" % token_parts[0])
    payment_info_reference = token_parts[1]

    remaining_token_parts = token_parts[2:]
    options = token_kwargs(remaining_token_parts, parser, support_legacy = False)
    if remaining_token_parts:
        raise TemplateSyntaxError("%r received an invalid token: %r" % \
                                  (token_parts[0], remaining_token_parts[0]))

    for (key, value) in options.items():
        options[key] = unicode(value)

    return PaymentDetailsNode(payment_info_reference, options)




ORDER_DETAILS_SIDEBAR__HEIGHT_OF_THREE_BORDERS_IN_EM = 3.5
ORDER_DETAILS_SIDEBAR__HEIGHT_OF_ORDER_SUMMARY_IN_EM = 15
ORDER_DETAILS_SIDEBAR__HEIGHT_OF_PLACE_ORDER_SECTION_IN_EM = 4

class OrderDetailsNode(Node):
    """
        Represents a template node for order details.
    """
    def __init__(self, custom_content_node_list):
        self._custom_content_node_list = custom_content_node_list

    def render(self, context):
        order_details_options = context.get("order_details_options", {})
        custom_content_after_items = self._custom_content_node_list.render(context)

        sidebar_background_min_height = ORDER_DETAILS_SIDEBAR__HEIGHT_OF_THREE_BORDERS_IN_EM + \
                                            ORDER_DETAILS_SIDEBAR__HEIGHT_OF_ORDER_SUMMARY_IN_EM

        if order_details_options.get("show_place_order_button", False):
            sidebar_background_min_height += ORDER_DETAILS_SIDEBAR__HEIGHT_OF_PLACE_ORDER_SECTION_IN_EM

        order_details_options["sidebar_background_min_height"] = sidebar_background_min_height

        template = get_template("custom-tags/order-details.html")
        context.update({
            "order_info": context.get("order_info"),
            "order_summary_options": order_details_options,
            "custom_content_after_items": custom_content_after_items
        })
        output = template.render(context)
        context.pop()

        return output

@register.tag
def order_details(parser, token):
    """ 
        Outputs HTML code needed to render detailed information about an order.
        
        Basic usage:
        
            {% order_details %}{% end_order_details %}
            
        It is possible to include customized content below the list of items of the order:
        
            {% order_details %}
              {% payment_details order_info.payment %}
            {% end_order_details %}
    """
    custom_content_node_list = parser.parse(("end_order_details",))
    parser.delete_first_token()
    return OrderDetailsNode(custom_content_node_list)




@register.filter
def mto2dstr(value):
    return convert_money_into_two_decimal_string(value)









