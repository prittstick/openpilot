from enum import IntEnum
import os
import threading
import time

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog


class PrimeType(IntEnum):
  UNKNOWN = -2
  UNPAIRED = -1
  NONE = 0
  MAGENTA = 1
  LITE = 2
  BLUE = 3
  MAGENTA_NEW = 4
  PURPLE = 5


class PrimeState:
  FETCH_INTERVAL = 5.0  # seconds between checks in the worker thread
  SLEEP_INTERVAL = 0.5  # seconds to sleep between checks in the worker thread

  def __init__(self):
    self._params = Params()
    self._lock = threading.Lock()
    self.prime_type: PrimeType = self._load_initial_state()

    self._running = False
    self._thread = None

  def _load_initial_state(self) -> PrimeType:
    prime_type_str = os.getenv("PRIME_TYPE") or self._params.get("PrimeType")
    try:
      if prime_type_str is not None:
        return PrimeType(int(prime_type_str))
    except (ValueError, TypeError):
      pass
    return PrimeType.UNKNOWN

  def _fetch_prime_status(self) -> None:
    # privacy: this build never polls comma's backend for prime/pairing status
    return

  def set_type(self, prime_type: PrimeType) -> None:
    with self._lock:
      if prime_type != self.prime_type:
        self.prime_type = prime_type
        self._params.put("PrimeType", int(prime_type))
        cloudlog.info(f"Prime type updated to {prime_type}")

  def _worker_thread(self) -> None:
    from openpilot.selfdrive.ui.ui_state import ui_state, device
    while self._running:
      if not ui_state.started and device._awake:
        self._fetch_prime_status()

      for _ in range(int(self.FETCH_INTERVAL / self.SLEEP_INTERVAL)):
        if not self._running:
          break
        time.sleep(self.SLEEP_INTERVAL)

  def start(self) -> None:
    if self._thread and self._thread.is_alive():
      return
    self._running = True
    self._thread = threading.Thread(target=self._worker_thread, daemon=True)
    self._thread.start()

  def stop(self) -> None:
    self._running = False
    if self._thread and self._thread.is_alive():
      self._thread.join(timeout=1.0)

  def get_type(self) -> PrimeType:
    with self._lock:
      return self.prime_type

  def is_prime(self) -> bool:
    with self._lock:
      return bool(self.prime_type > PrimeType.NONE)

  def is_paired(self) -> bool:
    with self._lock:
      return self.prime_type > PrimeType.UNPAIRED

  def __del__(self):
    self.stop()
