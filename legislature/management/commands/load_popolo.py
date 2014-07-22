import re

from django.core.management.base import BaseCommand, CommandError

import requests
from instances.models import Instance
from popolo.models import Membership, Organization, Post
from speeches.models import Speaker

class Command(BaseCommand):
    args = 'base-url'
    help = 'Imports people, memberships and organizations in Popolo format'

    def get(self, path):
        return requests.get(self.base_url + path).json()

    def handle(self, *args, **options):
        if not args:
            raise CommandError('Missing base URL')
        elif len(args) > 1:
            raise CommandError('Unexpected arguments: %s' % args[1:])

        self.base_url = args[0]
        if not self.base_url.endswith('/'):
            self.base_url += '/'

        instance, _ = Instance.objects.get_or_create(label='default')

        for json in self.get('organizations'):
            defaults = {
                'name': json['name'],
                'classification': json['classification'],
            }

            record, created = Organization.objects.get_or_create(
                identifiers__identifier=json['_id'],
                defaults=defaults,
            )
            if created:
                record.identifiers.create(
                    identifier=json['_id'],
                    scheme='Popolo',
                )
                if json.get('other_names'):
                    record.other_names.create(
                        name=json['other_names'][0]['name'],
                    )
                if json.get('sources'):
                    record.sources.create(
                        url=json['sources'][0]['url'],
                        note=json['sources'][0]['note'],
                    )
            else:
                for attr, value in defaults.items():
                    setattr(record, attr, value)
                record.save()

        for json in self.get('persons'):
            defaults = {
                'name': json['name'],
                'family_name': json['family_name'],
                'given_name': json['given_name'],
                'sort_name': json['sort_name'],
                'email': json.get('email'),
                'image': json.get('image'),
            }

            record, created = Speaker.objects.get_or_create(
                instance=instance,
                identifiers__identifier=json['_id'],
                defaults=defaults,
            )
            if created:
                part = re.search(r'([^/]+)\Z', json['sources'][0]['url']).group(1).lower()
                part = re.sub(r'[._-]+', '.', part)
                part = re.sub(r'[^a-z.]', '', part)
                record.identifiers.create(
                    identifier=json['_id'],
                    scheme='Popolo',
                )
                record.identifiers.create(
                    identifier='/ontology/person/ca-ns.%s' % part,
                    scheme='Akoma Ntoso',
                )
                record.sources.create(
                    url=json['sources'][0]['url'],
                )
            else:
                for attr, value in defaults.items():
                    setattr(record, attr, value)
                record.save()

        for json in self.get('posts'):
            defaults = {
                'role': json['role'],
                'organization': Organization.objects.get(identifiers__identifier=json['organization_id']),
            }

            record, created = Post.objects.get_or_create(
                label=json['label'],
                defaults=defaults,
            )
            if created:
                record.sources.create(
                    url=json['sources'][0]['url'],
                    note=json['sources'][0]['note'],
                )
            else:
                for attr, value in defaults.items():
                    setattr(record, attr, value)
                record.save()

        for json in self.get('memberships'):
            defaults = {
                'label': json.get('label', ''),  # @see https://github.com/openpolis/django-popolo/pull/12
                'role': json.get('role', ''),
            }
            if json.get('post_id'):
                defaults['post'] = Post.objects.get(label=json['label'])

            record, created = Membership.objects.get_or_create(
                organization=Organization.objects.get(identifiers__identifier=json['organization_id']),
                person=Speaker.objects.get(identifiers__identifier=json['person_id']),
                defaults=defaults,
            )
            if created:
                record.sources.create(
                    url=json['sources'][0]['url'],
                    note=json['sources'][0]['note'],
                )
            else:
                for attr, value in defaults.items():
                    setattr(record, attr, value)
                record.save()
