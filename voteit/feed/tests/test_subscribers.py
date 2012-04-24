from unittest import TestCase

from pyramid import testing
from repoze.folder.events import ObjectAddedEvent
from zope.component.event import objectEventNotify

from voteit.core.events import ObjectUpdatedEvent
from voteit.core.testing_helpers import register_workflows
from voteit.core.testing_helpers import bootstrap_and_fixture

from voteit.feed.interfaces import IFeedHandler


class FeedsTests(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()

    def _fixture(self):
        from voteit.core.models.meeting import Meeting
        from voteit.core.models.agenda_item import AgendaItem        
        root = bootstrap_and_fixture(self.config)
        root['m'] = Meeting() 
        root['m']['ai'] = AgendaItem()
        return root
        
    def _subscribers(self):
        #Add subscribers
        self.config.scan('voteit.feed.subscribers')
        #Add log handler
        self.config.include('voteit.feed.models')
        #Add LogEntry content type
        self.config.scan('voteit.feed.models')

    def test_discussion_post_added(self):
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        
        ai.set_workflow_state(self.request, 'upcoming')
        
        self._subscribers()
        
        from voteit.core.models.discussion_post import DiscussionPost
        ai['post'] = DiscussionPost()

        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        self.assertEqual(len(adapter.feed_storage), 1)
        self.assertEqual(adapter.feed_storage[0].tags, ('discussion_post', 'added',))
        
    def test_proposal_added(self):
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        
        ai.set_workflow_state(self.request, 'upcoming')
        
        self._subscribers()
        
        from voteit.core.models.proposal import Proposal
        ai['proposal'] = Proposal()

        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        self.assertEqual(len(adapter.feed_storage), 1)
        self.assertEqual(adapter.feed_storage[0].tags, ('proposal', 'added',))

    def test_poll_state_change(self):
        register_workflows(self.config)
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        
        meeting.set_workflow_state(self.request, 'upcoming')
        meeting.set_workflow_state(self.request, 'ongoing')
        ai.set_workflow_state(self.request, 'upcoming')
        ai.set_workflow_state(self.request, 'ongoing')
        
        from voteit.core.models.proposal import Proposal
        ai['p1'] = p1 = Proposal()
        ai['p2'] = p2 = Proposal()
        
        self._subscribers()
        
        from voteit.core.models.poll import Poll
        poll = Poll()
        poll.proposal_uids = (p1.uid, p2.uid)
        
        self.config.include('voteit.core.plugins.majority_poll')
        poll.set_field_value('poll_plugin', u'majority_poll')
        
        ai['p'] = poll

        poll.set_workflow_state(self.request, 'upcoming')
        poll.set_workflow_state(self.request, 'ongoing')

        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        self.assertEqual(len(adapter.feed_storage), 1)
        self.assertEqual(adapter.feed_storage[len(adapter.feed_storage)-1].tags, ('poll', 'ongoing',))
        
        poll.set_workflow_state(self.request, 'closed')
        
        self.assertEqual(len(adapter.feed_storage), 2)
        self.assertEqual(adapter.feed_storage[len(adapter.feed_storage)-1].tags, ('poll', 'closed',))
        
    def test_agenda_item_state_change(self):
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        
        meeting.set_workflow_state(self.request, 'upcoming')
        meeting.set_workflow_state(self.request, 'ongoing')
        
        self._subscribers() 
        
        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        
        ai.set_workflow_state(self.request, 'upcoming')

        self.assertEqual(len(adapter.feed_storage), 1)
        self.assertEqual(adapter.feed_storage[0].tags, ('agenda_item', 'upcoming',))        
        
        ai.set_workflow_state(self.request, 'ongoing')
        
        self.assertEqual(len(adapter.feed_storage), 2)
        self.assertEqual(adapter.feed_storage[len(adapter.feed_storage)-1].tags, ('agenda_item', 'ongoing',))

        ai.set_workflow_state(self.request, 'closed')
        
        self.assertEqual(len(adapter.feed_storage), 3)
        self.assertEqual(adapter.feed_storage[len(adapter.feed_storage)-1].tags, ('agenda_item', 'closed',))
        
        # this state change should only give a feed entry if the previous stace was private
        ai.set_workflow_state(self.request, 'upcoming')

        self.assertEqual(len(adapter.feed_storage), 3)
        self.assertEqual(adapter.feed_storage[len(adapter.feed_storage)-1].tags, ('agenda_item', 'closed',))

    def test_do_not_include_private_ais_when_discussion_added(self):
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        self._subscribers()
        from voteit.core.models.discussion_post import DiscussionPost
        ai['post'] = DiscussionPost()

        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        self.assertEqual(len(adapter.feed_storage), 0)

    def test_do_not_include_private_ais_when_proposal_added(self):
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        self._subscribers()
        from voteit.core.models.proposal import Proposal
        ai['post'] = Proposal()

        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        self.assertEqual(len(adapter.feed_storage), 0)

    def test_discussion_posts_appear_when_ai_visible(self):
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        self._subscribers()
        from voteit.core.models.discussion_post import DiscussionPost
        ai['post'] = DiscussionPost()
        ai.set_workflow_state(self.request, 'upcoming')
        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        self.assertEqual(len(adapter.feed_storage), 1)

    def test_proposals_appear_when_ai_visible(self):
        root = self._fixture()
        meeting = root['m']
        ai = meeting['ai']
        self._subscribers()
        from voteit.core.models.proposal import Proposal
        ai['post'] = Proposal()
        ai.set_workflow_state(self.request, 'upcoming')
        adapter = self.config.registry.queryAdapter(meeting, IFeedHandler)
        self.assertEqual(len(adapter.feed_storage), 1)
