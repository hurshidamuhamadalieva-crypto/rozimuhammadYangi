# -*- coding: utf-8 -*-
"""Offline regression checks; no Telegram messages are sent."""
import asyncio
import importlib
import os
import tempfile
import time
import unittest
from pathlib import Path

os.environ['BOT_TOKEN'] = '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijk'
_tmp = tempfile.TemporaryDirectory()
os.environ['DATA_DIR'] = _tmp.name

class BotTests(unittest.TestCase):
    def test_extension_preserves_remaining_days(self):
        from utils import extend_subscription
        old = time.time() + 10 * 86400
        u = {'subscription': {'active': True, 'end': old, 'start': time.time() - 86400}}
        end = extend_subscription(u, {'label': '1 oylik', 'days': 31})
        self.assertEqual(end, old + 31 * 86400)

    def test_lifetime_is_preserved(self):
        from utils import extend_subscription
        u = {'subscription': {'active': True, 'end': None}}
        self.assertIsNone(extend_subscription(u, {'label': '1 oylik', 'days': 31}))

    def test_new_driver_payment_marks_combined_application(self):
        from storage import get_user, payments_store
        from handlers.payment import _create_payment_record

        u = get_user('77')
        u['driver_status'] = 'none'
        payment_id = asyncio.run(_create_payment_record('77', '1m', 'admin'))
        self.assertTrue(payments_store.data['payments'][payment_id]['driver_application'])
        self.assertEqual(get_user('77')['driver_status'], 'pending')

    def test_access_checks_expiry_and_approval(self):
        from storage import get_user
        from utils import driver_allowed
        u = get_user('42')
        self.assertFalse(driver_allowed('42'))
        u['driver_status'] = 'approved'
        u['subscription'].update(active=True, end=time.time() + 100)
        self.assertTrue(driver_allowed('42'))
        u['subscription']['end'] = time.time() - 1
        self.assertFalse(driver_allowed('42'))

    def test_keyboard_layout_and_ad_buttons(self):
        from keyboards import route_kb, driver_channel_ad_kb, phone_request_kb, location_choice_kb
        rows = route_kb().inline_keyboard
        self.assertEqual([len(row) for row in rows[:6]], [2] * 6)
        for username in ('test_user', ''):
            self.assertEqual(len(driver_channel_ad_kb('abc', '42', username).inline_keyboard), 2)
        self.assertTrue(phone_request_kb().keyboard)
        self.assertTrue(location_choice_kb().keyboard)

    def test_import_handlers(self):
        for name in ('start', 'driver_admin', 'driver', 'payment', 'payment_admin', 'passenger', 'fallback'):
            importlib.import_module('handlers.' + name)

    def test_unapproved_cannot_view_or_take(self):
        from handlers.passenger import view_passenger_ad, take_passenger_ad
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        call = SimpleNamespace(from_user=SimpleNamespace(id=43), answer=AsyncMock())
        async def run():
            await view_passenger_ad(call)
            await take_passenger_ad(call)
        asyncio.run(run())
        self.assertEqual(call.answer.await_count, 2)

    def test_passenger_delivery_failure_is_reported(self):
        from handlers.passenger import _submit_passenger_ad
        from unittest.mock import AsyncMock, patch
        from storage import ads_store
        before = len(ads_store.data['passenger'])
        with patch('handlers.passenger.bot.send_message', new=AsyncMock(side_effect=RuntimeError('offline'))):
            ok = asyncio.run(_submit_passenger_ad(42, {'passenger_route': 'A', 'passenger_text': 'B'}, None))
        self.assertFalse(ok)
        self.assertEqual(len(ads_store.data['passenger']), before)

    def test_ad_broadcast_includes_both_buttons(self):
        from handlers.driver import _broadcast_driver_ad
        from storage import get_user, ads_store
        from unittest.mock import AsyncMock, patch
        u = get_user('44')
        u.update(driver_status='approved', driver_paused=False)
        u['subscription'].update(active=True, end=time.time() + 1000)
        ads_store.data['driver']['test'] = {'user': '44', 'text': 'Test', 'photo': 'photo', 'active': True}
        sender = AsyncMock()
        with patch('handlers.driver.bot.send_photo', new=sender):
            ok, error = asyncio.run(_broadcast_driver_ad('test'))
        self.assertTrue(ok)
        self.assertEqual(len(sender.call_args.kwargs['reply_markup'].inline_keyboard), 2)

    def test_html_name_is_escaped(self):
        from utils import display_name
        self.assertEqual(display_name({'full_name': '<name>'}, '42'), '&lt;name&gt;')

if __name__ == '__main__':
    unittest.main()
