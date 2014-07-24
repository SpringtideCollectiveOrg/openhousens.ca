from haystack import indexes
from speeches.models import Speech

# @note We want to use decay functions to decrease the relevance of older
#   speeches, but Haystack doesn't support scoring out-of-the-box.
# @see http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html
# @see http://www.stamkracht.com/extending-haystacks-elasticsearch-backend/
class SpeechIndex(indexes.SearchIndex, indexes.Indexable):
    # @see http://django-haystack.readthedocs.org/en/latest/searchfield_api.html
    text = indexes.CharField(document=True, model_attr='text')
    title = indexes.CharField(model_attr='title', boost=1.2)
    speaker = indexes.IntegerField(model_attr='speaker_id', null=True)
    start_date = indexes.DateTimeField(model_attr='start_date', null=True)

    # @see http://django-haystack.readthedocs.org/en/latest/searchindex_api.html
    # @see https://github.com/toastdriven/django-haystack/blob/master/haystack/indexes.py
    def get_model(self):
        return Speech

    def index_queryset(self, using=None):
        """
        Exclude narrative from the index.
        """
        return self.get_model()._default_manager.exclude(speaker_id=None, speaker_display=None)

    def load_all_queryset(self):
        """
        Reduce the number of SQL queries to render search results. We might
        alternatively store a rendered result or more fields in ElasticSearch.
        """
        return self.get_model()._default_manager.all().prefetch_related('speaker', 'speaker__memberships', 'speaker__memberships__organization', 'section', 'section__parent')

    # @see http://django-haystack.readthedocs.org/en/latest/boost.html
    def prepare(self, obj):
        """
        Decrease the relevance of speeches by anonymous speakers and by roles,
        including the Speaker, the Sergeant-at-Arms and clerks.
        """
        data = super(SpeechIndex, self).prepare(obj)
        if not obj.speaker_id and obj.speaker_display not in ('THE PREMIER', 'THE LIEUTENANT GOVERNOR', 'THE ADMINISTRATOR'):
            data['boost'] = 0.8
        return data

    def get_updated_field(self):
        return 'modified'
