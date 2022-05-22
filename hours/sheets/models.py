from django.db import models
from django.contrib.auth.models import User
import jdatetime as jdt

def current_year() -> int:
    return jdt.date.today().year

def current_month() -> int:
    return jdt.date.today().month

def current_mont_days(month: int, isleap: bool) -> int:
    """gets a month and returns that date's month days number with leap year consideration
       (for jalali months)"""

    days_num = jdt.j_days_in_month[month - 1]
    if month == 12 and isleap:
        days_num += 1
    return days_num

class Sheet(models.Model):
    user = models.ForeignKey(User, verbose_name="user", related_name="sheets", on_delete=models.CASCADE)
    year = models.PositiveIntegerField('year', default=current_year)
    month = models.PositiveIntegerField('month', default=current_month)
    data = models.JSONField(default=list)

    def __str__(self):
        return f"{self.user.username}_{self.year}_{self.month}"

    def save(self,  *args, **kwargs):
        if not len(self.data):
            self.data = Sheet.empty_sheet_data()
        super(Sheet, self).save( *args, **kwargs)

    @classmethod
    def empty_sheet_data(cls):
        today = jdt.date.today()
        month, year = today.month, today.year
        days_num = current_mont_days(month, today.isleap())
        data = [{
            "Day": day + 1,
            "WeekDay": jdt.date.j_weekdays_short_en[jdt.date(year, month, day + 1).weekday()],
        } for day in range(days_num)]
        return data



class ProjectFamily(models.Model):
    name = models.CharField('name', max_length=150)

    def __str__(self):
        return self.name

class Project(models.Model):
    family = models.ForeignKey(ProjectFamily, verbose_name="family", related_name="projects", on_delete=models.CASCADE, null=True)
    name = models.CharField('name', max_length=150)

    def __str__(self):
        return f"{self.family.name}-{self.name}"