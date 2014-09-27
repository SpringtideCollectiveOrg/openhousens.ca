# OpenHouseNS: Maintenance

## Migrations

    python manage.py migrate --noinput

## Abbreviations

Question Period section titles contain many abbreviations. Run this command to find new abbreviations:

    python manage.py abbreviations

If any new abbreviations are found, add them to `legislature/synonyms.py` so that they can be expanded in the views.

## Validations

    python manage.py validate
