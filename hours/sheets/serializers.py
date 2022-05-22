from rest_framework import serializers
from sheets.models import Sheet, Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']

class SheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sheet
        fields = "__all__"

    # def save(self):
    #     user = None
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         user = request.user
    #     print('user is:', user)