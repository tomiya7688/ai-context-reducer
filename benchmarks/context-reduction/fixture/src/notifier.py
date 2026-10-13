class TemporaryNotificationError(RuntimeError):
    pass

class PermanentNotificationError(RuntimeError):
    pass

def send_with_retry(send_once, message: str, attempts: int = 3) -> None:
    last_error = None
    for _ in range(attempts):
        try:
            send_once(message)
            return
        except TemporaryNotificationError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
