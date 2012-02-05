# This Python file uses the following encoding: utf-8

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from models import Address, Album, Country, UserProfile, Order, OrderItem, Page, PageContent, State
from forms import AlbumCreationForm, LoginForm, RegistrationForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, \
     HttpResponseForbidden, HttpResponseNotFound




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




def welcome_page(request):
    """ The first view of this application """
    return render_to_response("welcome.html", RequestContext(request))




def list_all_visible_albums(request):
    """ Lists all albums visible to the current user (logged in or not) """
    album_list = Album.objects.order_by('title')
    template_parameters = {'albums': album_list, 'is_album_list_page': True}
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

    return HttpResponseRedirect("/album/" + str(new_album.id) + "/")





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




@login_required
def show_profile(request):
    """ Shows user his/her profile page """
    return render_to_response('accounts/profile.html', RequestContext(request))




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

