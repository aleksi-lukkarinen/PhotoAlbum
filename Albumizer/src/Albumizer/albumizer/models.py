# This Python file uses the following encoding: utf-8

from django.db import models



class Album(models.Model):
    """ Representes a single album """

    title = models.CharField(
       max_length = 255,
       unique = True
    )
    description = models.TextField()



