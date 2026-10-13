# Notification retry

`send_with_retry` retries a notification only after `TemporaryNotificationError`.
Permanent failures are not retry candidates. The default retry budget is three attempts,
including the first send operation.
