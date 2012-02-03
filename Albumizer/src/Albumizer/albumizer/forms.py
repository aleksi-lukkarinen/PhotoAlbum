# This Python file uses the following encoding: utf-8
import copy
import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList, ErrorDict
from models import Address, Album, Country, UserProfile, Order, OrderItem, Page, PageContent, State




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




REGISTRATION_FORM_ERR_USERID_MISSING = u'Please enter a user id you would like to use.'
REGISTRATION_FORM_ERR_PASSWORD_MISSING = u'Please enter a password you would like to use.'
ERR_FIRST_NAME_MISSING = u'Please enter your first name.'
ERR_LAST_NAME_MISSING = u'Please enter your last name.'
ERR_GENDER_MISSING = u'Please enter your gender.'
ERR_EMAIL_MISSING = u'Please enter a real email address you are using.'

RE_VALID_USER_ID = re.compile("^[A-Za-z0-9_]*[A-Za-z0-9][A-Za-z0-9_]*$")
RE_VALID_PHONE_NUMBER = re.compile("^\+?[ 0-9]+$")

class RegistrationForm(CommonAlbumizerForm):
    """ Form class representing registration form used to add new users to database. """
    txtUserId = forms.CharField(
        min_length = 5,
        max_length = 30,
        label = "User ID",
        widget = forms.TextInput(attrs = {'size':'30'}),
        error_messages = {'required': (REGISTRATION_FORM_ERR_USERID_MISSING)},
        help_text = "e.g. \"lmikkola\" (5 - 30 letters A-Z, numbers 0-9 and underscores, min. 1 letter or number)"
    )
    txtPassword = forms.CharField(
        min_length = 8,
        max_length = 50,
        label = "Password",
        widget = forms.PasswordInput(attrs = {'size':'50'}),
        error_messages = {'required': (REGISTRATION_FORM_ERR_PASSWORD_MISSING)},
        help_text = "8 - 50 characters"
    )
    txtPasswordAgain = forms.CharField(
        required = False,
        label = "Re-Enter Password",
        widget = forms.PasswordInput(attrs = {'size':'50'})
    )

    txtFirstName = forms.CharField(
        max_length = 30,
        label = "First Name",
        widget = forms.TextInput(attrs = {'size':'30'}),
        error_messages = {'required': (ERR_FIRST_NAME_MISSING)},
        help_text = "e.g. \"Terhi-Anneli\" or \"Derek\" (max. 30 characters)"
    )
    txtLastName = forms.CharField(
        max_length = 30,
        label = "Last Name",
        error_messages = {'required': (ERR_LAST_NAME_MISSING)},
        help_text = "e.g. \"Virtanen-Kulmala\" or \"Smith\" (max. 30 characters)"
    )
    radGender = forms.ChoiceField(
        label = "Gender",
        choices = UserProfile.GENDER_CHOICES,
        error_messages = {'required': (ERR_GENDER_MISSING)},
        widget = forms.RadioSelect
    )
    txtEmail = forms.EmailField(
        max_length = 100,
        label = "Email",
        widget = forms.TextInput(attrs = {'size':'50'}),
        error_messages = {'required': (ERR_EMAIL_MISSING)},
        help_text = "real address like \"matti.virtanen@company.com\" (max. 100 characters)"
    )
    txtEmailAgain = forms.CharField(
        required = False,
        label = "Re-Enter Email",
        widget = forms.TextInput(attrs = {'size':'50'})
    )
    txtHomePhone = forms.CharField(
        required = False,
        max_length = 20,
        widget = forms.TextInput(attrs = {'size':'20'}),
        label = "Home Phone",
        help_text = "e.g. \"+358 44 123 4567\" (max. 20 characters)"
    )

    txtPostAddress1 = forms.CharField(
        required = False,
        max_length = 100,
        widget = forms.TextInput(attrs = {'size':'50'}),
        label = "Postal Address, Line 1",
        help_text = "e.g. \"Kaislapolku 5 A 24\" (max. 100 characters)"
    )
    txtPostAddress2 = forms.CharField(
        required = False,
        max_length = 100,
        widget = forms.TextInput(attrs = {'size':'50'}),
        label = "Postal Address, Line 2"
    )
    txtZipCode = forms.CharField(
        required = False,
        max_length = 10,
        widget = forms.TextInput(attrs = {'size':'10'}),
        label = "ZIP Code",
        help_text = "e.g. \"05100\" (max. 10 characters)"
    )
    txtCity = forms.CharField(
        required = False,
        max_length = 50,
        widget = forms.TextInput(attrs = {'size':'30'}),
        label = "City",
        help_text = "e.g. \"Tampere\" or \"Stockholm\" (max. 50 characters)"
    )
    cmbState = forms.ModelChoiceField(
        required = False,
        queryset = State.objects.all(),
        widget = forms.Select(),
        label = "State",
        help_text = "only for customers from USA, Australia and Brazil"
    )
    cmbCountry = forms.ModelChoiceField(
        required = False,
        queryset = Country.objects.all(),
        widget = forms.Select(),
        label = "Country"
    )

    chkServiceConditionsAccepted = forms.BooleanField(
        label = "I Hereby Accept the Terms and Conditions and the Privacy Policy of the Albumizer Service",
        error_messages = {'required': (u'This service cannot be used without accepting the Terms and Conditions.')}
    )


    def clean_txtUserId(self):
        """ Ensure that given userid is valid and that no user with that userid does already exist """
        userid = self.cleaned_data.get("txtUserId")
        if not userid:
            raise ValidationError(REGISTRATION_FORM_ERR_USERID_MISSING)

        userid = userid.strip()
        if not re.match(RE_VALID_USER_ID, userid):
            raise ValidationError("User id can contain only letters A-Z, numbers 0-9 and underscores.")

        if User.objects.filter(username__exact = userid):
            raise ValidationError("This user id is already reserved. Please try another one.")

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
            raise ValidationError("Unknown value as a gender.")

        return gender


    def clean_txtEmail(self):
        """ Trim the first email address. """
        email = self.cleaned_data.get("txtEmail")
        if not email:
            raise ValidationError(ERR_EMAIL_MISSING)

        email = email.strip()
        if not email:
            raise ValidationError(ERR_EMAIL_MISSING)

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
            if not re.match(RE_VALID_PHONE_NUMBER, homephone):
                raise ValidationError("Phone number can contain only numbers 0-9 and spaces, " +
                                      "and it may begin with a plus character.")

        return homephone


    def clean(self):
        """ Ensure that the two password are equal and that the two email addresses are equal. """
        cleaned_data = self.cleaned_data
        errors = self._errors

        if not errors.get("txtEmail"):
            email1 = cleaned_data.get("txtEmail")
            email2 = cleaned_data.get("txtEmailAgain")

            if email1 != email2:
                error_message = ("The email fields did not contain the same address. " +
                                "Make sure the address is written correctly.")

                error_list = errors.get("txtEmailAgain")
                if not error_list:
                    error_list = ErrorList()

                error_list.append(error_message)
                errors["txtEmailAgain"] = error_list

        if not errors.get("txtPassword"):
            password1 = cleaned_data.get("txtPassword")
            password2 = cleaned_data.get("txtPasswordAgain")

            if password1 != password2:
                error_message = ("The password fields did not contain the same password. " +
                                "Make sure the password is written correctly.")

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
        label = "Title",
        widget = forms.TextInput(attrs = {'size':'50'}),
        error_messages = {'required': (ERR_ALBUM_TITLE_MISSING)},
        help_text = "e.g. \"Holiday Memories\" or \"Dad's Birthday\" (max. 255 characters)"
    )
    txtAlbumDescription = forms.CharField(
        required = False,
        max_length = 255,
        label = "Description",
        widget = forms.Textarea(attrs = {'cols':'80', 'rows': '4'}),
        help_text = "Please descripbe the content of your new album (max. 255 characters)"
    )
    chkPublicAlbum = forms.BooleanField(
        required = False,
        label = "Album is Public",
        help_text = "If album is declared as a public one, it will be visible for everybody to browse"
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
        if Album.objects.filter(owner = current_user, title = album_title):
            raise ValidationError("You cannot have two albums with the same name. Please change the name to something different.")

        return album_title




LOGIN_FORM_ERR_USERID_MISSING = u'Please enter your user name.'

class LoginForm(CommonAlbumizerForm):
    """ Form class representing login form. """
    txtLoginUserName = forms.CharField(
        label = "User Name",
        widget = forms.TextInput(attrs = {'size':'50'}),
        error_messages = {'required': LOGIN_FORM_ERR_USERID_MISSING}
    )
    txtLoginPassword = forms.CharField(
        label = "Password",
        widget = forms.PasswordInput(attrs = {'size':'50'}),
        error_messages = {'required': (u'Please enter your password.')}
    )

    def clean_txtLoginUserName(self):
        """ Trim the user id. """
        username = self.cleaned_data.get("txtLoginUserName")
        if not username:
            raise ValidationError(LOGIN_FORM_ERR_USERID_MISSING)

        username = username.strip()
        if not username:
            raise ValidationError(LOGIN_FORM_ERR_USERID_MISSING)

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
                raise ValidationError("Wrong user name and/or password. Make sure they are correctly entered. Is your CAPS LOCK accidentally on?")

        return self.cleaned_data
















