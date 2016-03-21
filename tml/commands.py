from __future__ import absolute_import
# encoding: UTF-8
import os
import time
from .api.client import Client
from .cache import CachedClient
from .config import CONFIG
from .utils import pj, rel, rm_symlink, untar, chdir, ts
from .logger import get_logger
from .application import Application
from .language import Language

__author__ = 'xepa4ep'


def extract_version(client, app_key):
    return client.get_cache_version()


def download_release(cache_dir=None, force_dir=True):
    """Utility function that downloads latest release from cdn, extracts it and mark it as current release."""
    t0 = time.time()
    logger = get_logger()
    logger.debug('Starting cache download...')
    cache_dir = cache_dir or CachedClient.default_dir()
    if not force_dir:
        raise IOError("Directory `cache_dir` does not exist. Create before or et `force_dir` argument to true")
    if not os.path.exists(cache_dir):   # force dirs to create
        os.makedirs(cache_dir)
    os.chmod(cache_dir, 0777)
    app_key = CONFIG.application_key()
    client = Client(app_key)
    selected_version = extract_version(client, app_key)
    logger.debug("Downloading Version: %s", selected_version)

    archive_name = u'%s.tar.gz' % selected_version
    full_path = pj(cache_dir, archive_name)
    logger.debug("Downloading cache file: %s", selected_version)
    with open(full_path, 'wb') as fd:
        gzip_data = client.cdn_call('release', opts={'cache_version': selected_version, 'raw': True})
        fd.write(gzip_data)
    logger.debug("Extracting cache file...")
    version_path = pj(cache_dir, selected_version)
    untar(full_path, dest_path=version_path)
    logger.debug("Cache has been stored under `%s`", full_path)
    with chdir(cache_dir):
        current_ln = 'current'
        rm_symlink(current_ln)
        os.symlink(selected_version, current_ln)
    logger.debug("The new version `%s` has been marked as current", selected_version)
    t1 = time.time()
    logger.debug("Download process took %s seconds.", round(t1 - t0, 2))


def warmup_cache(version=None):
    t0 = time.time()
    logger = get_logger()
    logger.debug("Starting cache warmup...")
    app_key = CONFIG.application_key()
    client = Client(app_key)
    # 1. get version
    selected_version = version or extract_version(client, app_key)
    logger.debug("Warming up version: %s", selected_version)
    # 2. fetch and store app
    application = client.cdn_call('application', {'t': ts()}, {'cache_version': selected_version})
    CachedClient.instance().store(Application.cache_key, application)

    # 3. fetch sources
    sources = client.cdn_call('sources', {'t': ts()}, {'uncompressed': True, 'cache_version': selected_version}) or []
    for lang in application['languages'] or []:
        locale = lang['locale']
        lang_key = Language.cache_key(locale)
        language = client.cdn_call(lang_key, {'t': ts()}, {'cache_version': selected_version})
        CachedClient.instance().store(lang_key, language)
        for src in sources:
            src_key = '%s/sources/%s' % (locale, src)
            source = client.cdn_call(src_key, {'t': ts()}, {'cache_version':selected_version})
            CachedClient.instance().store(src_key, source)

    t1 = time.time()
    logger.debug("Cache warmup took %s", round(t1 - t0, 2))

