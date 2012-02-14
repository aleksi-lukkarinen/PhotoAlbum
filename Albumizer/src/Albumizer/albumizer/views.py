# This Python file uses the following encoding: utf-8

import hashlib, logging
from datetime import datetime
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import simplejson as json
from django.views.decorators.cache import cache_control
from Albumizer.albumizer import facebook_api
from models import UserProfile, FacebookProfile, Album, Page, PageContent, Country, State, \
        Address, ShoppingCartItem, Order, SPSPayment, OrderStatus, OrderItem
from forms import AlbumCreationForm, LoginForm, RegistrationForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, \
        HttpResponseForbidden, HttpResponseNotFound, HttpResponse




SPS_STATUS_SUCCESSFUL = "successful"
SPS_STATUS_CANCELED = "canceled"
SPS_STATUS_UNSUCCESSFUL = "unsuccessful"
VALID_SPS_PAYMENT_STATUSES = [SPS_STATUS_SUCCESSFUL, SPS_STATUS_CANCELED, SPS_STATUS_UNSUCCESSFUL]




commonLogger = logging.getLogger(__name__)
userActionLogger = logging.getLogger("albumizer.userActions")
paymentLogger = logging.getLogger("albumizer.payments")




def dispatch_by_method(request, *args, **kwargs):
    """
        This pseudo-view is meant to be used to dispatch requests to view
        functions according to the http method used in the request. This is
        useful for views requiring use of multiple http methods, because
        this way the code can be structured better and thus becomes clearer
        and a bit shorter. 
    """
    get_view = kwargs.pop("GET", None)
    post_view = kwargs.pop("POST", None)

    if request.method == "GET" and get_view is not None:
        return get_view(request, *args, **kwargs)
    elif request.method == "POST" and post_view is not None:
        return post_view(request, *args, **kwargs)
    else:
        return HttpResponseNotFound()




def add_public_caching_headers(response):
    """ A helper function to add http response some headers for responses that can be publicly cached. """
    response["Cache-Control"] = "public, must-revalidate, max-age=300"




def add_caching_preventing_headers(response):
    """ A helper function to add http response some headers to prevent all kinds of caching. """
    response["Pragma"] = "no-cache"
    response["Expires"] = "Sat, 01 Jan 2000 00:00:00 GMT"   # In the past on purpose, do not change!!
    response["Cache-Control"] = "private, no-cache, no-store, must-revalidate"




def render_to_response_as_public(*args, **kwargs):
    """ A shortcut function for rendering public content with headers allowing public caching. """
    response = render_to_response(*args, **kwargs)
    add_public_caching_headers(response)
    return response




def return_as_json(view_function):
    """ A view decorator for returning a json string as a response from view functions. """
    def _compose_request(*args, **kwargs):
        response = HttpResponse()
        add_caching_preventing_headers(response)
        response.write(unicode(view_function(*args, **kwargs)))
        return response

    return _compose_request




def prevent_all_caching(view_function):
    """ 
        A view decorator for settings response headers so that any cache-provider
        (including user's browser) does not cache any pages.
    """
    def _compose_request(*args, **kwargs):
        response = view_function(*args, **kwargs)
        add_caching_preventing_headers(response)
        return response

    return _compose_request




def welcome_page(request):
    """ The first view of this application. """
    template_parameters = {'latest_albums': Album.latest_public_ones()}
    return render_to_response_as_public("welcome.html", RequestContext(request, template_parameters))




def list_all_visible_albums(request):
    """ Lists all albums visible to the current user (logged in or not). """
    albums = Album.ones_visible_to(request.user)

    paginator = Paginator(albums, 20) # Show 20 albums per page

    # Make sure page request is an int. If not, deliver first page.
    try:
      page = int(request.GET.get('page', '1'))
    except ValueError:
      page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
      albums = paginator.page(page)
    except (EmptyPage, InvalidPage):
      albums = paginator.page(paginator.num_pages)

    template_parameters = {'albums': albums, 'is_album_list_page': True}
    return render_to_response_as_public('album/list-all.html', RequestContext(request, template_parameters))

def show_single_page(request, album_id, page_number):
    myalbum= get_object_or_404(Album, pk=album_id)
    mypage = get_object_or_404(Page, album=album_id, pageNumber=page_number)
    dict={"pageNumber":mypage.pageNumber,
          "albumTitle":myalbum.title}
    for pagecontent in mypage.pagecontents.all():
        dict[pagecontent.placeHolderID]=pagecontent.content
    return render_to_response('album/layouts/{0}.html'.format(mypage.layoutID), RequestContext(request, dict))


def show_single_album(request, album_id):
    """ Allows user to browse a single album. """
    album = Album.by_id(album_id)
    if not album:
        return render_to_response_as_public('album/not-found.html', RequestContext(request))

    if album.is_hidden_from_user(request.user):
        return render_to_response_as_public('album/view-access-denied.html', RequestContext(request))

    response = render_to_response_as_public('album/show-single.html', RequestContext(request, {'album': album}))
    if not album.isPublic:
        add_caching_preventing_headers(response)

    return response




@prevent_all_caching
def show_single_album_with_hash(request, album_id, secret_hash):
    """ Allows user to browse a single private album with a secret hash code. """

    album = Album.by_id_and_secret_hash(album_id, secret_hash)
    if not album:
        return render_to_response('album/not-found.html', RequestContext(request))

    if album.isPublic or album.is_owned_by(request.user):
        return HttpResponseRedirect(album.get_absolute_url())

    template_parameters = {'album': album, 'opened_using_secret_hash': True}
    return render_to_response('album/show-single.html', RequestContext(request, template_parameters))




@login_required
@prevent_all_caching
def create_album_GET(request):
    """ Displays a form which allows user to create new photo albums. """
    assert request.method == "GET"
    form = AlbumCreationForm(request)
    return render_to_response("album/create.html",
                              RequestContext(request, {"form": form}))

@login_required
@prevent_all_caching
def create_album_POST(request):
    """ Creates a new photo album and redirects to its view. """
    assert request.method == "POST"
    form = AlbumCreationForm(request, request.POST)
    if not form.is_valid():
        return render_to_response("album/create.html", RequestContext(request, {"form": form}))

    album_title = form.cleaned_data.get("txtAlbumTitle")
    album_description = form.cleaned_data.get("txtAlbumDescription") or ""
    album_publicity = form.cleaned_data.get("chkPublicAlbum")

    new_album = Album(
        owner = request.user,
        title = album_title,
        description = album_description,
        isPublic = album_publicity
    )
    new_album.save()

    userActionLogger.info("User %s created an album called \"%s\"." % (request.user.username, new_album.title))

    return HttpResponseRedirect(new_album.get_absolute_url())




@login_required
@prevent_all_caching
def edit_album(request, album_id):
    """ Allows user to edit a single album. """
    album_resultset = Album.objects.filter(id__exact = album_id)
    if not album_resultset:
        return render_to_response('album/not-found.html', RequestContext(request))

    album = album_resultset[0]
    if not album.is_editable_to_user(request.user):
        return render_to_response('album/edit-access-denied.html', RequestContext(request))

    return render_to_response('album/edit.html', RequestContext(request, {'album': album}))




@login_required
@prevent_all_caching
def add_album_to_shopping_cart(request):
    """ Allows user to add items into his/her shopping cart. """
    if request.method != "POST":
        return HttpResponseNotFound()




@prevent_all_caching
def get_registration_information_GET(request):
    """ Displays a form which allows user to register himself/herself into this service. """
    assert request.method == "GET"
    template_parameters = {
        "is_registration_page": True,
        "form": RegistrationForm()
    }
    return render_to_response("accounts/register.html",
                              RequestContext(request, template_parameters))

@prevent_all_caching
def get_registration_information_POST(request):
    """ Register an user to this service and redirects him/her to his/her profile. """
    assert request.method == "POST"
    form = RegistrationForm(request.POST)
    if not form.is_valid():
        return render_to_response("accounts/register.html",
                                  RequestContext(request, {"is_registration_page": True, "form": form}))

    username = form.cleaned_data.get("txtUserName")
    password = form.cleaned_data.get("txtPassword")
    firstname = form.cleaned_data.get("txtFirstName")
    lastname = form.cleaned_data.get("txtLastName")
    gender = form.cleaned_data.get("radGender")
    email = form.cleaned_data.get("txtEmail")
    homephone = form.cleaned_data.get("txtHomePhone") or ""
    postaddressline1 = form.cleaned_data.get("txtPostAddress1") or ""
    postaddressline2 = form.cleaned_data.get("txtPostAddress2") or ""
    zipcode = form.cleaned_data.get("txtZipCode") or ""
    city = form.cleaned_data.get("txtCity") or ""
    state = form.cleaned_data.get("cmbState")
    country = form.cleaned_data.get("cmbCountry")

    new_user = User.objects.create_user(username, email, password)
    new_user.first_name = firstname
    new_user.last_name = lastname
    new_user.save()

    user_profile = new_user.get_profile()
    user_profile.gender = gender
    user_profile.homePhone = homephone
    user_profile.save()

    userActionLogger.info("User %s (id %d) was created." % (username, new_user.id))

    if postaddressline1 or postaddressline2 or zipcode or city or state or country:
        new_address = Address(
            owner = new_user,
            postAddressLine1 = postaddressline1,
            postAddressLine2 = postaddressline2,
            zipCode = zipcode,
            city = city,
            state = state,
            country = country
        )
        new_address.save()
        userActionLogger.info("For user %s, an address (id %d) was created." % (username, new_address.id))

    authenticated_user = auth.authenticate(username = username, password = password)
    auth.login(request, authenticated_user)

    return HttpResponseRedirect(reverse("albumizer.views.show_profile"))




@prevent_all_caching
def log_in_GET(request):
    """ Displays a form which allows user to log in. """
    assert request.method == "GET"
    form = LoginForm()
    next_url = request.GET.get("next")
    template_parameters = {"is_login_page": True, "nextURL": next_url, "form": form}
    return render_to_response('accounts/login.html', RequestContext(request, template_parameters))


@prevent_all_caching
def log_in_POST(request):
    """ Logs an user in to the service and redirects him/her to his/her profile page. """
    assert request.method == "POST"
    form = LoginForm(request.POST)
    if not form.is_valid():
        next_url = request.POST.get("nextURL")
        template_parameters = {"is_login_page": True, "nextURL": next_url, "form": form}
        return render_to_response('accounts/login.html', RequestContext(request, template_parameters))

    next_url = request.POST.get("nextURL", reverse("albumizer.views.show_profile"))
    template_parameters = {"is_login_page": True, "nextURL": next_url, "form": form}
    username = form.cleaned_data.get("txtLoginUserName")
    password = form.cleaned_data.get("txtLoginPassword")

    user = auth.authenticate(username = username, password = password)
    if user is None:
        form.add_common_error(u"Unknown error: Albumizer was unable to authenticate this username.")
        commonLogger.info("Login failed for username %s." % username)
        return render_to_response('accounts/login.html', RequestContext(request, template_parameters))

    auth.login(request, user)
    userActionLogger.info("User %s (id %d) logged in." % (user.username, user.id))

    return HttpResponseRedirect(next_url)




def log_out(request):
    """ Allows user to log out and redirects him/her to the welcome page. """
    username = request.user.username;
    auth.logout(request)
    userActionLogger.info("User %s logged out." % username)
    return HttpResponseRedirect(reverse("albumizer.views.welcome_page"))




def validateFbToken(request, fbProfile, aToken):
    """ connects facebook to validate token
    userprofile is updated with values from facebook
    """
    response = facebook_api.getGraph(request, aToken)
    fbProfile.rawResponse = response;
    fbProfile.token = aToken
    fbProfile.lastQueryTime = datetime.now()
    fbProfile.save()
    data = json.loads(response)

    #sanity check
    if data["id"] <> str(fbProfile.facebookID):
        raise (RuntimeError,
               "response has data for some other facebook id than expected({0}<>{1})".format(
                    data["id"], fbProfile.facebookID)
       )


    #then collect data
    for key, value in data.iteritems():
        if key == "first_name":
            fbProfile.userProfile.user.first_name = value
        elif key == "last_name":
            fbProfile.userProfile.user.last_name = value
        elif key == "link":
            fbProfile.profileUrl = value
        elif key == "email":
            fbProfile.userProfile.user.email = value
        elif key == "gender":
            if value == "male":
                fbProfile.userProfile.gender = "M"
            elif value == "female":
                fbProfile.userProfile.gender = "F"
    fbProfile.userProfile.user.save()
    fbProfile.userProfile.save()
    fbProfile.save()

def checkfb(request, aToken, userid):
    """ Validates the authentication token, logs in the user.
        Return value is an empty string when authentication is successful.
        If authentication fails, the reason is returned in plain text.
        Some rare error situations will generate exceptions.
        """
    fbProfile = None

    #if user is already authenticated, just update the token
    if request.user.is_authenticated():
        #TODO handle a situation where user is authenticated with some the username+password-backend
        fbProfile = request.user.get_profile().facebookProfile
        if fbProfile.token == aToken:
            return ""
        validateFbToken(request, fbProfile, aToken)
    else:
        #check if user exists (using the facebook authentication backend        
        user = auth.authenticate(facebookID = userid)

        #create user if not yet found
        if user is None:
            fbProfile = FacebookProfile(facebookID = userid)
            #create new user
            fbusername = "facebook_" + userid

            #check if user has already been created but lacks a link to facebookprofile (invalid data but let's fix it)
            query = User.objects.filter(username = fbusername)
            userProf = None
            if query.exists():
                new_user = query[0]
                userProf = new_user.get_profile()
            else:
                new_user = User.objects.create_user(fbusername, "", "")
                userProf = new_user.get_profile()
            fbProfile.userProfile = userProf
            #validate token before creating the user
            validateFbToken(request, fbProfile, aToken)
            user = auth.authenticate(facebookID = userid)
            if user is None:
                raise RuntimeError(value = "facebook profile created, but authentication still failed")
        else:
            fbProfile = user.get_profile().facebookProfile
            validateFbToken(request, fbProfile, aToken)
            #we need to get the user again because validateFbToken saves through fbProfile and the user object here is 
            #not same object as the one found through fbProfile.userProfile.user 
            user = auth.authenticate(facebookID = userid)
            if user is None:
                raise RuntimeError(value = "facebook profile created, but authentication still failed")
        #user found and authenticated, let's login    
        auth.login(request, user)
        userActionLogger.info("User %s (id %d) logged in via Facebook." % (user.username, user.id))

    return ""

def facebook_login(request):
    #for testing purposes, you can check the urlpattern is working by entering the correct url to browser
    if request.method == "GET" :
        return HttpResponse("<div>You made a get request. Hooray!</div>")

    aToken = request.POST.get("accessToken", "")
    userid = request.POST.get("userID", "");

    reason = checkfb(request, aToken, userid)

    responsedata = {"success": len(reason) == 0, "reason":reason}
    return HttpResponse(json.dumps(responsedata), mimetype = "application/json");




@login_required
@prevent_all_caching
def show_profile(request):
    """ Shows user his/her profile page. """
    albums = Album.ones_owned_by(request.user)

    paginator = Paginator(albums, 10) # Show 10 albums per page

    # Make sure page request is an int. If not, deliver first page.
    try:
      page = int(request.GET.get('page', '1'))
    except ValueError:
      page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
      albums = paginator.page(page)
    except (EmptyPage, InvalidPage):
      albums = paginator.page(paginator.num_pages)

    template_parameters = {'albums': albums}
    return render_to_response('accounts/profile.html', RequestContext(request, template_parameters))




@login_required
@prevent_all_caching
def edit_account_information(request):
    """ Allows user to edit his/her personal information managed by the application """
    return render_to_response('accounts/edit-information.html', RequestContext(request))




@login_required
@prevent_all_caching
def edit_shopping_cart(request):
    """ Allows user to edit the content of his/her shopping cart """
    items = ShoppingCartItem.items_of_user(request.user)

    item_info = []
    sub_total_price = 0.00
    for item in items:
        item_price = item.album.price()
        row_total = item.count * item_price
        sub_total_price += row_total
        item_info.append({
            "title": item.album.title,
            "url": item.album.get_absolute_url(),
            "description": item.album.description,
            "creator": item.album.owner,
            "coverUrl": "",
            "number_of_units": item.count,
            "unit_price": item_price,
            "row_total": row_total
        })

    template_parameters = {
        "item_info": item_info,
        "sub_total_price": sub_total_price
    }
    return render_to_response('order/shopping-cart.html', RequestContext(request, template_parameters))




@login_required
@prevent_all_caching
def get_ordering_information(request):
    """ Lets user to enter non-product-related information required for making an order. """
    template_parameters = {}
    return render_to_response('order/information.html', RequestContext(request, template_parameters))




@login_required
@prevent_all_caching
def show_order_summary(request):
    """ Shows user a summary about his/her order and lets him/her to finally place the order. """
    template_parameters = {}
    return render_to_response('order/summary.html', RequestContext(request, template_parameters))




@login_required
@prevent_all_caching
def report_order_as_successful(request):
    """
        Actually creates an order based on the content of user's shopping cart and
        acknowledges user about the fact. After this, the shopping cart will be empty.
        User will be asked to pay the order via the Simple Payments service by clicking
        a link leading to the service.
    """
    sps_address = settings.SIMPLE_PAYMENT_SERVICE_URL
    sps_seller_id = settings.SIMPLE_PAYMENT_SERVICE_SELLER_ID
    sps_secret = settings.SIMPLE_PAYMENT_SERVICE_SECRET

    our_protocol = "http"
    our_domain = Site.objects.get_current().domain

    our_url_start = "%s://%s/" % (our_protocol, our_domain)
    report_view_name = "albumizer.views.report_sps_payment_status"
    sps_success_url = our_url_start + reverse(report_view_name, args = [SPS_STATUS_SUCCESSFUL])
    sps_cancel_url = our_url_start + reverse(report_view_name, args = [SPS_STATUS_CANCELED])
    sps_error_url = our_url_start + reverse(report_view_name, args = [SPS_STATUS_UNSUCCESSFUL])

    sps_payment_id = 3
    amount = 4

    checksum_source = "pid=%s&sid=%s&amount=%s&token=%s" % (sps_payment_id, sps_seller_id, amount, sps_secret)
    checksum = hashlib.md5(checksum_source).hexdigest()

    template_parameters = {
        "sps_address": sps_address,
        "sps_seller_id": sps_seller_id,
        "sps_payment_id": sps_payment_id,
        "sps_amount": amount,
        "sps_checksum": checksum,
        "sps_success_url": sps_success_url,
        "sps_cancel_url": sps_cancel_url,
        "sps_error_url": sps_error_url
    }
    return render_to_response('order/successful.html', RequestContext(request, template_parameters))




@login_required
@prevent_all_caching
def report_sps_payment_status(request, status):
    """
        Verifies correctness of the payment details the Simple Payments service
        sent. If everything is ok, the payment is registered as done and the user 
        is acknowledged about success of the payment.
    """
    if request.method != "GET" or not status in VALID_SPS_PAYMENT_STATUSES:
        return HttpResponseBadRequest()

    payment_id = request.GET.get("pid")
    reference = request.GET.get("ref")
    sps_checksum = request.GET.get("checksum")
    if not payment_id or not reference or not sps_checksum:
        return HttpResponseBadRequest()

    sps_secret = settings.SIMPLE_PAYMENT_SERVICE_SECRET
    our_checksum_source = "pid=%s&ref=%s&token=%s" % (payment_id, reference, sps_secret)
    our_checksum = hashlib.md5(our_checksum_source).hexdigest()
    if our_checksum != sps_checksum:
        return HttpResponseBadRequest()

    order_qs = Order.objects.filter(id__exact = payment_id)
    if not order_qs:
        return HttpResponseServerError()
    order = order_qs[0]

    template_parameters = {
        "order": order,
        "payment_id": payment_id
    }
    return render_to_response('payment/sps/%s.html' % status,
                              RequestContext(request, template_parameters))




@return_as_json
def api_json_get_latest_albums(request, how_many):
    """ Returns a json representation of data of the latest publicly visible albums. """
    return Album.latest_public_ones_as_json(int(how_many))




@return_as_json
def api_json_get_random_albums(request, how_many):
    """ Returns a json representation of data of random publicly visible albums. """
    return Album.pseudo_random_public_ones_as_json(int(how_many))




@return_as_json
def api_json_get_album_count(request):
    """ Returns the number of albums currently registered. """
    return Album.objects.count()




@return_as_json
def api_json_get_user_count(request):
    """ Returns the number of users currently registered. """
    return User.objects.count()









