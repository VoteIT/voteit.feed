import colander
import deform
from betahaus.pyracont.decorators import schema_factory

from voteit.feed import FeedMF as _


@schema_factory('RssSettingsMeetingSchema', title = _(u"RSS settings"))
class RssSettingsMeetingSchema(colander.MappingSchema):
    rss_feed = colander.SchemaNode(colander.Boolean(),
        title = _(u"Activate RSS feed"),
        description = _(u"rss_feed_checkbox_description",
                        default=u"When the checkbox below is checked your meeting will be able to show a public RSS feed that can be followed with a RSS reader. This feed will contain info about when changes are made in the meeting and who did the changes. You can access the feed on: 'The meeting URL' + '/feed'. This should be something like 'www.yourdomain.com/yourmeetingname/feed'. If you want the feed to show up in an iframe you can use '/framefeed' instead. This is an advanced feature and read more about it in the manual on wiki.voteit.se. Please note a word of warning: the feed is public for all who can figure it out."),
        default = False,
    )
