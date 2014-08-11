import calendar
import re

from django import template
from django.core.urlresolvers import reverse
from django.utils.html import conditional_escape
from django.utils.http import urlquote
from django.utils.safestring import mark_safe

from legislature.synonyms import upper_case_words, mixed_case_abbreviations, upper_case_abbreviations

register = template.Library()

first_letter = re.compile(r'(?<![</])\b[a-z]')
not_all_caps = re.compile(r'[a-gi-ru-z]')  # e.g. CFLs, DHAs, 75th
honorifics = re.compile(r'\b(?:Hon|Mr|Ms)\. ')
patronymic = re.compile(r"(Mac|Mc|'|-)([a-z])")
# @see http://blog.apastyle.org/apastyle/2012/03/title-case-and-sentence-case-capitalization-in-apa-style.html
lower_case_words = ('and', 'by', 'for', 'of', 'the', 'to')

def upper_case_letter(match):
    return match.group(0).upper()

def capitalize_patronymic(match):
    return match.group(1) + match.group(2).upper()

def html_mark_safe(template, *args):
    return mark_safe(template.format(*map(conditional_escape, args)))

def top_level_slug(section):
    if not section.parent_id:
        return section.slug
    elif not section.parent.parent_id:
        return section.parent.slug
    else:
        return section.parent.parent.slug

@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]

@register.filter
def heading(string):
    if not_all_caps.search(string):
        for pattern, repl in mixed_case_abbreviations:
          string = pattern.sub(repl, string)
        return string.rstrip('.')
    else:
        for pattern, repl in upper_case_abbreviations:
          string = pattern.sub(repl, string)
        words = []
        for word in string.split(' '):
            if word not in upper_case_words:
                word = word.lower()
                if word not in lower_case_words:
                    word = first_letter.sub(upper_case_letter, word)
                    if patronymic.match(word):
                        word = patronymic.sub(capitalize_patronymic, word)
            words.append(word)
        return ' '.join(words)

@register.filter
def speaker_party_name(speaker):
    return next(membership.organization.name for membership in speaker.memberships.all() if not membership.label)

@register.filter
def speaker_party_class(speaker):
    party = speaker_party_name(speaker)
    if party == 'Nova Scotia Liberal Party':
        return 'liberal'
    elif party == 'Nova Scotia New Democratic Party':
        return 'ndp'
    elif party == 'Progressive Conservative Association of Nova Scotia':
        return 'pc'
    return ''

@register.filter
def speaker_description(speaker):
    """
    We use speaker.memberships.all() instead of speaker.memberships.filter()
    to avoid additional queries to the database.
    """
    party = speaker_party_name(speaker)
    if party == 'Nova Scotia Liberal Party':
        party = 'Liberal'
    elif party == 'Nova Scotia New Democratic Party':
        party = 'NDP'
    elif party == 'Progressive Conservative Association of Nova Scotia':
        party = 'Progressive Conservative'
    label = next(membership.label for membership in speaker.memberships.all() if membership.label)
    return html_mark_safe(' <span itemprop="member" itemscope itemtype="http://schema.org/Organization">{0}</span> <span itemprop="jobTitle">{1}</span> ', party, label)

@register.filter
def speaker_name(name):
    return ' '.join(patronymic.sub(capitalize_patronymic, first_letter.sub(upper_case_letter, component.lower())) for component in name.split(' '))

invalid = re.compile('[^a-z_-]')
@register.filter
def speaker_dom_id(speaker):
    label = next(membership.label for membership in speaker.memberships.all() if membership.label)
    return invalid.sub('', label.replace('MLA for ', '').replace(' ', '_').lower())

@register.filter
def person_name(name):
    return honorifics.sub('', speaker_name(name))

@register.filter
def person_short_name(name):
    """
    Find the person's given name, even if given_name is not set.
    """
    return person_name(name).split(' ')[0]

@register.filter
def speech_speaker(speech):
    if speech.speaker_id:
        name = speech.speaker.name
    else:
        name = speech.speaker_display
    if not_all_caps.search(name):
        return name
    else:
        return speaker_name(name)

# Speech.objects.filter(speaker_id=None).exclude(speaker_display__in=('THE PREMIER', 'THE LIEUTENANT GOVERNOR', 'THE ADMINISTRATOR')).values_list('speaker_display', flat=True).order_by('speaker_display').distinct()
@register.filter
def speech_class(speech):
    if speech.speaker_id:
        return 'person'
    elif speech.speaker_display in ('THE PREMIER', 'THE LIEUTENANT GOVERNOR', 'THE ADMINISTRATOR'):
        return 'government'
    elif speech.speaker_display:
        return 'role'
    else:
        return 'narrative'

@register.filter
def tweet_text(speech):
    name = speech_speaker(speech)
    text = None
    if speech.title:
        text = heading(speech.title)
    elif speech.section.parent_id:
        text = heading(speech.section.title)
    if text:
        tweet = '%s on %s' % (name, text)
    else:
        tweet = name
    return urlquote(tweet)

@register.filter
def bill_action_html_attributes(description):
    title = None
    if description == 'First Reading':
        title = "The bill is introduced"
    elif description == 'Second Reading':
        title = "The House votes to refer the bill to committee"
    elif description == 'Law Amendments Committee':
        title = "The committee considers the bill and hears from interested people and organizations"
    elif description == 'Private and Local Bills':
        title = "The committee considers the bill and hears from interested people and organizations"
    elif description == 'Reported to the House':
        title = "The House votes to refer the bill to the Committee of the Whole House on Bills"
    elif description == 'Committee of the Whole House':
        title = "The Committee of the Whole House on Bills examines each clause of the bill"
    elif description == 'Third Reading':
        title = "The House votes to pass the bill"
    elif description == 'Royal Assent':
        title = "The Lieutenant Governor signs the bill into law"
    elif description == 'Commencement':
        title = "The law comes into force"
    if title:
        return mark_safe(' data-toggle="tooltip" title="%s"' % title)
    else:
        return ''

@register.filter
def hansard_url(section):
    if section.title == 'NOTICES OF MOTION UNDER RULE 32(3)':
        return reverse('legislature:notices-view', args=(top_level_slug(section),))
    else:
        return reverse('legislature:section-view', args=(top_level_slug(section),))

@register.filter
def single_page_hansard_url(section):
    if section.title == 'NOTICES OF MOTION UNDER RULE 32(3)':
        return reverse('legislature:notices-view-single-page', args=(top_level_slug(section),))
    else:
        return reverse('legislature:section-view-single-page', args=(top_level_slug(section),))
