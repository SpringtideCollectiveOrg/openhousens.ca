from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import DetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView

from speeches.models import Section
from speeches.mixins import UnmatchingSlugException

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

class SectionDetailView(DetailView):
    model = Section

    def get_context_data(self, **kwargs):
        context = super(SectionDetailView, self).get_context_data(**kwargs)
        context['speeches'] = kwargs['object'].descendant_speeches().prefetch_related('speaker', 'section', 'section__parent')
        return context
debate = SectionDetailView.as_view()
