from django.shortcuts import render_to_response
from django.views.generic.dates import ArchiveIndexView, YearArchiveView

from speeches.models import Section

def home(request):
    most_recent_debate = Section.objects.filter(parent=None).order_by('-start_date').first()
    return render_to_response('home.html', {'most_recent_debate': most_recent_debate})

def about(request):
    return render_to_response('about.html')

class DebateIndexView(ArchiveIndexView):
    queryset = Section.objects.all()
    date_field = 'start_date'
    template_name = 'section_list.html'
debates = DebateIndexView.as_view()

class DebateYearArchive(YearArchiveView):
    queryset = Section.objects.all()
    date_field = 'start_date'
    make_object_list = True
    template_name = 'section_list_by_year.html'
debates_by_year = DebateYearArchive.as_view()
