# This Python file uses the following encoding: utf-8

import json, hashlib
from datetime import datetime
from random import Random
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max, Q
from django.db.models.signals import post_save
from django.utils.html import escape




def json_serialization_handler(object_to_serialize):
    """ Serializes objects, which are not supported by the Python's json package. """
    if hasattr(object_to_serialize, 'isoformat'):    # for datetimes: serialize them into a standard format
        return object_to_serialize.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % \
                                (type(object_to_serialize), repr(object_to_serialize))




def serialize_into_json(object_to_serialize):
    """ 
        Serializes objects into json using Python's json package. In debug mode, the format is clearer,
        but in production, unnecessary line breaks and indenting is left out. 
    """
    if settings.DEBUG:
        return json.dumps(object_to_serialize, sort_keys = True, indent = 4, default = json_serialization_handler)
    else:
        return json.dumps(object_to_serialize, default = json_serialization_handler)




def convert_money_into_two_decimal_string(amount):
    """ Returns the price of this album as a string with two decimal places. """
    amount_str = unicode(int(amount * 100.0) / 100.0)
    period_pos = amount_str.find(".")
    if period_pos == -1:
        amount_str += ".00"
    else:
        numbers_after_period = len(amount_str) - period_pos - 1
        if numbers_after_period == 1:
            amount_str += "0"
        elif numbers_after_period == 0:
            amount_str += "00"

    return amount_str




#def usermodel_get_addresses(self):
#    """ Returns this user's addresses. """
#    return Address.objects.filter(owner__exact = self)
#
#def usermodel_get_albums(self):
#    """ Returns this user's albums. """
#    return Album.objects.filter(owner__exact = self)
#
#def usermodel_get_facebook_profile(self):
#    """ Returns this user's Facebook profile, if one exists. """
#    profile_qs = FacebookProfile.objects.filter(userProfile__exact = self.get_profile())
#    if profile_qs.count() > 0:
#        return profile_qs[0]
#    return None
#
#def usermodel_get_orders(self):
#    """ Returns this user's orders. """
#    return Order.objects.filter(orderer__exact = self)
#
#def usermodel_get_shopping_cart_items(self):
#    """ Returns items in this user's shopping cart. """
#    return ShoppingCartItem.objects.filter(user__exact = self)
#
#User.add_to_class("addresses", usermodel_get_addresses)
#User.add_to_class("albums", usermodel_get_albums)
#User.add_to_class("facebook_profile", usermodel_get_facebook_profile)
#User.add_to_class("orders", usermodel_get_orders)
#User.add_to_class("shopping_cart", usermodel_get_shopping_cart_items)




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
        verbose_name = u"service conditions accepted",
        help_text = u"date and time when service conditions were last accepted"
    )
    homePhone = models.CharField(
        max_length = 20,
        blank = True,
        verbose_name = u"home phone",
        help_text = u"e.g. \"+358 44 123 4567\" (max. 20 characters)"

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




class FacebookProfile(models.Model):
    userProfile = models.OneToOneField(
        UserProfile,
        related_name = "facebookProfile",
        verbose_name = "user profile",
        help_text = u"profile of the user owning the Facebook account this record represents"
    )
    facebookID = models.BigIntegerField(
        unique = True,
        verbose_name = "Facebook id"
    )
    token = models.TextField(
        blank = True,
        verbose_name = "token",
        help_text = u"authentication token given by Facebook"
    )
    profileUrl = models.URLField(
        blank = True,
        verbose_name = "profile url",
        help_text = u"e.g. http://www.facebook.com/mikko.mallikas"
    )

    lastQueryTime = models.DateTimeField(
        null = True,
        verbose_name = "time of last query",
        help_text = u"time when this information was last updated from Facebook"
    )
    rawResponse = models.TextField(
        blank = True,
        verbose_name = "raw response",
        help_text = u"the full user information from Facebook as it was given"
    )

    def user(self):
        return self.userProfile.user

    def __unicode__(self):
        return self.userProfile.__unicode__()

    class Meta():
        ordering = ["userProfile"]
        verbose_name = u"Facebook profile"
        verbose_name_plural = u"Facebook profiles"




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
    secretHash = models.TextField(
        max_length = 64,
        verbose_name = u"secret hash",
        help_text = u"automatically generated secret hexadecimal " + \
            "SHA256 hash for exposing a private album to a specific audience"
    )
    creationDate = models.DateTimeField(
        auto_now_add = True,
        blank = True,
        null = True,
        verbose_name = u"creation date"
    )

    _randomizer = Random()

    def save(self, *args, **kwargs):
        """ Generate/validate album data before saving. """
        if len(self.title.strip()) < 5:
            raise ValueError, "Length of album's title must be 5-255 non-whitespace characters (%s)." % self.title

        if not self.secretHash:
            self.secretHash = self.generate_secret_hash_for(self)

        super(Album, self).save(*args, **kwargs)

    @staticmethod
    def generate_secret_hash_for(album):
        hash_source = album.owner.username + album.title + unicode(datetime.now())
        return hashlib.sha256(hash_source.encode("ascii", "backslashreplace")).hexdigest()

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.owner)

    @models.permalink
    def get_absolute_url(self):
        return ("show_single_album", (), {"album_id": self.id})

    @models.permalink
    def get_secret_url(self):
        if not self.secretHash:
            self.secretHash = self.generate_secret_hash_for(self)
        return ("albumizer.views.show_single_album_with_hash", (),
                        {"album_id": self.id, "secret_hash": self.secretHash})

    def is_owned_by(self, user):
        """ Checks if this album is owned by a given user. """
        return user == self.owner

    def is_editable_to_user(self, user):
        """ Checks if this album is editable to a given user. """
        return self.is_owned_by(user)

    def is_visible_to_user(self, user):
        """ Checks if this album is visible to a given user. """
        return self.isPublic or self.is_owned_by(user)

    def is_hidden_from_user(self, user):
        """ Checks if this album is hidden from a given user. """
        return not self.is_visible_to_user(user)

    @staticmethod
    def does_exist(album_id):
        """ Returns True, if an album having given id exists. Otherwise returns False. """
        return Album.objects.filter(id__exact = album_id).exists()

    @staticmethod
    def by_id(album_id):
        """ Returns an album having given id, if one exists. Otherwise returns None. """
        album_resultset = Album.objects.filter(id__exact = album_id)
        if not album_resultset:
            return None
        return album_resultset[0]

    @staticmethod
    def by_id_and_secret_hash(album_id, secret_hash):
        """ Returns an album having given id and secret hash, if one exists. Otherwise returns None. """
        album_resultset = Album.objects.filter(id__exact = album_id, secretHash__exact = secret_hash)
        if not album_resultset:
            return None
        return album_resultset[0]

    @staticmethod
    def ones_owned_by(user):
        """ Returns a queryset of albums owned by given user and ordered by title. """
        return Album.objects.filter(owner = user).order_by('title')

    @staticmethod
    def ones_visible_to(user):
        """ Returns a queryset of albums visible to a given user. """
        return Album.objects.filter(Q(isPublic = True) | Q(owner = user)).order_by('title')

    def pages(self):
        """ Return a queryset of all pages of this album. """
        return Page.objects.filter(album__exact = self)

    def has_pages(self):
        """ Return True if this album has at least one page. Otherwise returns False. """
        return Page.objects.filter(album__exact = self).exists()

    def price(self):
        """ Calculates and returns the price of this album. """
        total = 0.0
        page_count = self.pages().count()
        if page_count < 1:
            return total
        total += settings.PRICE_PER_ALBUM
        total += page_count * settings.PRICE_PER_ALBUM_PAGE
        return total

    def price_as_2dstr(self):
        """ Calculates and returns the price of this album as a string with two decimal places. """
        return convert_money_into_two_decimal_string(self.price())

    def as_api_dict(self):
        """ Returns this album as an dictionary containing values wanted to be exposed in the public api. """
        return {
            "id": self.id,
            "title": escape(self.title),
            "description": escape(self.description),
            "ownerUname": escape(self.owner.username),
            "creationDate": self.creationDate
        }

    @staticmethod
    def list_as_api_dict(album_list):
        """ Returns a list of albums as an dictionary containing values wanted to be exposed in the public api. """
        return [album.as_api_dict() for album in album_list]

    @staticmethod
    def latest_public_ones(how_many = 20):
        """ Returns some latest publicly visible albums. """
        if how_many < 1:
            how_many = 1
        if how_many > 99:
            how_many = 99
        return Album.objects.filter(isPublic__exact = True).order_by("-creationDate")[:how_many]

    @classmethod
    def latest_public_ones_as_json(cls, how_many = 20):
        """ Returns some latest publicly visible albums as json. """
        return serialize_into_json(cls.list_as_api_dict(cls.latest_public_ones(how_many)))

    @classmethod
    def pseudo_random_public_ones(cls, how_many = 4):
        """ Returns some pseudo-random publicly visible albums. """
        if how_many < 1:
            how_many = 1
        if how_many > 9:
            how_many = 9

        max_album_id = Album.objects.aggregate(Max("id")).values()[0]
        if not max_album_id:
            return []

        albums = []
        album_ids = []
        missed_tries = 0
        while len(albums) < how_many and missed_tries < 10:
            base_album_id = cls._randomizer.randrange(0, max_album_id)
            albumQuery = Album.objects.filter(id__gte = base_album_id, isPublic__exact = True).order_by("id")[:1]
            album = albumQuery[0] if albumQuery else None
            if album is None:
                break
            if not album.id in album_ids:
                albums.append(album)
                album_ids.append(album.id)
            else:
                missed_tries += 1

        return albums

    @classmethod
    def pseudo_random_public_ones_as_json(cls, how_many = 4):
        """ Returns some pseudo-random publicly visible albums as json. """
        return serialize_into_json(cls.list_as_api_dict(cls.pseudo_random_public_ones(how_many)))

    class Meta():
        unique_together = ("owner", "title")
        ordering = ["owner", "title"]
        verbose_name = u"album"
        verbose_name_plural = u"albums"




class Layout(models.Model):
    """Represents a single layout"""
    name = models.CharField(
        max_length = 255,
        unique = True,
        verbose_name = u"name",
        help_text = u"friendly name of this layout"
    )
    imageFieldCount = models.IntegerField(
        default = 0,
        verbose_name = u"image field count",
        help_text = u"number of image fields in this layout"
    )
    textFieldCount = models.IntegerField(
        default = 0,
        verbose_name = u"text field count",
        help_text = u"number of text fields in this layout"
    )
    cssClass = models.CharField(
        max_length = 255,
        verbose_name = u"CSS class",
        help_text = u"css class that is used in the CSS content field"
    )
    cssContent = models.TextField(
        blank = True,
        verbose_name = u"CSS content",
        help_text = u"the actual css definitions for this layout"
    )

    def __unicode__(self):
        return u"%s/%s - %d image(s), %d text(s)" % \
            (self.name, self.cssClass, self.imageFieldCount, self.textFieldCount)

    class Meta():
        ordering = ["name"]
        verbose_name = u"page layout"
        verbose_name_plural = u"page layouts"




class Page(models.Model):
    """ Represents a single page. """
    album = models.ForeignKey(Album)
    pageNumber = models.IntegerField(
        verbose_name = u"page number"
    )
    layout = models.ForeignKey(Layout)

    def __unicode__(self):
        return u"%s, %s" % (self.album, self.pageNumber)

    @models.permalink
    def get_absolute_url(self):
        view_parameters = {
            "album_id": self.album.id,
            "page_number": self.pageNumber
        }
        return ("show_single_page", (), view_parameters)

    @models.permalink
    def get_secret_url(self):
        if not self.album.secretHash:
            self.album.secretHash = self.album.generate_secret_hash_for(self.album)
        view_parameters = {
            "album_id": self.album.id,
            "secret_hash": self.album.secretHash,
            "page_number": self.pageNumber
        }
        return ("albumizer.views.show_single_page_with_hash", (), view_parameters)

    @staticmethod
    def by_album_id_and_page_number(album_id, page_number):
        """ Returns a page of an album by album's id and page number, if one exists. Otherwise returns None. """
        page_queryset = Page.objects.filter(album__id__exact = album_id, pageNumber = page_number)
        if not page_queryset:
            return None
        return page_queryset[0]

    @staticmethod
    def by_album_id_page_number_and_secret_hash(album_id, page_number, secret_hash):
        """ 
            Returns a page of an album by album's id, page number and a secret hash, if one exists.
            Otherwise returns None.
        """
        page_queryset = Page.objects.filter(
            album__id__exact = album_id,
            album__secretHash__exact = secret_hash,
            pageNumber = page_number
        )

        if not page_queryset:
            return None
        return page_queryset[0]

    class Meta():
        unique_together = ("album", "pageNumber")
        ordering = ["album", "pageNumber"]
        verbose_name = u"page"
        verbose_name_plural = u"pages"




class PageContent(models.Model):
    """ Represents a single piece of content in a placeholder. """
    page = models.ForeignKey(Page, related_name = "pagecontents")
    placeHolderID = models.CharField(
        max_length = 255,
        verbose_name = u"placeholder id"
    )
    content = models.CharField(
        max_length = 255
    )
    image = models.ImageField(upload_to = '%Y/%m/%d', blank=True)

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

    @staticmethod
    def by_code(country_code):
        """ Returns a country having given code, if one exists. Otherwise returns None. """
        country_resultset = Country.objects.filter(code__exact = country_code)
        if not country_resultset:
            return None
        return country_resultset[0]

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
        output = unicode(self.owner)

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




class ShoppingCartItem(models.Model):
    """ Contains items, which a user currently has his/her shopping cart. """
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album)
    count = models.IntegerField()
    additionDate = models.DateTimeField(
        auto_now_add = True,
        verbose_name = u"addition date",
        help_text = u"time when the item was added into shopping cart"
    )

    @staticmethod
    def add(user, album_id):
        """ 
            Adds given item to given user's shopping cart, if it is not there already.
            Caller handles all exceptions (e.g. Album.DoesNotExist).
        """
        if not ShoppingCartItem.does_exist(user, album_id):
            album = Album.objects.get(id__exact = album_id)
            item = ShoppingCartItem(
                user = user,
                album = album,
                count = 1
            )
            item.save()

    @staticmethod
    def items_of_user(user):
        """ Return a queryset of all items in given user's shopping cart. """
        return ShoppingCartItem.objects.filter(user__exact = user)

    @staticmethod
    def does_exist(user, album_id):
        """ Returns True, if given item exist in given user's shopping cart. Otherwise returns False. """
        return ShoppingCartItem.objects.filter(user = user, album = album_id).exists()

    @staticmethod
    def update_count(user, album_id, new_count):
        """ 
            Updates count of given item of given user's shopping cart. 
            Caller handles all exceptions (e.g. ShoppingCartItem.DoesNotExist).
        """
        sc_item = ShoppingCartItem.objects.get(user = user, album = album_id)
        sc_item.count = new_count
        sc_item.save()

    @staticmethod
    def remove(user, album_id):
        """ 
            Removes given item of given user from user's shopping cart. 
            Caller handles all exceptions (e.g. ShoppingCartItem.DoesNotExist).
        """
        ShoppingCartItem.objects.get(user = user, album = album_id).delete()

    @staticmethod
    def remove_all_items_of_user(user):
        """ 
            Removes all items of given user from user's shopping cart. 
            Caller handles all exceptions (e.g. ShoppingCartItem.DoesNotExist).
        """
        ShoppingCartItem.objects.filter(user__exact = user).delete()

    def __unicode__(self):
        return u"%s, %s, %d, %s" % (self.user, self.album, self.count, self.additionDate)

    class Meta():
        unique_together = ("additionDate", "user", "album")
        ordering = ["user", "album"]
        verbose_name = u"shopping cart item"
        verbose_name_plural = u"shopping cart items"




class OrderStatus(models.Model):
    """ 
        Represents the current status of an order.
        
        Methods of this class do not need to check existence of any records they return, because the records
        are assumed to exist and to have been imported from fixtures during creation/migration of the database
        in use, and absence of any of those records is an error situation anyway. If we had logging and
        email capability, the existence of those records could be checked e.g. at startup or so and a report
        could be made if necessary.    
    """
    code = models.CharField(
        unique = True,
        max_length = 10,
        help_text = u"a short code name describing this state"
    )

    @staticmethod
    def ordered():
        """ Returns an OrderStatus, in which the order has been made but not paid yet. """
        return OrderStatus.objects.get(code__exact = "ordered")

    @staticmethod
    def paid_and_being_processed():
        """ Returns an OrderStatus, in which the order is already paid and is currently being processed. """
        return OrderStatus.objects.get(code__exact = "paid")

    @staticmethod
    def blocked():
        """ 
            Returns an OrderStatus, in which the order is already paid but the
            processing of the order is prevented for some reason.
        """
        return OrderStatus.objects.get(code__exact = "blocked")

    @staticmethod
    def sent():
        """ Returns an OrderStatus, in which the order is already processed and sent to the customer. """
        return OrderStatus.objects.get(code__exact = "sent")

    def __unicode__(self):
        return self.code

    class Meta():
        ordering = ["id"]
        verbose_name = u"order status"
        verbose_name_plural = u"order statuses"




class Order(models.Model):
    """ Represents a single order (containing many albums) as a whole. """
    orderer = models.ForeignKey(User)
    purchaseDate = models.DateTimeField(
        auto_now_add = True,
        verbose_name = u"purchase date"
    )
    status = models.ForeignKey(OrderStatus)
    statusClarification = models.CharField(
        blank = True,
        max_length = 255,
        help_text = u"clarification of the current state of the order and the reasons for it, if necessary"
    )

    @staticmethod
    def by_id(order_id):
        """ Returns an order having given id, if one exists. Otherwise returns None. """
        order_resultset = Order.objects.filter(id__exact = order_id)
        if not order_resultset:
            return None
        return order_resultset[0]

    def total_price(self):
        """ Calculates and returns the total price for this order. """
        items = self.items()
        total = 0.0
        for i in range(items.count()):
            total += items[i].count * items[i].album.price()
        total += settings.SHIPPING_EXPENSES
        return total

    def total_price_as_2dstr(self):
        """ Calculates and returns the total price for this order as a string with two decimal places. """
        return convert_money_into_two_decimal_string(self.total_price())

    @models.permalink
    def get_absolute_url(self):
        view_parameters = {"order_id": self.id}
        return ("show_single_order", (), view_parameters)

    def is_made_by(self, user):
        """ Checks if this order is made by a given user. """
        return user == self.orderer

    def is_paid(self):
        """ Returns True if this order is paid, otherwise False. """
        return SPSPayment.exists_for_order(self)

    def items(self):
        """ Return all items of this order. """
        return OrderItem.items_of_order(self)

    def __unicode__(self):
        return u"%s, %s" % (self.orderer, self.purchaseDate)

    class Meta():
        unique_together = ("orderer", "purchaseDate")
        ordering = ["orderer", "purchaseDate", "status"]
        verbose_name = u"order"
        verbose_name_plural = u"orders"




class SPSPayment(models.Model):
    """ Represents a payment related to an order when paid via the Simple Payments service. """
    order = models.OneToOneField(Order)
    amount = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        verbose_name = u"amount [€]",
        help_text = u"a number with max. 2 decimals, e.g. 2.45"
    )
    transactionDate = models.DateTimeField(
        auto_now_add = True,
        verbose_name = u"transaction date",
        help_text = u"time when the payment is made"
    )
    referenceCode = models.CharField(
        max_length = 255,
        verbose_name = u"reference code",
        help_text = u"payment reference code given by the Simple Payments service"
    )
    clarification = models.CharField(
        blank = True,
        max_length = 255,
        help_text = u"clarifying information related to the payment"
    )

    @staticmethod
    def of_order(order):
        """ Returns payment of given order, if one exists. """
        payment_qs = SPSPayment.objects.filter(order__exact = order)
        if payment_qs.count() < 1:
            return None
        return payment_qs[0]

    @staticmethod
    def exists_for_order(order):
        """ Checks if a payment for given order exists. """
        return SPSPayment.objects.filter(order__exact = order).exists()

    def amount_as_2dstr(self):
        """ Returns the amount of this payment as a string with two decimal places. """
        return convert_money_into_two_decimal_string(self.amount)

    def __unicode__(self):
        return u"%s, %s, %f" % (self.order, self.transactionDate, self.amount)

    class Meta():
        ordering = ["order"]
        verbose_name = u"Simple Payments service payment"
        verbose_name_plural = u"Simple Payments service payments"




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

    @staticmethod
    def items_of_order(order):
        """ Returns items of given order, if there are any. """
        return OrderItem.objects.filter(order__exact = order)

    class Meta():
        unique_together = ("order", "album")
        ordering = ["order", "album"]
        verbose_name = u"order item"
        verbose_name_plural = u"order items"




