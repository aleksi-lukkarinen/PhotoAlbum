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
        verbose_name = u"date and time when service conditions were accepted"
    )
    homePhone = models.CharField(
        max_length = 20,
        blank = True,
        verbose_name = u"home phone",
        help_text = u"e.g. \"+358 44 123 4567\" (max. 20 characters)"
    )
    facebookID = models.CharField(
        max_length = 255,
        blank = True,
        verbose_name = u"Facebook id"
    )

    def __unicode__(self):
        return u"%s %s (%s)" % (self.user.first_name, self.user.last_name, self.user.username)

    class Meta():
        ordering = ["user"]
        verbose_name = u"user profile"
        verbose_name_plural = u"user profiles"


def create_user_profile(sender, instance, created, **kwargs):
    """
        Post-save event handler to make sure that a new user profile is 
        created as soon as a new user is created to Django's user table.
    """
    if created:
        profile = UserProfile(user = instance)
        profile.save()

post_save.connect(create_user_profile, sender = User, dispatch_uid = "albumizer-models-profile-creation")




class Album(models.Model):
    """ Represents a single album. """
    owner = models.ForeignKey(User)
    title = models.CharField(
        max_length = 255,
        help_text = u"e.g. \"Holiday Memories\" or \"Dad's Birthday\" (max. 255 characters)"
    )
    description = models.TextField(
        max_length = 255,
        blank = True,
        help_text = u"Please descripbe the content of your new album (max. 255 characters)"
    )
    isPublic = models.BooleanField(
        verbose_name = u"is public",
        help_text = u"If album is declared as a public one, it will be visible for everybody to browse"
    )
    creationDate = models.DateTimeField(
        auto_now_add = True,
        blank = True,
        null = True,
        verbose_name = u"creation date"
    )

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.owner)

    def is_owned_by(self, user):
        """ Checks if this album is owner by a given user """
        return user == self.owner

    def is_editable_to_user(self, user):
        """ Checks if this album is editable to a given user """
        return self.is_owned_by(user)

    def is_visible_to_user(self, user):
        """ Checks if this album is visible to a given user """
        return self.isPublic or self.is_owned_by(user)

    def is_hidden_from_user(self, user):
        """ Checks if this album is hidden from a given user """
        return not self.is_visible_to_user(user)

    @staticmethod
    def get_latest_public():
        """ Returns 20 latest publicly visible albums """
        return Album.objects.filter(isPublic__exact = True).order_by("-creationDate")[:20]


    class Meta():
        unique_together = ("owner", "title")
        ordering = ["owner", "title"]
        verbose_name = u"album"
        verbose_name_plural = u"albums"




class Page(models.Model):
    """ Represents a single page. """
    album = models.ForeignKey(Album)
    pageNumber = models.IntegerField(
        verbose_name = u"page number"
    )
    layoutID = models.CharField(
        max_length = 255,
        verbose_name = u"layout id"
    )

    def __unicode__(self):
        return u"%s, %s" % (self.album, self.pageNumber)

    class Meta():
        unique_together = ("album", "pageNumber")
        ordering = ["album", "pageNumber"]
        verbose_name = u"page"
        verbose_name_plural = u"pages"




class PageContent(models.Model):
    """ Represents a single piece of content in a placeholder. """
    page = models.ForeignKey(Page)
    placeHolderID = models.CharField(
        max_length = 255,
        verbose_name = u"placeholder id"
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
        help_text = u"see <a href=\"http://www.iso.org/iso/country_codes/iso_3166_code_lists.htm\" " +
                    u"target=\"_new\">ISO 3166</a> " +
                    u"for a list of countries and their codes"
    )
    name = models.CharField(
        unique = True,
        max_length = 100
    )

    def __unicode__(self):
        return self.name

    class Meta():
        ordering = ["name"]
        verbose_name = u"country"
        verbose_name_plural = u"countries"




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
        verbose_name = u"state"
        verbose_name_plural = u"states"




class Address(models.Model):
    """ Represents a single address of a human (customer). """
    owner = models.ForeignKey(User)
    postAddressLine1 = models.CharField(
        max_length = 100,
        blank = True,
        verbose_name = u"post address, line 1",
        help_text = u"e.g. \"Kaislapolku 5 A 24\" (max. 100 characters)"
    )
    postAddressLine2 = models.CharField(
        max_length = 100,
        blank = True,
        verbose_name = u"post address, line 2"
    )
    zipCode = models.CharField(
        # 10 digits is the maximum length for post codes globally according to Wikipedia
        max_length = 10,
        blank = True,
        verbose_name = u"zip code",
        help_text = u"e.g. \"05100\" (max. 10 characters)"
    )
    city = models.CharField(
        max_length = 50,
        blank = True,
        help_text = u"e.g. \"Tampere\" or \"Stockholm\" (max. 50 characters)"
    )
    state = models.ForeignKey(
        State,
        blank = True,
        null = True,
        help_text = u"only for customers from USA, Australia and Brazil"
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
                output += u", "
            output += self.postAddressLine1
        if self.city:
            if output:
                output += u", "
            output += self.city
        if self.state:
            if output:
                output += u", "
            output += self.state.name
        if self.country:
            if output:
                output += u", "
            output += self.country.name

        return output

    class Meta():
        ordering = ["owner", "postAddressLine1"]
        verbose_name = u"address"
        verbose_name_plural = u"addresses"




class Order(models.Model):
    """ Represents a single order (containing many albums) as a whole. """
    orderer = models.ForeignKey(User)
    purchaseDate = models.DateTimeField(
        auto_now_add = True,
        verbose_name = u"purchase date"
    )
    status = models.IntegerField()

    def __unicode__(self):
        return u"%s, %s" % (self.orderer, self.purchaseDate)

    class Meta():
        unique_together = ("orderer", "purchaseDate")
        ordering = ["orderer", "purchaseDate", "status"]
        verbose_name = u"order"
        verbose_name_plural = u"orders"




class OrderItem(models.Model):
    """ Represents a single item (line) in an order. """
    order = models.ForeignKey(Order)
    album = models.ForeignKey(Album)
    count = models.IntegerField()
    deliveryAddress = models.ForeignKey(
        Address,
        verbose_name = u"delivery address"
    )

    def __unicode__(self):
        return u"%s, %s, %s, %d piece(s)" % (self.order.orderer, self.order.purchaseDate,
                                             self.album.title, self.count)

    class Meta():
        unique_together = ("order", "album")
        ordering = ["order", "album"]
        verbose_name = u"order item"
        verbose_name_plural = u"order items"




