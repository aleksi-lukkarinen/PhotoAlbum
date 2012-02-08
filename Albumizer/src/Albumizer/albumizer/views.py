# This Python file uses the following encoding: utf-8
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson as json 
from Albumizer.albumizer import facebook_api
from models import Address, Album, Country, UserProfile, Order, OrderItem, Page, PageContent, State, FacebookProfile
from forms import AlbumCreationForm, LoginForm, RegistrationForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, \
     HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from datetime import datetime



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


def return_json(content):
    """ A shortcut function for returning a json string as a response from view functions """
    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    response["Cache-Control"] = "no-cache"
    response.write(content)
    return response





def welcome_page(request):
    """ The first view of this application """
    random_albums = Album.get_pseudo_random_public(8)
    if len(random_albums) < 3:
        random_albums = None
    elif len(random_albums) > 4:
        random_albums = random_albums[0:(len(random_albums) / 4) * 4]

    template_parameters = {
        'latest_albums': Album.get_latest_public(),
        'random_albums': random_albums,
        'album_count': Album.objects.count(),
        'user_count': User.objects.count()
    }
    return render_to_response("welcome.html", RequestContext(request, template_parameters))




def list_all_visible_albums(request):
    """ Lists all albums visible to the current user (logged in or not) """
    albums = Album.objects.filter(isPublic = True).order_by('title')

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
    return render_to_response('album/list-all.html', RequestContext(request, template_parameters))




def show_single_album(request, album_id):
    """ Allows user to browse a single album """
    album_resultset = Album.objects.filter(id__exact = album_id)
    if not album_resultset:
        return render_to_response('album/not-found.html', RequestContext(request))

    album = album_resultset[0]
    if album.is_hidden_from_user(request.user):
        return render_to_response('album/view-access-denied.html', RequestContext(request))

    return render_to_response('album/show-single.html', RequestContext(request, {'album': album}))




@login_required
def create_album_GET(request):
    """ Displays a form which allows user to create new photo albums """
    assert request.method == "GET"
    form = AlbumCreationForm(request)
    return render_to_response("album/create.html",
                              RequestContext(request, {"form": form}))

@login_required
def create_album_POST(request):
    """ Creates a new photo album and redirects to its view """
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

    return HttpResponseRedirect("/album/" + unicode(new_album.id) + "/")





@login_required
def edit_album(request, album_id):
    """ Allows user to edit a single album """
    album_resultset = Album.objects.filter(id__exact = album_id)
    if not album_resultset:
        return render_to_response('album/not-found.html', RequestContext(request))

    album = album_resultset[0]
    if not album.is_editable_to_user(request.user):
        return render_to_response('album/edit-access-denied.html', RequestContext(request))

    return render_to_response('album/edit.html', RequestContext(request, {'album': album}))




@login_required
def add_album_to_shopping_cart(request):
    """ Allows user to add items into his/her shopping cart """
    if request.method != "POST":
        return HttpResponseNotFound()



def get_registration_information_GET(request):
    """ Displays a form which allows user to register himself/herself into this service """
    assert request.method == "GET"
    template_parameters = {
        "is_registration_page": True,
        "form": RegistrationForm()
    }
    return render_to_response("accounts/register.html",
                              RequestContext(request, template_parameters))

def get_registration_information_POST(request):
    """ Register an user to this service and redirects him/her to his/her profile """
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

    authenticated_user = auth.authenticate(username = username, password = password)
    auth.login(request, authenticated_user)

    return HttpResponseRedirect("/accounts/profile/")




def log_in_GET(request):
    """ Displays a form which allows user to log in """
    form = LoginForm()
    next_url = request.GET.get("next")
    template_parameters = {"is_login_page": True, "nextURL": next_url, "form": form}
    return render_to_response('accounts/login.html', RequestContext(request, template_parameters))


def log_in_POST(request):
    """ Logs an user in to the service and redirects him/her to his/her profile page """
    form = LoginForm(request.POST)
    if not form.is_valid():
        next_url = request.POST.get("nextURL")
        template_parameters = {"is_login_page": True, "nextURL": next_url, "form": form}
        return render_to_response('accounts/login.html', RequestContext(request, template_parameters))

    next_url = request.POST.get("nextURL", "/accounts/profile/")
    template_parameters = {"is_login_page": True, "nextURL": next_url, "form": form}
    username = form.cleaned_data.get("txtLoginUserName")
    password = form.cleaned_data.get("txtLoginPassword")

    user = auth.authenticate(username = username, password = password)
    if user is None:
        form.add_common_error(u"Unknown error: Albumizer was unable to authenticate this username.")
        return render_to_response('accounts/login.html', RequestContext(request, template_parameters))

    auth.login(request, user)

    return HttpResponseRedirect(next_url)




def log_out(request):
    """ Allows user to log out """
    auth.logout(request)
    return HttpResponseRedirect("/")

def validateFbToken(request, fbProfile, aToken):
    """ connects facebook to validate token
    userprofile is updated with values from facebook
    """
    response=facebook_api.getGraph(request, aToken)
    fbProfile.rawResponse=response;
    fbProfile.token=aToken
    fbProfile.lastQueryTime=datetime.now()
    fbProfile.save()
    data=json.loads(response)
    
    #sanity check
    if data["id"]<>str(fbProfile.facebookID):
        raise (RuntimeError, 
               "response has data for some other facebook id than expected({0}<>{1})".format(data["id"], fbProfile.facebookID)
       )
                                                                                             
    
    #then collect data
    for key, value in data.iteritems():
        if key=="first_name":
            fbProfile.userProfile.user.first_name=value
        elif key=="last_name":
            fbProfile.userProfile.user.last_name=value
        elif key=="link":
            fbProfile.profileUrl=value
        elif key=="email":
            fbProfile.userProfile.user.email=value
        elif key=="gender":
            if value=="male":        
                fbProfile.userProfile.gender="M"
            elif value=="female":
                fbProfile.userProfile.gender="F"
    fbProfile.userProfile.user.save()
    fbProfile.userProfile.save()
    fbProfile.save()
    
def checkfb(request,aToken, userid):
    """ Validates the authentication token, logs in the user.
        Return value is an empty string when authentication is successful.
        If authentication fails, the reason is returned in plain text.
        Some rare error situations will generate exceptions.
        """
    fbProfile=None
    
    #if user is already authenticated, just update the token
    if request.user.is_authenticated():
        #TODO handle a situation where user is authenticated with some the username+password-backend
        fbProfile=request.user.get_profile().facebookProfile
        if fbProfile.token==aToken:
            return ""
        validateFbToken(request, fbProfile, aToken)
    else:
        #check if user exists (using the facebook authentication backend        
        user=auth.authenticate(facebookID=userid)
    
        #create user if not yet found
        if user is None:
            fbProfile= FacebookProfile(facebookID=userid)
            #create new user
            fbusername="facebook_"+userid
            
            #check if user has already been created but lacks a link to facebookprofile (invalid data but let's fix it)
            query=User.objects.filter(username=fbusername)        
            userProf=None
            if query.exists():
                new_user=query[0]
                userProf=new_user.get_profile()
            else:
                new_user = User.objects.create_user(fbusername, "", "")    
                userProf = new_user.get_profile()
            fbProfile.userProfile=userProf
            #validate token before creating the user
            validateFbToken(request, fbProfile, aToken)
            user=auth.authenticate(facebookID=userid)
            if user is None:
                raise RuntimeError(value="facebook profile created, but authentication still failed")
        else:
            fbProfile=user.get_profile().facebookProfile
            validateFbToken(request, fbProfile, aToken)
            #we need to get the user again because validateFbToken saves through fbProfile and the user object here is 
            #not same object as the one found through fbProfile.userProfile.user 
            user=auth.authenticate(facebookID=userid)
            if user is None:
                raise RuntimeError(value="facebook profile created, but authentication still failed")
        #user found and authenticated, let's login    
        auth.login(request,user)
    
    return ""
    
def facebook_login(request):
    #for testing purposes, you can check the urlpattern is working by entering the correct url to browser
    if request.method=="GET" :
        return HttpResponse("<div>You made a get request. Hooray!</div>")
                            
    aToken=request.POST.get("accessToken", "")
    userid=request.POST.get("userID","");
        
    reason=checkfb(request,aToken,userid)
        
    responsedata={"success": len(reason)==0, "reason":reason}
    return HttpResponse(json.dumps(responsedata), mimetype="application/json");
    


@login_required
def show_profile(request):
    """ Shows user his/her profile page """
    albums = Album.objects.filter(owner=request.user).order_by('title')

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
def edit_account_information(request):
    """ Allows user to edit his/her personal information managed by the application """
    return render_to_response('accounts/edit-information.html', RequestContext(request))




@login_required
def edit_shopping_cart(request):
    """ Allows user to edit the content of his/her shopping cart """
    return render_to_response('order/shopping-cart.html', RequestContext(request))




@login_required
def get_ordering_information(request):
    """ 
        Lets user to enter non-product-related information required
        for making an order, and finally accept the order
    """
    return render_to_response('order/information.html', RequestContext(request))




@login_required
def report_order_as_succesful(request):
    """ Acknowledges user about a successful order """
    return render_to_response('order/successful.html', RequestContext(request))




def api_json_get_latest_albums(request, how_many):
    """ Returns a json representation of data of the latest publicly visible albums """
    return return_json(Album.get_latest_public_as_json(int(how_many)))




def api_json_get_random_albums(request, how_many):
    """ Returns a json representation of data of random publicly visible albums """
    return return_json(Album.get_pseudo_random_public_as_json(int(how_many)))




def api_json_get_album_count(request):
    """ Returns the number of albums currently registered """
    return return_json(Album.objects.count())




def api_json_get_user_count(request):
    """ Returns the number of users currently registered """
    return return_json(User.objects.count())









