# This Python file uses the following encoding: utf-8

import hashlib, json, logging, os
from datetime import datetime, timedelta
from random import Random
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import ImageField, Max, Q
from django.db.models.fields.files import ImageFieldFile
from django.db.models.signals import post_save
from django.utils.html import escape
import Image




commonLogger = logging.getLogger("albumizer")


PATH_OF_MISSING_COVER_IMAGE_SMALL = settings.STATIC_URL + "images/missing-cover-small.png"
PATH_OF_MISSING_COVER_IMAGE_LARGE = settings.STATIC_URL + "images/missing-cover-large.png"


FILE_EXTENSION_PREFIX_LARGE_THUMBNAIL = "thumb-large"
FILE_EXTENSION_PREFIX_SMALL_THUMBNAIL = "thumb-small"

class AlbumizerImageFieldFile(ImageFieldFile):
    """ 
        ImageFieldFile subclass, which is able to save give image with small and large thumbnails.
    """
    @staticmethod
    def _modify_to_thumbnail_path(path, extension_prefix_to_add):
        """ 
            Adds an prefix to files extension, e.g. "this.jpg" --> "this.thumb.jpg",
            and changes the actual extension to "jpg" (because thumbnails are saved as jpegs).
        """
        path_parts = path.split(".")
        path_parts.insert(-1, extension_prefix_to_add)
        path_parts[-1] = "jpg"
        changed_path = ".".join(path_parts)
        return changed_path

    def _create_thumbnail(self, width, height, target_path):
        """ 
            Creates a thumbnail image based on the original, which must be saved already.
        """
        if not os.path.exists(self.path):
            commonLogger.error(u"Thumbnail creation failed for image \"%s\": Image was not found." % self.path)
            return

        try:
            thumbnail_image = Image.open(self.path)
            thumbnail_image.thumbnail((width, height), Image.ANTIALIAS)
            thumbnail_image.save(target_path, "JPEG")
            if settings.FILE_UPLOAD_PERMISSIONS:
                os.chmod(target_path, settings.FILE_UPLOAD_PERMISSIONS)
        except Exception as e:
            commonLogger.error(u"Thumbnail creation failed for image \"%s\": %s" %
                               (self.path, unicode(e, errors = "ignore")))

    @staticmethod
    def _enforce_path_permissions(target_path):
        if not target_path or not settings.FILE_UPLOAD_FOLDER_PERMISSIONS or not settings.MEDIA_ROOT:
            return

        target_path = os.path.normpath(target_path)
        media_root = os.path.normpath(settings.MEDIA_ROOT)

        if not target_path.startswith(media_root) or not os.path.isdir(target_path):
            return

        path_parts = target_path[len(media_root) + 1:].split(os.path.sep)

        partial_path = media_root
        AlbumizerImageFieldFile._set_folder_permissions(partial_path)

        for path_part in path_parts:
            partial_path += os.path.sep + path_part
            AlbumizerImageFieldFile._set_folder_permissions(partial_path)

    @staticmethod
    def _set_folder_permissions(path):
        try:
            os.chmod(path, settings.FILE_UPLOAD_FOLDER_PERMISSIONS)
        except Exception as e:
            commonLogger.error(u"Setting of path permissions failed for \"%s\": %s" %
                                   (path, unicode(e, errors = "ignore")))

    @staticmethod
    def _delete_thumbnail(path):
        """ 
            Deletes a file poined by given path, if it exists.
        """
        if os.path.exists(path):
            os.remove(path)

    def large_thumbnail_path(self):
        """ 
            Returns path of the large thumbnail image.
        """
        return self._modify_to_thumbnail_path(self.path, FILE_EXTENSION_PREFIX_LARGE_THUMBNAIL)

    def small_thumbnail_path(self):
        """ 
            Returns path of the small thumbnail image.
        """
        return self._modify_to_thumbnail_path(self.path, FILE_EXTENSION_PREFIX_SMALL_THUMBNAIL)

    def large_thumbnail_url(self):
        """ 
            Returns url of the large thumbnail image.
        """
        return self._modify_to_thumbnail_path(self.url, FILE_EXTENSION_PREFIX_LARGE_THUMBNAIL)

    def small_thumbnail_url(self):
        """ 
            Returns url of the small thumbnail image.
        """
        return self._modify_to_thumbnail_path(self.url, FILE_EXTENSION_PREFIX_SMALL_THUMBNAIL)

    def save(self, name, content, save = True):
        """ 
            Lets the superclass to save the original image and creates the two thumbnail images.
        """
        super(AlbumizerImageFieldFile, self).save(name, content, save)
        self._create_thumbnail(self.field.small_thumb_width, self.field.small_thumb_height, \
                                    self.small_thumbnail_path())
        self._create_thumbnail(self.field.large_thumb_width, self.field.large_thumb_height, \
                                    self.large_thumbnail_path())
        self._enforce_path_permissions(os.path.split(self.path)[0])

    def delete(self, save = True):
        """ 
            Deletes the thumbnail images and the lets the superclass to delete the original image.
        """
        self._delete_thumbnail(self.small_thumbnail_path())
        self._delete_thumbnail(self.large_thumbnail_path())
        super(AlbumizerImageFieldFile, self).delete(save)




class AlbumizerImageField(ImageField):
    """ 
        ImageField subclass, which is able to save give image with small and large thumbnails.
    """
    attr_class = AlbumizerImageFieldFile

    def __init__(self, small_thumb_width = 100, small_thumb_height = 100,
                 large_thumb_width = 300, large_thumb_height = 300, *args, **kwargs):
        """ 
            Store sizes of large and small thumbnail. 
        """
        self.small_thumb_width = small_thumb_width
        self.small_thumb_height = small_thumb_height
        self.large_thumb_width = large_thumb_width
        self.large_thumb_height = large_thumb_height
        super(AlbumizerImageField, self).__init__(*args, **kwargs)




class UserProfile(models.Model):
    """ 
        Represents additional information about a single user.
    """
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
        created as soon as a new user is created into Django's user table.
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
    """ 
        Represents a single album.
    """
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
        """ 
            Generate/validate album data before saving.
        """
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

    def url_of_small_cover(self):
        """ 
            Returns the url of this album's small cover image, if one can be found. "Cover image" is the first
            found when iterating through pages ordered by their pageNumber field.
            
            If the small thumbnail of the image in question does not exist, existence of the larger thumbnail
            is checked and its url is returned if the image exists. 
            
            If the large thumbnail of the image in question does not exist either,
            the url of the actual image is returned.
             
            If there is no images in this album, this method returns an empty string. 
        """
        for page in self.pages():
            image_content = page.image_content()
            for content in image_content:
                if content.image:
                    if os.path.exists(content.image.small_thumbnail_path()):
                        return content.image.small_thumbnail_url()
                    if os.path.exists(content.image.large_thumbnail_path()):
                        return content.image.large_thumbnail_url()
                    return content.image.url
        return PATH_OF_MISSING_COVER_IMAGE_SMALL

    def url_of_large_cover(self):
        """ 
            Returns the url of this album's large cover image, if one can be found. "Cover image" is the first
            found when iterating through pages ordered by their pageNumber field.
            
            If the large thumbnail of the image in question does not exist, existence of the smaller thumbnail
            is checked and its url is returned if the image exists.
            
            If the small thumbnail of the image in question does not exist either,
            the url of the actual image is returned.
             
            If there is no images in this album, this method returns an empty string. 
        """
        for page in self.pages():
            image_content = page.image_content()
            for content in image_content:
                if content.image:
                    if os.path.exists(content.image.large_thumbnail_path()):
                        return content.image.large_thumbnail_url()
                    if os.path.exists(content.image.small_thumbnail_path()):
                        return content.image.small_thumbnail_url()
                    return content.image.url
        return PATH_OF_MISSING_COVER_IMAGE_LARGE

    def is_owned_by(self, user):
        """ 
            Checks if this album is owned by a given user.
        """
        return user == self.owner

    def is_editable_to_user(self, user):
        """ 
            Checks if this album is editable to a given user.
        """
        return self.is_owned_by(user)

    def is_visible_to_user(self, user):
        """ 
            Checks if this album is visible to a given user.
        """
        return self.isPublic or self.is_owned_by(user)

    def is_hidden_from_user(self, user):
        """ 
            Checks if this album is hidden from a given user.
        """
        return not self.is_visible_to_user(user)

    @staticmethod
    def does_exist(album_id):
        """ 
            Returns True, if an album having given id exists. Otherwise returns False.
        """
        return Album.objects.filter(id__exact = album_id).exists()

    @staticmethod
    def by_id(album_id):
        """ 
            Returns an album having given id, if one exists. Otherwise returns None.
        """
        album_resultset = Album.objects.filter(id__exact = album_id)
        if not album_resultset:
            return None
        return album_resultset[0]

    @staticmethod
    def by_id_and_secret_hash(album_id, secret_hash):
        """ 
            Returns an album having given id and secret hash, if one exists. Otherwise returns None.
        """
        album_resultset = Album.objects.filter(id__exact = album_id, secretHash__exact = secret_hash)
        if not album_resultset:
            return None
        return album_resultset[0]

    @staticmethod
    def ones_owned_by(user):
        """ 
            Returns a queryset of albums owned by given user and ordered by title.
        """
        return Album.objects.filter(owner = user).order_by('title')

    @staticmethod
    def ones_visible_to(user):
        """ 
            Returns a queryset of albums visible to a given user.
        """
        return Album.objects.filter(Q(isPublic = True) | Q(owner = user)).order_by('title')

    def pages(self):
        """ 
            Return a queryset of all pages of this album.
        """
        return Page.objects.filter(album__exact = self).order_by("pageNumber")

    def has_pages(self):
        """ 
            Return True if this album has at least one page. Otherwise returns False.
        """
        return Page.objects.filter(album__exact = self).exists()

    def price_excluding_vat_and_shipping(self, quantity = None, cumulative_total = None):
        """ 
            Calculates a price for a number of a single album, excluding VAT and shipping.
        """
        if quantity and quantity < 0:
            raise ValueError, "Quantity of an album cannot be negative"

        price_of_single_album = 0.00

        page_count = self.pages().count()
        if page_count > 0:
            price_of_single_album += settings.PRICE_PER_ALBUM
            price_of_single_album += page_count * settings.PRICE_PER_ALBUM_PAGE

        result_list = [price_of_single_album]

        if quantity:
            price_of_albums = 0.00
            if page_count > 0:
                price_of_albums = quantity * price_of_single_album
            result_list.append(price_of_albums)

        if cumulative_total != None:
            if page_count > 0:
                cumulative_total += price_of_albums
            result_list.append(cumulative_total)

        return result_list

    @staticmethod
    def price_for_several_albums_excluding_vat_and_shipping(album_info_list):
        """ 
            Calculates a prices for several albums, excluding VAT and shipping.
            
            album_info_list is a list of lists containing an Album object and a quantity, like
            [[album1, 3], [album2, 23], [album3, 1]] .
        """
        item_infos = {}
        sub_total_price_for_all_albums = 0.00
        for (album, quantity) in album_info_list:
            unit_price, sub_total_for_single_album, sub_total_price_for_all_albums = \
                album.price_excluding_vat_and_shipping(quantity, sub_total_price_for_all_albums)
            item_infos[album] = {
                "quantity": quantity,
                "unit_price": unit_price,
                "sub_total": sub_total_for_single_album
            }

        return {
            "items": item_infos,
            "sub_total": sub_total_price_for_all_albums
        }

    @staticmethod
    def price_for_several_albums_including_vat_and_shipping(album_info_list):
        """ 
            Calculates a prices for several albums, including VAT and shipping.
            
            album_info_list is a list of lists containing an Album object and a quantity, like
            [[album1, 3, address1], [album2, 23, address2], [album3, 1, address3]] .
        """
        items_by_address = {}
        sub_total_price_for_all_albums = 0.00
        for (album, quantity, address) in album_info_list:
            unit_price, sub_total_for_single_album, sub_total_price_for_all_albums = \
                album.price_excluding_vat_and_shipping(quantity, sub_total_price_for_all_albums)

            if not address in items_by_address.keys():
                items_by_address[address] = {"items": []}

            items_by_address[address]["items"].append({
                "album": album,
                "quantity": quantity,
                "unit_price": unit_price,
                "sub_total": sub_total_for_single_album
            })

        current_date = datetime.now()
        dispatch_timedelta = timedelta(days = 3)
        delivery_timedelta = timedelta(days = 14)

        single_shipping_expense = settings.SHIPPING_EXPENSES
        sub_total_shipping_expenses = 0.00
        for address, items in items_by_address.items():
            items_by_address[address]["estimated_dispatch_date"] = current_date + dispatch_timedelta
            items_by_address[address]["estimated_delivery_date"] = current_date + delivery_timedelta

            item_group_subtotal_before_shipping = 0.00
            for item_info in items["items"]:
                item_group_subtotal_before_shipping += item_info["sub_total"]

            items_by_address[address]["item_group_subtotal_before_shipping"] = item_group_subtotal_before_shipping

            items_by_address[address]["shipping_expenses"] = single_shipping_expense

            item_group_subtotal_with_shipping = item_group_subtotal_before_shipping + single_shipping_expense
            items_by_address[address]["item_group_subtotal_with_shipping"] = item_group_subtotal_with_shipping

            sub_total_shipping_expenses += single_shipping_expense

        order_total_price_before_vat = sub_total_price_for_all_albums + sub_total_shipping_expenses

        vat_percentage = settings.VAT_PERCENTAGE
        vat_amount = vat_percentage / 100.0 * order_total_price_before_vat
        order_total_price = order_total_price_before_vat + vat_amount

        return {
            "items_by_address": items_by_address,
            "price_of_items": sub_total_price_for_all_albums,
            "shipping_expenses": sub_total_shipping_expenses,
            "order_total_price_before_vat": order_total_price_before_vat,
            "vat_percentage": vat_percentage,
            "vat_amount": vat_amount,
            "order_total_price": order_total_price
        }

    def deletePage(self, page_number):
        """ 
            Deletes the given page from this album.
        """
        query = self.pages().filter(pageNumber = page_number)[:1]
        if query:
            #delete page
            query[0].delete()
            #then fix page numbers
            query = self.pages().order_by("pageNumber")
            counter = 0
            for page in query.all():
                counter += 1
                page.pageNumber = counter
                page.save()

    def as_api_dict(self):
        """ 
            Returns this album as an dictionary containing values wanted to be exposed in the public api.
        """
        return {
            "id": self.id,
            "title": escape(self.title),
            "description": escape(self.description),
            "ownerUname": escape(self.owner.username),
            "creationDate": self.creationDate,
            "urlOfSmallCover": self.url_of_small_cover(),
            "urlOfLargeCover": self.url_of_large_cover()
        }

    @staticmethod
    def list_as_api_dict(album_list):
        """ 
            Returns a list of albums as an dictionary containing values wanted to be exposed in the public api.
        """
        return [album.as_api_dict() for album in album_list]

    @staticmethod
    def latest_public_ones(how_many = 20):
        """ 
            Returns some latest publicly visible albums.
        """
        if how_many < 1:
            how_many = 1
        if how_many > 99:
            how_many = 99
        return Album.objects.filter(isPublic__exact = True).order_by("-creationDate")[:how_many]

    @classmethod
    def latest_public_ones_as_json(cls, how_many = 20):
        """ 
            Returns some latest publicly visible albums as json.
        """
        return serialize_into_json(cls.list_as_api_dict(cls.latest_public_ones(how_many)))

    @classmethod
    def pseudo_random_public_ones(cls, how_many = 4):
        """ 
            Returns some pseudo-random publicly visible albums.
        """
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
        """ 
            Returns some pseudo-random publicly visible albums as json.
        """
        return serialize_into_json(cls.list_as_api_dict(cls.pseudo_random_public_ones(how_many)))

    class Meta():
        unique_together = ("owner", "title")
        ordering = ["owner", "title"]
        verbose_name = u"album"
        verbose_name_plural = u"albums"




class Layout(models.Model):
    """ 
        Represents a single layout.
    """
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
    """ 
        Represents a single page of an album.
    """
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

    def url_of_small_cover(self):
        """ 
            Returns the url of this page's small cover image, if one can be found. "Cover image" is the first
            found when iterating through pages content in ascending order.
            
            If the small thumbnail of the image in question does not exist, existence of the larger thumbnail
            is checked and its url is returned if the image exists. 
            
            If the large thumbnail of the image in question does not exist either,
            the url of the actual image is returned.
             
            If there are no images on this page, this method returns an empty string. 
        """
        for content in self.image_content():
            if content.image:
                if os.path.exists(content.image.small_thumbnail_path()):
                    return content.image.small_thumbnail_url()
                if os.path.exists(content.image.large_thumbnail_path()):
                    return content.image.large_thumbnail_url()
                return content.image.url
        return PATH_OF_MISSING_COVER_IMAGE_SMALL

    def url_of_large_cover(self):
        """ 
            Returns the url of this page's large cover image, if one can be found. "Cover image" is the first
            found when iterating through pages content in ascending order.
            
            If the large thumbnail of the image in question does not exist, existence of the smaller thumbnail
            is checked and its url is returned if the image exists.
            
            If the small thumbnail of the image in question does not exist either,
            the url of the actual image is returned.
             
            If there are no images on this page, this method returns an empty string. 
        """
        for content in self.image_content():
            if content.image:
                if os.path.exists(content.image.large_thumbnail_path()):
                    return content.image.large_thumbnail_url()
                if os.path.exists(content.image.small_thumbnail_path()):
                    return content.image.small_thumbnail_url()
                return content.image.url
        return PATH_OF_MISSING_COVER_IMAGE_LARGE

    def content(self):
        """  
        
        """
        return PageContent.objects.filter(page = self).order_by("placeHolderID")

    def image_content(self):
        """  
        
        """
        return self.content().filter(placeHolderID__contains = "_image_").order_by("-placeHolderID")

    def caption_content(self):
        """  
        
        """
        return self.content().filter(placeHolderID__contains = "_caption_").order_by("-placeHolderID")

    @staticmethod
    def by_album_id_and_page_number(album_id, page_number):
        """ 
            Returns a page of an album by album's id and page number, if one exists. Otherwise returns None.
        """
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




def get_album_photo_upload_path(page_content_model_instance, original_filename):
    """
        Generates full path for an uploaded image, relative to the mediaroot.
    """
    user_id = unicode(page_content_model_instance.page.album.owner.id)
    album_id = unicode(page_content_model_instance.page.album.id)
    page_number = unicode(page_content_model_instance.page.pageNumber)
    placeholder_number = unicode(page_content_model_instance.placeHolderID.split("_")[-1])
    extension = original_filename.split('.')[-1]

    security_hash_base = user_id + album_id + page_number + placeholder_number + unicode(settings.SECRET_KEY)
    security_hash_base += unicode(datetime.now())
    security_hash = hashlib.md5(security_hash_base.encode("ascii", "backslashreplace")).hexdigest()

    filename = "%s-%s-%s-%s-%s.%s" % \
                    (user_id, album_id, page_number, placeholder_number, security_hash, extension)
    path = "photos/albums/%s/%s/%s/%s" % (user_id[0], user_id, album_id, filename)

    if len(path) > 250:
        path = path.split(".")[0][:245] + ".%s" % extension

    return path

class PageContent(models.Model):
    """ 
        Represents a single piece of content in a placeholder.
    """
    page = models.ForeignKey(Page, related_name = "pagecontents")
    placeHolderID = models.CharField(
        max_length = 255,
        verbose_name = u"placeholder id"
    )
    content = models.CharField(
        max_length = 255
    )
    image = AlbumizerImageField(
        upload_to = get_album_photo_upload_path,
        blank = True,
        max_length = 255
    )

    def __unicode__(self):
        return u"%s, %s, %s" % (self.page, self.placeHolderID, self.content)

    class Meta():
        unique_together = ("page", "placeHolderID")
        verbose_name = u"page content"
        verbose_name_plural = u"page contents"




class Country(models.Model):
    """ 
        Represents a single country.
    """
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
        """ 
            Returns a country having given code, if one exists. Otherwise returns None.
        """
        country_resultset = Country.objects.filter(code__exact = country_code)
        if not country_resultset:
            return None
        return country_resultset[0]

    class Meta():
        ordering = ["name"]
        verbose_name = u"country"
        verbose_name_plural = u"countries"




class State(models.Model):
    """ 
        Represents a single state, like Texas (and there are states in other countries than USA, too).
    """
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
    """ 
        Represents a single address of a human (customer).
    """
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

    @staticmethod
    def addresses_of_user(user):
        """ 
            Return a queryset of all addresses of given user.
        """
        return Address.objects.filter(owner__exact = user)

    class Meta():
        ordering = ["owner", "postAddressLine1"]
        verbose_name = u"address"
        verbose_name_plural = u"addresses"




class ShoppingCartItem(models.Model):
    """ 
        Contains items, which a user currently has his/her shopping cart.
    """
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album)
    count = models.IntegerField()
    additionDate = models.DateTimeField(
        auto_now_add = True,
        verbose_name = u"addition date",
        help_text = u"time when the item was added into shopping cart"
    )
    deliveryAddress = models.ForeignKey(
        Address,
        null = True,
        verbose_name = u"delivery address"
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
        """ 
            Return a queryset of all items in given user's shopping cart. 
        """
        return ShoppingCartItem.objects.filter(user__exact = user)

    @staticmethod
    def items_of_user_with_albums(user):
        """ 
            Return a queryset of all items in given user's shopping cart preloading albums. 
        """
        return ShoppingCartItem.objects.select_related('album').filter(user__exact = user)

    @staticmethod
    def items_of_user_with_albums_and_addresses(user):
        """ 
            Return a queryset of all items in given user's shopping cart preloading albums and addresses.
        """
        return ShoppingCartItem.objects.select_related('album', 'deliveryAddress').filter(user__exact = user)

    @staticmethod
    def cart_info_for_user(user):
        """ 
            Returns information about items in given user's shopping cart.
            
            Returns a dictionary, see Album.price_for_several_albums_excluding_vat_and_shipping().
        """
        items = ShoppingCartItem.items_of_user_with_albums(user)
        album_count_list = [(i.album, i.count) for i in items]
        return Album.price_for_several_albums_excluding_vat_and_shipping(album_count_list)

    @staticmethod
    def order_info_for_user(user):
        """ 
            Returns information about items in given user's shopping cart
            treating the cart content as a complete order.
            
            Returns a dictionary, see Album.price_for_several_albums_including_vat_and_shipping().
        """
        items = ShoppingCartItem.items_of_user_with_albums(user)
        album_count_address_list = [(i.album, i.count, i.deliveryAddress) for i in items]
        return Album.price_for_several_albums_including_vat_and_shipping(album_count_address_list)

    @staticmethod
    def does_exist(user, album_id):
        """ 
            Returns True, if given item exist in given user's shopping cart. Otherwise returns False. 
        """
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

    @staticmethod
    def validation_hash_for_shopping_cart(request, exclude_addresses = True, extra_key = None):
        """ 
            Generates a hash which can be used to ensure that content
            of shopping cart does not change during checkout process.
        """
        hash_base = unicode(request.user.username) + request.META.get("REMOTE_ADDR", "") + \
                    request.META.get("REMOTE_HOST", "") + request.META.get("HTTP_USER_AGENT", "") + \
                    settings.SECRET_KEY

        if extra_key:
            hash_base += extra_key

        items = ShoppingCartItem.items_of_user(request.user)
        if exclude_addresses:
            for item in items:
                hash_base += unicode(item.album) + unicode(item.count)
        else:
            for item in items:
                hash_base += unicode(item.album) + unicode(item.count) + unicode(item.deliveryAddress)

        return hashlib.sha256(hash_base.encode("ascii", "backslashreplace")).hexdigest()

    @staticmethod
    def is_validation_hash_valid(request, exclude_addresses = True, extra_key = None):
        """ 
            Validates hash returned by ShoppingCartItem.validation_hash_for_shopping_cart().
        """
        if request.method == "GET":
            given_hash = request.GET.get("v")
        else:
            given_hash = request.POST.get("v")

        if not given_hash:
            return False

        our_hash = ShoppingCartItem.validation_hash_for_shopping_cart(request, exclude_addresses, extra_key)

        return our_hash == given_hash

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
        """ 
            Returns an OrderStatus, in which the order has been made but not paid yet. 
        """
        return OrderStatus.objects.get(code__exact = "ordered")

    @staticmethod
    def paid_and_being_processed():
        """ 
            Returns an OrderStatus, in which the order is already paid and is currently being processed. 
        """
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
        """ 
            Returns an OrderStatus, in which the order is already processed and sent to the customer. 
        """
        return OrderStatus.objects.get(code__exact = "sent")

    def __unicode__(self):
        return self.code

    class Meta():
        ordering = ["id"]
        verbose_name = u"order status"
        verbose_name_plural = u"order statuses"




class Order(models.Model):
    """ 
        Represents a single order (containing many albums) as a whole. 
    """
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
        """ 
            Returns an order having given id, if one exists. Otherwise returns None. 
        """
        order_resultset = Order.objects.filter(id__exact = order_id)
        if not order_resultset:
            return None
        return order_resultset[0]

    @staticmethod
    def create_from_shopping_cart_for_user(user):
        """
            Creates a new order based on the current content of given user's shopping cart.
            Returns the created Order instance.
            
            If given user's shopping cart is empty, a ShoppingCartEmptyError will be raised. 
        """
        cart_items = ShoppingCartItem.items_of_user(user)
        if not cart_items:
            raise ShoppingCartEmptyError("Unable to create an order from an empty shopping cart.")

        new_order = Order(
            orderer = user,
            status = OrderStatus.ordered()
        )
        new_order.save()

        for cart_item in cart_items:
            new_order_item = OrderItem(
                order = new_order,
                album = cart_item.album,
                count = cart_item.count,
                deliveryAddress = cart_item.deliveryAddress
            )
            new_order_item.save()

        cart_items.delete()

        return new_order


    def info(self):
        """ 
            Returns information about items belonging to this order.
            
            Returns a dictionary, see Album.price_for_several_albums_including_vat_and_shipping().
            In addition, the returned dictionary contains keys "order" containing this Order instance,
            and if this order has been paid, "payment" containing the corresponding SPSPayment instance. 
        """
        album_count_address_list = [(i.album, i.count, i.deliveryAddress) for i in self.items()]
        order_info = Album.price_for_several_albums_including_vat_and_shipping(album_count_address_list)
        order_info["order"] = self
        if self.is_paid():
            order_info["payment_info"] = self.payment().info()
        return order_info

    @models.permalink
    def get_absolute_url(self):
        view_parameters = {"order_id": self.id}
        return ("show_single_order", (), view_parameters)

    def is_made_by(self, user):
        """ 
            Checks if this order is made by a given user. 
        """
        return user == self.orderer

    def is_paid(self):
        """ 
            Returns True if this order is paid (via Simple Payments), otherwise False. 
        """
        return SPSPayment.exists_for_order(self)

    def is_just_ordered(self):
        """ 
            Returns True if this order has just been ordered but has not been paid yet, otherwise False. 
        """
        return self.status == OrderStatus.ordered()

    def is_paid_and_being_processed(self):
        """ 
            Returns True if this order has been paid and is currently being processed, otherwise False. 
        """
        return self.status == OrderStatus.paid_and_being_processed()

    def is_sent(self):
        """ 
            Returns True if this order has already been sent to the delivery address, otherwise False. 
        """
        return self.status == OrderStatus.sent()

    def is_blocked(self):
        """ 
            Returns True if this order is currently blocked for some reason, otherwise False. 
        """
        return self.status == OrderStatus.blocked()

    def payment(self):
        """ 
            Returns (Simple Payments) payment for this order, if one exists.
        """
        if not self.is_paid():
            return None
        return SPSPayment.of_order(self)

    def items(self):
        """ 
            Return all items of this order. 
        """
        return OrderItem.items_of_order(self)

    def __unicode__(self):
        return u"%s, %s" % (self.orderer, self.purchaseDate)

    class Meta():
        unique_together = ("orderer", "purchaseDate")
        ordering = ["orderer", "purchaseDate", "status"]
        verbose_name = u"order"
        verbose_name_plural = u"orders"




class SPSPayment(models.Model):
    """ 
        Represents a payment related to an order when paid via the Simple Payments service.
    """
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

    def info(self):
        return {
            "payment": self,
            "order_date": self.order.purchaseDate,
            "payer": self.order.orderer.first_name + u" " + self.order.orderer.last_name,
            "payee": u"Albumizer Plc.",
            "amount": self.amount,
            "via": SPSPayment.service_name(),
            "transaction_date": self.transactionDate,
            "reference_code": self.referenceCode,
            "clarification": self.clarification
        }

    @staticmethod
    def of_order(order):
        """ 
            Returns payment of given order, if one exists. 
        """
        payment_qs = SPSPayment.objects.filter(order__exact = order)
        if payment_qs.count() < 1:
            return None
        return payment_qs[0]

    @staticmethod
    def exists_for_order(order):
        """ 
            Checks if a payment for given order exists. 
        """
        return SPSPayment.objects.filter(order__exact = order).exists()

    @staticmethod
    def service_name():
        """ 
            Returns canonical name of this payment service. 
        """
        return "Simple Payments"

    def __unicode__(self):
        return u"%s, %s, %f" % (self.order, self.transactionDate, self.amount)

    class Meta():
        ordering = ["order"]
        verbose_name = u"Simple Payments service payment"
        verbose_name_plural = u"Simple Payments service payments"




class OrderItem(models.Model):
    """ 
        Represents a single item (line) in an order. 
    """
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
        """ 
            Returns items of given order, if there are any.
        """
        return OrderItem.objects.filter(order__exact = order)

    class Meta():
        unique_together = ("order", "album")
        ordering = ["order", "album"]
        verbose_name = u"order item"
        verbose_name_plural = u"order items"




class AlbumizerModelError(Exception):
    """
        Base class for exceptions defined in this module.
    """
    pass




class ShoppingCartEmptyError(AlbumizerModelError):
    """
        This exception is raised when some operation is tried to perform with an empty shopping cart. 
    """
    def __init__(self, error_message):
        self.message = error_message




def json_serialization_handler(object_to_serialize):
    """ 
        Serializes objects, which are not supported by the Python's json package.
    """
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




