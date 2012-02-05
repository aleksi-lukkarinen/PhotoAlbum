# This Python file uses the following encoding: utf-8

import codecs, fileinput, os, string, time
from datetime import datetime, timedelta
from optparse import make_option
from random import Random
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from Albumizer.albumizer.models import Address, Album, Country, UserProfile, Order, OrderItem, Page, PageContent, State



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
    _generated_users = []

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
        time.sleep(0.001)

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


        for user_number in range(1, number_of_users + 1):
            user_data = self.generate_user_data()

            username = user_data["username"]
            unique_username = username
            postfix_counter = 2
            while (User.objects.filter(username__exact = unique_username)):
                unique_username = unicode(username + unicode(postfix_counter))
                postfix_counter += 1

            new_user = User(username = unique_username, email = user_data["email"], password = "salasana")
            new_user.first_name = user_data["first_name"]
            new_user.last_name = user_data["last_name"]
            new_user.date_joined = user_data["serviceConditionsAccepted"]
            new_user.save()
            self._generated_users.append(new_user)

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


            number_of_addresses = self._albumRandomizer.randrange(0, 10)
            for address_number in range(1, number_of_addresses + 1):
                address_data = self.generate_address_data()

                new_address = Address()
                new_address.owner = new_user
                new_address.postAddressLine1 = address_data["postAddressLine1"]
                new_address.postAddressLine2 = address_data["postAddressLine2"]
                new_address.zipCode = address_data["zipCode"]
                new_address.city = address_data["city"]
                new_address.state = address_data["state"]
                new_address.country = address_data["country"]
                new_address.save()

                if verbosity >= 2:
                    message = u"  - address: %s, %s, %s, %s\n" % \
                                      (new_address.postAddressLine1, new_address.zipCode,
                                       new_address.city, unicode(new_address.country))
                    self.stdout.write(message.encode("ascii", "backslashreplace"))
                elif verbosity == 1:
                    self.stdout.write(u"d ")

            if verbosity >= 2:
                self.stdout.write(u"\n")



            number_of_albums = self._albumRandomizer.randrange(min_number_of_albums, max_number_of_albums + 1)
            for album_number in range(1, number_of_albums + 1):
                album_data = self.generate_album_data(new_user)

                album_title = album_data["title"]
                unique_album_title = album_title
                postfix_counter = 2
                while (Album.objects.filter(owner__exact = new_user, title__exact = unique_album_title)):
                    unique_album_title = unicode(album_title + u" " + unicode(postfix_counter))
                    postfix_counter += 1

                new_album = Album()
                new_album.owner = new_user
                new_album.title = unique_album_title
                new_album.description = album_data["description"]
                new_album.isPublic = album_data["is_public"]
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

                    new_page = Page()
                    new_page.album = new_album
                    new_page.pageNumber = page_number
                    new_page.save()

                    if verbosity >= 2:
                        message = u" %d" % page_number
                        self.stdout.write(message.encode("ascii", "backslashreplace"))
                    elif verbosity == 1:
                        self.stdout.write(u"p ")

                if verbosity >= 2:
                    self.stdout.write(u"\n\n")



            number_of_orders = self._orderRandomizer.randrange(min_number_of_orders, max_number_of_orders + 1)
            for order_number in range(0, number_of_orders):
                order_data = self.generate_order_data(new_user)
                if not order_data["success"]:
                    message = u"  - no valid albums and/or addresses to create orders with\n\n"
                    self.stdout.write(message.encode("ascii", "backslashreplace"))
                    break;

                new_order = Order()
                new_order.orderer = new_user
                new_order.status = order_data["status"]
                new_order.save()
                new_order.purchaseDate = order_data["purchase_date"]
                new_order.save()

                if verbosity >= 2:
                    message = u"  - order: %s\n" % new_order.purchaseDate
                    self.stdout.write(message.encode("ascii", "backslashreplace"))
                elif verbosity == 1:
                    self.stdout.write(u"o ")


                number_of_order_items = self._orderRandomizer.randrange(1, 10)
                for order_item_number in range(0, number_of_order_items):
                    order_item_data = self.generate_order_item_data(new_user, new_order)

                    if order_item_data["no_more_albums"]:
                        break;

                    new_order_item = OrderItem()
                    new_order_item.order = new_order
                    new_order_item.album = order_item_data["album"]
                    new_order_item.count = order_item_data["count"]
                    new_order_item.deliveryAddress = order_item_data["address"]
                    new_order_item.save()

                    if verbosity >= 2:
                        message = u"            (%d) %s, %d, %s\n" % \
                                        (order_item_number, new_order_item.album, new_order_item.count,
                                         unicode(new_order_item.deliveryAddress))
                        self.stdout.write(message.encode("ascii", "backslashreplace"))
                    elif verbosity == 1:
                        self.stdout.write(u"i ")

                if verbosity >= 2:
                    self.stdout.write(u"\n")



            if verbosity >= 1:
                self.stdout.write(u"\n")

        if verbosity >= 1:
            self.stdout.write(u"\nAll data has been created. Program created users with the following usernames:\n")
            self.stdout.write(self._generated_users[0].username.encode("ascii", "backslashreplace"))
            for i in range(1, number_of_users - 1):
                self.stdout.write(u", " + self._generated_users[i].username.encode("ascii", "backslashreplace"))
            if number_of_users > 1:
                self.stdout.write(u" and " +
                        self._generated_users[number_of_users - 1].username.encode("ascii", "backslashreplace"))
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


    def generate_album_data(self, user):
        """ Generates information related to a single photo album """
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

        title = self.decorate_album_title(title)

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


    def generate_order_data(self, user):
        """ Generates information related to a single order as a whole"""
        status = self._orderRandomizer.randrange(0, 4)

        valid_addresses_found = False
        orderable_albums_found = False
        purchase_date_calculation_counter = 0
        o_maxtimdelta = datetime.now() - user.date_joined
        o_deltaseconds = int(o_maxtimdelta.total_seconds())
        while not orderable_albums_found and purchase_date_calculation_counter < 10:
            purchase_date_calculation_counter += 1;
            o_randomdeltaseconds = self._nameRandomizer.randrange(0, o_deltaseconds)
            o_datetime = user.date_joined + timedelta(seconds = o_randomdeltaseconds)

            if Album.objects.filter(Q(creationDate__lt = o_datetime), Q(isPublic = True) | Q(owner = user)):
                orderable_albums_found = True

        if orderable_albums_found:
            while Order.objects.filter(orderer__exact = user, purchaseDate__exact = o_datetime):
                o_datetime = o_datetime + timedelta(milliseconds = 1)

            if Address.objects.filter(owner__exact = user):
                valid_addresses_found = True

        return {
            "success": (orderable_albums_found and valid_addresses_found),
            "purchase_date": o_datetime,
            "status": status
        }


    def generate_order_item_data(self, user, order):
        """ Generates information related to a single line of an order """
        count = self._orderRandomizer.randrange(1, 6)

        valid_addresses_qs = Address.objects.filter(owner__exact = user)
        address = valid_addresses_qs[self._orderRandomizer.randrange(0, valid_addresses_qs.count())]

        album = None
        no_more_albums = False
        ids_of_albums_in_order = OrderItem.objects.filter(order = order).values_list('album', flat = True)
        orderable_albums_qs = Album.objects.filter(
                Q(creationDate__lt = order.purchaseDate),
                Q(isPublic = True) | Q(owner = user),
                ~ Q(id__in = ids_of_albums_in_order))
        if orderable_albums_qs.count() < 1:
            no_more_albums = True
        else:
            album = orderable_albums_qs[self._orderRandomizer.randrange(0, orderable_albums_qs.count())]

        return {
            "no_more_albums": no_more_albums,
            "album": album,
            "count": count,
            "address": address
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



