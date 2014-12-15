import os.path

from boto.s3.connection import S3Connection
from six.moves.urllib.parse import urlsplit
from speeches.management.commands.load_akomantoso import Command as AkomaNtosoCommand


class Command(AkomaNtosoCommand):
    def document_list(self, options):
        parsed = urlsplit(options['dir'])
        bucket = S3Connection().get_bucket(parsed.netloc.replace('.s3.amazonaws.com', ''))

        start_date = options['start_date']
        valid = lambda f: f >= start_date if start_date else lambda _: True

        return [key.generate_url(3600)
                for key in bucket.get_all_keys(prefix=parsed.path[1:])
                if os.path.splitext(key.key)[1][1:] == self.document_extension and valid(os.path.basename(key.key))]

    def document_valid(self, path):
        return True
