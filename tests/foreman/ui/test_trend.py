# -*- encoding: utf-8 -*-
"""Test class for Trend UI"""

from fauxfactory import gen_string
from robottelo.constants import TREND_TYPES
from robottelo.decorators import tier1
from robottelo.test import UITestCase
from robottelo.ui.factory import make_trend
from robottelo.ui.session import Session


class TrendTest(UITestCase):
    """Implements Trend tests in UI.

    Please note that we have static amount of Trend types and trendables, so it
    is not possible to generate values for them. In case you want to interact
    with them through automation, it is must have condition to provide unique
    elements from corresponding lists.
    In most cases it will not be possible to re-run tests due condition of
    uniqueness described above.
    """

    @tier1
    def test_positive_create(self):
        """Create new trend

        @Feature: Trend - Positive Create

        @Assert: Trend is created successfully
        """
        with Session(self.browser) as session:
            make_trend(session, trend_type=TREND_TYPES['model'])
            search = self.trend.search(TREND_TYPES['model'])
            self.assertIsNotNone(search)

    @tier1
    def test_positive_update(self):
        """Update trend entity value

        @Feature: Trend - Positive Update

        @Assert: Trend entity is updated successfully
        """
        name = gen_string('alphanumeric')
        new_name = gen_string('alphanumeric')
        with Session(self.browser) as session:
            make_trend(
                session,
                trend_type=TREND_TYPES['facts'],
                trendable='clientcert',
                name=name,
            )
            search = self.trend.search(name)
            self.assertIsNotNone(search)

            self.trend.update(name, 'clientcert', new_name)
            search = self.trend.search(new_name)
            self.assertIsNotNone(search)

    @tier1
    def test_positive_delete(self):
        """Delete existing trend

        @Feature: Trend - Positive Delete

        @Assert: Trend is deleted
        """
        with Session(self.browser) as session:
            make_trend(session, trend_type=TREND_TYPES['environment'])
            self.trend.delete(TREND_TYPES['environment'])
