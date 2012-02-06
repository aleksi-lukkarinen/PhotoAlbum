# This Python file uses the following encoding: utf-8

from django import template




register = template.Library()




def mod(value, arg):
    """ Returns True if value mod arg == 0, otherwise False. """
    if value % arg == 0:
        return True
    else:
        return False

register.filter("mod", mod)
