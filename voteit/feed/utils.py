# -*- coding: utf-8 -*-
import os

from feedgen.feed import FeedGenerator
from pyramid.traversal import resource_path
from repoze.catalog.query import Any, Eq
from voteit.core import _ as voteit_mf

from voteit.feed.exceptions import FeedDirectoryNotFound
from voteit.feed.interfaces import IFeedSettings
from voteit.feed import _


def get_feed_dir(settings):
    if 'voteit.feed.dir' not in settings:
        raise FeedDirectoryNotFound("voteit.feed.dir not present in settings")
    path = settings['voteit.feed.dir']
    if os.access(path, os.W_OK):
        return path
    raise FeedDirectoryNotFound("%s is not a writable directory" % path)


def get_meeting_rss_file_name(request):
    fname = "%s.rss" % request.meeting.uid
    file_dir = get_feed_dir(request.registry.settings)
    return os.path.join(file_dir, fname)


def create_feed_object(request):
    settings = IFeedSettings(request.meeting, {})
    te = request.localizer.translate
    fg = FeedGenerator()
    fg.id(rss_feed_url(request, token=settings.get('token', None))) #Mandatory for atom feeds
    fg.title(request.meeting.title)
    fg.description(settings.get('description_text', te(_("No description"))))
    #fg.author({'name': 'XXXX', 'email': 'xxx@xxx.de'})
    fg.link(href=request.resource_url(request.meeting), rel='alternate')
    #fg.icon('http://ex.com/icon.jpg')
    #fg.logo('http://ex.com/logo.jpg')
    #fg.rights('cc-by')
    #fg.subtitle('This is a cool feed!')
    fg.link(href=rss_feed_url(request, token=settings.get('link_token')), rel='self')
    fg.language(request.localizer.locale_name)
    # Fetch objects we want to interact with
    limit = settings.get('limit', 50)
    type_names = list(settings.get('type_names', ()))
    items = get_feed_items(request, type_names, limit=limit)
    # Create feed entries
    for obj in items:
        # Newest first is already the case in items
        fe = fg.add_entry(order='append')
        author_txt = request.creators_info(obj.creator, portrait=False, no_tag=True)
        # Needed?
        fe.id(request.resource_url(obj))
        if obj.type_name == 'Poll':
            fe.title(te(_("${state} poll: ${title}",
                          mapping={'state': te(voteit_mf(obj.current_state_title(request))), 'title': obj.title})))
            fe.content()
            #fe.summary()
        if obj.type_name == 'DiscussionPost':
            fe.title(te(_("Discussion post by ${name}", mapping={'name': author_txt})))
            fe.content(obj.text)
            #fe.summary()
        if obj.type_name == 'Proposal':
            fe.title(te(_("Proposal by ${name}", mapping={'name': author_txt})))
            fe.content(request.render_proposal_text(obj, tag_func=lambda x: x))
            #fe.summary()
        fe.link(href=request.resource_url(obj), rel='alternate')
        fe.author(name=author_txt)
    return fg


def get_feed_items(request, type_names, limit=50):
    query = Any('type_name', type_names) & \
            Eq('path', resource_path(request.meeting))
    docids = request.root.catalog.query(query, sort_index='created', reverse=True)[1]
    # We need to exclude entries within a private agenda item
    # Since resolve docids returns a generator this shouldn't cause too much performance problems.
    items = []
    for obj in request.resolve_docids(docids, perm=None):
        # FIXME: Wfs will be refactored in voteit.core
        if obj.type_name == 'Poll' and obj.get_workflow_state() == 'private':
            continue
        if obj.__parent__.get_workflow_state() in ('upcoming', 'ongoing', 'closed'):
            items.append(obj)
        if len(items) >= limit:
            break
    return items


def write_rss_file(request):
    fg = create_feed_object(request)
    fname = get_meeting_rss_file_name(request)
    fg.rss_file(fname, pretty=True)


def rss_feed_url(request, token=None):
    query = {}
    if token:
        query['t'] = token
    return request.resource_url(request.meeting, 'meeting_feed.rss', query=query)
