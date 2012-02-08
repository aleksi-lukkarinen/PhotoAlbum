# This Python file uses the following encoding: utf-8

from datetime import datetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from models import Address, Album, Country, UserProfile, Order, OrderItem, Page, PageContent, State,FacebookProfile
from forms import RegistrationForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, HttpResponse
from django.utils import simplejson as json 
from Albumizer.albumizer import facebook_api


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

    if request.method == "GET":
        form = RegistrationForm()
        return render_to_response("accounts/register.html",
                                  RequestContext(request, {"is_registration_page": True, "form": form}))

    elif request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # The user information is already validated in the form handling code
            userid = form.cleaned_data.get("txtUserId")
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

            new_user = User.objects.create_user(userid, email, password)
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

            authenticated_user = auth.authenticate(username = userid, password = password)
            auth.login(request, authenticated_user)

            return HttpResponseRedirect("/accounts/profile/")

        else:
            return render_to_response("accounts/register.html",
                                      RequestContext(request, {"is_registration_page": True, "form": form}))

    else:
        return HttpResponseBadRequest()




def log_in(request):
    """ Allows user to log in """
    if request.method == "POST":
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

            next_url = request.POST.get("next_url", "/accounts/profile/")
            return HttpResponseRedirect(next_url)
        else:
            template_parameters = {"is_login_page": True, "username": username, "error_list": error_list}
            return render_to_response('accounts/login.html', RequestContext(request, template_parameters))
    else:
        next_url = request.GET.get("next")
        return render_to_response('accounts/login.html',
                                  RequestContext(request, {"is_login_page": True, "next_url": next_url}))




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

