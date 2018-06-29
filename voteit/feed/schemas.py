# -*- coding: utf-8 -*-
from uuid import uuid4

import colander
import deform

from voteit.feed import _


RSS_TYPES = (
    ("Proposal", _("Proposal")),
    ("DiscussionPost", _("Discussion post")),
    ("Poll", _("Poll")),
)


class FeedSettingsSchema(colander.Schema):
    enable_rss = colander.SchemaNode(
        colander.Bool(),
        title = _("Enalbe RSS feeds"),
    )
    link_token = colander.SchemaNode(
        colander.String(),
        title = _("Add token to link"),
        description=_("Adds the following token to the link to make it impossible to guess. "),
        default=str(uuid4()),
        missing="",
    )
    type_names = colander.SchemaNode(
        colander.Set(),
        title=_("Include the following types"),
        widget=deform.widget.CheckboxChoiceWidget(values=RSS_TYPES),
        validator=colander.ContainsOnly([x[0] for x in RSS_TYPES])
    )
    limit = colander.SchemaNode(
        colander.Int(),
        title=_("Limit to a maximum number of items"),
        default=50,
        validator=colander.Range(min=5, max=200),
    )
    description_text = colander.SchemaNode(
        colander.String(),
        title = _("Description text for RSS feed"),
        description=_("Only visible within the feed"),
        default=_("An RSS feed this VoteIT meeting"),
    )

    def validator(self, form, value):
        if value["enable_rss"] and not len(value['type_names']):
            exc = colander.Invalid(form, _("Types missing"))
            exc["type_names"] = _("If RSS is enabled, you need to pick content types to add to the feed.")
            raise exc


def includeme(config):
    config.add_schema('Feed', FeedSettingsSchema, 'settings')
