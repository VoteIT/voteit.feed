# -*- coding: utf-8 -*-
from arche.interfaces import IObjectAddedEvent
from arche.interfaces import IObjectUpdatedEvent
from arche.interfaces import IObjectWillBeRemovedEvent
from arche.utils import AttributeAnnotations
from pyramid.interfaces import INewResponse
from pyramid.threadlocal import get_current_request
from voteit.core.interfaces import IWorkflowStateChange
from voteit.core.models.interfaces import IAgendaItem
from voteit.core.models.interfaces import IDiscussionPost
from voteit.core.models.interfaces import IMeeting
from voteit.core.models.interfaces import IPoll
from voteit.core.models.interfaces import IProposal
from zope.component import adapter
from zope.interface import implementer

from voteit.feed.interfaces import IFeedSettings
from voteit.feed.utils import write_rss_file


@adapter(IMeeting)
@implementer(IFeedSettings)
class FeedSettings(AttributeAnnotations, object):
    attr_name = '_voteit_feed_settings'


# Cases when RSS feed needs an update:
# - Added, deleted, modified posts
# - Workflow changes for Agenda Items and for Polls


def mark_need_for_rewrite(*args):
    request = get_current_request()
    if not hasattr(request, '_maybe_write_new_feed'):
        request._maybe_write_new_feed = True


def check_ai_state_change(context, event):
    if event.old_state == 'private' or event.new_state == 'private':
        mark_need_for_rewrite()


def maybe_rewrite_rss(event):
    request = event.request
    if getattr(request, 'exception', None) is None and hasattr(request, '_maybe_write_new_feed'):
        settings = IFeedSettings(request.meeting, {})
        if settings.get('enable_rss'):
            write_rss_file(request)


def includeme(config):
    config.registry.registerAdapter(FeedSettings)
    for content_iface in (IPoll, IProposal, IDiscussionPost):
        for event_iface in (IObjectUpdatedEvent, IObjectAddedEvent, IObjectWillBeRemovedEvent):
            config.add_subscriber(mark_need_for_rewrite, [content_iface, event_iface])
    # FIXME: IWorkflowStateChange may disappear when WF is rewritten in VoteIT
    config.add_subscriber(check_ai_state_change, [IAgendaItem, IWorkflowStateChange])
    config.add_subscriber(maybe_rewrite_rss, INewResponse)
