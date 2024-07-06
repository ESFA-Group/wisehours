from django import template
from django.utils.safestring import mark_safe
import jdatetime as jdt
register = template.Library()

def current_mont_days(month: int, isleap: bool) -> int:
    """gets a month and returns that date's month days number with leap year consideration
    (for jalali months)"""

    days_num = jdt.j_days_in_month[month - 1]
    if month == 12 and isleap:
        days_num += 1
    return days_num

@register.filter(name="make_range")
def make_range(num):
    return range(int(num))


@register.filter(name="get_days_in_month")
def get_days_in_month(monthNumber: int, isleap: bool=False):
    days = current_mont_days(monthNumber, isleap)
    return range(1, days+1)

@register.filter(name="render_month_options")
def render_month_options(selected_month=None):
    months = [
        (1, "Farvardin"),
        (2, "Ordibehesht"),
        (3, "Khordad"),
        (4, "Tir"),
        (5, "Mordad"),
        (6, "Shahrivar"),
        (7, "Mehr"),
        (8, "Aban"),
        (9, "Azar"),
        (10, "Dey"),
        (11, "Bahman"),
        (12, "Esfand"),
    ]

    options_html = ""
    for value, name in months:
        selected_attr = " selected" if value == selected_month else ""
        options_html += f'<option value="{value}"{selected_attr}>{name}</option>'

    return mark_safe(options_html)