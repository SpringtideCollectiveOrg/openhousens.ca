# OpenHouseNS: Maintenance

## Migrations

    python manage.py migrate --noinput

## Abbreviations

Question Period section titles contain many abbreviations. Run this command to find new abbreviations:

    python manage.py abbreviations

If any new abbreviations are found, add them to `legislature/synonyms.py` so that they can be expanded in the views.

## Validations

All speeches should belong to a section:

```python
from speeches.models import Speech
Speech.objects.filter(section=None)
```

All sections should have speeches:

```python
from speeches.models import Section
for section in Section.objects.filter(speech__section_id=None).filter(children__parent_id=None).order_by('start_date'):
    print(section.get_ancestors[0].start_date, section.title)
```

All boundaries should match a membership label:

```python
import requests
from popolo.models import Membership
url = 'http://represent.opennorth.ca/boundaries/nova-scotia-electoral-districts/?limit=0'
for boundary in requests.get(url).json()['objects']:
    try:
        _ = Membership.objects.get(label='MLA for %s' % boundary['name'].replace('—', '-'))  # m-dash
    except Membership.DoesNotExist:
        print(boundary['name'])
```