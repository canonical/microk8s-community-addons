#!/usr/bin/env bash

set -e

source $SNAP/actions/common/utils.sh

echo "Disabling the private registry"
use_manifest registry/registry delete
use_manifest registry/registry-help apply
echo "The registry is disabled. Use 'microk8s disable hostpath-storage:destroy-storage' to free the storage space."
