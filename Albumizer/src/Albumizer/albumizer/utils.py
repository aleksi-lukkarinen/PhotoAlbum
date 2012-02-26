# This Python file uses the following encoding: utf-8




def convert_money_into_two_decimal_string(amount):
    """ Returns the price of this album as a string with two decimal places. """
    amount_str = unicode(round(amount, 2))
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




