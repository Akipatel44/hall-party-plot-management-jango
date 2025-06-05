# File: hall_app/templatetags/custom_filters.py
from django import template

register = template.Library()

# Example filter - you can add your own custom filters here
@register.filter
def currency(value):
    """Format a number as currency (₹)"""
    return f"₹{value}"

# Example filter for calculating total price
@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    return value * arg

# Add any other custom filters you need here