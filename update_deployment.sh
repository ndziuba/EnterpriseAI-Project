#!/bin/bash
# Variables
VERSION=$(python get_bento_version.py)
OUTPUT=$(bentoml deployment get --context default --kube-namespace yatai prod)
CURRENT_VERSION=$(echo "$OUTPUT" | grep -oP "'version': '\K[^']+")
CONFIG=$(cat << EOF
{
    "cluster_name": "default",
    "name": "staging",
    "description": "",
    "targets": [
        {
            "type": "stable",
            "bento_repository": "wf_classifier",
            "bento": "",
            "config": {
                "hpa_conf": {
                }
            }
        }
    ],
    "kube_namespace": "yatai"
}
EOF
)
# Check if the current version is different from the new version
if [ "$VERSION" != "$CURRENT_VERSION" ]; then
    # Update the version
    UPDATED_CONFIG=$(echo $CONFIG | jq --arg VERSION "$VERSION" '.targets[0].bento = $VERSION')
    # Write the update
    echo $UPDATED_CONFIG > deployment.json
    # Update the deployment
    bentoml deployment update --file deployment.json
else
    echo "The current version is the same as the new version."
fi
