from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy

decorators = [login_required(login_url=reverse_lazy("sheets:login"))]

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

@method_decorator(decorators, name='dispatch')
class BaseView(JSONResponseMixin, TemplateView):
    template_name = ''
    extra_context = None

    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super().render_to_response(context)

    def get_context_data(self, *args, **kwargs):          
        context = super(BaseView, self).get_context_data(*args, **kwargs)
        if self.extra_context:
            context.update(self.extra_context)
        return context

class HomePageView(BaseView):
    template_name = 'home.html'

class HoursView(BaseView):
    template_name = "hours.html"


class InfoView(BaseView):
    template_name = "info.html"

@method_decorator([staff_member_required], name='dispatch')
class ReportsView(BaseView):
    template_name = "reports.html"