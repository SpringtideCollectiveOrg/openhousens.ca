import calendar
import json
import re
from collections import defaultdict
from heapq import nlargest
from operator import itemgetter

import bleach
from django import forms
from django.db.models import Count
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import ListView, DetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView
from django_bleach.templatetags.bleach_tags import bleach_args
from haystack.forms import SearchForm
from haystack.query import RelatedSearchQuerySet
from haystack.views import SearchView
from popolo.models import Organization
from speeches.models import Section, Speaker, Speech
from speeches.search import SpeakerForm

from legislature.models import Action, Bill

STOPWORDS = frozenset([
    # nltk.corpus.stopwords.words('english')
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her',
    'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs',
    'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with',
    'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now',
    # @see https://github.com/rhymeswithcycle/openparliament/blob/master/parliament/text_analysis/frequencymodel.py
    "it's", "we're", "we'll", "they're", "can't", "won't", "isn't", "don't", "he's",
    "she's", "i'm", "aren't", "government", "house", "committee", "would", "speaker",
    "motion", "mr", "mrs", "ms", "member", "minister", "canada", "members", "time",
    "prime", "one", "parliament", "us", "bill", "act", "like", "canadians", "people",
    "said", "want", "could", "issue", "today", "hon", "order", "party", "canadian",
    "think", "also", "new", "get", "many", "say", "look", "country", "legislation",
    "law", "department", "two", "day", "days", "madam", "must", "that's", "okay",
    "thank", "really", "much", "there's", "yes", "no",
    # HTML tags
    'sup',
    # Nova Scotia
    "nova", "scotia", "scotians", "province",
    # artifacts
    "\ufffd", "n't",
])

r_punctuation = re.compile(r"[^\s\w0-9'’—-]", re.UNICODE)
r_whitespace = re.compile(r'[\s—]+')

def home(request):
    hansard = Section.objects.filter(parent=None).order_by('-start_date').first()

    # Get the latest hansard's speeches as in DebateDetailView.
    section_ids = []
    for section in hansard._get_descendants(include_self=True):
        if section.title != 'NOTICES OF MOTION UNDER RULE 32(3)':
            section_ids.append(section.id)
    speeches = Speech.objects.filter(section__in=section_ids)

    # @see https://github.com/rhymeswithcycle/openparliament/blob/master/parliament/text_analysis/analyze.py
    # @see https://github.com/rhymeswithcycle/openparliament/blob/master/parliament/text_analysis/frequencymodel.py

    # Get the counts of all non-stopwords.
    word_counts = defaultdict(int)
    total_count = 0

    for speech in speeches:
        for word in r_whitespace.split(r_punctuation.sub('', bleach.clean(speech.text, **bleach_args).lower())):
            if word not in STOPWORDS and len(word) > 2:
                word_counts[word] += 1
                total_count += 1

    word_counts = {word: count for word, count in word_counts.items()}
    most_common_words = nlargest(50, word_counts.items(), key=itemgetter(1))

    return render_to_response('home.html', {
        'hansard': hansard,
        'most_common_words': json.dumps(most_common_words),
    })


def about(request):
    return render_to_response('about.html', {'title': 'About'})


class TitleAdder(object):
    def get_context_data(self, **kwargs):
        context = super(TitleAdder, self).get_context_data(**kwargs)
        context.update(title=self.page_title)
        return context


class DebateArchiveIndexView(ArchiveIndexView):
    queryset = Section.objects.filter(parent=None)
    date_field = 'start_date'
    template_name = 'section_archive.html'
debates = DebateArchiveIndexView.as_view()


class DebateYearArchiveView(TitleAdder, YearArchiveView):
    queryset = Section.objects.filter(parent=None).order_by('start_date')
    date_field = 'start_date'
    template_name = 'section_archive_year.html'
    make_object_list = True
    page_title = lambda self: 'Debates from %s' % self.get_year()
debates_by_year = DebateYearArchiveView.as_view()


class DebateMonthArchiveView(TitleAdder, MonthArchiveView):
    queryset = Section.objects.filter(parent=None).order_by('start_date')
    date_field = 'start_date'
    template_name = 'section_archive_month.html'
    make_object_list = True
    page_title = lambda self: 'Debates from %s %s' % (calendar.month_name[int(self.get_month())], self.get_year())
    month_format = '%m'  # Use integers in paths.
debates_by_month = DebateMonthArchiveView.as_view()


class SpeakerListView(ListView):
    queryset = Speaker.objects.exclude(email=None).order_by('sort_name').prefetch_related('memberships')
    template_name = 'speaker_list.html'

    def get_context_data(self, **kwargs):
        context = super(SpeakerListView, self).get_context_data(**kwargs)
        context['memberships_counts'] = Organization.objects.filter(classification='political party').annotate(memberships_count=Count('memberships')).order_by('-memberships_count').prefetch_related('other_names')
        context['former_list'] = sorted(Speaker.objects.filter(email=None), key=lambda v: v.name.split(' ')[-1].lower())
        return context
people = SpeakerListView.as_view()


class SpeakerDetailView(ListView):
    paginate_by = 15
    template_name = 'speaker_detail.html'
    notices = False

    def get_queryset(self):
        self.object = get_object_or_404(Speaker, slugs__slug=self.kwargs.get('slug', None))
        qs = self.object.speech_set.order_by('-start_date', '-id').select_related('section', 'section__parent', 'section__parent__parent')
        if self.notices:
            qs = qs.filter(section__heading='NOTICES OF MOTION UNDER RULE 32(3)')
        else:
            qs = qs.exclude(section__heading='NOTICES OF MOTION UNDER RULE 32(3)')
        return qs

    def get_context_data(self, **kwargs):
        context = super(SpeakerDetailView, self).get_context_data(**kwargs)
        context['speaker'] = self.object
        context['notices'] = self.notices
        return context
person = SpeakerDetailView.as_view()
person_notices = SpeakerDetailView.as_view(notices=True)


class DebateDetailView(ListView):
    paginate_by = 15
    template_name = 'section_detail.html'
    notices = False

    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.list/ListView/
    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.detail/DetailView/
    # @see https://docs.djangoproject.com/en/1.4/topics/class-based-views/#dynamic-filtering
    def get_queryset(self):
        self.object = get_object_or_404(Section, parent_id=None, slug=self.kwargs.get('slug', None))
        self.notices_present = False
        section_ids = []
        for section in self.object._get_descendants(include_self=True):
            if section.title == 'NOTICES OF MOTION UNDER RULE 32(3)':
                self.notices_present = True
                if self.notices:
                    section_ids.append(section.id)
            elif not self.notices:
                section_ids.append(section.id)
        return Speech.objects.filter(section__in=section_ids).prefetch_related('speaker', 'speaker__memberships', 'speaker__memberships__organization', 'section', 'section__parent')

    def get_context_data(self, **kwargs):
        context = super(DebateDetailView, self).get_context_data(**kwargs)
        context['section'] = self.object
        context['notices'] = self.notices
        context['notices_present'] = self.notices_present
        return context
debate = DebateDetailView.as_view()
notices = DebateDetailView.as_view(notices=True)
debate_single_page = DebateDetailView.as_view(paginate_by=None)
notices_single_page = DebateDetailView.as_view(paginate_by=None, notices=True)


class BillListView(ListView):
    model = Bill
    template_name = 'bill_list.html'
bills = BillListView.as_view()


class BillDetailView(DetailView):
    model = Bill
    template_name = 'bill_detail.html'
bill = BillDetailView.as_view()


# @see http://django-haystack.readthedocs.org/en/latest/views_and_forms.html#creating-your-own-form
# @see https://github.com/toastdriven/django-haystack/blob/master/haystack/forms.py
class SpeechForm(SearchForm):
    """
    A form with a hidden integer field that searches the speaker ID field
    """
    p = forms.IntegerField(required=False, widget=forms.HiddenInput())
    speaker = None  # the speaker object

    def __init__(self, *args, **kwargs):
        if kwargs.get('searchqueryset') is None:
            kwargs['searchqueryset'] = RelatedSearchQuerySet()
        super(SpeechForm, self).__init__(*args, **kwargs)

    # @see http://django-haystack.readthedocs.org/en/latest/searchqueryset_api.html
    # @see http://django-haystack.readthedocs.org/en/latest/searchqueryset_api.html#SearchQuerySet.auto_query
    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data.get('p'):
            try:
                self.speaker = Speaker.objects.get(id=self.cleaned_data['p'])
            except Speaker.DoesNotExist:
                pass

        if not self.cleaned_data.get('q'):
            return self.no_query_found()

        # SearchForm calls `auto_query` here, which will escape colons.
        sqs = self.searchqueryset.raw_search(self.cleaned_data['q'])

        if self.load_all:
            sqs = sqs.load_all()

        # Like HighlightedSearchForm and ModelSearchForm.
        sqs = sqs.highlight().models(Section, Speech)

        if self.speaker:
            sqs = sqs.filter(speaker=self.speaker.id)

        return sqs


# @see http://django-haystack.readthedocs.org/en/latest/views_and_forms.html#views
# @see https://github.com/toastdriven/django-haystack/blob/master/haystack/views.py
class CustomSearchView(SearchView):
    def __init__(self, *args, **kwargs):
        kwargs['form_class'] = SpeechForm
        super(CustomSearchView, self).__init__(*args, **kwargs)

    def build_form(self, *args, **kwargs):
        self.searchqueryset = RelatedSearchQuerySet()
        if self.request.GET.get('sort') == 'newest':
            self.searchqueryset = self.searchqueryset.order_by('-start_date')
        return super(CustomSearchView, self).build_form(*args, **kwargs)

    def extra_context(self):
        if not self.query:
            return {}

        self.form_class = SpeakerForm
        person_form = self.build_form()
        return {
            'speaker_results': person_form.search(),
        }
