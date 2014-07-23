import calendar
import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic import ListView, DetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView

import requests
from haystack.views import SearchView
from lxml import html
from speeches.models import Section, Speaker
from speeches.search import SpeakerForm, SpeechForm

from legislature.models import Action, Bill

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

class DebateArchiveIndexView(ArchiveIndexView):
    queryset = Section.objects.filter(parent=None)
    date_field = 'start_date'
    template_name = 'section_archive.html'
debates = DebateArchiveIndexView.as_view()

class DebateYearArchiveView(TitleAdder, YearArchiveView):
    queryset = Section.objects.filter(parent=None)
    date_field = 'start_date'
    template_name = 'section_archive_year.html'
    make_object_list = True
    page_title = lambda self: 'Debates from %s' % self.get_year()
debates_by_year = DebateYearArchiveView.as_view()

class DebateMonthArchiveView(TitleAdder, MonthArchiveView):
    queryset = Section.objects.filter(parent=None)
    date_field = 'start_date'
    template_name = 'section_archive_month.html'
    make_object_list = True
    page_title = lambda self: 'Debates from %s %s' % (calendar.month_name[int(self.get_month())], self.get_year())
    month_format = '%m'  # Use integers in paths.
debates_by_month = DebateMonthArchiveView.as_view()

class SpeakerListView(ListView):
    queryset = Speaker.objects.exclude(email=None).order_by('sort_name')
    template_name = 'speaker_list.html'

    def get_context_data(self, **kwargs):
        context = super(SpeakerListView, self).get_context_data(**kwargs)
        context['former_list'] = sorted(Speaker.objects.filter(email=None), key=lambda v: v.name.split(' ')[-1])
        return context
people = SpeakerListView.as_view()

class BillListView(ListView):
    template_name = 'bill_list.html'

    # @see http://docs.opencivicdata.org/en/latest/proposals/0006.html
    def get_queryset(self):
        url = 'http://nslegislature.ca/index.php/proceedings/status-of-bills/sort/status'
        page = requests.get(url)
        tree = html.fromstring(page.text)
        tree.make_links_absolute(url)

        bills = []
        for tr in tree.xpath('//tr[@valign="top"]'):
            bill = Bill(
                identifier=int(tr.xpath('./td[2]//text()')[0]),
                title=tr.xpath('./td[3]//text()')[0].replace('(amended)', '').rstrip('*\n '),
                status=tr.xpath('./td[1]//text()')[0],
                modified=datetime.datetime.strptime(tr.xpath('./td[4]//text()')[0], '%B %d, %Y').date(),
                url=tr.xpath('./td[3]//@href')[0],
            )
            bills.append(bill)

        return bills
bills = BillListView.as_view()

class BillDetailView(DetailView):
    template_name = 'bill_detail.html'

    # @see http://ccbv.co.uk/projects/Django/1.5/django.views.generic.detail/DetailView/
    def get_object(self):
        url = 'http://nslegislature.ca/index.php/proceedings/bills/%s' % self.kwargs.get(self.slug_url_kwarg, None)
        page = requests.get(url)
        tree = html.fromstring(page.text)
        tree.make_links_absolute(url)

        div = tree.xpath('//div[@id="content"]')[0]

        bill = Bill(
            identifier=int(div.xpath('./h3//text()')[0].rsplit(' ', 1)[1]),
            title=div.xpath('./h2//text()')[0].replace('(amended)', '').rstrip('*\n '),
            url=url,
            law_amendments_committee_submissions_url=div.xpath('string(.//@href[contains(.,"/committees/submissions/")])'),
        )

        # @see http://nslegislature.ca/index.php/proceedings/bills/liquor_control_act_-_bill_52
        matches = div.xpath('./p[not(@class)]//@href')
        if matches:
            bill.creator = Speaker.objects.get(sources__url=matches[0].rstrip('/'))

        # Some descriptions are identical to titles.
        description = div.xpath('./h3//text()')[1].rstrip('*\n ')
        if bill.title != description:
            bill.description = description

        actions = []
        for tr in div.xpath('.//tr'):
            matches = tr.xpath('./td//text()')
            if matches and matches[0] != 'View':
                action = Action(description=tr.xpath('./th//text()')[0].rstrip())
                try:
                    action.date = datetime.datetime.strptime(matches[0].split(';', 1)[0], '%B %d, %Y').date()
                except ValueError:
                    action.text = matches[0]
                actions.append(action)

        # Assigning `actions` to `action_set` will trigger a database call.
        setattr(bill, 'actions', actions)

        return bill
bill = BillDetailView.as_view()

class SpeakerDetailView(ListView):
    paginate_by = 15
    template_name = 'speaker_detail.html'

    def get_queryset(self):
        self.object = get_object_or_404(Speaker, slugs__slug=self.kwargs.get('slug', None))
        return self.object.speech_set.all().order_by('-start_date', '-id').prefetch_related('section', 'speaker')

    def get_context_data(self, **kwargs):
        context = super(SpeakerDetailView, self).get_context_data(**kwargs)
        context['speaker'] = self.object
        return context
person = SpeakerDetailView.as_view()

class DebateDetailView(ListView):
    paginate_by = 15
    template_name = 'section_detail.html'

    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.list/ListView/
    # @see http://ccbv.co.uk/projects/Django/1.6/django.views.generic.detail/DetailView/
    # @see https://docs.djangoproject.com/en/1.4/topics/class-based-views/#dynamic-filtering
    def get_queryset(self):
        self.object = get_object_or_404(Section, slug=self.kwargs.get('slug', None))
        return self.object.descendant_speeches().prefetch_related('speaker', 'speaker__memberships', 'speaker__memberships__organization', 'section', 'section__parent')

    def get_context_data(self, **kwargs):
        context = super(DebateDetailView, self).get_context_data(**kwargs)
        context['section'] = self.object
        return context
debate = DebateDetailView.as_view()

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
