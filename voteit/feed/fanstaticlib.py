""" Fanstatic lib"""
from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

from voteit.core.fanstaticlib import voteit_common_js
from voteit.core.fanstaticlib import voteit_main_css


voteit_feed_lib = Library('voteit_feed', '')

voteit_feed_css = Resource(voteit_feed_lib, 'voteit_feed.css', depends=(voteit_main_css,))

voteit_feed = Group((voteit_feed_css,))