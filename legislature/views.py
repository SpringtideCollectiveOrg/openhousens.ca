from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView

from speeches.models import Section

def home(request):
    hansard = Section.objects.filter(parent=None).order_by('-start_date').first()
    return render_to_response('home.html', {'hansard': hansard})

def about(request):
    return render_to_response('about.html', {'title': 'About'})

class TitleAdder(object):
    def get_context_data(self, **kwargs):
        context = super(TitleAdder, self).get_context_data(**kwargs)
        context.update(title=self.page_title)
        return context

class DebateIndexView(ArchiveIndexView):
    queryset = Section.objects.filter(parent=None)
    date_field = 'start_date'
    template_name = 'section_list.html'
debates = DebateIndexView.as_view()

class DebateYearArchive(TitleAdder, YearArchiveView):
    queryset = Section.objects.filter(parent=None)
    date_field = 'start_date'
    template_name = 'section_list_by_year.html'
    make_object_list = True
    page_title = lambda self: 'Debates from %s' % self.get_year()
debates_by_year = DebateYearArchive.as_view()

class DebateMonthArchive(TitleAdder, MonthArchiveView):
    queryset = Section.objects.filter(parent=None)
    date_field = 'start_date'
    template_name = 'section_list_by_year.html'
    make_object_list = True
    page_title = lambda self: 'Debates from %s' % self.get_year()
    month_format = '%m'  # Use integers in paths.
debates_by_month = DebateMonthArchive.as_view()

class SpeechListView(ListView):
    paginate_by = 15
    template_name = 'section_detail.html'

    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.list/ListView/
    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.detail/DetailView/
    # @see https://docs.djangoproject.com/en/1.4/topics/class-based-views/#dynamic-filtering
    def get_queryset(self):
        self.section = get_object_or_404(Section, slug=self.kwargs.get('slug', None))
        return self.section.descendant_speeches().prefetch_related('speaker', 'section', 'section__parent')

    def get_context_data(self, **kwargs):
        context = super(SpeechListView, self).get_context_data(**kwargs)
        context['section'] = self.section
        return context
debate = SpeechListView.as_view()
