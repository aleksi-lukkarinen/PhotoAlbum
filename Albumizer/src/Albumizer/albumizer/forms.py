# This Python file uses the following encoding: utf-8

from django import forms


GENDER_CHOICES = (("m", "Male"), ("f", "Female"))




class RegistrationForm(forms.Form):
    """ Form class representing registration form used to add new users to database """
    txtUserId = forms.CharField(
        min_length = 5,
        max_length = 20,
        label = "User ID",
        help_text = "5 - 20 characters, like \"lmikkola\" "
    )
    txtPassword = forms.CharField(
        min_length = 10,
        max_length = 40,
        label = "Password",
        widget = forms.PasswordInput
    )
    txtPasswordAgain = forms.CharField(
        min_length = 10,
        max_length = 40,
        label = "Re-Enter Password",
        widget = forms.PasswordInput
    )

    txtFirstName = forms.CharField(
        max_length = 30,
        label = "First Name"
    )
    txtLastName = forms.CharField(
        max_length = 40,
        label = "Last Name"
    )
    radGender = forms.ChoiceField(
        label = "Gender",
        choices = GENDER_CHOICES,
        widget = forms.RadioSelect
    )
    txtEmail = forms.EmailField(
        max_length = 100,
        label = "Email"
    )
    txtEmailAgain = forms.EmailField(
        max_length = 100,
        label = "Re-Enter Email"
    )

    txtPostAddress1 = forms.CharField(
        required = False,
        max_length = 100,
        label = "Postal Address, Line 1"
    )
    txtPostAddress2 = forms.CharField(
        required = False,
        max_length = 100,
        label = "Postal Address, Line 2"
    )
    txtZipCode = forms.CharField(
        required = False,
        max_length = 10,
        label = "ZIP Code"
    )
    txtCity = forms.CharField(
        required = False,
        max_length = 50,
        label = "City"
    )
    txtCountry = forms.CharField(
        required = False,
        max_length = 100,
        label = "Country"
    )

    txtHomePhone = forms.CharField(
        required = False,
        max_length = 20,
        label = "Home Phone"
    )

    chkServiceConditionsAccepted = forms.BooleanField(
        label = "I Hereby Accept Terms and Conditions of Albumizer Service"
    )




