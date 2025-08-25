from django.views.generic.base import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from sheets.customDecorators import *
from django.db.models import QuerySet

import pandas as pd
import numpy as np
import io
import json
import jdatetime as jdt
import openpyxl
from io import BytesIO

from sheets.models import Sheet, User
from sheets.api_views import MonthlyReportApiView


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Ensure that arbitrary objects -- such as Django model
        # instances or querysets -- can be serialized as JSON.
        return context


@method_decorator(decorators, name="dispatch")
class BaseView(JSONResponseMixin, TemplateView):
    template_name = ""
    extra_context = None

    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get("format") == "json":
            return self.render_to_json_response(context)
        else:
            return super().render_to_response(context)

    def get_context_data(self, *args, **kwargs):
        context = super(BaseView, self).get_context_data(*args, **kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        context.update(self.get_context())
        return context

    def get_context(self) -> dict:
        """
        adds custom context to response
        can be overridden in children classes
        """
        context = dict()
        return context


class HomePageView(BaseView):
    template_name = "home.html"


class HoursView(BaseView):
    template_name = "hours.html"


class PersonalInfoView(BaseView):
    template_name = "personal_info.html"

    def post(self, request):
        context = {}
        if request.POST.get("saveUserData"):
            self.save_user_data(request)
            context = {"submitted": True}
            return super(TemplateView, self).render_to_response(context)

    def save_user_data(self, request):
        request.user.first_name = request.POST.get("firstName", "")
        request.user.last_name = request.POST.get("lastName", "")
        request.user.first_name_p = request.POST.get("firstNameP", "")
        request.user.last_name_p = request.POST.get("lastNameP", "")
        request.user.national_ID = request.POST.get("nationalID", "")
        request.user.dob = request.POST.get("dob", "")
        request.user.email = request.POST.get("email", "")
        request.user.mobile1 = request.POST.get("mobile1", "")
        request.user.mobile2 = request.POST.get("mobile2", "")
        request.user.emergency_phone = request.POST.get("emergencyPhone", "")
        request.user.address = request.POST.get("address", "")
        request.user.laptop_info = request.POST.get("laptopInfo", "")
        request.user.bank_name = request.POST.get("bankName", "")
        request.user.card_number = request.POST.get("cardNumber", "")
        request.user.account_number = request.POST.get("accountNumber", "")
        request.user.SHEBA_number = request.POST.get("SHEBANumber", "")
        if request.FILES.get("personalImage"):
            personal_image = request.FILES["personalImage"]
            request.user.personal_image.save(personal_image.name, personal_image)
        if request.FILES.get("nationalIDFrontImage"):
            national_ID_front_image = request.FILES["nationalIDFrontImage"]
            request.user.national_ID_front_image.save(
                national_ID_front_image.name, national_ID_front_image
            )
        if request.FILES.get("nationalIDBackImage"):
            national_ID_back_image = request.FILES["nationalIDBackImage"]
            request.user.national_ID_back_image.save(
                national_ID_back_image.name, national_ID_back_image
            )
        if request.FILES.get("birthCertFirstPage"):
            birth_cert_first_page = request.FILES["birthCertFirstPage"]
            request.user.birth_cert_first_page.save(
                birth_cert_first_page.name, birth_cert_first_page
            )
        if request.FILES.get("birthCertChangesPage"):
            birth_cert_changes_page = request.FILES["birthCertChangesPage"]
            request.user.birth_cert_changes_page.save(
                birth_cert_changes_page.name, birth_cert_changes_page
            )
        if request.FILES.get("studentCard"):
            student_card = request.FILES["studentCard"]
            request.user.student_card.save(student_card.name, student_card)
        if request.FILES.get("militaryServiceCard"):
            military_service_card = request.FILES["militaryServiceCard"]
            request.user.military_service_card.save(
                military_service_card.name, military_service_card
            )
        request.user.save()


class DailyReport(BaseView):
    template_name = "daily_report.html"

    def post(self, request):
        context = {}
        if request.POST.get("saveUserData"):
            self.save_user_data(request)
            context = {"submitted": True}
            return super(TemplateView, self).render_to_response(context)


@method_decorator([daily_report_manager_required], name="dispatch")
class DailyReportManagement(BaseView):
    template_name = "daily_report_management.html"

    # def get_context_data(self, **kwargs):
    #     """
    #     Override this method to add context to the template.
    #     """
    #     context = super().get_context_data(**kwargs)
        
    #     if self.request.user.is_staff:
    #         user_role = 'admin'
    #     elif self.request.user.groups.filter(name='Manager').exists():
    #         user_role = 'manager'
    #     else:
    #         user_role = 'user'
        
    #     context['user_role'] = user_role
        
    #     return context    
        
    def post(self, request):
        context = {}
        if request.POST.get("saveUserData"):
            self.save_user_data(request)
            context = {"submitted": True}
            return super(TemplateView, self).render_to_response(context)


class HoursInfoView(BaseView):
    template_name = "hours_info.html"


@method_decorator([project_report_manager_required], name="dispatch")
class ReportsView(BaseView):
    template_name = "reports.html"


@method_decorator([financial_manager_required], name="dispatch")
class PaymentHandleView(BaseView):
    template_name = "payment.html"


@method_decorator([financial_manager_required], name="dispatch")
class AlterPaymentHandleView(BaseView):
    template_name = "alter_payment.html"


class FoodFormView(BaseView):
    template_name = "food_form.html"


@method_decorator([food_manager_required], name="dispatch")
class FoodDataView(BaseView):
    template_name = "food_data.html"


@method_decorator([project_report_manager_required], name="dispatch")
class DetailedReportView(View):

    def get(self, request):

        year = request.GET.get("year")
        month = request.GET.get("month")
        sheets = Sheet.objects.filter(year=year, month=month)

        buffer = io.BytesIO()
        writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
        for sheet in sheets:
            df = pd.DataFrame(sheet.data)
            df.to_excel(writer, sheet_name=sheet.user.get_full_name())
        writer.close()

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f"attachment; filename=detailed_report_{year}_{month}.xlsx"
        )
        return response


@method_decorator([project_report_manager_required], name="dispatch")
class MainReportView(View):

    def get(self, request):

        year = request.GET.get("year")
        month = request.GET.get("month")
        sheets = Sheet.objects.filter(year=year, month=month)
        sheetless_users = User.objects.select_related().exclude(
            sheets__year=year, sheets__month=month
        )

        hours, payments = MonthlyReportApiView.get_sheet_sums(sheets, sheetless_users)
        hours_df = pd.DataFrame(hours).transpose()
        hours_df = hours_df.reindex(np.roll(hours_df.index, 1))
        payments_df = pd.DataFrame(payments).transpose()

        buffer = io.BytesIO()
        writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
        hours_df.to_excel(writer, sheet_name="hours")
        payments_df.to_excel(writer, sheet_name="payments")
        writer.close()

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f"attachment; filename=main_report_{year}_{month}.xlsx"
        )
        return response


@method_decorator([project_report_manager_required], name="dispatch")
class UsersMonthlyReportView(View):

    def get(self, request):

        year = request.GET.get("year")
        users = User.objects.all()
        data = dict()
        for u in users:
            sheets = Sheet.objects.filter(year=year, user=u).values("month", "total")
            data[u.get_full_name()] = {
                sheet["month"]: round(sheet["total"] / 60, 2) for sheet in sheets
            }

        df = pd.DataFrame(data)
        df = df.transpose()
        df = df[sorted(df)]
        df["total"] = df.sum(axis=1)

        buffer = io.BytesIO()
        writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="hours")
        writer.close()

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f"attachment; filename=users_monthly_report_{year}.xlsx"
        )
        return response


@method_decorator([project_report_manager_required], name="dispatch")
class ProjectsYearlyReportView(View):

    def get(self, request):

        year = request.GET.get("year")
        d = dict()
        for i in range(1, 13):
            qs = Sheet.objects.filter(month=i, year=year)
            d[i] = self.get_info(qs).to_dict()

        for month, data in d.items():
            for prj, minute in data.items():
                d[month][prj] = round(minute / 60, 2)

        df = pd.DataFrame(d)
        df = df.transpose()
        df["total"] = df.sum(axis=1)
        df.loc["total"] = df.sum()

        buffer = io.BytesIO()
        writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="hours")
        writer.close()

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f"attachment; filename=projects_yearly_report_{year}.xlsx"
        )
        return response

    def get_info(self, queryset: QuerySet) -> pd.Series:
        if not queryset.count():
            return pd.Series(dtype="float64")
        df_all = pd.DataFrame()
        for sheet in queryset:
            df = sheet.transform()
            if "Hours" not in df:
                continue
            df.drop(["Day", "WeekDay", "Hours"], axis=1, inplace=True)
            df_all = df_all.add(df, fill_value=0)
        return df_all.sum()


@method_decorator([financial_manager_required], name="dispatch")
class PaymentExportView(View):

    def post(self, request):
        ids = json.loads(request.POST.get("IDs"))
        month_names_en = jdt.date.j_months_en
        month_names_fa = jdt.date.j_months_fa
        payment_method = request.POST.get("paymentMethod")
        payment_type = request.POST.get("paymentType")
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        export_type = request.POST.get("exportType")
        string = str()
        melli_count = 0
        for i in ids:
            user = User.objects.get(pk=i)
            sheet = Sheet.objects.get(user=user, month=month, year=year)
            amount = (
                sheet.get_base_payment()
                if payment_type == "base"
                else sheet.get_complementary_payment()
            )
            amount = int(amount)
            match export_type:
                case "default":
                    string = self.fill_default_export(
                        string,
                        payment_method,
                        month_names_en,
                        user,
                        amount,
                        month,
                        year,
                    )
                case "melli2":
                    melli_count += 1
                    string += self.fill_melli_new_export(
                        payment_method,
                        user,
                        amount,
                        melli_count
                )
                case "melli":
                    string = self.fill_melli_export(
                        string,
                        payment_method,
                        user,
                        amount,
                    )
                case "sepah":
                    string = self.fill_sepah_export(
                        string,
                        payment_method,
                        month_names_fa,
                        user,
                        amount,
                        month,
                        year,
                    )
                    
        if export_type == "melli":
            file_name = f"{export_type}_{year}_{month}.txt"
            buffer = io.StringIO(string)
            response = HttpResponse(buffer.getvalue(), content_type="text/plain")
            response["Content-Disposition"] = f"attachment; filename={file_name}"
            return response
        
        file_name = f"{export_type}_{year}_{month}.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        
        if export_type == "melli2":
            header = [
                "ردیف",
                "مبلغ (ریال)",
                "شماره حساب ملی / شبا مقصد",
                "نام گیرنده",
                "بابت",
                "شناسه واریز (اختیاری - حداکثر 35 کاراکتر)",
                "کد ملی (اختیاری)",
            ]
            ws.append(header)
            
        elif export_type == "sepah":
            header = [
                "شماره شبای مقصد",
                "مبلغ واریز(ریال)",
                "شرح مقصد",
                "شناسه واریز/شماره قبض",
            ]
            ws.append(header)

        for _, line in enumerate(string.splitlines(), start=1):
            columns = line.split(",")
            ws.append(columns)

        # Save the workbook to an in-memory buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # Prepare the response
        response = HttpResponse(
            buffer,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response

    def fill_default_export(
        self, string, payment_method, month_names, user, amount, month, year
    ):
        if payment_method == "AN":  # account number
            string += f"{user.account_number},{amount},salary {month_names[month - 1]} {year}\n"
        elif payment_method == "SN":
            string += f"{user.SHEBA_number},{amount},{user.first_name},{user.last_name},salary {month_names[month - 1]} {year},\n"
        return string

    def fill_melli_export(self, string, payment_method, user, amount):
        if payment_method == "AN":
            string += f"{amount} , {user.account_number} , 1 , {user.first_name} {user.last_name}\n"
        elif payment_method == "SN":
            string += (
                f"{amount},IR{user.SHEBA_number},1,{user.first_name} {user.last_name}\n"
            )
        return string

    def fill_melli_new_export(self, payment_method, user, amount, count):
        name_p = f"{user.first_name_p} {user.last_name_p}"
        if payment_method == "AN":
            return f"{count},{amount},{user.account_number},{name_p},حقوق,,{user.national_ID}\n"
        elif payment_method == "SN":
            return f"{count},{amount},IR{user.SHEBA_number},{name_p},حقوق,,{user.national_ID}\n"
        return ""

    def fill_sepah_export(
        self, string, payment_method, month_names, user, amount, month, year
    ):
        if payment_method == "AN":
            string += f"{user.account_number},{amount},بابت حقوق {month_names[month - 1]} ماه {year},\n"
        elif payment_method == "SN":
            string += f"{user.SHEBA_number},{amount},بابت حقوق {month_names[month - 1]} ماه {year},\n"
        return string


@method_decorator([financial_manager_required], name="dispatch")
class PaymentExcelExportView(View):

    def post(self, request, year: str, month: str):
        sheets = Sheet.objects.filter(year=year, month=month)

        payments_info = []
        for sheet in sheets:
            if sheet.user == None:
                continue
            payment_info = {
                "userID": sheet.user_id,
                "user": sheet.user.get_full_name(),
                "bankName": sheet.user.bank_name,
            }
            payment_info.update(sheet.get_payment_info())

            payments_info.append(payment_info)

        df = pd.DataFrame(payments_info)

        buffer = io.BytesIO()
        writer = pd.ExcelWriter(buffer, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="hours", index=False)
        writer.close()

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f"attachment; filename=payment_report_{year}_{month}.xlsx"
        )
        return response


@method_decorator([financial_manager_required], name="dispatch")
class PaymentExcelImportView(View):

    def post(self, request, year: str, month: str):

        file = request.FILES["file"]
        df = pd.read_excel(file)
        df.fillna(0, inplace=True)

        not_found_name = []

        for index, row in df.iterrows():
            user_id = row["userID"]
            wage = row["wage"]
            base = row["basePayment"]
            r1 = row["reduction1"]
            r2 = row["reduction2"]
            add1 = row["addition1"]
            row = row.to_dict()
            try:
                current_sheet = Sheet.objects.get(
                    user_id=user_id, year=year, month=month
                )
            except:
                not_found_name.append(
                    {"name": row["user_name"], "user_id": row["user_id"]}
                )
                continue
            current_sheet.wage = wage
            current_sheet.base_payment = base
            current_sheet.reduction1 = r1
            current_sheet.reduction2 = r2
            current_sheet.reduction3 = row["reduction3"]
            current_sheet.food_reduction = row["food_reduction"]
            current_sheet.addition1 = add1
            current_sheet.addition2 = row["addition2"]
            current_sheet.payment_status = row["paymentStatus"]
            current_sheet.save()

            user = User.objects.get(pk=user_id)
            user.wage = wage
            user.base_payment = base
            user.reduction1 = r1
            user.reduction2 = r2
            user.addition1 = add1
            user.save()

            user_sheets = Sheet.objects.filter(user=user, year=year, month__gte=month)
            for sheet in user_sheets:
                sheet.wage = wage
                sheet.base_payment = base
                sheet.reduction1 = r1
                sheet.reduction2 = r2
                sheet.addition1 = add1
                sheet.save()

        response_data = {
            "message": "success",
            "users_not_found": not_found_name,
        }

        return JsonResponse(response_data)
