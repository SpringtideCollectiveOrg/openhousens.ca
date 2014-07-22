from django.db import models
from django.utils.encoding import python_2_unicode_compatible

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
    date = models.DateField()
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    url = models.URLField()

    class Meta:
        ordering = ('identifier',)

    def __str__(self):
        return self.title

    @property
    def slug(self):
        return self.url.rsplit('/', 1)[1]
