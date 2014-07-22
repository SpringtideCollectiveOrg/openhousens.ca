import calendar

from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import ListView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView

from haystack.views import SearchView
from speeches.models import Section, Speaker
from speeches.search import SpeakerForm, SpeechForm

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
    template_name = 'section_list_by_month.html'
    make_object_list = True
    page_title = lambda self: 'Debates from %s %s' % (calendar.month_name[int(self.get_month())], self.get_year())
    month_format = '%m'  # Use integers in paths.
debates_by_month = DebateMonthArchive.as_view()

class SpeakerListView(ListView):
    queryset = Speaker.objects.exclude(email=None).order_by('sort_name')
    template_name = 'speaker_list.html'

    def get_context_data(self, **kwargs):
        context = super(SpeakerListView, self).get_context_data(**kwargs)
        context['former_list'] = sorted(Speaker.objects.filter(email=None), key=lambda v: v.name.split(' ')[-1])
        return context
people = SpeakerListView.as_view()

class SpeakerView(ListView):
    paginate_by = 15
    template_name = 'speaker_detail.html'

    def get_queryset(self):
        self.object = get_object_or_404(Speaker, slugs__slug=self.kwargs.get('slug', None))
        return self.object.speech_set.all().order_by('-start_date', '-id').prefetch_related('section', 'speaker')

    def get_context_data(self, **kwargs):
        context = super(SpeakerView, self).get_context_data(**kwargs)
        context['speaker'] = self.object
        return context
person = SpeakerView.as_view()

class DebateView(ListView):
    paginate_by = 15
    template_name = 'section_detail.html'

    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.list/ListView/
    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.detail/DetailView/
    # @see https://docs.djangoproject.com/en/1.4/topics/class-based-views/#dynamic-filtering
    def get_queryset(self):
        self.object = get_object_or_404(Section, slug=self.kwargs.get('slug', None))
        return self.object.descendant_speeches().prefetch_related('speaker', 'speaker__memberships', 'speaker__memberships__organization', 'section', 'section__parent')

    def get_context_data(self, **kwargs):
        context = super(DebateView, self).get_context_data(**kwargs)
        context['section'] = self.object
        return context
debate = DebateView.as_view()

# @see https://github.com/mysociety/sayit/blob/master/speeches/search.py
class CustomSearchView(SearchView):
    def __init__(self, *args, **kwargs):
        kwargs['form_class'] = SpeechForm
        super(CustomSearchView, self).__init__(*args, **kwargs)

    def extra_context(self):
        if not self.query:
            return {}

        self.form_class = SpeakerForm
        person_form = self.build_form()
        return {
            'speaker_results': person_form.search(),
        }

# @todo add bills and bill views
