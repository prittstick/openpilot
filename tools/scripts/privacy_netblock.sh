#!/usr/bin/env bash
# privacy: device-level network blocking for comma / third-party endpoints.
# GitHub (branch updates) stays reachable.
#
# usage:
#   sudo ./tools/scripts/comma_netblock.sh on     # block comma endpoints
#   sudo ./tools/scripts/comma_netblock.sh off     # restore (needed before reverting to stock)
#
# The block is a marked section in /etc/hosts. It does not survive an AGNOS
# reflash — re-run "on" after any OS flash.
set -euo pipefail

HOSTS_FILE="/etc/hosts"
BEGIN="# BEGIN openpilot-privacy netblock"
END="# END openpilot-privacy netblock"

BLOCKLIST=(
  api.commadotai.com
  athena.comma.ai
  connect.comma.ai
  o33823.ingest.sentry.io
  commadist.azureedge.net
  xtrapath3.izatcloud.net
  online-live2.services.u-blox.com
)

remove_block() {
  sed -i "/^${BEGIN}$/,/^${END}$/d" "$HOSTS_FILE"
}

add_block() {
  remove_block
  {
    echo "$BEGIN"
    for host in "${BLOCKLIST[@]}"; do
      echo "0.0.0.0 $host"
    done
    echo "$END"
  } >> "$HOSTS_FILE"
}

case "${1:-}" in
  on)
    [ "$(id -u)" -eq 0 ] || { echo "run as root: sudo $0 on" >&2; exit 1; }
    add_block
    echo "netblock enabled"
    ;;
  off)
    [ "$(id -u)" -eq 0 ] || { echo "run as root: sudo $0 off" >&2; exit 1; }
    remove_block
    echo "netblock disabled"
    ;;
  *)
    echo "usage: sudo $0 on|off" >&2
    exit 1
    ;;
esac

# flush DNS caches if available (best effort)
resolvectl flush-caches 2>/dev/null || true
