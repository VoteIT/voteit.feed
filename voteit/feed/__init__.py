from pyramid.i18n import TranslationStringFactory

FeedMF = TranslationStringFactory('voteit.feed')


def includeme(config):
    """ Include feed adapter, register views and content factories."""
    config.scan('voteit.feed')
    from pyramid.chameleon_zpt import renderer_factory as zpt_rf
    config.add_renderer('.xml', zpt_rf)
    config.add_translation_dirs('voteit.feed:locale/')
    from voteit.feed.models import FeedHandler
    config.registry.registerAdapter(FeedHandler)
