from rest_framework import serializers
from aggregator.models import Source, Article

class SourceSeralizer(serializers.ModelSerializer):
    
    class Meta:
        model = Source
        fields = ['id', 'name', 'url', 'rss_feed_url', 'last_fetched_time', 'created_at']

class ArticleSerializer(serializers.ModelSerializer):

    source = serializers.PrimaryKeyRelatedField(read_only=True)
    source_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 
            'title', 
            'link', 
            'publication_date', 
            'content_snippet', 
            'fetched_date',
            'guid',
            'source', # This will be the ID of the source
            'source_info', # if using SerializerMethodField
        ]
    def get_source_info(self, obj):
        if obj.source:
            return {
                'id': obj.source.id,
                'name': obj.source.name,
                'url': obj.source.url
            }
        
class ArticleDetailSerializer(serializers.ModelSerializer):
    source = SourceSeralizer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 
            'title', 
            'link', 
            'publication_date', 
            'content_snippet', 
            'fetched_date',
            'guid',
            'source',         
        ]