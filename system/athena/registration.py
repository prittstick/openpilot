#!/usr/bin/env python3
from pathlib import Path

from openpilot.common.params import Params
from openpilot.selfdrive.selfdrived.alertmanager import set_offroad_alert
from openpilot.system.hardware import PC
from openpilot.system.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog


UNREGISTERED_DONGLE_ID = "UnregisteredDevice"

def is_registered_device() -> bool:
  dongle = Params().get("DongleId")
  return dongle not in (None, UNREGISTERED_DONGLE_ID)


def register(show_spinner=False) -> str | None:
  """
  privacy: this build never contacts comma's backend to register.

  The dongle ID is taken from params or /persist (all devices built since
  March 2024 ship with it stored there). If none is available the device
  simply stays unregistered, which keeps manager and the UI functional
  without any network traffic.
  """
  params = Params()

  dongle_id: str | None = params.get("DongleId")
  if dongle_id is None and Path(Paths.persist_root()+"/comma/dongle_id").is_file():
    with open(Paths.persist_root()+"/comma/dongle_id") as f:
      dongle_id = f.read().strip()

  if dongle_id is None:
    dongle_id = UNREGISTERED_DONGLE_ID
    cloudlog.warning("no dongle_id available, staying unregistered (offline build)")

  params.put("DongleId", dongle_id)
  set_offroad_alert("Offroad_UnregisteredHardware", (dongle_id == UNREGISTERED_DONGLE_ID) and not PC)
  return dongle_id


if __name__ == "__main__":
  print(register())
