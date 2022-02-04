#!/usr/bin/env bash

set -e

source $SNAP/actions/common/utils.sh
CURRENT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
source $CURRENT_DIR/../common/utils.sh

echo "Enabling Metrics-Server"

KUBECTL="$SNAP/kubectl --kubeconfig=${SNAP_DATA}/credentials/client.config"
use_addon_manifest metrics-server/metrics-server apply

refresh_opt_in_config "authentication-token-webhook" "true" kubelet
restart_service kubelet

echo "Metrics-Server is enabled"
