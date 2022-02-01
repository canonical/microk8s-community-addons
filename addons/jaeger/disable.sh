#!/usr/bin/env bash

set -e
source $SNAP/actions/common/utils.sh
echo "Disabling Jaeger"
read -ra ARGUMENTS <<< "$1"

KUBECTL="$SNAP/kubectl --kubeconfig=${SNAP_DATA}/credentials/client.config"
MANIFESTS_PATH="${SNAP}/addons/core/addons/jaeger/jaeger"

if [ ! -z "${ARGUMENTS[@]}" ]
then

  $KUBECTL delete -f "${MANIFESTS_PATH}/crds" || true
  manifests="service_account.yaml role.yaml role_binding.yaml operator.yaml"
  KUBECTL="$SNAP/kubectl --kubeconfig=${SNAP_DATA}/credentials/client.config -n ${ARGUMENTS[0]}"
  for yaml in $manifests
  do
    sed "s/namespace: default/namespace: ${ARGUMENTS[0]}/g" $MANIFESTS_PATH/$yaml | $KUBECTL delete -f - || true
    sleep 3
  done

else

  $KUBECTL delete -f "${MANIFESTS_PATH}" || true
  $KUBECTL delete -f "${MANIFESTS_PATH}/crds" || true

fi
echo "The Jaeger operator is disabled"
