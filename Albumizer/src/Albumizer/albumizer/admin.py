# This Python file uses the following encoding: utf-8

from django.contrib import admin
from django.contrib.auth.models import User
from models import UserProfile, FacebookProfile, Album, Page, PageContent, Country, State, \
        Address, ShoppingCartItem, Order, SPSPayment, OrderStatus, OrderItem




class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'homePhone', 'serviceConditionsAccepted')
    list_filter = ('gender', 'serviceConditionsAccepted')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'serviceConditionsAccepted'
    raw_id_fields = ('user',)




class FacebookProfileAdmin(admin.ModelAdmin):
    list_display = ('userProfile', 'facebookID', 'profileUrl', 'lastQueryTime')
    search_fields = ('facebookID', 'userProfile__user__first_name', 'userProfile__user__last_name')
    date_hierarchy = 'lastQueryTime'
    raw_id_fields = ('userProfile',)




class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'owning_customer', 'creationDate', 'isPublic', 'description')
    list_filter = ('isPublic',)
    search_fields = ('title', 'owner__username', 'owner__first_name', 'owner__last_name', 'description')
    date_hierarchy = 'creationDate'
    raw_id_fields = ('owner',)

    def owning_customer(self, obj):
        return obj.owner
    owning_customer.short_description = 'owning user'
    owning_customer.admin_order_field = 'owner'




class PageAdmin(admin.ModelAdmin):
    list_display = ('album', 'pageNumber', 'layoutID')
    search_fields = ('album__title',)
    raw_id_fields = ('album',)




class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page', 'placeHolderID', 'content')
    raw_id_fields = ('page',)




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
    raw_id_fields = ('owner',)




class ShoppingCartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'count', 'additionDate')
    search_fields = ('user__username', 'album__title')
    date_hierarchy = 'additionDate'
    raw_id_fields = ('user', 'album')




class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderer', 'purchaseDate', 'status')
    list_filter = ('status',)
    search_fields = ('customer__username',)
    date_hierarchy = 'purchaseDate'
    raw_id_fields = ('orderer',)




class SPSPaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'transactionDate', 'amount', 'referenceCode', 'clarification')
    search_fields = ('referenceCode', 'clarification')
    date_hierarchy = 'transactionDate'
    raw_id_fields = ('order',)




class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('code',)




class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('album', 'count', 'order', 'date_of_order')
    search_fields = ('order__orderer__username', 'album__title')

    def date_of_order(self, obj):
        return obj.order.purchaseDate
    date_of_order.short_description = 'date of order'
    raw_id_fields = ('order', 'album', 'deliveryAddress')




admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(FacebookProfile, FacebookProfileAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(PageContent, PageContentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(ShoppingCartItem, ShoppingCartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(SPSPayment, SPSPaymentAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

