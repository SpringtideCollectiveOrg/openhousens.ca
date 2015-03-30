# coding: utf-8
import os
import re

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from speeches.models import Speaker
from twitter import OAuth, Twitter

twitter = Twitter(auth=OAuth(
    token=os.getenv('TWITTER_ACCESS_TOKEN'),
    token_secret=os.getenv('TWITTER_TOKEN_SECRET'),
    consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
    consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
))


@python_2_unicode_compatible
class Bill(models.Model):
    STATUS_CHOICES = (
        ('1st', 'First Reading'),
        ('2nd', 'Second Reading'),
        ('LA', 'Law Amendments Committee'),
        ('PL', 'Private & Local Bills Committee'),
        ('WH', 'Committee of the Whole House'),
        ('3rd', 'Third Reading'),
        ('RA', 'Royal Assent'),
    )

    identifier = models.PositiveIntegerField()
    title = models.TextField()
    description = models.TextField()
    classification = models.TextField()
    creator = models.ForeignKey(Speaker, blank=True, null=True, on_delete=models.SET_NULL)
    modified = models.DateField()
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    slug = models.TextField()
    url = models.URLField()
    law_amendments_committee_submissions_url = models.URLField()

    def __str__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('legislature:bill-view', (), {'slug': self.slug})


@python_2_unicode_compatible
class Action(models.Model):
    description = models.TextField()
    date = models.DateField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    bill = models.ForeignKey(Bill, blank=True, null=True)  # had to be NULL for migration

    class Meta:
        ordering = ['date']
        unique_together = ('bill', 'description')

    def __str__(self):
        return self.description


@receiver(post_save, sender=Action)
def tweet_bill_status(sender, instance, created, **kwargs):
    # @note Disable Twitter when scraping bills for the first time.
    if created and os.getenv('TWITTER_CONSUMER_SECRET', False):
        if instance.bill.status == '1st':
            text = 'The {title} was introduced {url}'
        if instance.bill.status == '2nd':
            text = 'The House voted on referring the {title} to committee {url}'
        elif instance.bill.status == 'LA' or instance.bill.status == 'PL':
            text = 'A committee considered the {title} {url}'
        elif instance.bill.status == 'WH':
            text = 'The House debated the {title} {url}'
        elif instance.bill.status == '3rd':
            text = 'The House voted on passing the {title} {url}'
        elif instance.bill.status == 'RA':
            text = 'The {title} became law {url}'

        title = instance.bill.title
        title = re.sub(r'\s+', ' ', title)
        title = re.sub(r'\AAn ', '', title)
        title = re.sub(r' \([Aa]mended\)', '', title)

        # Accounts for "{title}" (7) and 22-character "{url}" (5).
        # @see https://dev.twitter.com/rest/reference/get/help/configuration
        title_maxlength = 130 - len(text)
        if len(title) > title_maxlength:
            title = title[:title_maxlength - 1] + '…'

        twitter.statuses.update(status=text.format(title=title, url='http://www.openhousens.ca%s' % instance.bill.get_absolute_url()))
