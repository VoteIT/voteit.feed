from logging import getLogger

from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('voteit.feed')


logger = getLogger(__name__)


def includeme(config):
    from voteit.feed.exceptions import FeedDirectoryNotFound
    from voteit.feed.utils import get_feed_dir
    settings = config.registry.settings
    try:
        get_feed_dir(settings)
    except FeedDirectoryNotFound as exc:
        logger.critical("voteit.feed.dir not configured correctly - aborting load of voteit.feed: %s", str(exc))
        return
    config.add_translation_dirs('voteit.feed:locale/')
    config.include('.models')
    config.include('.schemas')
    config.include('.views')
