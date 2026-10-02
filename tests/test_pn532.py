"""Host fake UART/socket tests. No network or physical door is controlled."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class PN532Tests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.response = bytes(19) + bytes([0, 1, 15, 255])
        self.socket_failure = False
        owner = self

        class UART:
            def __init__(self, *args): owner.events.append(('UART', args))
            def init(self, *args, **kwargs): owner.events.append(('init', args, kwargs))
            def write(self, data): owner.events.append(('write', data))
            def read(self):
                owner.events.append(('read',))
                return owner.response

        class Socket:
            def connect(self, target):
                owner.events.append(('connect', target))
                if owner.socket_failure: raise OSError('fake connection failure')
            def send(self, value): owner.events.append(('send', value))
            def close(self): owner.events.append(('close',))

        self.clock = types.SimpleNamespace(sleep=lambda n: self.events.append(('sleep', n)))
        self.socket = types.SimpleNamespace(AF_INET=2, SOCK_STREAM=1, socket=lambda *args: Socket())
        spec = importlib.util.spec_from_file_location(
            'pn532_under_test', Path(__file__).resolve().parents[1] / 'pn532.py')
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'machine': types.SimpleNamespace(UART=UART, Pin=object)}):
            spec.loader.exec_module(self.module)
        self.module.time = self.clock
        self.card = self.module.PN532(2, 115200)
        self.assertEqual(self.events, [('UART', (2, 115200)),
                                     ('init', (115200,), {'bits': 8, 'parity': None, 'stop': 1})])
        self.events.clear()

    def scan_events(self):
        return [('write', bytes.fromhex('0000ff04fcd44a0200e000')),
                ('sleep', 0.1), ('sleep', 0.1), ('read',), ('sleep', 0.2)]

    def filter(self, cards):
        out = io.StringIO()
        def verify():
            self.events.append(('verify',))
            return cards
        self.card.the_verify = verify
        with patch.dict(sys.modules, {'socket': self.socket, 'time': self.clock}), contextlib.redirect_stdout(out):
            result = self.card.filter()
        self.assertIsNone(result)
        return out.getvalue()

    def test_uid_formatting_for_every_byte_and_scan_timing(self):
        for value in range(256):
            self.response = bytes(19) + bytes([value] * 4)
            self.events.clear()
            self.assertEqual(self.card.spawncard_number(), format(value, '02x') * 4)
            self.assertEqual(self.events, self.scan_events())
            self.assertEqual(self.card.cardnumber, self.response)

    def test_short_and_none_responses_preserve_exceptions(self):
        for length in range(7):
            self.response = bytes(length)
            self.assertIsNone(self.card.spawncard_number())
        for length in range(7, 23):
            self.response = bytes(length)
            with self.assertRaises(IndexError): self.card.spawncard_number()
        self.response = None
        with self.assertRaises(TypeError): self.card.spawncard_number()

    def test_authorized_filter_keeps_send_text_order_and_state(self):
        self.assertEqual(self.filter({'00010fff': 'Alice'}), 'Alice\nwelcomeAlice\n')
        self.assertEqual(self.events, self.scan_events() + [('verify',), ('verify',),
                         ('connect', ('192.168.5.185', 8008)), ('sleep', 0.2),
                         ('send', '{"name":"Alice"}'), ('sleep', 0.2), ('close',)])
        self.assertFalse(self.module.door_state)

    def test_unknown_card_does_not_open_socket(self):
        self.assertEqual(self.filter({}), 'invader\n')
        self.assertEqual(self.events, self.scan_events() + [('verify',)])
        self.assertFalse(self.module.door_state)

    def test_connection_failure_preserves_existing_door_state(self):
        self.socket_failure = True
        self.assertEqual(self.filter({'00010fff': 'Alice'}), '')
        self.assertTrue(self.module.door_state)
        self.assertEqual(self.events[-1], ('connect', ('192.168.5.185', 8008)))

    def test_malformed_filter_response_triggers_existing_wakeup(self):
        for response in (None, bytes(7), bytes(22)):
            self.response = response
            self.events.clear()
            self.filter({})
            self.assertEqual(self.events[-3:], [('write', self.module.WAKEUP),
                                              ('sleep', 0.1), ('sleep', 0.1)])


if __name__ == '__main__':
    unittest.main()
