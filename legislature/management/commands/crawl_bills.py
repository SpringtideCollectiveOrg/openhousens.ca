###############################################################
#
# Bill crawler/indexer
# Moved out of views.py
#
# This will scrape bill data as appropriate. If a bill exists
# as an object in the database and it has not been modified
# since the last check, it will not be updated.
#
# Twitter auto-updates rely on bills being saved in the database.
#
###############################################################

import re
import calendar
import datetime
import requests
from django.core.management.base import BaseCommand, CommandError

from lxml import html

import requests
from instances.models import Instance
from popolo.models import Membership, Organization, Post
from speeches.models import Speaker
from legislature.models import Action, Bill
import django.core.exceptions

def crawl_detailed(bill):
    page = requests.get(bill.url)
    tree = html.fromstring(page.text)
    div = tree.xpath('//div[@id="content"]')[0]
    
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
    
    #    actions = []
    for tr in div.xpath('.//tr'):
        matches = tr.xpath('./td//text()')
        if matches and matches[0] != 'View':  # Skip link to statute
            description = tr.xpath('./th//text()')[0].strip()
            if description == 'Second Reading Passed':
                description = 'Second Reading'
            action = Action(description=description,bill=bill)
            print action.__dict__
            try:
                action.date = datetime.datetime.strptime(matches[0].split(';', 1)[0], '%B %d, %Y').date()  # Use the first date
            except ValueError:
                action.text = matches[0]
            action.save()
            print "Save action "+str(action.id)+" assoc w bill "+str(bill)


    # Assigning `actions` to an `action_set` will trigger a database call.
    return bill


class Command(BaseCommand):
    help = 'Imports bills from the NS Legislature website.'

    def get(self, path):
        return requests.get(self.base_url + path).json()

    def handle(self, *args, **options):

        url = 'http://nslegislature.ca/index.php/proceedings/status-of-bills/sort/status'
        page = requests.get(url)
        tree = html.fromstring(page.text)
        tree.make_links_absolute(url)
        bills_found = 0
        bills_found_new = 0
        
        for tr in tree.xpath('//tr[@valign="top"]'):
            identifier=identifier=int(tr.xpath('./td[2]//text()')[0])
            bills_found += 1
            
            bill = None
            bill_is_new = 0
            try:
                bill = Bill.objects.get(identifier=identifier)
            except Bill.DoesNotExist:
                print "Bill not found in database, trying fetch. Identifier is "+str(identifier)
                bill = Bill(
                        identifier=identifier,
                        title=tr.xpath('./td[3]//text()')[0].rstrip('*\n '),
                        status=tr.xpath('./td[1]//text()')[0],
                        modified=datetime.datetime.strptime(tr.xpath('./td[4]//text()')[0], '%B %d, %Y').date(),
                        url=tr.xpath('./td[3]//@href')[0],
                        )
                bill_is_new = 1
                bills_found_new = bills_found_new+1
            
            
            bill_modified_old = bill.modified
            bill.save()
            bill=crawl_detailed(bill)
            if bill.modified != bill_modified_old:
                print "Bill has changed. Bill ID "+str(bill.identifier)
                bill.save() # save it
            elif bill_is_new == 1:
                bill.save() # it's new, so save it!
        print "*** Crawl Complete: "+str(bills_found)+" bills found, "+str(bills_found_new)+" of which were new"

