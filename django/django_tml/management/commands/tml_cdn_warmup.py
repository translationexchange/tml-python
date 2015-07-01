from django.core.management.base import BaseCommand
from django.conf import settings
from logging import getLogger
from django_tml.translator import Translator
from django_tml.cache import Writeonly
from tml.api.client import Client
from tml.api.cdn import Client as CDNClient


class Command(BaseCommand):
    """
    Warmup cached data
    """
    def handle(self, *args, **options):
        if not settings.TML.get('cdn'):
            print 'CDN not used'
            return
        t = Translator(settings)
        cached_version = t.build_client().client.version
        basic_client = Client(settings.TML.get('token'))
        current_version = CDNClient.current_version(basic_client)
        if cached_version == current_version:
            print 'Cached version is same %d' % cached_version
            return
        print 'Warmup cache for new version %d' % current_version
        cache = Writeonly.wrap(CDNClient(settings.TML.get('token'), current_version))
        for request in cache.keys:
            print 'Warmup %s' % request[0]
            cache.get(*request)
        print 'Warmup complete'
        print 'Update current_version in cache'
        CDNClient.current_version(Writeonly.wrap(basic_client))