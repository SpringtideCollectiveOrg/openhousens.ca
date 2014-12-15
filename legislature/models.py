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
    url = models.URLField()
    law_amendments_committee_submissions_url = models.URLField()

    def __str__(self):
        return self.title

    @property
    def slug(self):
        return self.url.rsplit('/', 1)[1][:70]


@python_2_unicode_compatible
class Action(models.Model):
    description = models.TextField()
    date = models.DateField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    bill = models.ForeignKey(Bill, blank=True, null=True)  # had to be NULL for migration

    def __str__(self):
        return self.description


@receiver(post_save, sender=Bill)
def tweet_bill_status(sender, instance, **kwargs):
    # @todo Should only tweet if the bill's status changed.
    if instance.status == '1st':
        text = "The %s was introduced"
    if instance.status == '2nd':
        text = "The House voted on referring the %s to committee"
    elif instance.status == 'LA' or instance.status == 'PL':
        text = "A committee considered the %s"
    elif instance.status == 'WH':
        text = "The House debated the %s"
    elif instance.status == '3rd':
        text = "The House voted on passing the %s"
    elif instance.status == 'RA':
        text = "The %s became law"

    title = instance.title
    title = re.sub(r'\s+', ' ', title)
    title = re.sub(r'\AAn ', '', title)
    title = re.sub(r' \([Aa]mended\)', '', title)

    title_maxlength = 142 - len(text)  # accounts for "%s"
    if len(title) > title_maxlength:
        title = title[:title_maxlength - 1] + '…'

    twitter.statuses.update(status=text % title)
