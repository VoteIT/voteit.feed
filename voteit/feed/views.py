import pytz

import colander
from deform import Form
from deform import ValidationFailure
from betahaus.viewcomponent import view_action
from betahaus.pyracont.factories import createSchema
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.traversal import find_resource
from pyramid.url import resource_url
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from voteit.core import fanstaticlib
from voteit.core import security
from voteit.core.helpers import ajax_options
from voteit.core.models.interfaces import IAgendaItem
from voteit.core.models.interfaces import IMeeting
from voteit.core.models.schemas import add_csrf_token
from voteit.core.models.schemas import button_save
from voteit.core.models.schemas import button_cancel
from voteit.core.views.base_view import BaseView

from voteit.feed import FeedMF as _
from voteit.feed.fanstaticlib import voteit_feed
from voteit.feed.models import IFeedHandler


class FeedView(BaseView):
    
    @view_config(context=IMeeting, name='feed', permission=NO_PERMISSION_REQUIRED)
    def feed(self):
        """ Renders a rss feed for the meeting """
        return Response(render("templates/meeting_feed.xml", self._get_feed(), request = self.request), content_type='application/rss+xml') 
    
    @view_config(context=IMeeting, name='framefeed', renderer="templates/meeting_framefeed.pt", permission=NO_PERMISSION_REQUIRED)
    def framefeed(self):
        """ Renders a html feed for the meeting """
        voteit_feed.need()
        return self._get_feed()
          
    def _get_feed(self):
        ''' Makes a respone dict for renderers '''
        def _get_url(entry):
            """ If something stored in the database is deleted,
                the query won't return any object since that UID won't exist.
            """
            brains = self.api.get_metadata_for_query(uid=entry.context_uid)
            if brains:
                resource = find_resource(self.api.root, brains[0]['path'])
                return resource_url(resource, self.request)
            return resource_url(self.api.meeting, self.request)
        
        # Borrowed from PyRSS2Gen, thanks for this workaround
        def _format_date(dt):
            """convert a datetime into an RFC 822 formatted date
        
            Input date must be in GMT.
            """
            # Looks like:
            #   Sat, 07 Sep 2002 00:00:01 GMT
            # Can't use strftime because that's locale dependent
            #
            # Isn't there a standard way to do this for Python?  The
            # rfc822 and email.Utils modules assume a timestamp.  The
            # following is based on the rfc822 module.
            tz = pytz.timezone('GMT')
            dt = tz.normalize(dt.astimezone(tz))
            return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
                    ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()],
                    dt.day,
                    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][dt.month-1],
                    dt.year, dt.hour, dt.minute, dt.second)

        feed_handler = self.request.registry.getAdapter(self.context, IFeedHandler)
        self.response['entries'] = feed_handler.feed_storage.values()
        self.response['format_date'] = _format_date
        self.response['active'] = self.context.get_field_value('rss_feed', False);
        self.response['feed_not_active_notice'] = self.api.translate(_(u"This RSS-feed isn't enabled."))
        # only show entries when meeting is ongoing
        self.response['closed'] = self.context.get_workflow_state() == 'closed'
        self.response['get_url'] = _get_url
        return self.response
    
    @view_config(context=IMeeting, name="rss_settings", renderer="voteit.core.views:templates/base_edit.pt", permission=security.EDIT)
    def rss_settings(self):
        schema = createSchema("RssSettingsMeetingSchema").bind(context=self.context, request=self.request)
        add_csrf_token(self.context, self.request, schema)
        form = Form(schema, buttons=(button_save, button_cancel), use_ajax=True, ajax_options=ajax_options)
        self.api.register_form_resources(form)
        fanstaticlib.jquery_form.need()

        post = self.request.POST
        if 'save' in post:
            controls = post.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                if self.request.is_xhr:
                    return Response(render("voteit.core.views:templates/ajax_edit.pt", self.response, request = self.request))
                return self.response
            
            self.context.set_field_appstruct(appstruct)
            
            url = resource_url(self.context, self.request)
            if self.request.is_xhr:
                return Response(headers = [('X-Relocate', url)])
            return HTTPFound(location=url)

        if 'cancel' in post:
            self.api.flash_messages.add(_(u"Canceled"))

            url = resource_url(self.context, self.request)
            if self.request.is_xhr:
                return Response(headers = [('X-Relocate', url)])
            return HTTPFound(location=url)

        #No action - Render form
        appstruct = self.context.get_field_appstruct(schema)
        self.response['form'] = form.render(appstruct)
        return self.response

@view_action('settings_menu', 'rss_settings', title = _(u"RSS settings"), link = "rss_settings", permission = security.MODERATE_MEETING)
def generic_menu_link(context, request, va, **kw):
    """ This is for simple menu items for the meeting root """
    api = kw['api']
    url = "%s%s" % (api.meeting_url, va.kwargs['link'])
    return """<li><a href="%s">%s</a></li>""" % (url, api.translate(va.title))

    
@view_action('meeting', 'feed', title = _(u"RSS feed"), link = "feed", )
def feed_menu_link(context, request, va, **kw):
    """ This is for simple menu items for the meeting root """
    api = kw['api']
    url = api.resource_url(api.meeting, request) + va.kwargs['link']
    if api.meeting.get_field_value('rss_feed', False):
        return """<li><a href="%s">%s</a></li>""" % (url, api.translate(va.title))
    return '' # pragma : no coverage

@view_action('head', 'feed')
def feed_head_link(context, request, va, **kw):
    api = kw['api']
    if api.meeting and api.meeting.get_field_value('rss_feed', False): 
        return '<link rel="alternate" type="application/rss+xml" title="%s" href="%sfeed">' %  (api.meeting.title, api.resource_url(api.meeting, api.request))
    return '' # pragma : no coverage
