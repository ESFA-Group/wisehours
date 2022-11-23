from django.db import models
from django.contrib.auth.models import AbstractUser

import pandas as pd
import jdatetime as jdt


class User(AbstractUser):
    wage = models.IntegerField('wage', default=0)

    def __str__(self):
        return self.get_full_name()
    
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
    mean = models.PositiveIntegerField('mean', default=0)       # in minutes
    total = models.PositiveIntegerField('total', default=0)     # in minutes
    submitted = models.BooleanField('submitted', default=False)

    def __str__(self):
        return f"{self.user.username}_{self.year}_{self.month}"

    def save(self,  *args, **kwargs):
        if not len(self.data):
            today = jdt.date.today()
            month, year = today.month, today.year
            self.data = Sheet.empty_sheet_data(year, month)
        df = self.transform()
        self.mean = self.get_mean(df)
        self.total = self.get_total(df)
        super(Sheet, self).save( *args, **kwargs)

    @classmethod
    def empty_sheet_data(cls, year: int, month: int) -> list:
        is_leap = jdt.date(year, month, 1).isleap()
        days_num = current_mont_days(month, is_leap)
        data = [{
            "Day": day + 1,
            "WeekDay": jdt.date.j_weekdays_short_en[jdt.date(year, month, day + 1).weekday()],
        } for day in range(days_num)]
        return data

    def hhmm2minutes(self, string: str) -> int:
        """converter function
           convert string with hh:mm fromat to minutes
        """
        try:
            h, m = string.split(":")
            return int(h) * 60 + int(m)
        except:
            return 0

    def parse_project_porp(self, string: str) -> int:
        try:
            return int(string.replace("%", "").strip()) / 100
        except:
            return 0

    def get_sheet_projects(self, df: pd.DataFrame) -> list:
        defaults = ['Day', 'WeekDay', 'Hours']
        projects = df.columns.difference(defaults)
        return list(projects)

    def transform(self) -> pd.DataFrame:
        """transforms sheet data to a pandas DataFrame.
           all project cols and "Hours" col will contain minutes instead of hh:mm and percentage format
        """
        df = pd.DataFrame(self.data)
        if "Hours" not in df.columns:
            return df
        projects = self.get_sheet_projects(df)
        df["Hours"] = df["Hours"].apply(self.hhmm2minutes)
        df[projects] = df[projects].applymap(self.parse_project_porp).apply(lambda col: col * df["Hours"])
        return df

    def get_mean(self, df: pd.DataFrame) -> int:
        if "Hours" not in df.columns:
            return 0
        df = df.loc[df["Hours"] > 0]
        return df["Hours"].sum() / len(df)

    def get_total(self, df: pd.DataFrame) -> int:
        if "Hours" not in df.columns:
            return 0
        return df["Hours"].sum()

class ProjectFamily(models.Model):
    name = models.CharField('name', max_length=150)

    class Meta:
        verbose_name_plural = "Projec Families"

    def __str__(self):
        return self.name

class Project(models.Model):
    family = models.ForeignKey(ProjectFamily, verbose_name="family", related_name="projects", on_delete=models.CASCADE, null=True)
    name = models.CharField('name', max_length=150)

    def __str__(self):
        return f"{self.family.name}-{self.name}"