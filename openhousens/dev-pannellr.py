from .local import *


#rickey's local db settings
import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://postgres:Jennifer1@localhost/openhousens')}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': os.getenv('ELASTICSEARCH_URL', 'http://127.0.0.1:9200/'),
        'INDEX_NAME': 'openhousens',
        'EXCLUDED_INDEXES': [
            'speeches.search_indexes.SpeechIndex',
            'speeches.search_indexes.SectionIndex',
        ],
    },
}
