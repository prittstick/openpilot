import jwt
import os
from datetime import datetime, timedelta, UTC
from openpilot.system.hardware.hw import Paths

API_HOST = os.getenv('API_HOST', 'https://api.commadotai.com')

# name: jwt signature algorithm
KEYS = {"id_rsa": "RS256",
        "id_ecdsa": "ES256"}


class ApiDisabledError(RuntimeError):
  """privacy: this build never talks to comma's API backend."""


class Api:
  def __init__(self, dongle_id):
    self.dongle_id = dongle_id
    self.jwt_algorithm, self.private_key, _ = get_key_pair()

  def get(self, *args, **kwargs):
    raise ApiDisabledError("comma API access is disabled in this build")

  def post(self, *args, **kwargs):
    raise ApiDisabledError("comma API access is disabled in this build")

  def request(self, method, endpoint, timeout=None, access_token=None, **params):
    raise ApiDisabledError(f"comma API access is disabled in this build: {endpoint}")

  def get_token(self, payload_extra=None, expiry_hours=1):
    # local JWT signing only, no network involved
    now = datetime.now(UTC).replace(tzinfo=None)
    payload = {
      'identity': self.dongle_id,
      'nbf': now,
      'iat': now,
      'exp': now + timedelta(hours=expiry_hours)
    }
    if payload_extra is not None:
      payload.update(payload_extra)
    token = jwt.encode(payload, self.private_key, algorithm=self.jwt_algorithm)
    if isinstance(token, bytes):
      token = token.decode('utf8')
    return token


def api_get(endpoint, method='GET', timeout=None, access_token=None, session=None, **params):
  # privacy: no data transfer with comma's backend, no matter the caller
  raise ApiDisabledError(f"comma API access is disabled in this build: {endpoint}")


def get_key_pair() -> tuple[str, str, str] | tuple[None, None, None]:
  for key in KEYS:
    if os.path.isfile(Paths.persist_root() + f'/comma/{key}') and os.path.isfile(Paths.persist_root() + f'/comma/{key}.pub'):
      with open(Paths.persist_root() + f'/comma/{key}') as private, open(Paths.persist_root() + f'/comma/{key}.pub') as public:
        return KEYS[key], private.read(), public.read()
  return None, None, None
