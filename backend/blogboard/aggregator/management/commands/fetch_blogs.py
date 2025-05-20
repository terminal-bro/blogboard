# aggregator_app/management/commands/fetch_blogs.py

import feedparser
import logging # For logging information and errors
from datetime import datetime
from django.utils import timezone # For handling timezone-aware datetimes
from django.core.management.base import BaseCommand, CommandError
from aggregator.models import Source, Article
# For parsing datetimes from various formats that feedparser might return
from dateutil import parser as date_parser


# Configure logging
logger = logging.getLogger(__name__)
# You can customize logging further, e.g., by adding handlers in your settings.py

class Command(BaseCommand):
    help = 'Fetches new blog posts from registered RSS/Atom feeds'

    def handle(self, *args, **options):
        """
        The main logic of the management command.
        """
        self.stdout.write(self.style.SUCCESS('Starting to fetch blog posts...'))
        
        sources = Source.objects.all()
        if not sources.exists():
            self.stdout.write(self.style.WARNING('No sources found in the database. Add some sources first.'))
            return

        new_articles_count_total = 0
        updated_sources_count = 0

        for source in sources:
            self.stdout.write(f"Processing source: {source.name} ({source.rss_feed_url})")
            try:
                # It's good practice to set a user-agent
                # Some servers might block requests without one.
                # You can make this more descriptive of your aggregator.
                agent = "BlogAggregator/1.0 (+http://your-aggregator-website.com)" # Replace with your details
                feed_data = feedparser.parse(source.rss_feed_url, agent=agent)

                if feed_data.bozo: # bozo is 1 if the feed is not well-formed
                    # bozo_exception often contains more details
                    error_message = f"Feed for {source.name} is not well-formed or could not be parsed. "
                    if hasattr(feed_data, 'bozo_exception'):
                        error_message += f"Reason: {feed_data.bozo_exception}"
                    logger.warning(error_message)
                    self.stderr.write(self.style.ERROR(error_message))
                    continue # Skip to the next source

                new_articles_for_source = 0
                for entry in feed_data.entries:
                    article_link = entry.get('link')
                    if not article_link:
                        logger.warning(f"Skipping entry without a link in feed for {source.name}: {entry.get('title', 'No Title')}")
                        continue

                    # --- Duplicate Check ---
                    # Prioritize GUID if available and unique, otherwise use link
                    article_guid = entry.get('id') # 'id' is often used for GUID in feeds
                    
                    # Check if article already exists by link or guid
                    # This ensures we don't create duplicates if the link is the most reliable unique field.
                    if Article.objects.filter(link=article_link).exists():
                        # self.stdout.write(f"Article already exists (by link): {article_link}")
                        continue
                    
                    # Optional: More robust check if GUID is reliable
                    # if article_guid and Article.objects.filter(guid=article_guid, source=source).exists():
                    #     self.stdout.write(f"Article already exists (by GUID): {article_guid} for source {source.name}")
                    #     continue


                    # --- Extract Article Details ---
                    title = entry.get('title', 'No Title Provided')
                    
                    # --- Publication Date Parsing ---
                    published_time_struct = entry.get('published_parsed') # feedparser pre-parses this
                    publication_date = None
                    if published_time_struct:
                        try:
                            # Convert struct_time to datetime object
                            publication_date = datetime(*published_time_struct[:6])
                            # Make it timezone-aware using Django's current timezone
                            # It's often better to store everything in UTC.
                            # If TIME_ZONE in settings.py is 'UTC', this will be UTC.
                            publication_date = timezone.make_aware(publication_date, timezone.get_current_timezone())
                        except Exception as e:
                            logger.warning(f"Could not parse publication date for '{title}' from {source.name}. Error: {e}")
                            # Fallback if 'published_parsed' fails or is not present
                            published_raw = entry.get('published') or entry.get('updated')
                            if published_raw:
                                try:
                                    publication_date = date_parser.parse(published_raw)
                                    if timezone.is_naive(publication_date):
                                        publication_date = timezone.make_aware(publication_date, timezone.get_current_timezone())
                                except Exception as e_inner:
                                     logger.warning(f"Could not parse raw publication date string '{published_raw}' for '{title}'. Error: {e_inner}")


                    content_snippet = entry.get('summary', '')
                    if not content_snippet and entry.get('content'):
                        # Sometimes full content is in 'content' field (list of dicts)
                        # Taking the first one if available
                        content_list = entry.get('content')
                        if isinstance(content_list, list) and len(content_list) > 0:
                            content_snippet = content_list[0].get('value', '')
                    
                    # Truncate snippet if it's too long (optional)
                    # MAX_SNIPPET_LENGTH = 1000 
                    # if len(content_snippet) > MAX_SNIPPET_LENGTH:
                    #    content_snippet = content_snippet[:MAX_SNIPPET_LENGTH] + "..."

                    try:
                        Article.objects.create(
                            source=source,
                            title=title,
                            link=article_link,
                            publication_date=publication_date,
                            content_snippet=content_snippet,
                            guid=article_guid # Store GUID if available
                        )
                        new_articles_for_source += 1
                        new_articles_count_total += 1
                    except Exception as e: # Catch integrity errors or other DB issues
                        self.stderr.write(self.style.ERROR(f"Error saving article '{title}' from {source.name}: {e}"))
                        logger.error(f"Error saving article '{title}' from {source.name}: {e}", exc_info=True)


                if new_articles_for_source > 0:
                    self.stdout.write(self.style.SUCCESS(f"Added {new_articles_for_source} new articles from {source.name}."))
                
                # Update last_fetched_time for the source
                source.last_fetched_time = timezone.now()
                source.save(update_fields=['last_fetched_time'])
                updated_sources_count +=1

            except Exception as e:
                # Catch other errors like network issues, timeouts, etc.
                self.stderr.write(self.style.ERROR(f"Failed to process source {source.name}: {e}"))
                logger.error(f"Failed to process source {source.name}: {e}", exc_info=True)
        
        self.stdout.write(self.style.SUCCESS(f"Finished fetching posts. Total new articles: {new_articles_count_total} from {updated_sources_count} successfully processed sources."))

