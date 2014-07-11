import calendar
import re

from django import template
from django.utils.http import urlquote

from legislature.synonyms import upper_case_words, mixed_case_abbreviations, upper_case_abbreviations

register = template.Library()

first_letter = re.compile(r'\b[a-z]')
not_all_caps = re.compile(r'[a-gi-ru-z]')  # e.g. CFLs, DHAs, 75th
honorifics = re.compile(r'\b(?:Hon|Mr|Ms)\. ')
patronymic = re.compile(r"(Mac|Mc|'|-)([a-z])")
# @see http://blog.apastyle.org/apastyle/2012/03/title-case-and-sentence-case-capitalization-in-apa-style.html
lower_case_words = ('and', 'by', 'for', 'of', 'the', 'to')

def upper_case_letter(match):
    return match.group(0).upper()

def capitalize_patronymic(match):
    return match.group(1) + match.group(2).upper()

@register.filter()
def month_name(month_number):
    return calendar.month_name[month_number]

@register.filter()
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

@register.filter()
def speech_speaker(speech):
    if speech.speaker_id:
        name = speech.speaker.name
    else:
        name = speech.speaker_display
    if not_all_caps.search(name):
        return name
    else:
        return speaker_name(name)

@register.filter()
def speaker_name(name):
    return ' '.join(patronymic.sub(capitalize_patronymic, component.lower().capitalize()) for component in name.split(' '))

@register.filter()
def person_name(name):
    return honorifics.sub('', speaker_name(name))

@register.filter()
def speech_class(speech):
    if speech.speaker_id:
        return 'person'
    elif speech.speaker_display in ('THE PREMIER', 'THE LIEUTENANT GOVERNOR', 'THE ADMINISTRATOR'):
        return 'government'
    elif speech.speaker_display:
        return 'role'
    else:
        return 'narrative'

@register.filter()
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
