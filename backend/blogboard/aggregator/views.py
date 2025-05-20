from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from aggregator.models import Source,Article
from aggregator.serializers import SourceSeralizer, ArticleSerializer, ArticleDetailSerializer

class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSeralizer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'url', 'rss_feed_url']
    ordering_fields = ['name', 'last_fetched_time', 'created_at']
    ordering = ['name']

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['source', 'publication_date']
    search_fields = ['title', 'content_snippet', 'source__name','link']
    ordering = ['-publication_date']

    
    def get_serializer_class(self):
        if self.action == 'retreive':
            return ArticleDetailSerializer
        return ArticleSerializer
    

    