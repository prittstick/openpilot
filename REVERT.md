# Privacy build: revert runbook

This branch (`tesla-steering-tuning-private`) disables driver monitoring and
removes all data transfer to Comma (and other third parties) from the device.
Updates still arrive over GitHub (`git fetch origin`), nothing else.

The changes are code-only and state-neutral:

- no new params are written, `/persist` is untouched, the real dongle ID from
  `/persist` is preserved, so stock functionality resumes with no cleanup
- the only device-level change is `/etc/hosts`, managed by
  `tools/scripts/privacy_netblock.sh`

## Runtime revert to default openpilot

ssh into the device, then:

```bash
cd /data/openpilot
sudo ./tools/scripts/privacy_netblock.sh off   # restore comma connectivity first
git fetch origin
git checkout master                          # stock commaai/openpilot mirror
sudo reboot
```

After reboot the device runs default openpilot: athenad, uploader and crash
reporting reconnect to Comma automatically (that is stock behavior — remove
the netblock first or stock will look broken). No re-registration is needed.

Notes:

- reverting to `master` deliberately means the device contacts Comma again.
- the fork's `master` is a snapshot of commaai/openpilot; it only advances when
  it is synced in the fork (optionally automate this with a GitHub Action).
- `/etc/hosts` changes do not survive an AGNOS reflash; after any OS flash,
  re-run `privacy_netblock.sh on` (and remember it must be off before a future
  revert).

## First boot of a new device (pragmatic)

A brand-new device ships with stock openpilot, which contacts Comma as soon as
it has internet (athena connect, prime status query, upload of any logs).
To keep that window minimal: connect WiFi, install this branch via
`git fetch origin && git checkout tesla-steering-tuning-private`, and only
drive after switching. See the plan discussion for exactly what the window
sends.

## What is disabled in this branch

| Change | File |
| --- | --- |
| Driver monitoring model off, constant benign state published | `selfdrive/monitoring/dmonitoringd.py`, `system/manager/process_config.py` |
| Registration never calls comma's backend | `system/athena/registration.py` |
| Driving allowed while unregistered (no registration gate) | `system/hardware/hardwared.py` |
| athenad / uploader / webrtcd never run | `system/manager/manager.py` |
| Crash reporting (sentry) hard-off | `system/sentry.py` |
| Comma API client stubbed out | `common/api.py` |
| UI prime/pairing status polling removed | `selfdrive/ui/lib/prime_state.py` |
| Qualcomm XTRA GPS assistance download removed | `system/qcomgpsd/qcomgpsd.py` |
| u-blox AssistNow online removed | `system/ubloxd/pigeond.py` |
| AGNOS OS images never flashed from comma servers | `system/updated/updated.py` |
| `/etc/hosts` blocking for comma endpoints | `tools/scripts/privacy_netblock.sh` |

Known trade-offs: Comma Connect pairing/prime is nonfunctional (by design);
the driver camera preview shows stale data if opened; GPS cold-start fix is
slower without assistance data; some repo CI tests fail (harmless for a
private fork).

Device note: comma 3X units built before 2/28/24 have no factory dongle ID
in `/persist`. With this build they stay permanently "UnregisteredDevice"
(stock would obtain an ID by sending IMEI/serial to comma's backend). This
build removes the "must be registered" onroad gate, so driving works anyway;
reverting to stock `master` restores that gate and the device will register
with comma on next boot with internet to drive again.
