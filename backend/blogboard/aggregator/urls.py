from django.urls import path,include
from rest_framework.routers import DefaultRouter
from aggregator.views import ArticleViewSet,SourceViewSet

router = DefaultRouter()
router.register(r'sources', SourceViewSet, basename='source')
router.register(r'article',ArticleViewSet,basename='article')

urlpatterns = [
    path('', include(router.urls))
]