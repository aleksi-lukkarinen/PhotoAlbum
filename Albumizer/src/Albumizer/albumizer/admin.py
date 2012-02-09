# This Python file uses the following encoding: utf-8

from django.contrib import admin
from django.contrib.auth.models import User
from models import UserProfile, FacebookProfile, Album, Page, PageContent, Country, State, Address, Order, OrderItem




class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'homePhone', 'serviceConditionsAccepted')
    list_filter = ('gender', 'serviceConditionsAccepted')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'serviceConditionsAccepted'




class FacebookProfileAdmin(admin.ModelAdmin):
    list_display = ('userProfile', 'facebookID', 'token', 'profileUrl', 'lastQueryTime', 'rawResponse')
    search_fields = ('facebookID', 'userProfile__user__first_name', 'userProfile__user__last_name')
    date_hierarchy = 'lastQueryTime'




class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owning_customer', 'creationDate', 'isPublic', 'description')
    list_filter = ('isPublic',)
    search_fields = ('title', 'owner__username', 'owner__first_name', 'owner__last_name', 'description')
    date_hierarchy = 'creationDate'

    def owning_customer(self, obj):
        return obj.owner
    owning_customer.short_description = 'owning user'
    owning_customer.admin_order_field = 'owner'




class PageAdmin(admin.ModelAdmin):
    list_display = ('album', 'pageNumber', 'layoutID')
    search_fields = ('album__title',)




class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page', 'placeHolderID', 'content')




class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    list_max_show_all = 500




class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_max_show_all = 500




class AddressAdmin(admin.ModelAdmin):
    list_display = ('owner', 'postAddressLine1', 'zipCode', 'city', 'state', 'country')
    search_fields = ('owner__username', 'postAddressLine1', 'zipCode', 'city', 'state__name', 'country__name')
    list_editable = ('postAddressLine1', 'zipCode', 'city', 'state', 'country')




class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderer', 'purchaseDate', 'status')
    list_filter = ('status',)
    search_fields = ('customer__username',)
    date_hierarchy = 'purchaseDate'




class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('album', 'count', 'order', 'date_of_order')
    search_fields = ('order__orderer__username', 'album__title')

    def date_of_order(self, obj):
        return obj.order.purchaseDate
    date_of_order.short_description = 'date of order'




admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(FacebookProfile, FacebookProfileAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(PageContent, PageContentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

