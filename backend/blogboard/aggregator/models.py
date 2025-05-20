from django.db import models
from django.utils import timezone

class Source(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the blog source")
    url = models.URLField(max_length=500, unique=True, help_text="Main URL of the blog")
    rss_feed_url = models.URLField(max_length=500, unique=True, help_text="URL of the RSS/Atom feed")
    last_fetched_time = models.DateTimeField(null=True, blank= True , help_text= "when the feed waslast updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Blog Source'
        verbose_name_plural = 'Blog Sources'
        ordering = ['name']

    

class Article(models.Model):

    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name= "articles", help_text= "the blog source of this article")
    title = models.CharField(max_length=500, help_text= "Title of the article")
    link = models.URLField(max_length=1000, unique= True, help_text="Permanent link of the article")
    publication_date = models.DateTimeField(null= True, blank=True, help_text= "when the article was originally published")
    content_snippet = models.TextField(blank=True, help_text= "Content of the article")
    fetched_date = models.DateTimeField(auto_now_add=True, help_text="When this article was fetched and stored")
    guid = models.CharField(max_length=500, blank=True, null=True, db_index=True,help_text="globally unique identifier if available")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-publication_date','-fetched_date']
