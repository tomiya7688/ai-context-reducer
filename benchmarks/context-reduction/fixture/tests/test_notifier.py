import unittest
from src.notifier import TemporaryNotificationError, send_with_retry

class NotificationTests(unittest.TestCase):
    def test_send_with_retry_retries_temporary_failure(self):
        calls = []
        def send_once(message):
            calls.append(message)
            if len(calls) == 1:
                raise TemporaryNotificationError("temporary")
        send_with_retry(send_once, "hello")
        self.assertEqual(["hello", "hello"], calls)

if __name__ == "__main__":
    unittest.main()
