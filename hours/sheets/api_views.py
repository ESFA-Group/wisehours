from calendar import month
from venv import create
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import jdatetime as jdt

from sheets.models import Project, Sheet
from sheets.serializers import ProjectSerializer, SheetSerializer

class ProjectListApiView(ListAPIView):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class SheetApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, year, month):
        try: 
            sheet = Sheet.objects.get(user=self.request.user, year=year, month=month)
        except Sheet.DoesNotExist:
            empty_sheet_data = Sheet.empty_sheet_data()
            today = jdt.date.today()
            month, year = today.month, today.year
            res = {"data": empty_sheet_data, "month": month, "year": year}
            return Response(res, status=status.HTTP_200_OK)           

        serializer = SheetSerializer(sheet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, year, month):
        sheet, created = Sheet.objects.get_or_create(user=self.request.user, year=year, month=month)
        data = request.data.get("data", [])
        data.sort(key=lambda row: int(row.get("Day", 0)))
        sheet.data = request.data['data']
        sheet.save()
        return Response({"success": True}, status=status.HTTP_200_OK)

class InfoApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pass