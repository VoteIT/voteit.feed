from pyramid.i18n import TranslationStringFactory

FeedMF = TranslationStringFactory('voteit.feed')


def includeme(config):
    """ Include feed adapter, register views and content factories."""
    config.scan('voteit.feed')
    config.add_translation_dirs('voteit.feed:locale/')
    from voteit.core.models.interfaces import IMeeting
    from voteit.feed.interfaces import IFeedHandler
    from voteit.feed.models import FeedHandler
    config.registry.registerAdapter(FeedHandler, (IMeeting,), IFeedHandler)