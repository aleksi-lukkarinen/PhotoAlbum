from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from models import Album
from django.http import HttpResponseRedirect, HttpResponseBadRequest




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
    album = get_object_or_404(Album, pk = album_id)
    return render_to_response('album/show-single.html', RequestContext(request, {'album': album}))




@login_required
def edit_album(request, album_id):
    """ Allows user to edit a single album """
    album = get_object_or_404(Album, pk = album_id)
    return render_to_response('album/edit.html', RequestContext(request, {'album': album}))




def get_registration_information(request):
    """ Allows user to register himself/herself into this service """
    return render_to_response("accounts/register.html", RequestContext(request, {"is_registration_page": True}))




def log_in(request):
    """ Allows user to log in """

    if request.method == "GET":
        nextURL = request.GET.get("next")
        return render_to_response('accounts/login.html',
                                  RequestContext(request, {"is_login_page": True, "nextURL": nextURL}))
    elif request.method == "POST":
        error_list = []

        username = request.POST.get("txtLoginUserName", "").strip()
        if username == "":
            error_list.append("Please enter username.")

        password = request.POST.get("txtLoginPassword", "").strip()
        if password == "":
            error_list.append("Please enter password.")

        if not error_list:
            user = auth.authenticate(username = username, password = password)
            if user is None or not user.is_active:
                error_list.append("No account was found with the given credentials. " +
                                 "If the account should exist, at least one of the " +
                                 "user name and the password is wrong.")

        if not error_list:
            auth.login(request, user)

            nextURL = request.POST.get("nextURL", "/accounts/profile/")
            return HttpResponseRedirect(nextURL)
        else:
            template_parameters = {"is_login_page": True, "username": username, "error_list": error_list}
            return render_to_response('accounts/login.html', RequestContext(request, template_parameters))
    else:
        return HttpResponseBadRequest()




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
    """ Lets user to enter non-product-related information required for making an order, and finally accept the order """
    return render_to_response('order/information.html', RequestContext(request))




@login_required
def report_order_as_succesful(request):
    """ Acknowledges user about a successful order """
    return render_to_response('order/successful.html', RequestContext(request))
