import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPForbidden

from voteit.feed.interfaces import IFeedHandler


class FeedViewTests(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        self.config.testing_securitypolicy(userid='admin',
                                           permissive=True)

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from voteit.feed.views import FeedView
        return FeedView

    def _fixture(self):
        from voteit.core.testing_helpers import bootstrap_and_fixture
        from voteit.core.testing_helpers import register_catalog
        from voteit.core.models.meeting import Meeting
        from voteit.core.models.agenda_item import AgendaItem
        from voteit.core.models.discussion_post import DiscussionPost
        self.config.include('voteit.feed')
        self.config.registry.settings['default_timezone_name'] = "Europe/Stockholm"
        self.config.include('voteit.core.models.date_time_util')
        register_catalog(self.config)
        root = bootstrap_and_fixture(self.config)
        root['m'] = Meeting()
        root['m'].set_field_value('rss_feed', True)
        root['m']['ai'] = AgendaItem()
        root['m']['ai'].set_workflow_state(self.request, 'upcoming')
        root['m']['ai']['dp'] = DiscussionPost()
        return root

    def test_feed(self):
        from pyramid.interfaces import IResponse
        root = self._fixture()
        obj = self._cut(root['m'], self.request)
        res = obj.feed()
        self.assertTrue(IResponse.providedBy(res))
        self.assertIn('<link>http://example.com/m/</link>', res.body)
        self.assertIn('<link>http://example.com/m/ai/dp/</link>', res.body)
        self.assertIn('admin has written a post in', res.body)

    def test_feed_with_deleted_entry(self):
        from pyramid.interfaces import IResponse
        root = self._fixture()
        del root['m']['ai']
        obj = self._cut(root['m'], self.request)
        res = obj.feed()
        self.assertTrue(IResponse.providedBy(res))
        self.assertIn('<link>http://example.com/m/</link>', res.body)
        self.assertNotIn('<link>http://example.com/m/ai/dp/</link>', res.body)
        self.assertIn('admin has written a post in', res.body)

    def test_framefeed(self):
        root = self._fixture()
        obj = self._cut(root['m'], self.request)
        res = obj.framefeed()
        self.assertEqual(res['active'], True)
        self.assertEqual(len(res['entries']), 2)

    def test_rss_settings(self):
        root = self._fixture()
        obj = self._cut(root['m'], self.request)
        res = obj.rss_settings()
        self.assertIn("Activate RSS feed", res['form'])

    def test_rss_settings_post_without_ajax(self):
        root = self._fixture()
        request = testing.DummyRequest(post = {'save': 'save', '__formid__': 'deform'},
                                       is_xhr = False)
        obj = self._cut(root['m'], request)
        res = obj.rss_settings()
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.location, 'http://example.com/m/')
        self.assertEqual(root['m'].get_field_value('rss_feed'), False)

    def test_rss_settings_post_with_ajax(self):
        root = self._fixture()
        request = testing.DummyRequest(post = {'save': 'save', '__formid__': 'deform'},
                                       is_xhr = True)
        obj = self._cut(root['m'], request)
        res = obj.rss_settings()
        self.assertEqual(res.headers['X-Relocate'], 'http://example.com/m/')
        self.assertEqual(root['m'].get_field_value('rss_feed'), False)

    def test_rss_settings_validation_error(self):
        root = self._fixture()
        # Since the session with csrf tokens isn't initiatet, it will be '' as default
        # - hence causing a validation failiure here
        postdata = {'save': 'save', 'csrf_token': 'bad_token', '__formid__': 'deform'}
        request = testing.DummyRequest(post = postdata,
                                       is_xhr = False)
        obj = self._cut(root['m'], request)
        self.assertRaises(HTTPForbidden, obj.rss_settings)
        # and with ajax
        request = testing.DummyRequest(post = postdata,
                                       is_xhr = True)
        obj = self._cut(root['m'], request)
        self.assertRaises(HTTPForbidden, obj.rss_settings)

    def test_rss_settings_cancel(self):
        self.config.include('voteit.core.models.flash_messages')
        root = self._fixture()
        postdata = {'cancel': 'cancel', '__formid__': 'deform'}
        request = testing.DummyRequest(post = postdata,
                                       is_xhr = False)
        obj = self._cut(root['m'], request)
        res = obj.rss_settings()
        self.assertEqual(res.status, '302 Found')
        # and with ajax
        request = testing.DummyRequest(post = postdata,
                                       is_xhr = True)
        obj = self._cut(root['m'], request)
        res = obj.rss_settings()
        self.assertEqual(res.headers['X-Relocate'], 'http://example.com/m/')



#class FeedViewComponentTests(unittest.TestCase):
#
#    def setUp(self):
#        self.request = testing.DummyRequest()
#        self.config = testing.setUp(request=self.request)
#        self.config.testing_securitypolicy(userid='admin',
#                                           permissive=True)
#
#    def tearDown(self):
#        testing.tearDown()
