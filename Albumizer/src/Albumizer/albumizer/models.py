# This Python file uses the following encoding: utf-8

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

class UserProfile(models.Model):
    """ Represents additional information about a single user. """

    GENDER_CHOICES = (
        (u"M", u"Male"),
        (u"F", u"Female")
    )

    user = models.OneToOneField(User)
    gender = models.CharField(
        max_length = 1,
        choices = GENDER_CHOICES
    )
    serviceConditionsAccepted = models.DateTimeField(
        auto_now_add = True,
        verbose_name = "date and time when service conditions were accepted"
    )
    homePhone = models.CharField(
        max_length = 20,
        blank = True,
        verbose_name = "home phone",
        help_text = "e.g. \"+358 44 123 4567\" (max. 20 characters)"
    )

    def __unicode__(self):
        return "%s %s (%s)" % (self.user.first_name, self.user.last_name, self.user.username)

    class Meta():
        ordering = ["user"]
        verbose_name = "user profile"
        verbose_name_plural = "user profiles"

def create_user_profile(sender, instance, created, **kwargs):
    """
        Post-save event handler to make sure that a new user profile is 
        created as soon as a new user is created to Django's user table.
    """
    if created:
        UserProfile.objects.create(user = instance)

post_save.connect(create_user_profile, sender = User)

class FacebookProfile(models.Model):
    userProfile=models.OneToOneField(
        UserProfile,
        related_name="facebookProfile"
    )
    
    facebookID = models.BigIntegerField(
        unique=True,
        verbose_name = "Facebook id"
    )
    
    token= models.TextField(
        blank=True,
        verbose_name="Facebook authentication token"
    )
    
    profileUrl=models.URLField(
        blank=True
    )
    
    lastQueryTime=models.DateTimeField(
        null=True
    )
    rawResponse=models.TextField(
        blank=True,
        verbose_name="raw response from facebook"
    )
    
    def __unicode__(self):
        return self.userProfile.__unicode__()
    
class Album(models.Model):
    """ Represents a single album. """
    owner = models.ForeignKey(User)
    title = models.CharField(
       max_length = 255
    )
    description = models.TextField(
        blank = True
    )
    isPublic = models.BooleanField(
        verbose_name = "is public"
    )

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.owner)

    class Meta():
        unique_together = ("owner", "title")
        ordering = ["owner", "title"]
        verbose_name = "album"
        verbose_name_plural = "albums"




class Page(models.Model):
    """ Represents a single page. """
    album = models.ForeignKey(Album)
    pageNumber = models.IntegerField(
        verbose_name = "page number"
    )
    layoutID = models.CharField(
        max_length = 255,
        verbose_name = "layout id"
    )

    def __unicode__(self):
        return "%s, %s" % (self.album, self.pageNumber)

    class Meta():
        unique_together = ("album", "pageNumber")
        ordering = ["album", "pageNumber"]
        verbose_name = "page"
        verbose_name_plural = "pages"




class PageContent(models.Model):
    """ Represents a single piece of content in a placeholder. """
    page = models.ForeignKey(Page)
    placeHolderID = models.CharField(
        max_length = 255,
        verbose_name = "placeholder id"
    )
    content = models.CharField(
        max_length = 255
    )

    def __unicode__(self):
        return u"%s, %s, %s" % (self.page, self.placeHolderID, self.content)

    class Meta():
        unique_together = ("page", "placeHolderID")
        verbose_name = u"page content"
        verbose_name_plural = u"page contents"




class Country(models.Model):
    """ Represents a single country. """
    code = models.CharField(
        primary_key = True,
        max_length = 10,
        help_text = "see <a href=\"http://www.iso.org/iso/country_codes/iso_3166_code_lists.htm\" target=\"_new\">ISO 3166</a> " +
                    "for a list of countries and their codes"
    )
    name = models.CharField(
        unique = True,
        max_length = 100
    )

    def __unicode__(self):
        return self.name

    class Meta():
        ordering = ["name"]
        verbose_name = "country"
        verbose_name_plural = "countries"




class State(models.Model):
    """ Represents a single state, like Texas (and there are states in other countries than USA, too). """
    name = models.CharField(
        unique = True,
        max_length = 100
    )

    def __unicode__(self):
        return self.name

    class Meta():
        ordering = ["name"]
        verbose_name = "state"
        verbose_name_plural = "states"




class Address(models.Model):
    """ Represents a single address of a human (customer). """
    owner = models.ForeignKey(User)
    postAddressLine1 = models.CharField(
        max_length = 100,
        blank = True,
        verbose_name = "post address, line 1",
        help_text = "e.g. \"Kaislapolku 5 A 24\" (max. 100 characters)"
    )
    postAddressLine2 = models.CharField(
        max_length = 100,
        blank = True,
        verbose_name = "post address, line 2"
    )
    zipCode = models.CharField(
        # 10 digits is the maximum length for post codes globally according to Wikipedia
        max_length = 10,
        blank = True,
        verbose_name = "zip code",
        help_text = "e.g. \"05100\" (max. 10 characters)"
    )
    city = models.CharField(
        max_length = 50,
        blank = True,
        help_text = "e.g. \"Tampere\" or \"Stockholm\" (max. 50 characters)"
    )
    state = models.ForeignKey(
        State,
        blank = True,
        null = True,
        help_text = "only for customers from USA, Australia and Brazil"
    )
    country = models.ForeignKey(
        Country,
        blank = True,
        null = True
    )

    def __unicode__(self):
        output = str(self.owner)

        if self.postAddressLine1:
            if output:
                output += ", "
            output += self.postAddressLine1
        if self.city:
            if output:
                output += ", "
            output += self.city
        if self.state:
            if output:
                output += ", "
            output += self.state.name
        if self.country:
            if output:
                output += ", "
            output += self.country.name

        return output

    class Meta():
        ordering = ["owner", "postAddressLine1"]
        verbose_name = "address"
        verbose_name_plural = "addresses"




class Order(models.Model):
    """ Represents a single order (containing many albums) as a whole. """
    orderer = models.ForeignKey(User)
    purchaseDate = models.DateTimeField(
        auto_now_add = True,
        verbose_name = "purchase date"
    )
    status = models.IntegerField()

    def __unicode__(self):
        return "%s, %s" % (self.orderer, self.purchaseDate)

    class Meta():
        unique_together = ("orderer", "purchaseDate")
        ordering = ["orderer", "purchaseDate", "status"]
        verbose_name = "order"
        verbose_name_plural = "orders"




class OrderItem(models.Model):
    """ Represents a single item (line) in an order. """
    order = models.ForeignKey(Order)
    album = models.ForeignKey(Album)
    count = models.IntegerField()
    deliveryAddress = models.ForeignKey(
        Address,
        verbose_name = "delivery address"
    )

    def __unicode__(self):
        return "%s, %s, %s, %d piece(s)" % (self.order.orderer, self.order.purchaseDate,
                                            self.album.title, self.count)

    class Meta():
        unique_together = ("order", "album")
        ordering = ["order", "album"]
        verbose_name = "order item"
        verbose_name_plural = "order items"




