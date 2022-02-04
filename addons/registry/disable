#!/usr/bin/env bash

set -e

source $SNAP/actions/common/utils.sh
CURRENT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
source $CURRENT_DIR/../common/utils.sh

echo "Disabling the private registry"
use_addon_manifest registry/registry delete
use_addon_manifest registry/registry-help apply
echo "The registry is disabled. Use 'microk8s disable hostpath-storage:destroy-storage' to free the storage space."
