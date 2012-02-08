# This Python file uses the following encoding: utf-8

from django import template




register = template.Library()



# UNNECESSARY (THERE IS A BUILT-IN FEATURE), CAN BE REMOVED - A.L. 6.2.2012
#
#def mod(value, arg):
#    """ Returns True if value mod arg == 0, otherwise False. """
#    if value % arg == 0:
#        return True
#    else:
#        return False
#
#register.filter("mod", mod)
