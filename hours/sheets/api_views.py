from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import QuerySet, Sum
from sheets import customPermissions
from django.http import HttpResponse


import jdatetime as jdt
import pandas as pd
import io
import re

from sheets.models import Project, Sheet, User, Food_data
from sheets.serializers import ProjectSerializer, SheetSerializer


def camel_to_snake(s: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    snake = pattern.sub("_", s).lower()
    return snake


def _setup_sheet(sheet, user):
    sheet.user_name = user.get_full_name()
    sheet.wage = user.wage
    sheet.base_payment = user.base_payment
    sheet.reduction1 = user.reduction1
    sheet.reduction2 = user.reduction2
    sheet.reduction3 = user.reduction3
    sheet.food_reduction = user.food_reduction
    sheet.addition1 = user.addition1
    sheet.addition2 = user.addition2
    return sheet


class ProjectListApiView(ListAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class SheetApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year: str, month: str):
        try:
            sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        except Sheet.DoesNotExist:
            empty_sheet_data = Sheet.empty_sheet_data(int(year), int(month))
            res = {
                "data": empty_sheet_data,
                "month": month,
                "year": year,
                "submitted": False,
            }
            return Response(res, status=status.HTTP_200_OK)

        serializer = SheetSerializer(sheet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, year: str, month: str):
        if "saveSheet" in request.data:
            user = self.request.user
            sheet, created = Sheet.objects.get_or_create(
                user=user, year=year, month=month
            )
            if created:
                sheet.user_name = user.get_full_name()
                sheet.wage = user.wage
                sheet.base_payment = user.base_payment
                sheet.reduction1 = user.reduction1
                sheet.reduction2 = user.reduction2
                sheet.reduction3 = user.reduction3
                sheet.food_reduction = user.food_reduction
                sheet.addition1 = user.addition1
                sheet.addition2 = user.addition2
            data = request.data.get("data", [])
            data.sort(key=lambda row: int(row.get("Day", 0)))
            sheet.data = request.data["data"]
            sheet.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        elif "editSheet" in request.data:
            data = request.data.get("row", {})
            field = request.data.get("field", "")
            user = User.objects.get(pk=data["userID"])
            update_data = {camel_to_snake(field): data[field]}
            sheet = Sheet.objects.filter(user=user, year=year, month=month)
            sheet.update(**update_data)
            return Response(sheet.first().get_payment_info(), status=status.HTTP_200_OK)

    def put(self, request, year: str, month: str):
        try:
            sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        except Sheet.DoesNotExist:
            return Response({"notFound": True}, status=status.HTTP_404_NOT_FOUND)
        if (
            request.user.check_info()
        ):  # if the user has entered needed personal information
            sheet.submitted = True
            sheet.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response({"flaw": True}, status=status.HTTP_200_OK)


class InfoApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        today = jdt.date.today()
        month, year = today.month, today.year

        all_sheets = Sheet.objects.all()

        user_month_info = self.get_info(
            all_sheets.filter(user=request.user, month=month)
        )
        user_year_info = self.get_info(
            all_sheets.filter(user=request.user, year=year).exclude(month=month)
        )
        user_year_info = user_year_info.add(user_month_info, fill_value=0)
        user_tot_info = self.get_info(
            all_sheets.filter(user=request.user).exclude(year=year)
        )
        user_tot_info = user_tot_info.add(user_year_info, fill_value=0)

        esfa_month_info = self.get_info(all_sheets.filter(month=month))
        esfa_year_info = self.get_info(
            all_sheets.filter(year=year).exclude(month=month)
        )
        esfa_year_info = esfa_year_info.add(esfa_month_info, fill_value=0)
        esfa_tot_info = self.get_info(all_sheets.exclude(year=year))
        esfa_tot_info = esfa_tot_info.add(esfa_year_info, fill_value=0)

        last_month = month - 1 if month != 1 else 12
        monthly_sheets = (
            Sheet.objects.filter(year=year, user=request.user)
            .values("total", "month")
            .order_by("month")
        )
        user_monthly_hours = list(monthly_sheets)
        info = {
            "user_month_info": user_month_info.to_dict(),
            "user_year_info": user_year_info.to_dict(),
            "user_tot_info": user_tot_info.to_dict(),
            "esfa_month_info": esfa_month_info.to_dict(),
            "esfa_year_info": esfa_year_info.to_dict(),
            "esfa_tot_info": esfa_tot_info.to_dict(),
            "last_hero": self.get_hero(year, last_month),
            "last_esfa_mean": self.get_month_mean(year, last_month),
            "last_user_mean": self.get_month_mean(year, last_month, user=request.user),
            "user_monthly_hours": user_monthly_hours,
        }

        # print('info is:', info)
        return Response(info, status=status.HTTP_200_OK)

    def get_hero(self, year: int, month: int) -> str:
        hero_name = "Anonymous Anonymousian"
        hero = Sheet.objects.filter(year=year, month=month).order_by("-total").first()
        if hero:  # hero may be None
            hero_name = hero.user.get_full_name()
        return hero_name

    def get_month_mean(self, year: int, month: int, user=None) -> str:
        sheets = Sheet.objects.filter(year=year, month=month)
        if user is not None:
            sheets = sheets.filter(user=user)
        if not sheets.count():
            return 0
        tot = sheets.aggregate(Sum("total"))
        return tot["total__sum"] / sheets.count()

    def get_info(self, queryset: QuerySet) -> pd.Series:
        if not queryset.count():
            return pd.Series(dtype="float64")
        df_all = pd.DataFrame()
        for sheet in queryset:
            df = sheet.transform()
            df.drop(["Day", "WeekDay"], axis=1, inplace=True)
            df_all = df_all.add(df, fill_value=0)
        return df_all.sum()


class PublicMonthlyReportApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year: str, month: str):

        sheets = Sheet.objects.filter(year=year, month=month)
        hours, activeUsers = PublicMonthlyReportApiView.get_sheet_sums(sheets)
        res = {
            "hours": hours,
            "activeUsers": activeUsers,
        }

        return Response(res, status=status.HTTP_200_OK)

    @classmethod
    def get_sheet_sums(cls, sheets: QuerySet) -> dict:
        projects = [p["name"] for p in Project.objects.values("name")]
        projects.append("Total")

        # a pandas Series which will be a summation of all desiered sheet sums
        projects_sum = pd.Series({p: 0 for p in projects})

        for sheet in sheets:
            sheet_sum = cls.get_sum(sheet)
            projects_sum = projects_sum.add(sheet_sum, fill_value=0)

        return projects_sum.apply(cls.minute_formatter).to_dict(), sheets.count()

    @classmethod
    def get_sum(self, sheet: Sheet) -> pd.Series:
        """returns sheet column sums"""
        df = sheet.transform()
        df.drop(["Day", "WeekDay"], axis=1, inplace=True)
        df.rename(columns={"Hours": "Total"}, inplace=True)
        return df.sum()

    @classmethod
    def minute_formatter(cls, minutes: int) -> str:
        return f"{int(minutes // 60)}:{int(minutes % 60)}"


class MonthlyReportApiView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, year: str, month: str):

        sheets = Sheet.objects.filter(year=year, month=month)
        submitted_sheets = sheets.filter(submitted=True)
        submitted_user_names = [
            sheet.user.get_full_name() for sheet in submitted_sheets
        ]
        sheetless_users = User.objects.select_related().exclude(
            sheets__year=year, sheets__month=month
        )
        sheetless_user_names = [user.get_full_name() for user in sheetless_users]
        hours, payments = MonthlyReportApiView.get_sheet_sums(sheets, sheetless_users)
        res = {
            "hours": hours,
            # "payments": payments,
            "usersNum": User.objects.count(),
            "sheetsNum": sheets.count(),
            "submittedSheetsNum": submitted_sheets.count(),
            "sheetlessUsers": sheetless_user_names,
            "submittedUsers": submitted_user_names,
        }

        return Response(res, status=status.HTTP_200_OK)

    @classmethod
    def get_sheet_sums(cls, sheets: QuerySet, sheetless_users: QuerySet) -> dict:
        projects = [p["name"] for p in Project.objects.values("name")]
        projects.append("Total")

        # a pandas Series which contains all projects.
        # a user's sheet sum should be added to this Series in order to contain all projects even the value is 0
        projects_empty = pd.Series({p: 0 for p in projects})
        # a pandas Series which will be a summation of all desiered sheet sums
        projects_sum = pd.Series({p: 0 for p in projects})

        hours = dict()
        payments = dict()
        for sheet in sheets:
            sheet_sum = cls.get_sum(sheet)
            sheet_sum = projects_empty.add(sheet_sum, fill_value=0)
            projects_sum = projects_sum.add(sheet_sum, fill_value=0)
            full_name = sheet.user.get_full_name() if sheet.user else "Deleted User"
            hours[full_name] = sheet_sum.apply(cls.minute_formatter).to_dict()
            wage = sheet.user.wage if sheet.user else 0
            payments[full_name] = sheet_sum.apply(
                lambda x: int(x / 60 * wage)
            ).to_dict()
        for user in sheetless_users:
            full_name = user.get_full_name()
            hours[full_name] = projects_empty.to_dict()
            payments[full_name] = 0
        hours["Total"] = projects_sum.apply(cls.minute_formatter).to_dict()
        return hours, payments

    @classmethod
    def get_sum(self, sheet: Sheet) -> pd.Series:
        """returns sheet column sums"""
        df = sheet.transform()
        df.drop(["Day", "WeekDay"], axis=1, inplace=True)
        df.rename(columns={"Hours": "Total"}, inplace=True)
        return df.sum()

    @classmethod
    def minute_formatter(cls, minutes: int) -> str:
        return f"{int(minutes // 60)}:{int(minutes % 60)}"


class PaymentApiView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, year: str, month: str):
        sheets = (
            Sheet.objects.select_related("user")
            .filter(year=year, month=month)
            .order_by("user__last_name")
        )
        data = list()
        for sheet in sheets:
            user = sheet.user
            if not sheet.user:
                continue
            payment_info = sheet.get_payment_info()
            payment_info.update(
                {
                    "userID": user.id,
                    "user": user.get_full_name() + (" ☑️" if sheet.submitted else ""),
                    "bankName": user.bank_name,
                }
            )
            data.append(payment_info)

        return Response(data, status=status.HTTP_200_OK)


class PublicPaymentApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year: str, month: str):
        sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        data = sheet.get_public_payment_info()
        return Response(data, status=status.HTTP_200_OK)


class AlterPaymentApiView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, year: str, month: str):
        users = User.objects.filter(is_active=1)
        data = list()

        for user in users:
            sheet, created = Sheet.objects.get_or_create(
                user=user, year=year, month=month
            )
            if created:
                sheet = _setup_sheet(sheet, user)
                sheet.save()
            payment_info = sheet.get_payment_info()
            payment_info.update(
                {
                    "userID": user.id,
                    "user": user.get_full_name(),
                    "bankName": user.bank_name,
                }
            )
            data.append(payment_info)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, year: str, month: str):
        editted_row = request.data["row"]
        id = editted_row["userID"]
        wage = editted_row["wage"]
        base = editted_row["basePayment"]

        user = User.objects.get(pk=id)
        user.wage = wage
        user.base_payment = base
        user.save()
        user_sheets = Sheet.objects.filter(user=id, year=1403)
        for sheet in user_sheets:
            if sheet.month >= int(month):
                sheet.wage = wage
                sheet.base_payment = base
                sheet.save()

        currentSheet = Sheet.objects.get(user=id, year=1403, month=month)
        currentSheet.reduction1 = int(editted_row["reduction1"])
        currentSheet.reduction2 = int(editted_row["reduction2"])
        currentSheet.reduction3 = int(editted_row["reduction3"])
        currentSheet.food_reduction = int(editted_row["food_reduction"])
        currentSheet.addition1 = int(editted_row["addition1"])
        currentSheet.addition2 = int(editted_row["addition2"])
        currentSheet.payment_status = int(editted_row["paymentStatus"])
        currentSheet.save()

        return Response(currentSheet.get_payment_info(), status=status.HTTP_200_OK)


class OrderFoodApiView(APIView):

    def get(self, request, year: str, month: str):
        sheet, created = Sheet.objects.get_or_create(
            user=self.request.user, year=year, month=month
        )
        return Response(sheet.food_data, status=status.HTTP_200_OK)

    def post(self, request, year: str, month: str):
        data = request.data["data"]
        index = int(request.data["index"])
        sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        self.updateSheetFoodData(data, index, sheet)
        self.update_sheet_food_reduction(sheet, year, month)
        return Response(sheet.food_data, status=status.HTTP_200_OK)

    def updateSheetFoodData(self, data, i, sheet):
        if i >= len(sheet.food_data):
            sheet.food_data.extend([[]] * (i + 1 - len(sheet.food_data)))
        sheet.food_data[i] = data
        sheet.save()

    def update_sheet_food_reduction(self, sheet, year, month):
        food_data, created = Food_data.objects.get_or_create(year=year, month=month)

        flat_list = [item for sublist in sheet.food_data for item in sublist]
        order_data = filtered_list = [
            item
            for item in flat_list
            if item["month"] == month and len(item["foods"]) > 0
        ]

        sheet.food_reduction = self.calculateSheetFoodPrice(order_data, food_data.data)
        sheet.save()

    def calculateSheetFoodPrice(self, order_data, food_data):
        food_price_map = {}

        # Iterate over the food data and map prices based on the day ranges
        for food_entry in food_data:
            day = food_entry["day"]
            for food_item in food_entry["data"]:
                food_id = food_item["id"]
                price = food_item["price"]
                food_price_map[(day, food_id)] = price

        # Step 2: Calculate total price
        total_price = 0

        for order in order_data:
            order_day = int(order["day"])
            foods = order["foods"]

            # Determine the applicable day for pricing
            applicable_day = 1
            for day in food_data:
                if day["day"] <= order_day:
                    applicable_day = day["day"]
                else:
                    break

            for food_id in foods:
                food_price_key = (applicable_day, food_id)
                if food_price_key in food_price_map:
                    total_price += food_price_map[food_price_key]

        return total_price

class FoodDataApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, year: str, month: str):
        last_food_data = Food_data.objects.last()
        food_data, created = Food_data.objects.get_or_create(year=year, month=month)

        if created and last_food_data is not None and len(last_food_data.data) > 0:
            newfooddata = last_food_data.data[-1]
            newfooddata["day"] = 1
            food_data.data = [newfooddata]
            food_data.save()

        return Response([food_data.data, food_data.order_mode], status=status.HTTP_200_OK)

class FoodManagementApiView(APIView):
    permission_classes = [customPermissions.IsFoodManager]

    def post(self, request, year: str, month: str):
        submittedFoodNames = request.data
        food_data = Food_data.objects.get(year=year, month=month)

        if not food_data.data:
            food_data.data = [
                {
                    "day": 1,
                    "data": [
                        {"id": int(key), "name": name, "price": 0}
                        for key, name in submittedFoodNames.items()
                    ],
                }
            ]
        else:
            submitted_ids = {int(key) for key in submittedFoodNames.keys()}

            for db_record in food_data.data:
                existing_items = {item["id"]: item for item in db_record["data"]}

                for key, name in submittedFoodNames.items():
                    food_id = int(key)
                    existing_item = existing_items.get(food_id)
                    if existing_item:
                        existing_item["name"] = name
                    else:
                        db_record["data"].append(
                            {"id": food_id, "name": name, "price": 0}
                        )

                # Remove items from the database that are not in the submitted data
                db_record["data"] = [
                    item for item in db_record["data"] if item["id"] in submitted_ids
                ]

        food_data.save()

        return Response(food_data.data, status=status.HTTP_200_OK)

    def put(self, request, year: str, month: str):
        requestTargetType = request.data['type']
        food_data = Food_data.objects.get(year=year, month=month)
        if requestTargetType == "order_mode":
            mode = request.data["data"]
            return self.updateOrderMode(food_data, mode)
        if requestTargetType == "food_data":
            submittedFoodData = request.data["data"]
            return self.updateFoodsPrice(year, month, submittedFoodData, food_data)

    def updateOrderMode(self, food_data, mode):
        food_data.order_mode = mode
        food_data.save()
        return Response({}, status=status.HTTP_200_OK)

    def updateFoodsPrice(self, year, month, submittedFoodData, food_data):
        if not food_data.data:
            food_data.data = [
                {
                    "day": 1,
                    "data": [
                        {"id": int(key), "name": name, "price": 0}
                        for key, name in submittedFoodData.items()
                    ],
                }
            ]
        else:
            food_data.data = submittedFoodData
        food_data.save()
        self.update_all_foodReductions(year, month)
        return Response(food_data.data, status=status.HTTP_200_OK)
        
    def update_all_foodReductions(self, year, month):
        OrderFoodApiObject = OrderFoodApiView()
        
        sheets = Sheet.objects.filter(year=year, month=month)
        
        for sheet in sheets:
            sheet.food_reduction = 0
            if sheet.food_data != []:
                OrderFoodApiObject.update_sheet_food_reduction(sheet, year, month)
            sheet.save()
        
        return

class DailyFoodsOrder(APIView):

    def get(self, request, year: str, month: str, weekIndex: str, day: str):
        sheets = Sheet.objects.filter(year=year, month=month).exclude(food_data=[])
        food_data = Food_data.objects.get(year=year, month=month)
        if len(food_data.data) == 0:
            return Response([], status=status.HTTP_200_OK)
        food_data = food_data.data[0]["data"]

        d = [{"id": item["id"], "name": item["name"], "count": 0} for item in food_data]

        for sh in sheets:
            if sh.food_data is not []:
                TargetWeekFoodData = sh.food_data[int(weekIndex)]
                selectedFoods = next(
                    (item for item in TargetWeekFoodData if item["day"] == day), None
                )
                if selectedFoods:
                    self.update_counts(d, selectedFoods["foods"])

        return Response(d, status=status.HTTP_200_OK)

    def post(self, request, year: str, month: str, weekIndex: str, day: str):
        sheets = Sheet.objects.filter(year=year, month=month).exclude(food_data=[])
        food_data_obj = Food_data.objects.filter(year=year, month=month).first()
        if not food_data_obj or not food_data_obj.data:
            return Response([], status=status.HTTP_200_OK)

        food_data = food_data_obj.data[0]["data"]
        d = [
            [{"id": item["id"], "name": item["name"], "count": 0} for item in food_data]
            for _ in range(7)
        ]

        for sh in sheets:
            TargetWeekFoodData = sh.food_data[int(weekIndex)]
            for index, item in enumerate(TargetWeekFoodData):
                self.update_counts(d[index], item["foods"])

        unique_food_names = {item["name"] for item in food_data}
        weekdays = [
            "شنبه",
            "یکشنبه",
            "دوشنبه",
            "سه شنبه",
            "چهارشنبه",
            "پنچ شنبه",
            "جمعه",
        ]

        data_dict = {name: [0] * 7 for name in unique_food_names}
        data_dict["روز/غذا"] = weekdays

        for day_idx, day_data in enumerate(d):
            food_count_map = {item["name"]: item["count"] for item in day_data}
            for name in unique_food_names:
                data_dict[name][day_idx] = food_count_map.get(name, 0)

        df = pd.DataFrame(data_dict)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f"attachment; filename=food_order_{year}_{month}_week{weekIndex}.xlsx"
        )
        return response

    def update_counts(self, items, ids):
        for item in items:
            if item["id"] in ids:
                item["count"] += 1
