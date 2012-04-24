from zope.interface import Attribute
from zope.interface import Interface


class IFeedHandler(Interface):
    """ An adapter for meetings that handle feeds. """
    feed_storage = Attribute("""Storage for feed content.""")

    def __init__(context):
        """ Object needs a meeting to adapt. """
    
    def add(context_uid, message, tags=()):
        """ Add a feed entry.
            context_uid: the uid of the object that triggered the entry.
            message: the message to store.
            tags: list of tags, works as a feed category.
        """

class IFeedEntry(Interface):
    """ A persistent feed entry. """
    created = Attribute("When it was created, in UTC time.")
    context_uid = Attribute("UID of the context that triggered this feed entry.")
    message = Attribute("Message")
    tags = Attribute("Tags, works pretty much like categories for feed entries.")

    def __init__(context_uid, message, tags=()):
        """ Create a feed entry. """