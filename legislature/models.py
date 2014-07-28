from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from speeches.models import Speaker

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
        return self.url.rsplit('/', 1)[1]

@python_2_unicode_compatible
class Action(models.Model):
    description = models.TextField()
    date = models.DateField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.description
