from django.core.management.base import BaseCommand, CommandError

import requests
from speeches.models import Speaker
from popolo.models import Membership, Organization, Post
from instances.models import Instance

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
            record, created = Organization.objects.get_or_create(
                identifiers__identifier=json['_id'],
                defaults={
                    'name': json['name'],
                    'classification': json['classification'],
                }
            )
            if created:
                record.identifiers.create(
                    identifier=json['_id'],
                    scheme='JSON',
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

        for json in self.get('persons'):
            record, created = Speaker.objects.get_or_create(
                instance=instance,
                identifiers__identifier=json['_id'],
                defaults={
                    'name': json['name'],
                    'family_name': json['family_name'],
                    'given_name': json['given_name'],
                    'email': json.get('email'),
                    'image': json.get('image'),
                }
            )
            if created:
                record.identifiers.create(
                    identifier=json['_id'],
                    scheme='JSON',
                )
                record.sources.create(
                    url=json['sources'][0]['url'],
                )

        for json in self.get('posts'):
            record, created = Post.objects.get_or_create(
                label=json['label'],
                defaults={
                    'role': json['role'],
                    'organization': Organization.objects.get(identifiers__identifier=json['organization_id']),
                }
            )
            if created:
                record.sources.create(
                    url=json['sources'][0]['url'],
                    note=json['sources'][0]['note'],
                )

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
