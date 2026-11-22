#!/usr/bin/env python3
import time
import cereal.messaging as messaging
from openpilot.common.realtime import config_realtime_process


def dmonitoringd_thread():
  config_realtime_process([0, 1, 2, 3], 5)

  pm = messaging.PubMaster(['driverMonitoringState'])

  # privacy: driver monitoring is disabled. dmonitoringmodeld does not run, so
  # there is no driverStateV2 input to consume. Publish a constant benign state
  # at the stock 20Hz so downstream consumers (selfdrived liveness and events,
  # controlsd awareness-based decel, modeld isRHD) see a permanently attentive
  # driver. No distraction events are ever generated.
  while True:
    loop_start = time.monotonic()

    dat = messaging.new_message('driverMonitoringState', valid=True)
    dat.driverMonitoringState = {
      "faceDetected": False,
      "isDistracted": False,
      "awarenessStatus": 1.,
      "awarenessActive": 1.,
      "awarenessPassive": 1.,
      "isActiveMode": False,
      "isRHD": False,
      "isLowStd": True,
    }
    pm.send('driverMonitoringState', dat)

    # 20Hz, matching the stock service rate in cereal/services.py
    time.sleep(max(0., 0.05 - (time.monotonic() - loop_start)))


def main():
  dmonitoringd_thread()


if __name__ == '__main__':
  main()
