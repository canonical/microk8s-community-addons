#!/usr/bin/env bash

set -e

source $SNAP/actions/common/utils.sh
CURRENT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
source $CURRENT_DIR/../common/utils.sh

echo "Enabling default storage class."
echo "WARNING: Hostpath storage is not suitable for production environments."
echo ""
run_with_sudo mkdir -p ${SNAP_COMMON}/default-storage

declare -A map
map[\$SNAP_COMMON]="$SNAP_COMMON"
use_addon_manifest hostpath-storage/storage apply "$(declare -p map)"
echo "Storage will be available soon."

if [ -e ${SNAP_DATA}/var/lock/clustered.lock ]
then
  echo ""
  echo "WARNING: The storage class enabled does not persist volumes across nodes."
  echo ""
fi
