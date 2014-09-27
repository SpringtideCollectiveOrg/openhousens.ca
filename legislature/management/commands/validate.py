import requests

from django.core.management.base import BaseCommand
from popolo.models import Membership

from speeches.models import Section, Speech

class Command(BaseCommand):
    help = 'Validates speeches, sections and memberships'

    def handle(self, *args, **options):
        # All speeches should belong to a section.
        speeches_without_sections = Speech.objects.filter(section=None)
        if speeches_without_sections:
            print('%d speeches without sections' % speeches_without_sections.count())

        # All sections should have speeches or sections.
        sections_without_speeches = Section.objects.filter(speech__section_id=None).filter(children__parent_id=None).order_by('start_date')
        if sections_without_speeches:
            print('%d sections without speeches' % sections_without_speeches.count())
            for section in sections_without_speeches:
                print(section.get_ancestors[0].start_date, section.title)

        # All boundaries should match a membership label.
        url = 'http://represent.opennorth.ca/boundaries/nova-scotia-electoral-districts/?limit=0'
        for boundary in requests.get(url).json()['objects']:
            try:
                _ = Membership.objects.get(label='MLA for %s' % boundary['name'].replace('—', '-'))  # m-dash
            except Membership.DoesNotExist:
                print('%s matches no membership' % boundary['name'])
