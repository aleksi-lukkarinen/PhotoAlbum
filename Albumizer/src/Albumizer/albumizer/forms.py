# This Python file uses the following encoding: utf-8

import copy, re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.forms import BoundField, NON_FIELD_ERRORS
from django.forms.util import ErrorList, ErrorDict
from django.forms.widgets import Input
from django.forms import ModelForm
from models import UserProfile, Album, Layout, Country, State, Address, ShoppingCartItem




CHECKOUT_ERR_MSG_INVALID_HASH = \
    "User and/or content of the shopping cart have changed since the beginning of the checkout process, " + \
    "or phases of the checkout process have been tried to perform in wrong order. Please start again " + \
    "from the Shopping Cart."

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




class CommonAlbumizerBaseForm(forms.BaseForm):
    """  """

    error_css_class = 'error'
    required_css_class = 'required'


    def __init__(self, *args, **kwargs):
        """ override default label suffix """
        kwargs["label_suffix"] = kwargs.get("label_suffix", '')
        super(CommonAlbumizerBaseForm, self).__init__(*args, **kwargs)

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




class CommonAlbumizerForm(CommonAlbumizerBaseForm, forms.Form):
    """ Superclass for all standard Albumizer forms for implementing common features. """




REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING = u'Please enter a username you would like to use.'
REGISTRATION_FORM_ERR_MSG_FIRST_PASSWORD_MISSING = u'Please enter a password you would like to use.'
REGISTRATION_FORM_ERR_MSG_SECOND_PASSWORD_MISSING = u'Please re-enter the password you would like to use.'
REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING = u'Please enter your first name.'
REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING = u'Please enter your last name.'
REGISTRATION_FORM_ERR_MSG_GENDER_MISSING = u'Please enter your gender.'
REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING = u'Please enter a real email address you are using.'
REGISTRATION_FORM_ERR_MSG_SECOND_EMAIL_MISSING = u'Please re-enter the email address you are using.'
REGISTRATION_FORM_ERR_MSG_TERMS_AND_CONDITIONS_NOT_ACCEPTED = \
    u'This service cannot be used without accepting the Terms and Conditions.'

RE_VALID_USER_ID = "^[A-Za-z0-9_]*[A-Za-z0-9][A-Za-z0-9_]*$"
COMPILED_RE_VALID_USER_ID = re.compile(RE_VALID_USER_ID)

RE_VALID_PHONE_NUMBER = "^\+?[ 0-9]+$"
COMPILED_RE_VALID_PHONE_NUMBER = re.compile(RE_VALID_PHONE_NUMBER)

#read-only widget from http://lazypython.blogspot.com/2008/12/building-read-only-field-in-django.html
from django.forms.util import flatatt
from django.utils.html import escape

from django.utils.safestring import mark_safe

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs):
        final_attrs = self.build_attrs(attrs, name = name)
        if hasattr(self, 'initial'):
            value = self.initial
        return mark_safe(u"<span %s>%s</span>" % (flatatt(final_attrs), escape(value) or ''))

    def _has_changed(self, initial, data):
        return False

class ReadOnlyField(forms.Field):
    widget = ReadOnlyWidget
    def __init__(self, widget = None, label = None, initial = None, help_text = None):
        super(type(self), self).__init__(self, label = label, initial = initial,
            help_text = help_text, widget = widget)
        self.widget.initial = initial

    def clean(self, value):
        return self.widget.initial

class UserAuthForm(CommonAlbumizerBaseForm, ModelForm):

    username = forms.CharField(
        min_length = 5,
        max_length = 30,
        label = u"Username",
        widget = forms.TextInput(attrs = {
            'size': '30',
            'pattern': RE_VALID_USER_ID,
            'required': 'required',
            'autofocus': 'autofocus',
            'title': REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING)},
        help_text = u"e.g. \"lmikkola\" (5 - 30 letters A-Z, numbers 0-9 and underscores, min. 1 letter or number)"
    )
    first_name = forms.CharField(
        max_length = 30,
        label = u"First Name",
        widget = forms.TextInput(attrs = {
            'size':'30',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING)},
        help_text = u"e.g. \"Terhi-Anneli\" or \"Derek\" (max. 30 characters)"
    )
    last_name = forms.CharField(
        max_length = 30,
        label = u"Last Name",
        widget = forms.TextInput(attrs = {
            'size':'30',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING)},
        help_text = u"e.g. \"Virtanen-Kulmala\" or \"Smith\" (max. 30 characters)"
    )
    password = forms.CharField(
        min_length = 8,
        max_length = 50,
        label = u"Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_FIRST_PASSWORD_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_FIRST_PASSWORD_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_FIRST_PASSWORD_MISSING)},
        help_text = u"8 - 50 characters"
    )
    txtPasswordAgain = forms.CharField(
        required = True,
        label = u"Re-Enter Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_SECOND_PASSWORD_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_SECOND_PASSWORD_MISSING
        })
    )

    email = forms.EmailField(
        max_length = 100,
        label = u"Email",
        widget = AlbumizerEmailInput(attrs = {
            'size':'50',
            'required': 'required',
            'placeholder': 'firstname.lastname@domain',
            'title': REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING)},
        help_text = u"real address like \"matti.virtanen@company.com\" (max. 100 characters)"
    )
    txtEmailAgain = forms.CharField(
        label = u"Re-Enter Email",
        widget = AlbumizerEmailInput(attrs = {
            'size':'50',
            'required': 'required',
            'placeholder': 'firstname.lastname@domain',
            'title': REGISTRATION_FORM_ERR_MSG_SECOND_EMAIL_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_SECOND_EMAIL_MISSING
        })
    )
    def save(self, commit = True):

        #must override default behavior when setting password
        user = super(UserAuthForm, self).save(commit = False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    def clean_username(self):
        """ Ensure that given userid is valid and that no user with that userid does already exist """
        userid = self.cleaned_data.get("username")
        if not userid:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING)

        userid = userid.strip()
        if not re.match(COMPILED_RE_VALID_USER_ID, userid):
            raise ValidationError(u"User name can contain only letters A-Z, numbers 0-9 and underscores.")

        if User.objects.filter(username__exact = userid):
            raise ValidationError(u"This user name is already reserved. Please try another one.")

        return userid
    def clean(self):
        """ Ensure that the two password are equal and that the two email addresses are equal. """
        cleaned_data = self.cleaned_data
        errors = self._errors


        if not errors.get("email") and self.fields.get("txtEmailAgain", "") <> "":
            email1 = cleaned_data.get("email")
            email2 = cleaned_data.get("txtEmailAgain")

            if email1 != email2:
                error_message = (u"The email fields did not contain the same address. " +
                                 u"Make sure the address is written correctly.")

                error_list = errors.get("txtEmailAgain")
                if not error_list:
                    error_list = ErrorList()

                error_list.append(error_message)
                errors["txtEmailAgain"] = error_list

        if not errors.get("password"):
            password1 = cleaned_data.get("password")
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
    class Meta:
        model = User
        fields = ('username', 'password', 'txtPasswordAgain', 'first_name', 'last_name', 'email', 'txtEmailAgain')

class EditUserAuthForm(UserAuthForm):

    username = forms.CharField(
        required = False,
        min_length = 5,
        max_length = 30,
        label = u"Username",
        widget = ReadOnlyWidget(),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING)},
        help_text = u""
    )
    def __init__(self, *args, **kwargs):
        #some modifications to the super class
        #this is done in __init__ so the fields don't have to be copy-pasted as members in this class
        super(EditUserAuthForm, self).__init__(*args, **kwargs)
        self.fields["password"].required = False
        del self.fields["password"].widget.attrs["required"]
        self.fields["txtPasswordAgain"].required = False
        del self.fields["txtPasswordAgain"].widget.attrs["required"]
        del self.fields["txtEmailAgain"]

    def clean_username(self):
        return self.instance.username if self.instance else self.fields["username"]
    class Meta(UserAuthForm.Meta):
        pass

class UserProfileForm(CommonAlbumizerBaseForm, ModelForm):
    gender = forms.ChoiceField(
        label = u"Gender",
        choices = UserProfile.GENDER_CHOICES,
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_GENDER_MISSING)},
        widget = forms.RadioSelect(attrs = {
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_GENDER_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_GENDER_MISSING
        })
    )
    class Meta:
        model = UserProfile
        exclude = ('user',)

class AddressModelForm(CommonAlbumizerBaseForm, ModelForm):
    class Meta:
        model = Address
        exclude = ('owner',)

class RegistrationModelForm(CommonAlbumizerForm):
    chkServiceConditionsAccepted = forms.BooleanField(
        widget = forms.CheckboxInput(attrs = {
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_TERMS_AND_CONDITIONS_NOT_ACCEPTED,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_TERMS_AND_CONDITIONS_NOT_ACCEPTED
        }),
        label = u"I Hereby Accept the Terms and Conditions and the Privacy Policy of the Albumizer Service",
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_TERMS_AND_CONDITIONS_NOT_ACCEPTED)}
    )

class UserInformationForm(CommonAlbumizerForm):
    txtUserName = forms.CharField(
        min_length = 5,
        max_length = 30,
        label = u"Username",
        widget = forms.TextInput(attrs = {
            'size': '30',
            'pattern': RE_VALID_USER_ID,
            'required': 'required',
            'autofocus': 'autofocus',
            'title': REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING)},
        help_text = u"e.g. \"lmikkola\" (5 - 30 letters A-Z, numbers 0-9 and underscores, min. 1 letter or number)"
    )
    txtPassword = forms.CharField(
        min_length = 8,
        max_length = 50,
        label = u"Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_FIRST_PASSWORD_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_FIRST_PASSWORD_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_FIRST_PASSWORD_MISSING)},
        help_text = u"8 - 50 characters"
    )
    txtPasswordAgain = forms.CharField(
        required = False,
        label = u"Re-Enter Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_SECOND_PASSWORD_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_SECOND_PASSWORD_MISSING
        })
    )

    txtFirstName = forms.CharField(
        max_length = 30,
        label = u"First Name",
        widget = forms.TextInput(attrs = {
            'size':'30',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING)},
        help_text = u"e.g. \"Terhi-Anneli\" or \"Derek\" (max. 30 characters)"
    )
    txtLastName = forms.CharField(
        max_length = 30,
        label = u"Last Name",
        widget = forms.TextInput(attrs = {
            'size':'30',
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING)},
        help_text = u"e.g. \"Virtanen-Kulmala\" or \"Smith\" (max. 30 characters)"
    )
    radGender = forms.ChoiceField(
        label = u"Gender",
        choices = UserProfile.GENDER_CHOICES,
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_GENDER_MISSING)},
        widget = forms.RadioSelect(attrs = {
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_GENDER_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_GENDER_MISSING
        })
    )
    txtEmail = forms.EmailField(
        max_length = 100,
        label = u"Email",
        widget = AlbumizerEmailInput(attrs = {
            'size':'50',
            'required': 'required',
            'placeholder': 'firstname.lastname@domain',
            'title': REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING
        }),
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING)},
        help_text = u"real address like \"matti.virtanen@company.com\" (max. 100 characters)"
    )
    txtEmailAgain = forms.CharField(
        required = False,
        label = u"Re-Enter Email",
        widget = AlbumizerEmailInput(attrs = {
            'size':'50',
            'required': 'required',
            'placeholder': 'firstname.lastname@domain',
            'title': REGISTRATION_FORM_ERR_MSG_SECOND_EMAIL_MISSING,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_SECOND_EMAIL_MISSING
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


    def clean_txtUserName(self):
        """ Ensure that given userid is valid and that no user with that userid does already exist """
        userid = self.cleaned_data.get("txtUserName")
        if not userid:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_USERNAME_MISSING)

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
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING)

        firstname = firstname.strip()
        if not firstname:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_FIRST_NAME_MISSING)

        return firstname


    def clean_txtLastName(self):
        """ Trim the last name. """
        lastname = self.cleaned_data.get("txtLastName")
        if not lastname:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING)

        lastname = lastname.strip()
        if not lastname:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_LAST_NAME_MISSING)

        return lastname


    def clean_radGender(self):
        gender = self.cleaned_data.get("radGender")
        if not gender:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_GENDER_MISSING)

        if not gender in ('M', 'F'):
            raise ValidationError(u"Unknown value as a gender.")

        return gender


    def clean_txtEmail(self):
        """ Trim the first email address. """
        email = self.cleaned_data.get("txtEmail")
        if not email:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING)

        email = email.strip()
        if not email:
            raise ValidationError(REGISTRATION_FORM_ERR_MSG_FIRST_EMAIL_MISSING)

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

class AddressForm(CommonAlbumizerForm):

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

class RegistrationForm(UserInformationForm, AddressForm):
    """ Form class representing registration form used to add new users to database. """


    chkServiceConditionsAccepted = forms.BooleanField(
        widget = forms.CheckboxInput(attrs = {
            'required': 'required',
            'title': REGISTRATION_FORM_ERR_MSG_TERMS_AND_CONDITIONS_NOT_ACCEPTED,
            'x-moz-errormessage': REGISTRATION_FORM_ERR_MSG_TERMS_AND_CONDITIONS_NOT_ACCEPTED
        }),
        label = u"I Hereby Accept the Terms and Conditions and the Privacy Policy of the Albumizer Service",
        error_messages = {'required': (REGISTRATION_FORM_ERR_MSG_TERMS_AND_CONDITIONS_NOT_ACCEPTED)}
    )



ALBUM_CREATION_ERR_MSG_ALBUM_TITLE_MISSING = u'Please enter a title for the new album.'

class AlbumCreationForm(CommonAlbumizerForm):
    """ Form class representing album creation form used to add new albums to database. """
    txtAlbumTitle = forms.CharField(
        max_length = 255,
        min_length = 5,
        label = u"Title",
        widget = forms.TextInput(attrs = {
            'size':'50',
            'required': 'required',
            'autofocus': 'autofocus',
            'title': ALBUM_CREATION_ERR_MSG_ALBUM_TITLE_MISSING,
            'x-moz-errormessage': ALBUM_CREATION_ERR_MSG_ALBUM_TITLE_MISSING
        }),
        error_messages = {'required': ALBUM_CREATION_ERR_MSG_ALBUM_TITLE_MISSING},
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
            raise ValidationError(ALBUM_CREATION_ERR_MSG_ALBUM_TITLE_MISSING)

        album_title = album_title.strip()
        if not album_title:
            raise ValidationError(ALBUM_CREATION_ERR_MSG_ALBUM_TITLE_MISSING)

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
            'required': 'required',
            'autofocus': 'autofocus',
            'title': LOGIN_FORM_ERR_USERNAME_MISSING,
            'x-moz-errormessage': LOGIN_FORM_ERR_USERNAME_MISSING
        }),
        error_messages = {'required': LOGIN_FORM_ERR_USERNAME_MISSING}
    )
    txtLoginPassword = forms.CharField(
        label = u"Password",
        widget = forms.PasswordInput(attrs = {
            'size':'50',
            'required': 'required',
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
    """  """
    chcPageLayout = forms.ModelChoiceField(
        queryset = '',
        empty_label = None,
        label = u'Layout',
        help_text = u'Select layout for page'
    )

    def __init__(self, *args, **kwargs):
        super(AddPageForm, self).__init__(*args, **kwargs)
        layouts = Layout.objects.all()
        self.fields['chcPageLayout'].queryset = layouts




class EditPageForm(CommonAlbumizerForm):
    """  """

    def __init__(self, page, *args, **kwargs):
        """ This makes it possible to pass the page object to this object as a constructor parameter. """
        captions = page.layout.textFieldCount
        images = page.layout.imageFieldCount
        super(EditPageForm, self).__init__(*args, **kwargs)

        for i in range(1, captions + 1):
            self.fields['txtCaption_%s' % i] = forms.CharField(label = u'%s. Caption' % i, required = False)

        for i in range(1, images + 1):
            self.fields['imgUpload_%s' % i] = forms.ImageField(label = u'%s. Image' % i, required = False)




class DeliveryAddressChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        label = u"%s %s" % (obj.owner.first_name, obj.owner.last_name)

        if obj.postAddressLine1:
            label += u", %s" % obj.postAddressLine1

        if obj.postAddressLine2:
            label += u", %s" % obj.postAddressLine2

        if obj.zipCode:
            label += u", %s" % obj.zipCode

        if obj.city:
            label += u", %s" % obj.city

        if obj.state:
            label += u", %s" % unicode(obj.state)

        if obj.country:
            label += u", %s" % unicode(obj.country)

        return label




def build_delivery_address_form(request):
    """ Builds a form class representing form asking for delivery addresses for items of an order. """

    def init(self, *args, **kwargs):
        kwargs["initial"] = self.__initial
        super(self.__class__, self).__init__(*args, **kwargs)

    def has_items(self):
        """ Returns True if there are items which to choose addresses for. """
        return self.__items.exists()

    def has_addresses(self):
        """ Returns True if there are addresses which to choose from. """
        return self.__addresses.exists()

    def get_address_fields(self):
        """ Iterates through all address field_dict in form. """
        for name in self.__address_fields:
            yield BoundField(self, self.__address_fields[name], name)

    def get_item_address_pairs(self):
        """ Iterates through all (order items / address) pairs displayed on the form. """
        for field_name in self.__address_fields:
            yield (self.__items.get(id__exact = field_name.split("_")[1]),
                   self.cleaned_data.get(field_name))

    def clean_hdnValidationHash(self):
        """ Ensures that the validation hash gotten from sent form is correct. """
        given_hash = self.cleaned_data.get("hdnValidationHash")
        our_hash = ShoppingCartItem.validation_hash_for_shopping_cart(request)
        if not given_hash == our_hash:
            self.add_common_error(CHECKOUT_ERR_MSG_INVALID_HASH)

    items = ShoppingCartItem.items_of_user_with_albums_and_addresses(request.user)
    addresses = Address.addresses_of_user(request.user)
    validation_hash = ShoppingCartItem.validation_hash_for_shopping_cart(request)

    field_dict = {}
    address_field_dict = {}
    initial_value_dict = {}

    field_dict["hdnValidationHash"] = forms.CharField(
        widget = forms.HiddenInput()
    )
    initial_value_dict["hdnValidationHash"] = validation_hash

    for item in items:
        field_name = u"cmbAddress_" + unicode(item.id)

        new_field = DeliveryAddressChoiceField(
            queryset = addresses,
            empty_label = None,
            label = item.album.title
        )
        field_dict[field_name] = new_field
        address_field_dict[field_name] = new_field

        if item.deliveryAddress:
            initial_value_dict[field_name] = item.deliveryAddress

    members = {
        "__request": request,
        "__items": items,
        "__addresses": addresses,
        "__validation_hash": validation_hash,
        "base_fields": field_dict,
        "__address_fields": address_field_dict,
        "__initial": initial_value_dict,
        "has_items": has_items,
        "has_addresses": has_addresses,
        "address_fields": get_address_fields,
        "item_address_pairs": get_item_address_pairs,
        "clean_hdnValidationHash": clean_hdnValidationHash,
        "__init__": init
    }

    return type("DeliveryAddressForm", (CommonAlbumizerBaseForm,), members)


