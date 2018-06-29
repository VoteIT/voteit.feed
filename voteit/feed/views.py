# -*- coding: utf-8 -*-
import os

from arche.views.base import BaseView, DefaultEditForm
from pyramid.response import FileResponse
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from voteit.core import security
from voteit.core.models.interfaces import IMeeting
from voteit.core.views.control_panel import control_panel_category
from voteit.core.views.control_panel import control_panel_link

from voteit.feed import _
from voteit.feed.interfaces import IFeedSettings
from voteit.feed.utils import get_meeting_rss_file_name, rss_feed_url
from voteit.feed.utils import write_rss_file


@view_config(context = IMeeting,
             name = "meeting_feed.rss",
             permission = NO_PERMISSION_REQUIRED)
class MeetingRSSFeedView(BaseView):

    def __call__(self):
        settings = IFeedSettings(self.context)
        if not settings.get('enable_rss'):
            raise HTTPForbidden("RSS feeds not enabled")
        token = settings.get('link_token')
        if token and token != self.request.GET.get('t', object()):
            raise HTTPNotFound("RSS URL doesn't match")
        rss_file_name = get_meeting_rss_file_name(self.request)
        if not os.path.isfile(rss_file_name):
            raise HTTPNotFound("No entries")
        return FileResponse(rss_file_name, content_type='application/rss+xml')


@view_config(context = IMeeting,
             name = "feed_settings_form",
             renderer = "arche:templates/form.pt",
             permission = security.MODERATE_MEETING)
class ProposalSettingsForm(DefaultEditForm):
    type_name = 'Feed'
    schema_name = 'settings'
    title = _("Feed settings")

    @property
    def feed_settings(self):
        return IFeedSettings(self.context)

    def appstruct(self):
        return dict(self.feed_settings)

    def save_success(self, appstruct):
        if dict(self.feed_settings) != appstruct:
            self.feed_settings.clear()
            self.feed_settings.update(appstruct)
        if appstruct['enable_rss']:
            # Rewriting this every time settings change is a good idea
            write_rss_file(self.request)
        return HTTPFound(location=self.request.resource_url(self.context))


def feeds_enabled(context, request, va):
    settings = IFeedSettings(request.meeting, {})
    return bool(settings.get('enable_rss', False))


def rss_feed_link(context, request, va, **kw):
    settings = IFeedSettings(request.meeting, {})
    if settings.get('enable_rss', False):
        link_token = settings.get('link_token', None)
        return """<a href="%s">%s</a>""" % (
            rss_feed_url(request, token=link_token),
            request.localizer.translate(va.title)
        )


def includeme(config):
    config.scan(__name__)
    config.add_view_action(
        control_panel_category,
        'control_panel', 'feed',
        panel_group='control_panel_feed',
        title=_("RSS Feeds"),
        check_active=feeds_enabled,
    )
    config.add_view_action(
        control_panel_link,
        'control_panel_feed', 'settings',
        title=_("Settings"),
        view_name='feed_settings_form',
    )
    config.add_view_action(
        rss_feed_link,
        'control_panel_feed', 'link_to_feed',
        title=_("Link to RSS feed"),
    )
