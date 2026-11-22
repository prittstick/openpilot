"""Install exception handler for process crash."""
from enum import Enum

from openpilot.common.swaglog import cloudlog


class SentryProject(Enum):
  # python project
  SELFDRIVE = "https://6f3c7076c1e14b2aa10f5dde6dda0cc4@o33823.ingest.sentry.io/77924"
  # native project
  SELFDRIVE_NATIVE = "https://3e4b586ed21a4479ad5d85083b639bc6@o33823.ingest.sentry.io/157615"


def report_tombstone(fn: str, message: str, contents: str) -> None:
  cloudlog.error({'tombstone': message})


def capture_exception(*args, **kwargs) -> None:
  cloudlog.error("crash", exc_info=kwargs.get('exc_info', 1))


def set_tag(key: str, value: str) -> None:
  pass


def init(project: SentryProject) -> bool:
  # privacy: crash reporting is disabled. This build never sends anything
  # to sentry.io, regardless of origin or registration state.
  return False
