# This Python file uses the following encoding: utf-8

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList


GENDER_CHOICES = (("m", "Male"), ("f", "Female"))




class RegistrationForm(forms.Form):
    """ Form class representing registration form used to add new users to database """
    txtUserId = forms.CharField(
        min_length = 5,
        max_length = 30,
        label = "User ID",
        error_messages = {'required': (u'Please enter a user id you would like to use.')},
        help_text = "e.g. \"lmikkola\" (5 - 30 characters)"
    )
    txtPassword = forms.CharField(
        min_length = 8,
        max_length = 50,
        label = "Password",
        widget = forms.PasswordInput(attrs = {'size':'50'}),
        error_messages = {'required': (u'Please enter a password you would like to use.')},
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
        error_messages = {'required': (u'Your first name is a mandatory information.')},
        help_text = "e.g. \"Terhi-Anneli\" or \"Derek\" (max. 30 characters)"
    )
    txtLastName = forms.CharField(
        max_length = 30,
        label = "Last Name",
        error_messages = {'required': (u'Your last name is a mandatory information.')},
        help_text = "e.g. \"Virtanen-Kulmala\" or \"Smith\" (max. 30 characters)"
    )
    radGender = forms.ChoiceField(
        label = "Gender",
        choices = GENDER_CHOICES,
        error_messages = {'required': (u'Your gender is a mandatory information.')},
        widget = forms.RadioSelect
    )
    txtEmail = forms.EmailField(
        max_length = 100,
        label = "Email",
        widget = forms.TextInput(attrs = {'size':'50'}),
        error_messages = {'required': (u'Please enter a real email address you are using.')},
        help_text = "real address like \"matti.virtanen@company.com\" (max. 100 characters)"
    )
    txtEmailAgain = forms.CharField(
        required = False,
        label = "Re-Enter Email"
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
    txtCountry = forms.CharField(
        required = False,
        max_length = 100,
        widget = forms.TextInput(attrs = {'size':'30'}),
        label = "Country",
        help_text = "e.g. \"Danmark\" (max. 100 characters)"
    )

    txtHomePhone = forms.CharField(
        required = False,
        max_length = 20,
        widget = forms.TextInput(attrs = {'size':'20'}),
        label = "Home Phone",
        help_text = "e.g. \"+358 44 123 4567\" (max. 20 characters)"
    )

    chkServiceConditionsAccepted = forms.BooleanField(
        label = "I Hereby Accept Terms and Conditions of the Albumizer Service",
        error_messages = {'required': (u'This service cannot be used without accepting the Terms and Conditions.')}
    )


    def clean_txtUserId(self):
        """ Ensure that given userid is valid and that no user with that userid does already exist """
        userid = self.cleaned_data.get("txtUserId")

        if userid:
            userid = userid.strip()



        return userid


    def clean_txtEmail(self):
        """ Trim the first email address. """
        email = self.cleaned_data.get("txtEmail")

        if email:
            email = email.strip()

        return email


    def clean_txtEmailAgain(self):
        """ Trim the second email address. """
        email = self.cleaned_data.get("txtEmailAgain")

        if email:
            email = email.strip()

        return email


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

        if errors:
            raise ValidationError("Please correct the errors presented below.")

        return cleaned_data
