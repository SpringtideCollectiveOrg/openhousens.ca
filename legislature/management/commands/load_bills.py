import datetime
import re

import requests
from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from lxml import html
from speeches.models import Speaker

from legislature.models import Action, Bill


class Command(BaseCommand):
    help = 'Imports bills from the NS Legislature website.'

    def get(self, path):
        return requests.get(self.base_url + path).json()

    def handle(self, *args, **options):
        url = 'http://nslegislature.ca/index.php/proceedings/status-of-bills/sort/status'
        page = requests.get(url)
        tree = html.fromstring(page.text)
        tree.make_links_absolute(url)

        for tr in tree.xpath('//tr[@valign="top"]'):
            identifier = int(tr.xpath('./td[2]//text()')[0])

            try:
                bill = Bill.objects.get(identifier=identifier)
            except Bill.DoesNotExist:
                bill = Bill(identifier=identifier)
            as_dict = model_to_dict(bill)

            bill.title = re.sub(r'\s+', ' ', tr.xpath('./td[3]//text()')[0]).rstrip('* ')
            bill.status = tr.xpath('./td[1]//text()')[0]
            bill.modified = datetime.datetime.strptime(tr.xpath('./td[4]//text()')[0], '%B %d, %Y').date()
            bill.url = tr.xpath('./td[3]//@href')[0]
            bill.slug = bill.url.rsplit('/', 1)[1][:70]

            page = requests.get(bill.url)
            tree = html.fromstring(page.text)
            tree.make_links_absolute(url)

            div = tree.xpath('//div[@id="content"]')[0]

            bill.law_amendments_committee_submissions_url = div.xpath('string(.//@href[contains(.,"/committees/submissions/")])')

            # @see http://nslegislature.ca/index.php/proceedings/bills/liquor_control_act_-_bill_52
            matches = div.xpath('./p[not(@class)]//@href')
            if matches:
                bill.creator = Speaker.objects.get(sources__url=matches[0].rstrip('/'))

            # Some descriptions are identical to titles.
            description = div.xpath('./h3//text()')[1].rstrip('*\n ')
            if bill.title != description:
                bill.description = description

            if div.xpath('.//text()[contains(.,"Law Amendments Committee")]'):
                bill.classification = 'Public Bills'
            elif div.xpath('.//text()[contains(.,"Private and Local Bills")]'):
                bill.classification = 'Private and Local Bills'

            if not bill.pk or as_dict != model_to_dict(bill):
                bill.save()

            for tr in div.xpath('.//tr'):
                matches = tr.xpath('./td//text()')
                if matches and matches[0] != 'View':  # Skip link to statute
                    description = tr.xpath('./th//text()')[0].strip()
                    if description == 'Second Reading Passed':
                        description = 'Second Reading'

                    # Avoids importing duplicates.
                    try:
                        Action.objects.get(description=description, bill=bill)
                    except Action.DoesNotExist:
                        action = Action(description=description, bill=bill)
                        try:
                            action.date = datetime.datetime.strptime(matches[0].split(';', 1)[0], '%B %d, %Y').date()  # Use the first date
                        except ValueError:
                            action.text = matches[0]
                        action.save()
