import unittest

import colander
from pyramid import testing
from betahaus.pyracont.factories import createSchema


class FeedSchemaTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_integration(self):
        self.config.scan('voteit.feed.schemas')
        schema = createSchema('RssSettingsMeetingSchema')
        self.assertIsInstance(schema, colander.SchemaNode)
