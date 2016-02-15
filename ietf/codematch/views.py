from django.http import HttpResponseRedirect
from ietf.codematch.helpers.utils import (render_page)
from ietf.codematch import constants
from dal import autocomplete
from ietf.person.models import Person


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


def index(request):
    return render_page(request, constants.TEMPLATE_INDEX)


def about(request):
    return render_page(request, constants.TEMPLATE_ABOUT)


def back(request):
    template = "/codematch/index"

    if "previous_template" in request.session:
        template = request.session["previous_template"]

    return HttpResponseRedirect(template)
