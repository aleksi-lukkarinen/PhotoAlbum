# This Python file uses the following encoding: utf-8

from django.db import models

class User(models.Model):
    userName=models.CharField(
        max_length=255)
    facebookID=models.CharField(
        max_length=255)
    
class Album(models.Model):
    """ Represents a single album """

    title = models.CharField(
       max_length = 255,
       unique = True
    )
    description = models.TextField()
    isPublic =models.BooleanField()
    owner =models.ForeignKey(User)
    
class Page(models.Model):
    """Represents a single page"""
    pageNumber =models.IntegerField()
    layoutID=models.CharField(
        max_length= 255)
    album=models.ForeignKey(Album)
    
class PageContent(models.Model):
    """Represents content in a placeholder"""
    placeHolderID = models.CharField(
        max_length=255)
    content=models.CharField(
        max_length=255)
    page=models.ForeignKey(Page)
    

class Country(models.Model):
    code=models.CharField(
        max_length=10)
    name=models.CharField(
        max_length=255)
     
class Address(models.Model):
    streetAddress=models.CharField(
        max_length=255)
    postOffice=models.CharField(
        max_length=255)
    postCode=models.CharField(
        #10 digits is the maximum length for post codes globally according to Wikipedia
        max_length=10)    
    country=models.ForeignKey(Country)
    
class Order(models.Model):
    purchaseDate=models.DateTimeField()
    status=models.IntegerField()
    customer=models.ForeignKey(User)
    
class OrderItem(models.Model):
    count=models.IntegerField()
    order=models.ForeignKey(Order)
    album=models.ForeignKey(Album)
    deliveryAddress=models.ForeignKey(Address)





