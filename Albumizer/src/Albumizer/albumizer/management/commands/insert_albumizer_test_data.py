# This Python file uses the following encoding: utf-8

import codecs, fileinput, gc, os, string, time
from datetime import datetime, timedelta
from optparse import make_option
from random import Random
from django import db
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max, Q
from Albumizer.albumizer.models import UserProfile, FacebookProfile, Album, Layout, Page, PageContent, \
        Country, State, Address, ShoppingCartItem, Order, SPSPayment, OrderStatus, OrderItem



DATAFILE_PATH = os.path.join(os.path.dirname(__file__), 'test-data/').replace('\\', '/')
DATAFILE_MEN_FIRST_NAMES = DATAFILE_PATH + "men-first-names.txt"
DATAFILE_WOMEN_FIRST_NAMES = DATAFILE_PATH + "women-first-names.txt"
DATAFILE_LAST_NAMES = DATAFILE_PATH + "last-names.txt"
DATAFILE_STREET_NAMES = DATAFILE_PATH + "street-names.txt"
DATAFILE_EMAIL_DOMAINS = DATAFILE_PATH + "email-domains.txt"
DATAFILE_TEL_AREA_CODES = DATAFILE_PATH + "telephone-area-codes.txt"
DATAFILE_COMMON_ADJECTIVES = DATAFILE_PATH + "common-adjectives.txt"
DATAFILE_COMMON_NOUNS = DATAFILE_PATH + "common-nouns.txt"
DATAFILE_PEOPLE_NOUNS = DATAFILE_PATH + "people-nouns.txt"
DATAFILE_COMMON_VERBS = DATAFILE_PATH + "common-verbs.txt"
DATAFILE_TITLE_PHRASES = DATAFILE_PATH + "title-phrases.txt"
DATAFILE_COUNTRIES = DATAFILE_PATH + "countries.txt"
DATAFILE_CITIES_REGIONS = DATAFILE_PATH + "cities-and-regions.txt"
DATAFILE_PARAGRAPHS = DATAFILE_PATH + "paragraphs.txt"
DATAFILE_FINNISH_REGIONS = DATAFILE_PATH + "finnish-regions.txt"
DATAFILE_HTML_TAGS = DATAFILE_PATH + "html-tags.txt"




class Command(BaseCommand):
    """ Generates randomized data to be used to populate database during development and testing. """
    help = u"Generates and inserts to database some randomized data to be used during development and testing."
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option("--users",
            action = "store",
            type = "int",
            dest = "users",
            default = 10,
            help = "Number of users to generate, 1-500000, default 10"),
        make_option("--albumsmax",
            action = "store",
            type = "int",
            dest = "albumsmax",
            default = 10,
            help = "Maximum number of albums to generate per user, 0-100, default 10"),
        make_option("--albumsmin",
            action = "store",
            type = "int",
            dest = "albumsmin",
            default = 0,
            help = "Minimum number of albums to generate per user, 0-100, default 0"),
        make_option("--ordersmax",
            action = "store",
            type = "int",
            dest = "ordersmax",
            default = 10,
            help = "Maximum number of orders to generate per user, 0-100, default 10"),
        make_option("--ordersmin",
            action = "store",
            type = "int",
            dest = "ordersmin",
            default = 0,
            help = "Minimum number of orders to generate per user, 0-100, default 0"),
        )

    _men_first_names = []
    _women_first_names = []
    _last_names = []
    _street_names = []
    _email_domains = []
    _tel_area_codes = []
    _common_adjectives = []
    _common_nouns = []
    _people_nouns = []
    _common_verbs = []
    _title_phrases = []
    _countries = []
    _cities_regions = []
    _paragraphs = []
    _finnish_regions = []
    _html_tags = []
    _genderRandomizer = Random()
    _nameRandomizer = Random()
    _emailRandomizer = Random()
    _phoneRandomizer = Random()
    _albumRandomizer = Random()
    _orderRandomizer = Random()
    _addressRandomizer = Random()
    _male_gender = UserProfile.GENDER_CHOICES[0][0]
    _female_gender = UserProfile.GENDER_CHOICES[1][0]
    _address_letters = u"ABCDEFGHJKLMNPRST"
    _trans_tbl_email_username_src = u"åäöÅÄÖáÁàÀèÈéÉêÊëËíÍìÌïÏîÎóÓòÒôÔúÚùÙûÛüÜýÝỳỲÿŸšŠß"
    _trans_tbl_email_username_dest = u"aaoAAOaAaAeEeEeEeEiIiIiIiIoOoOoOuUuUuUuUyYyYyYsSs"
    _trans_tbl_email_username = {}
    _ids_of_generated_users = []




    def _read_data_file(self, filename):
        """ Reads lines of a file to a list and trims them """
        return [unicode(line.strip(), encoding = "utf-8") for line in fileinput.input(filename)]




    def handle(self, *args, **options):
        """ Populates the Albumizer database with random test data """
        verbosity = int(options.get("verbosity"))
        number_of_users = options.get("users")
        max_number_of_albums = options.get("albumsmax")
        min_number_of_albums = options.get("albumsmin")
        max_number_of_orders = options.get("ordersmax")
        min_number_of_orders = options.get("ordersmin")

        if number_of_users < 1:
            self.stdout.write(u"No users to be created.\n")
            return

        if number_of_users > 500000:
            number_of_users = 500000

        if min_number_of_albums < 0:
            min_number_of_albums = 0
        if min_number_of_albums > 100:
            min_number_of_albums = 100

        if max_number_of_albums < 0:
            max_number_of_albums = 0
        if max_number_of_albums > 100:
            max_number_of_albums = 100

        if min_number_of_albums > max_number_of_albums:
            min_number_of_albums, max_number_of_albums = max_number_of_albums, min_number_of_albums


        if min_number_of_orders < 0:
            min_number_of_orders = 0
        if min_number_of_orders > 100:
            min_number_of_orders = 100

        if max_number_of_orders < 0:
            max_number_of_orders = 0
        if max_number_of_orders > 100:
            max_number_of_orders = 100

        if min_number_of_orders > max_number_of_orders:
            min_number_of_orders, max_number_of_orders = max_number_of_orders, min_number_of_orders


        self.stdout.write(u"Initializing data structures...\n\n");

        self._men_first_names = self._read_data_file(DATAFILE_MEN_FIRST_NAMES)
        self._women_first_names = self._read_data_file(DATAFILE_WOMEN_FIRST_NAMES)
        self._last_names = self._read_data_file(DATAFILE_LAST_NAMES)
        self._street_names = self._read_data_file(DATAFILE_STREET_NAMES)
        self._email_domains = self._read_data_file(DATAFILE_EMAIL_DOMAINS)
        self._tel_area_codes = self._read_data_file(DATAFILE_TEL_AREA_CODES)
        self._common_adjectives = self._read_data_file(DATAFILE_COMMON_ADJECTIVES)
        self._common_nouns = self._read_data_file(DATAFILE_COMMON_NOUNS)
        self._people_nouns = self._read_data_file(DATAFILE_PEOPLE_NOUNS)
        self._common_verbs = self._read_data_file(DATAFILE_COMMON_VERBS)
        self._title_phrases = self._read_data_file(DATAFILE_TITLE_PHRASES)
        self._countries = self._read_data_file(DATAFILE_COUNTRIES)
        self._cities_regions = self._read_data_file(DATAFILE_CITIES_REGIONS)
        self._paragraphs = self._read_data_file(DATAFILE_PARAGRAPHS)
        self._finnish_regions = self._read_data_file(DATAFILE_FINNISH_REGIONS)
        self._html_tags = self._read_data_file(DATAFILE_HTML_TAGS)

        for i in range(1, len(self._trans_tbl_email_username_src)):
            self._trans_tbl_email_username[ord(self._trans_tbl_email_username_src[i])] = \
                    self._trans_tbl_email_username_dest[i]


        self.stdout.write(u"Inserting test data to Albumizer database. " +
                          u"This may take some time, so please wait patiently.\n\n")

        if number_of_users == 1:
            self.stdout.write(u"Generating one user, ")
        else:
            self.stdout.write(u"Generating %d users, " % number_of_users)

        if min_number_of_albums == max_number_of_albums:
            if max_number_of_albums == 1:
                self.stdout.write(u"one album per user.")
            else:
                self.stdout.write(u"%d albums per user." % max_number_of_albums)
        else:
            self.stdout.write(u"%d-%d albums per user." % (min_number_of_albums, max_number_of_albums))

        self.stdout.write(u"\n\n")

        length_of_pause_in_seconds = 10
        for user_number in range(1, number_of_users + 1):
            if user_number % 15 == 0:
                message = u"Pausing for %d seconds:  " % length_of_pause_in_seconds
                self.stdout.write(message.encode("ascii", "backslashreplace"))
                for i in range(length_of_pause_in_seconds):
                    time.sleep(1)
                    self.stdout.write("* ".encode("ascii", "backslashreplace"))
                self.stdout.write("\n\n".encode("ascii", "backslashreplace"))

            user_data = self.generate_user_data()

            username = user_data["username"]
            unique_username = username
            postfix_counter = 2
            while (User.objects.filter(username__exact = unique_username).exists()):
                unique_username = unicode(username + unicode(postfix_counter))
                postfix_counter += 1

            new_user = User(username = unique_username, email = user_data["email"], password = "")
            new_user.first_name = user_data["first_name"]
            new_user.last_name = user_data["last_name"]
            new_user.date_joined = user_data["serviceConditionsAccepted"]
            new_user.set_password("salasana")
            new_user.save()
            self._ids_of_generated_users.append(new_user.id)

            user_profile = new_user.get_profile()
            user_profile.gender = user_data["gender"]
            user_profile.homePhone = user_data["phone"]
            user_profile.serviceConditionsAccepted = user_data["serviceConditionsAccepted"]
            user_profile.save()

            if verbosity >= 2:
                message = u"New user (%d): %s, %s %s, %s, %s, %s, %s\n" % \
                                  (user_number, new_user.username, new_user.first_name, new_user.last_name,
                                   user_profile.gender, user_profile.homePhone, new_user.email,
                                   unicode(user_profile.serviceConditionsAccepted))
                self.stdout.write(message.encode("ascii", "backslashreplace"))
            elif verbosity == 1:
                self.stdout.write(u"U%d: " % user_number)

            del user_profile




            number_of_addresses = self._albumRandomizer.randrange(0, 10)
            for address_number in range(1, number_of_addresses + 1):
                address_data = self.generate_address_data()

                new_address = Address(
                    owner = new_user,
                    postAddressLine1 = address_data["postAddressLine1"],
                    postAddressLine2 = address_data["postAddressLine2"],
                    zipCode = address_data["zipCode"],
                    city = address_data["city"],
                    state = address_data["state"],
                    country = address_data["country"],
                )
                new_address.save()

                if verbosity >= 2:
                    message = u"  - address: %s, %s, %s, %s\n" % \
                                      (new_address.postAddressLine1, new_address.zipCode,
                                       new_address.city, unicode(new_address.country))
                    self.stdout.write(message.encode("ascii", "backslashreplace"))
                elif verbosity == 1:
                    self.stdout.write(u"d ")

                del new_address
                del address_data

            if verbosity >= 2:
                self.stdout.write(u"\n")







            number_of_albums = self._albumRandomizer.randrange(min_number_of_albums, max_number_of_albums + 1)
            for album_number in range(1, number_of_albums + 1):
                album_data = self.generate_album_data(new_user)

                album_title = album_data["title"]
                unique_album_title = album_title
                postfix_counter = 2
                while (Album.objects.filter(owner__exact = new_user, title__exact = unique_album_title).exists()):
                    unique_album_title = unicode(album_title + u" " + unicode(postfix_counter))
                    postfix_counter += 1

                new_album = Album(
                    owner = new_user,
                    title = unique_album_title,
                    description = album_data["description"],
                    isPublic = album_data["is_public"]
                )
                new_album.save()
                new_album.creationDate = album_data["creation_date"]
                new_album.save()

                if verbosity >= 2:
                    message = u"  - album: %s, %s, %s\n           %s...\n\n" % \
                                      (new_album.title, new_album.isPublic,
                                       new_album.creationDate,
                                       new_album.description[0:30].replace(u"\n", u"\n           "))
                    self.stdout.write(message.encode("ascii", "backslashreplace"))
                elif verbosity == 1:
                    self.stdout.write(u"a ")


                if verbosity >= 2:
                    message = u"    * pages:"
                    self.stdout.write(message.encode("ascii", "backslashreplace"))

                number_of_pages = self._albumRandomizer.randrange(0, 20)
                for page_number in range(1, number_of_pages + 1):
                    #page_data = self.generate_page_data()

                    new_page = Page(
                        album = new_album,
                        pageNumber = page_number
                    )
                    new_page.save()

                    if verbosity >= 2:
                        message = u" %d" % page_number
                        self.stdout.write(message.encode("ascii", "backslashreplace"))
                    elif verbosity == 1:
                        self.stdout.write(u"p ")

                    del new_page

                if verbosity >= 2:
                    message = u"\n    * Price: %s euros\n\n" % new_album.price_as_2dstr()
                    self.stdout.write(message.encode("ascii", "backslashreplace"))

                del new_album
                del album_data



            shopping_cart_data = self.generate_shopping_cart_data(new_user)
            if not shopping_cart_data["success"] and verbosity >= 2:
                message = u"  - no valid albums to create shopping cart with\n\n"
                self.stdout.write(message.encode("ascii", "backslashreplace"))
            else:
                message = u"  - shopping cart:\n"
                self.stdout.write(message.encode("ascii", "backslashreplace"))

                item_counter = 0
                for item in shopping_cart_data["items"]:
                    item_counter += 1
                    new_shopping_cart_item = ShoppingCartItem(
                        user = new_user,
                        album = item["album"],
                        count = item["count"]
                    )
                    new_shopping_cart_item.save()
                    new_shopping_cart_item.additionDate = item["additionDate"]
                    new_shopping_cart_item.save()

                    if verbosity >= 2:
                        message = u"            (%d) %s, %d, %s\n" % \
                                        (item_counter, new_shopping_cart_item.album, new_shopping_cart_item.count,
                                         new_shopping_cart_item.additionDate)
                        self.stdout.write(message.encode("ascii", "backslashreplace"))
                    elif verbosity == 1:
                        self.stdout.write(u"c ")

                    del new_shopping_cart_item

                if verbosity >= 2:
                    self.stdout.write("\n".encode("ascii", "backslashreplace"))

            del shopping_cart_data






            most_recent_order = None
            most_recent_order_purchasedate = datetime(1900, 1, 1, 0, 0, 0)
            generated_orders = []
            number_of_orders = self._orderRandomizer.randrange(min_number_of_orders, max_number_of_orders + 1)
            for order_number in range(number_of_orders):
                order_data = self.generate_order_data(new_user)
                if not order_data["success"]:
                    if verbosity >= 2:
                        message = u"  - no valid albums and/or addresses to create orders with\n\n"
                        self.stdout.write(message.encode("ascii", "backslashreplace"))
                    break;

                new_order = Order(
                    orderer = new_user,
                    status = order_data["status"]
                )
                new_order.save()
                new_order.purchaseDate = order_data["purchase_date"]
                new_order.save()

                generated_orders.append(new_order)

                if new_order.purchaseDate > most_recent_order_purchasedate:
                    most_recent_order_purchasedate = new_order.purchaseDate
                    most_recent_order = new_order

                if verbosity >= 2:
                    message = u"  - order: %s\n" % new_order.purchaseDate
                    self.stdout.write(message.encode("ascii", "backslashreplace"))
                elif verbosity == 1:
                    self.stdout.write(u"o ")

                order_item_counter = 0;
                for item in order_data["items"]:
                    order_item_counter += 1

                    new_order_item = OrderItem(
                        order = new_order,
                        album = item["album"],
                        count = item["count"],
                        deliveryAddress = item["address"]
                    )
                    new_order_item.save()

                    if verbosity >= 2:
                        message = u"            (%d) %s, %d, %s\n" % \
                                        (order_item_counter, new_order_item.album, new_order_item.count,
                                         unicode(new_order_item.deliveryAddress))
                        self.stdout.write(message.encode("ascii", "backslashreplace"))
                    elif verbosity == 1:
                        self.stdout.write(u"i ")

                if verbosity >= 2:
                    message = u"            Total price: %s euros\n" % new_order.total_price_as_2dstr()
                    if order_number < number_of_orders - 1:
                        message += u"\n"
                    self.stdout.write(message.encode("ascii", "backslashreplace"))

                del new_order
                del order_data

            if most_recent_order and self._orderRandomizer.randrange(0, 100) > 50:
                order_status_factor = self._orderRandomizer.randrange(0, 100)
                if order_status_factor < 33:
                    most_recent_order.status = OrderStatus.ordered()
                elif order_status_factor < 80:
                    most_recent_order.status = OrderStatus.paid_and_being_processed()
                else:
                    most_recent_order.status = OrderStatus.blocked()
                    most_recent_order.statusClarification = u"We are temporarily out of stock, but will send " + \
                                                            u"the products as soon as they arrive to our warehouse."

                most_recent_order.save()

                if verbosity >= 2:
                    message = u"\n  - status of the most recent order (%s) is \"%s\"\n" % \
                                            (most_recent_order.purchaseDate, most_recent_order.status)
                    self.stdout.write(message.encode("ascii", "backslashreplace"))

            del most_recent_order

            if verbosity >= 2:
                self.stdout.write("\n".encode("ascii", "backslashreplace"))

            for order in generated_orders:
                if order.status != OrderStatus.ordered():
                    payment_data = self.generate_sps_payment_data(order)

                    new_sps_payment = SPSPayment(
                        order = order,
                        amount = payment_data["amount"],
                        referenceCode = payment_data["referenceCode"],
                        clarification = payment_data["clarification"]
                    )

                    new_sps_payment.save()
                    new_sps_payment.transactionDate = payment_data["transactionDate"]
                    new_sps_payment.save()

                    if verbosity >= 2:
                        message = u"  - SPS payment for order (%s), %s euros, made %s, ref code %s\n" % \
                                        (order.purchaseDate, new_sps_payment.amount_as_2dstr(),
                                         new_sps_payment.transactionDate, new_sps_payment.referenceCode)
                        self.stdout.write(message.encode("ascii", "backslashreplace"))
                    elif verbosity == 1:
                        self.stdout.write(u"y ")

                    del new_sps_payment
                    del payment_data

            del generated_orders

            if verbosity >= 1:
                self.stdout.write(u"\n")

            db.reset_queries()
            gc.collect()




        if verbosity >= 1:
            self.stdout.write(u"\nAll data has been created.")
            if self._ids_of_generated_users:
                self.stdout.write(u" Program created users with the following usernames:\n");
                username = User.objects.get(id__exact = self._ids_of_generated_users[0]).username
                self.stdout.write(username.encode("ascii", "backslashreplace"))
                for i in range(1, number_of_users - 1):
                    username = User.objects.get(id__exact = self._ids_of_generated_users[i]).username
                    self.stdout.write(u", " + username.encode("ascii", "backslashreplace"))
                if number_of_users > 1:
                    username = User.objects.get(id__exact = self._ids_of_generated_users[number_of_users - 1]).username
                    self.stdout.write(u" and " + username.encode("ascii", "backslashreplace"))
            self.stdout.write(u"\n")




    def generate_user_data(self):
        """ Generates information related to a single user """
        gender = self._male_gender
        if self._genderRandomizer.randrange(0, 100) > 50:
            gender = self._female_gender


        first_name_list = self._men_first_names
        if gender == self._female_gender:
            first_name_list = self._women_first_names


        index_first_name_beginning = self._nameRandomizer.randrange(0, len(first_name_list))
        first_name = first_name_list[index_first_name_beginning]
        username = first_name[0:2].lower()
        if self._nameRandomizer.randrange(0, 100) >= 90:
            index_first_name_ending = self._nameRandomizer.randrange(0, len(first_name_list))
            while index_first_name_beginning == index_first_name_ending:
                index_first_name_beginning = self._nameRandomizer.randrange(0, len(first_name_list))
            first_name_beginning = first_name_list[index_first_name_ending]
            first_name += u"-" + first_name_beginning
            username = username[0] + first_name_beginning[0].lower()


        index_last_name_beginning = self._nameRandomizer.randrange(0, len(self._last_names))
        last_name = self._last_names[index_last_name_beginning]
        username += last_name[0:8].lower()
        if self._nameRandomizer.randrange(0, 100) >= 90:
            index_last_name_ending = self._nameRandomizer.randrange(0, len(self._last_names))
            while index_last_name_beginning == index_last_name_ending:
                index_first_name_beginning = self._nameRandomizer.randrange(0, len(self._last_names))
            last_name_ending = self._last_names[index_last_name_ending]
            last_name += u"-" + last_name_ending
            username = username[0:8] + last_name_ending[0:4].lower()


        email_domain = self._email_domains[self._emailRandomizer.randrange(0, len(self._email_domains))]
        if self._nameRandomizer.randrange(0, 100) >= 50:
            email = username
        else:
            email = first_name + u"." + last_name
        email += u"@" + email_domain


        username = username.translate(self._trans_tbl_email_username)
        email = email.translate(self._trans_tbl_email_username)


        phone = self._tel_area_codes[self._phoneRandomizer.randrange(0, len(self._tel_area_codes))]
        if self._nameRandomizer.randrange(0, 100) >= 40:
            phone = u"+358 " + phone[1:]
        phone += u" "

        number_of_digits = self._phoneRandomizer.randrange(6, 9)
        number_of_digits_in_first_part = int(number_of_digits / 2)

        for i in range(0, number_of_digits_in_first_part):
            phone += unicode(self._phoneRandomizer.randrange(0, 10))
        phone += u" "
        for i in range(0, number_of_digits - number_of_digits_in_first_part):
            phone += unicode(self._phoneRandomizer.randrange(0, 10))

        sa_year = self._nameRandomizer.randrange(1990, datetime.now().year - 1)
        sa_month = self._nameRandomizer.randrange(1, 13)
        sa_day = self._nameRandomizer.randrange(1, 29)
        sa_hour = self._nameRandomizer.randrange(0, 24)
        sa_minute = self._nameRandomizer.randrange(0, 60)
        sa_second = self._nameRandomizer.randrange(0, 60)
        sa_datetime = datetime(sa_year, sa_month, sa_day, sa_hour, sa_minute, sa_second)

        return {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "gender": gender,
            "phone" : phone,
            "serviceConditionsAccepted": sa_datetime
        }




    def generate_album_title(self):
        """ Generates a title for a single photo album """
        album_type_factor = self._albumRandomizer.randrange(0, 99)

        title = u""
        if album_type_factor < 3:
            title = self._title_phrases[self._albumRandomizer.randrange(0, len(self._title_phrases))]
            previous_title = u""
            while (title != previous_title):
                previous_title = title
                title = title.replace(u"{adj}", self._common_adjectives[
                            self._albumRandomizer.randrange(0, len(self._common_adjectives))], 1)
            previous_title = u""
            while (title != previous_title):
                previous_title = title
                title = title.replace(u"{noun}", self._common_nouns[
                            self._albumRandomizer.randrange(0, len(self._common_nouns))], 1)
            previous_title = u""
            while (title != previous_title):
                previous_title = title
                title = title.replace(u"{verb}", self._common_verbs[
                            self._albumRandomizer.randrange(0, len(self._common_verbs))], 1)
        elif album_type_factor < 15:
            if self._albumRandomizer.randrange(0, 100) < 30:
                title = u"the "
            factor = self._albumRandomizer.randrange(0, 100)
            if factor < 25:
                title += self._people_nouns[self._albumRandomizer.randrange(0, len(self._people_nouns))]
            elif factor < 50:
                title += self._countries[self._albumRandomizer.randrange(0, len(self._countries))]
            elif factor < 75:
                title += self._cities_regions[self._albumRandomizer.randrange(0, len(self._cities_regions))]
            else:
                first_name_list = self._men_first_names
                if self._albumRandomizer.randrange(0, 100) < 50:
                    first_name_list = self._women_first_names
                title += first_name_list[self._albumRandomizer.randrange(0, len(first_name_list))]
            if self._albumRandomizer.randrange(0, 100) < 50:
                title += u"'s "
                if self._albumRandomizer.randrange(0, 100) < 50:
                    title += self._common_adjectives[
                                    self._albumRandomizer.randrange(0, len(self._common_adjectives))] + u" "
                title += self._common_nouns[self._albumRandomizer.randrange(0, len(self._common_nouns))]
        elif album_type_factor < 30:
            title = self._common_adjectives[self._albumRandomizer.randrange(0, len(self._common_adjectives))]
            if self._albumRandomizer.randrange(0, 100) < 30:
                if self._albumRandomizer.randrange(0, 100) < 50:
                    title += u"ish"
                else:
                    title += u"ness"
            if self._albumRandomizer.randrange(0, 100) < 30:
                title = u"the " + title
                if self._albumRandomizer.randrange(0, 100) < 30:
                    title += u" one"
        elif album_type_factor < 40:
            title = self._common_nouns[self._albumRandomizer.randrange(0, len(self._common_nouns))]
            if self._albumRandomizer.randrange(0, 100) < 30:
                title += u"-like"
            if self._albumRandomizer.randrange(0, 100) < 40:
                title = u"the " + title
                if self._albumRandomizer.randrange(0, 100) < 20:
                    title += u" one"
        elif album_type_factor < 90:
            fact = self._albumRandomizer.randrange(0, 100)
            if fact < 30:
                title = self._common_verbs[self._albumRandomizer.randrange(0, len(self._common_verbs))]
                if title[-1:] == u"e":
                    title = title[:-1]
                title += u"ing"
            elif fact < 70:
                title = self._common_nouns[self._albumRandomizer.randrange(0, len(self._common_nouns))]
                if self._albumRandomizer.randrange(0, 100) < 50 and title[-1:] != u"s":
                    title += u"s"
                if self._albumRandomizer.randrange(0, 100) < 40:
                    title = self._common_adjectives[
                                self._albumRandomizer.randrange(0, len(self._common_adjectives))] + u" " + title
            else:
                title = self._common_adjectives[self._albumRandomizer.randrange(0, len(self._common_adjectives))]
                if self._albumRandomizer.randrange(0, 100) < 40:
                    title += u" " + self._common_nouns[self._albumRandomizer.randrange(0, len(self._common_nouns))]

            if self._albumRandomizer.randrange(0, 100) < 40:
                title = u"the " + title

            if self._albumRandomizer.randrange(0, 100) < 40:
                fact = self._albumRandomizer.randrange(0, 100)
                if fact < 30:
                    title_tmp = self._common_verbs[self._albumRandomizer.randrange(0, len(self._common_verbs))]
                    if title_tmp.endswith(u"e"):
                        title_tmp = title_tmp[:-1]
                    title_tmp += u"ing"
                elif fact < 70:
                    title_tmp = self._common_nouns[self._albumRandomizer.randrange(0, len(self._common_nouns))]
                    if self._albumRandomizer.randrange(0, 100) < 50 and title_tmp.endswith(u"s"):
                        title_tmp += u"s"
                    if self._albumRandomizer.randrange(0, 100) < 40:
                        title_tmp = self._common_adjectives[
                                    self._albumRandomizer.randrange(0, len(self._common_adjectives))] + u" " + title_tmp
                else:
                    title_tmp = self._common_adjectives[self._albumRandomizer.randrange(0, len(self._common_adjectives))]
                    if self._albumRandomizer.randrange(0, 100) < 40:
                        title_tmp += u" " + self._common_nouns[self._albumRandomizer.randrange(0, len(self._common_nouns))]

                if self._albumRandomizer.randrange(0, 100) < 40:
                    title += u" and"
                else:
                    title += u" of"
                title += u" the " + title_tmp


            if self._albumRandomizer.randrange(0, 100) < 70:
                fact = self._albumRandomizer.randrange(0, 100)
                if fact < 33:
                    title += u" of "
                    fact2 = self._albumRandomizer.randrange(0, 100) < 40
                    if fact2 < 33:
                        first_name_list = self._men_first_names
                        if self._albumRandomizer.randrange(0, 100) < 50:
                            first_name_list = self._women_first_names
                        title += first_name_list[self._albumRandomizer.randrange(0, len(first_name_list))]
                    elif fact2 < 66:
                        title += self._cities_regions[self._albumRandomizer.randrange(0, len(self._cities_regions))]
                    else:
                        title += self._countries[self._albumRandomizer.randrange(0, len(self._countries))]
                elif fact < 66:
                    title += u" at "
                    if self._albumRandomizer.randrange(0, 100) < 50:
                        title += self._countries[self._albumRandomizer.randrange(0, len(self._countries))]
                    else:
                        title += self._cities_regions[self._albumRandomizer.randrange(0, len(self._cities_regions))]
                else:
                    title += u" in "
                    if self._albumRandomizer.randrange(0, 100) < 50:
                        title += self._countries[self._albumRandomizer.randrange(0, len(self._countries))]
                    else:
                        title += self._cities_regions[self._albumRandomizer.randrange(0, len(self._cities_regions))]

        else:
            if self._albumRandomizer.randrange(0, 100) < 40:
                title = u"at "
            else:
                title = u"in "
            title += self._countries[self._albumRandomizer.randrange(0, len(self._countries))]

        if self._albumRandomizer.randrange(0, 100) < 10:
            title = title.replace(u"ing", u"in'")

        if self._albumRandomizer.randrange(0, 100) < 10:
            title = title.replace(u" and ", u" & ")

        if self._albumRandomizer.randrange(0, 100) < 10:
            title = title.replace(u"for", u"4")
            title = title.replace(u"four", u"4")
            title = title.replace(u" you ", u" u ")
            title = title.replace(u" one ", u" 1 ")
            title = title.replace(u" love ", u" <3 ")

        title_case_factor = self._albumRandomizer.randrange(0, 100)
        if title_case_factor < 10:
            title = title.lower()
        elif title_case_factor < 80:
            title = title.title()
        else:
            title = title.capitalize()
        title = title.replace(u"'S ", u"'s ")

        if self._albumRandomizer.randrange(0, 100) < 2:
            title = title.replace(u"i", u"1")
            title = title.replace(u"I", u"1")
            title = title.replace(u"s", u"5")
            title = title.replace(u"S", u"5")
            title = title.replace(u"a", u"4")
            title = title.replace(u"A", u"4")
            title = title.replace(u"t", u"7")
            title = title.replace(u"T", u"7")
            title = title.replace(u"o", u"0")
            title = title.replace(u"O", u"0")

        if self._albumRandomizer.randrange(0, 100) < 4:
            if self._albumRandomizer.randrange(0, 100) < 50:
                title = title.replace(u" ", u"")
            else:
                title = title.replace(u" ", u"-")

        return self.decorate_album_title(title)




    def generate_album_data(self, user):
        """ Generates information related to a single photo album """
        title = self.generate_album_title()
        title_generation_tries = 1
        while len(title) < 5 and title_generation_tries < 5:
            title_generation_tries += 1
            title = self.generate_album_title()
        if len(title) < 5:
            title = "<Title generation failed>"
        if len(title) > 255:
            title = title[0:255]

        description = u""
        for i in range(0, self._albumRandomizer.randrange(1, 4)):
            description_words = self._paragraphs[self._albumRandomizer.randrange(0, len(self._paragraphs))].split()
            description_start = self._albumRandomizer.randrange(0, len(description_words))
            description_end = self._albumRandomizer.randrange(0, len(description_words))
            if description_end < description_start:
                description_start, description_end = description_end, description_start
            if description_end - description_start > 15:
                description_end = description_end - (description_end - description_start - 15)
            description += u" ".join(description_words[description_start: description_end]) + u"\n"
        description = description[:-1]
        description = description[0:255]

        if self._albumRandomizer.randrange(0, 99) < 30:
            description = self.decorate_with_html(description)


        is_public = True
        if self._albumRandomizer.randrange(0, 100) > 70:
            is_public = False

        c_maxtimdelta = datetime.now() - user.date_joined
        c_deltaseconds = int(c_maxtimdelta.total_seconds())
        c_randomdeltaseconds = self._nameRandomizer.randrange(0, c_deltaseconds)
        c_datetime = user.date_joined + timedelta(seconds = c_randomdeltaseconds)

        return {
            "title": title,
            "description": description,
            "is_public": is_public,
            "creation_date": c_datetime
        }




    def decorate_album_title(self, title):
        """ May insert some decorations to given title """
        if self._albumRandomizer.randrange(0, 99) < 5:
            title = self.decorate_with_html(title)

        decoration_type_factor = self._albumRandomizer.randrange(0, 99)
        if decoration_type_factor < 90:
            return title                    # no decoration
        elif decoration_type_factor < 94:
            return u":: " + title + u" ::"
        else:
            heart_position_factor = self._albumRandomizer.randrange(0, 99)
            if heart_position_factor < 50:
                return title + u" " + self.compose_heart_string()
            elif heart_position_factor < 85:
                return self.compose_heart_string() + u" " + title
            else:
                return self.compose_heart_string() + u" " + title + u" " + self.compose_heart_string()




    def compose_heart_string(self):
        """ Compose a string of hearts (like <3) to be used in titles """
        hearts = "<3"
        for i in range(0, self._albumRandomizer.randrange(0, 3)):
            hearts += " <3"
        return hearts




    def decorate_with_html(self, text):
        """ Inserts a pair of html tags to the given text """
        text_length = len(text)

        if text_length < 4:
            return text

        tag = self._html_tags[self._albumRandomizer.randrange(0, len(self._html_tags))]
        closing_position = self._albumRandomizer.randrange(len(text) / 2, text_length)
        opening_position = self._albumRandomizer.randrange(0, closing_position)

        while closing_position < text_length and text[closing_position] != " ":
            closing_position += 1

        while opening_position > 0 and text[opening_position - 1] != " ":
            opening_position -= 1

        return text[0:opening_position] + "<" + tag + ">" + \
               text[opening_position: closing_position] + "</" + tag + ">" + \
               text[closing_position: text_length]




    def generate_shopping_cart_data(self, user):
        """ Generates information related to user's shopping cart """

        orderable_albums_qs = Album.ones_visible_to(user)
        orderable_albums_qs_count = orderable_albums_qs.count()

        if not orderable_albums_qs_count:
            return {"success": False}

        number_of_cart_items = self._orderRandomizer.randrange(1, 10)
        if number_of_cart_items > orderable_albums_qs_count:
            number_of_cart_items = orderable_albums_qs_count

        max_album_id = orderable_albums_qs.aggregate(Max("id")).values()[0]
        if not max_album_id:
            return []

        albums = []
        album_ids = []
        missed_tries = 0
        while len(albums) < number_of_cart_items and missed_tries < 10:
            base_album_id = self._orderRandomizer.randrange(0, max_album_id)
            album = orderable_albums_qs.filter(id__gte = base_album_id).order_by("id")[0]
            if not album.id in album_ids:
                albums.append(album)
                album_ids.append(album.id)
            else:
                missed_tries += 1

        if not albums:
            return {"success": False}

        cart_item_infos = []
        for album in albums:
            cart_item_infos.append({
                "album": album,
                "count": self._orderRandomizer.randrange(1, 6),
                "additionDate": datetime.now()
            })

        return {
            "success": True,
            "items": cart_item_infos
        }




    def generate_order_data(self, user):
        """ Generates information related to a single order """
        status = OrderStatus.sent()

        orderable_albums_qs = Album.objects.filter(id__lt = 0)  # empty qs, don't modify
        purchase_date_calculation_counter = 0
        o_maxtimdelta = datetime.now() - user.date_joined
        o_deltaseconds = int(o_maxtimdelta.total_seconds())

        while orderable_albums_qs.count() < 1 and purchase_date_calculation_counter < 10:
            purchase_date_calculation_counter += 1;
            o_randomdeltaseconds = self._orderRandomizer.randrange(0, o_deltaseconds)
            o_datetime = user.date_joined + timedelta(seconds = o_randomdeltaseconds)

            orderable_albums_qs = Album.objects.filter(
                    Q(creationDate__lt = o_datetime),
                    Q(isPublic = True) | Q(owner = user))

        if not orderable_albums_qs.exists():
            return {"success": False}

        valid_addresses_qs = Address.objects.filter(owner__exact = user)
        if not valid_addresses_qs.exists():
            return {"success": False}

        while Order.objects.filter(orderer__exact = user, purchaseDate__exact = o_datetime).exists():
            o_datetime = o_datetime + timedelta(minutes = self._orderRandomizer.randrange(5, 15))

        album_infos = []
        number_of_valid_addresses = valid_addresses_qs.count()

        ids_of_orderable_albums = [id for id in orderable_albums_qs.values_list('id', flat = True)]

        number_of_order_items = self._orderRandomizer.randrange(1, 10)
        if number_of_order_items > orderable_albums_qs.count():
            number_of_order_items = orderable_albums_qs.count()

        for order_item_number in range(1, number_of_order_items + 1):
            album_id = ids_of_orderable_albums[self._orderRandomizer.randrange(0, len(ids_of_orderable_albums))]
            album = orderable_albums_qs.get(id__exact = album_id)
            ids_of_orderable_albums.remove(album_id)
            count = self._orderRandomizer.randrange(1, 6)
            address = valid_addresses_qs[self._orderRandomizer.randrange(0, number_of_valid_addresses)]
            album_infos.append({
                "album": album,
                "count": count,
                "address": address
            })

        return {
            "success": True,
            "purchase_date": o_datetime,
            "status": status,
            "items": album_infos
        }




    def generate_sps_payment_data(self, order):
        """ 
            Generates information related to a single transaction
            via Simple Payments service related to given order.
        """

        secondsFromOrder = self._orderRandomizer.randrange(5, 20)
        transactionDate = order.purchaseDate + timedelta(seconds = secondsFromOrder)

        return {
            "order": order,
            "amount": order.total_price(),
            "transactionDate": transactionDate,
            "referenceCode": self._orderRandomizer.randrange(1234567890, 9876543210),
            "clarification": ""
        }




    def generate_address_data(self):
        """ Generates information related to a single postal address """

        postAddressLine1 = self._street_names[self._addressRandomizer.randrange(0, len(self._street_names))] + u" "
        postAddressLine1 += unicode(self._addressRandomizer.randrange(1, 150))

        if self._addressRandomizer.randrange(0, 100) > 70:
            postAddressLine1 += \
                u" " + self._address_letters[self._addressRandomizer.randrange(0, len(self._address_letters))] + \
                u" " + unicode(self._addressRandomizer.randrange(1, 100))

        zipcode = ""
        for i in range(0, 5):
            zipcode += unicode(self._addressRandomizer.randrange(0, 10))

        city = self._finnish_regions[self._addressRandomizer.randrange(0, len(self._finnish_regions))].capitalize()

        state = None

        country = Country.objects.get(code__exact = "FI")

        return {
            "postAddressLine1": postAddressLine1,
            "postAddressLine2": "",
            "zipCode": zipcode,
            "city": city,
            "state": state,
            "country": country,
        }



