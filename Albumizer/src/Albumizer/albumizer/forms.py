# This Python file uses the following encoding: utf-8

import copy
import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList, ErrorDict
from django.forms.widgets import Input
from models import UserProfile, FacebookProfile, Album, Layout, Page, PageContent, Country, State, \
        Address, ShoppingCartItem, Order, SPSPayment, OrderStatus, OrderItem



class AlbumizerEmailInput(Input):
    """ Input widget for emails with type according to html5. """
    input_type = 'email'




class AlbumizerURLInput(Input):
    """ Input widget for urls with type according to html5. """
    input_type = 'url'




class AlbumizerTelInput(Input):
    """ Input widget for telephone numbers with type according to html5. """
    input_type = 'tel'




class AlbumizerSearchCriteriaInput(Input):
    """ Input widget for search criteria with type according to html5. """
    input_type = 'search'




class CommonAlbumizerForm(forms.Form):
    """ Superclass for all Albumizer forms for implementing common features. """
    def add_common_error(self, error_string):
        """ Adds an error message, which is not related to any particular field. """
        if not error_string:
            return

        error_list = self._errors.get(NON_FIELD_ERRORS, ErrorList())
        error_list.append(error_string)
        self._errors[NON_FIELD_ERRORS] = error_list

    def field_errors(self):
        """ Returns a dictionary containing only field-related errors. """
        error_dict = copy.copy(self._errors)
        if not error_dict:
            error_dict = ErrorDict()
        if NON_FIELD_ERRORS in error_dict:
            del error_dict[NON_FIELD_ERRORS]
        return error_dict




REGISTRATION_FORM_ERR_USERNAME_MISSING = u'Please enter a username you would like to use.'
REGISTRATION_FORM_ERR_FIRST_PASSWORD_MISSING = u'Please enter a password you would like to use.'
REGISTRATION_FORM_ERR_SECOND_PASSWORD_MISSING = u'Please re-enter the password you would like to use.'
ERR_FIRST_NAME_MISSING = u'Please enter your first name.'
ERR_LAST_NAME_MISSING = u'Please enter your last name.'
ERR_GENDER_MISSING = u'Please enter your gender.'
ERR_FIRST_EMAIL_MISSING = u'Please enter a real email address you are using.'
ERR_SECOND_EMAIL_MISSING = u'Please re-enter the email address you are using.'
ERR_TERMS_AND_CONDITIONS_NOT_ACCEPTED = u'This service cannot be used without accepting the Terms and Conditions.'

RE_VALID_USER_ID = "^[A-Za-z0-9_]*[A-Za-z0-9][A-Za-z0-9_]*$"
COMPILED_RE_VALID_USER_ID = re.compile(RE_VALID_USER_ID)

RE_VALID_PHONE_NUMBER = "^\+?[ 0-9]+$"
COMPILED_RE_VALID_PHONE_NUMBER = re.compile(RE_VALID_PHONE_NUMBER)

class RegistrationForm(CommonAlbumizerForm):
    """ Form class representing registration form used to add new users to database. """
    txtUserName = forms.CharField(
        min_length = 5,
        max_length = 30,
        label = u"Username",
        widget = forms.TextInput(attrs = {
            'size': '30',
            'pattern': RE_VALID_USER_ID,
            'required': 'true',
            'autofocus': 'true',
            'title': REGISTRATION_FORM_ERR_USERNAME_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_USERNAME_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_USERNAME_MISSING)},
        help_text = u"e.g. \"lmikkola\" (5 - 30 letters A-Z, numbers 0-9 and underscores, min. 1 letter or number)"
    )
    txtPassword = forms.CharField(
        min_length = 8,
        max_length = 50,
        label = u"Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'true',
            'title': REGISTRATION_FORM_ERR_FIRST_PASSWORD_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_FIRST_PASSWORD_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_FIRST_PASSWORD_MISSING)},
        help_text = u"8 - 50 characters"
    )
    txtPasswordAgain = forms.CharField(
        required = False,
        label = u"Re-Enter Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'true',
            'title': REGISTRATION_FORM_ERR_SECOND_PASSWORD_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_SECOND_PASSWORD_MISSING
        })
    )

    txtFirstName = forms.CharField(
        max_length = 30,
        label = u"First Name",
        widget = forms.TextInput(attrs = {
            'size':'30',
            'required': 'true',
            'title': ERR_FIRST_NAME_MISSING,
            'x-moz-errormessage': ERR_FIRST_NAME_MISSING
        }),
        error_messages = {'required': (ERR_FIRST_NAME_MISSING)},
        help_text = u"e.g. \"Terhi-Anneli\" or \"Derek\" (max. 30 characters)"
    )
    txtLastName = forms.CharField(
        max_length = 30,
        label = u"Last Name",
        widget = forms.TextInput(attrs = {
            'size':'30',
            'required': 'true',
            'title': ERR_LAST_NAME_MISSING,
            'x-moz-errormessage': ERR_LAST_NAME_MISSING
        }),
        error_messages = {'required': (ERR_LAST_NAME_MISSING)},
        help_text = u"e.g. \"Virtanen-Kulmala\" or \"Smith\" (max. 30 characters)"
    )
    radGender = forms.ChoiceField(
        label = u"Gender",
        choices = UserProfile.GENDER_CHOICES,
        error_messages = {'required': (ERR_GENDER_MISSING)},
        widget = forms.RadioSelect(attrs = {
            'required': 'true',
            'title': ERR_GENDER_MISSING,
            'x-moz-errormessage': ERR_GENDER_MISSING
        })
    )
    txtEmail = forms.EmailField(
        max_length = 100,
        label = u"Email",
        widget = AlbumizerEmailInput(attrs = {
            'size':'50',
            'required': 'true',
            'placeholder': 'firstname.lastname@domain',
            'title': ERR_FIRST_EMAIL_MISSING,
            'x-moz-errormessage': ERR_FIRST_EMAIL_MISSING
        }),
        error_messages = {'required': (ERR_FIRST_EMAIL_MISSING)},
        help_text = u"real address like \"matti.virtanen@company.com\" (max. 100 characters)"
    )
    txtEmailAgain = forms.CharField(
        required = False,
        label = u"Re-Enter Email",
        widget = AlbumizerEmailInput(attrs = {
            'size':'50',
            'required': 'true',
            'placeholder': 'firstname.lastname@domain',
            'title': ERR_SECOND_EMAIL_MISSING,
            'x-moz-errormessage': ERR_SECOND_EMAIL_MISSING
        })
    )
    txtHomePhone = forms.CharField(
        required = False,
        max_length = 20,
        widget = AlbumizerTelInput(attrs = {
            'size':'20',
            'pattern': RE_VALID_PHONE_NUMBER
        }),
        label = u"Home Phone",
        help_text = u"e.g. \"+358 44 123 4567\" (max. 20 characters)"
    )

    txtPostAddress1 = forms.CharField(
        required = False,
        max_length = 100,
        widget = forms.TextInput(attrs = {'size':'50'}),
        label = u"Postal Address, Line 1",
        help_text = u"e.g. \"Kaislapolku 5 A 24\" (max. 100 characters)"
    )
    txtPostAddress2 = forms.CharField(
        required = False,
        max_length = 100,
        widget = forms.TextInput(attrs = {'size':'50'}),
        label = u"Postal Address, Line 2"
    )
    txtZipCode = forms.CharField(
        required = False,
        max_length = 10,
        widget = forms.TextInput(attrs = {'size':'10'}),
        label = u"ZIP Code",
        help_text = u"e.g. \"05100\" (max. 10 characters)"
    )
    txtCity = forms.CharField(
        required = False,
        max_length = 50,
        widget = forms.TextInput(attrs = {'size':'30'}),
        label = u"City",
        help_text = u"e.g. \"Tampere\" or \"Stockholm\" (max. 50 characters)"
    )
    cmbState = forms.ModelChoiceField(
        required = False,
        queryset = State.objects.all(),
        widget = forms.Select(),
        label = u"State",
        help_text = u"only for customers from USA, Australia and Brazil"
    )
    cmbCountry = forms.ModelChoiceField(
        required = False,
        queryset = Country.objects.all(),
        widget = forms.Select(),
        label = u"Country"
    )

    chkServiceConditionsAccepted = forms.BooleanField(
        widget = forms.CheckboxInput(attrs = {
            'required': 'true',
            'title': ERR_TERMS_AND_CONDITIONS_NOT_ACCEPTED,
            'x-moz-errormessage': ERR_TERMS_AND_CONDITIONS_NOT_ACCEPTED
        }),
        label = u"I Hereby Accept the Terms and Conditions and the Privacy Policy of the Albumizer Service",
        error_messages = {'required': (ERR_TERMS_AND_CONDITIONS_NOT_ACCEPTED)}
    )


    def clean_txtUserName(self):
        """ Ensure that given userid is valid and that no user with that userid does already exist """
        userid = self.cleaned_data.get("txtUserName")
        if not userid:
            raise ValidationError(REGISTRATION_FORM_ERR_USERNAME_MISSING)

        userid = userid.strip()
        if not re.match(COMPILED_RE_VALID_USER_ID, userid):
            raise ValidationError(u"User name can contain only letters A-Z, numbers 0-9 and underscores.")

        if User.objects.filter(username__exact = userid):
            raise ValidationError(u"This user name is already reserved. Please try another one.")

        return userid


    def clean_txtFirstName(self):
        """ Trim the first name. """
        firstname = self.cleaned_data.get("txtFirstName")
        if not firstname:
            raise ValidationError(ERR_FIRST_NAME_MISSING)

        firstname = firstname.strip()
        if not firstname:
            raise ValidationError(ERR_FIRST_NAME_MISSING)

        return firstname


    def clean_txtLastName(self):
        """ Trim the last name. """
        lastname = self.cleaned_data.get("txtLastName")
        if not lastname:
            raise ValidationError(ERR_LAST_NAME_MISSING)

        lastname = lastname.strip()
        if not lastname:
            raise ValidationError(ERR_LAST_NAME_MISSING)

        return lastname


    def clean_radGender(self):
        gender = self.cleaned_data.get("radGender")
        if not gender:
            raise ValidationError(ERR_GENDER_MISSING)

        if not gender in ('M', 'F'):
            raise ValidationError(u"Unknown value as a gender.")

        return gender


    def clean_txtEmail(self):
        """ Trim the first email address. """
        email = self.cleaned_data.get("txtEmail")
        if not email:
            raise ValidationError(ERR_FIRST_EMAIL_MISSING)

        email = email.strip()
        if not email:
            raise ValidationError(ERR_FIRST_EMAIL_MISSING)

        return email


    def clean_txtEmailAgain(self):
        """ Trim the second email address. """
        email = self.cleaned_data.get("txtEmailAgain")

        if email:
            email = email.strip()

        return email


    def clean_txtHomePhone(self):
        """ Trim the home phone number and ensure that it is well-formed. """
        homephone = self.cleaned_data.get("txtHomePhone")

        if homephone:
            homephone = homephone.strip()
            if not re.match(COMPILED_RE_VALID_PHONE_NUMBER, homephone):
                raise ValidationError(u"Phone number can contain only numbers 0-9 and spaces, " +
                                      u"and it may begin with a plus character.")

        return homephone


    def clean(self):
        """ Ensure that the two password are equal and that the two email addresses are equal. """
        cleaned_data = self.cleaned_data
        errors = self._errors

        if not errors.get("txtEmail"):
            email1 = cleaned_data.get("txtEmail")
            email2 = cleaned_data.get("txtEmailAgain")

            if email1 != email2:
                error_message = (u"The email fields did not contain the same address. " +
                                 u"Make sure the address is written correctly.")

                error_list = errors.get("txtEmailAgain")
                if not error_list:
                    error_list = ErrorList()

                error_list.append(error_message)
                errors["txtEmailAgain"] = error_list

        if not errors.get("txtPassword"):
            password1 = cleaned_data.get("txtPassword")
            password2 = cleaned_data.get("txtPasswordAgain")

            if password1 != password2:
                error_message = (u"The password fields did not contain the same password. " +
                                 u"Make sure the password is written correctly.")

                error_list = errors.get("txtPasswordAgain")
                if not error_list:
                    error_list = ErrorList()

                error_list.append(error_message)
                errors["txtPasswordAgain"] = error_list

        self._errors = errors
        return cleaned_data




ERR_ALBUM_TITLE_MISSING = u'Please enter a title for the new album.'

class AlbumCreationForm(CommonAlbumizerForm):
    """ Form class representing album creation form used to add new albums to database. """
    txtAlbumTitle = forms.CharField(
        max_length = 255,
        min_length = 5,
        label = u"Title",
        widget = forms.TextInput(attrs = {
            'size':'50',
            'required': 'true',
            'autofocus': 'true',
            'title': ERR_ALBUM_TITLE_MISSING,
            'x-moz-errormessage': ERR_ALBUM_TITLE_MISSING
        }),
        error_messages = {'required': ERR_ALBUM_TITLE_MISSING},
        help_text = u"e.g. \"Holiday Memories\" or \"Dad's Birthday\" (5-255 characters)"
    )
    txtAlbumDescription = forms.CharField(
        required = False,
        max_length = 255,
        label = u"Description",
        widget = forms.Textarea(attrs = {'cols':'80', 'rows': '4'}),
        help_text = u"Please describe the content of your new album (max. 255 characters)"
    )
    chkPublicAlbum = forms.BooleanField(
        required = False,
        label = u"Album is Public",
        help_text = u"If album is declared as a public one, it will be visible for everybody to browse"
    )

    def __init__(self, request, *args, **kwargs):
        """ This makes it possible to pass the request object to this object as a constructor parameter. """
        self.request = request
        super(AlbumCreationForm, self).__init__(*args, **kwargs)

    def clean_txtAlbumTitle(self):
        """ 
            Trim the album name and ensure that there is no album
            with the same name and owned by the current user.
        """
        album_title = self.cleaned_data.get("txtAlbumTitle")
        if not album_title:
            raise ValidationError(ERR_ALBUM_TITLE_MISSING)

        album_title = album_title.strip()
        if not album_title:
            raise ValidationError(ERR_ALBUM_TITLE_MISSING)

        current_user = self.request.user
        if not self.request.POST.get("cmdEditAlbum"):
            if Album.objects.filter(owner = current_user, title = album_title):
                raise ValidationError(u"You cannot have two albums with the same name. " +
                                      u"Please change the name to something different.")

        return album_title




LOGIN_FORM_ERR_USERNAME_MISSING = u'Please enter your username.'
LOGIN_FORM_ERR_PASSWORD_MISSING = u'Please enter your password.'

class LoginForm(CommonAlbumizerForm):
    """ Form class representing login form. """
    txtLoginUserName = forms.CharField(
        label = u"Username",
        widget = forms.TextInput(attrs = {
            'size':'50',
            'required': 'true',
            'autofocus': 'true',
            'title': LOGIN_FORM_ERR_USERNAME_MISSING,
            'x-moz-errormessage': LOGIN_FORM_ERR_USERNAME_MISSING
        }),
        error_messages = {'required': LOGIN_FORM_ERR_USERNAME_MISSING}
    )
    txtLoginPassword = forms.CharField(
        label = u"Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'true',
            'title': LOGIN_FORM_ERR_PASSWORD_MISSING,
            'x-moz-errormessage': LOGIN_FORM_ERR_PASSWORD_MISSING
        }),
        error_messages = {'required': LOGIN_FORM_ERR_PASSWORD_MISSING}
    )

    def clean_txtLoginUserName(self):
        """ Trim the username. """
        username = self.cleaned_data.get("txtLoginUserName")
        if not username:
            raise ValidationError(LOGIN_FORM_ERR_USERNAME_MISSING)

        username = username.strip()
        if not username:
            raise ValidationError(LOGIN_FORM_ERR_USERNAME_MISSING)

        return username

    def clean(self):
        """ Ensure, that there is an user with the given user id and that the password is correct for that user. """
        username = self.cleaned_data.get("txtLoginUserName")
        password = self.cleaned_data.get("txtLoginPassword")

        user_candidate = None
        user_candidate_queryset = User.objects.filter(username__exact = username)
        if user_candidate_queryset:
            user_candidate = user_candidate_queryset[0]
        if not user_candidate or not user_candidate.check_password(password) or not user_candidate.is_active:
            if not self._errors:
                raise ValidationError(u"Wrong user name and/or password. Make sure they are correctly entered. " +
                                      u"Is your CAPS LOCK accidentally on?")

        return self.cleaned_data







class AddPageForm(CommonAlbumizerForm):
	chcPageLayout = forms.ModelChoiceField(
        queryset='',
        empty_label=None,
        label= u'Layout',
        help_text= u'Select layout for page'
    )

	def __init__(self, *args, **kwargs):
		super(AddPageForm, self).__init__(*args, **kwargs)
		layouts = Layout.objects.all()
		self.fields['chcPageLayout'].queryset = layouts
		
		
		
		
class EditPageForm(CommonAlbumizerForm):
    
    def __init__(self, page, *args, **kwargs):
        """ This makes it possible to pass the page object to this object as a constructor parameter. """
        captions = page.layout.textFieldCount
        images = page.layout.imageFieldCount
        super(EditPageForm, self).__init__(*args, **kwargs)
        
        for i in range(1,captions+1):
            self.fields['txtCaption_%s' % i] = forms.CharField(label= u'%s. Caption' % i, required = False)
            
        for i in range(1,images+1):
            self.fields['imgUpload_%s' % i] = forms.ImageField(label= u'%s. Image' % i, required = False)
