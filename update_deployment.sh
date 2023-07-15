#!/bin/bash
# Variables
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
VERSION=$(python get_bento_version.py)
OUTPUT=$(bentoml deployment get --context default --kube-namespace yatai staging)
CURRENT_VERSION=$(echo "$OUTPUT" |  grep -oP "version='.*?'" | cut -d "'" -f 2 | head -n 1)
CONFIG=$(cat << EOF
{
    "cluster_name": "default",
    "name": "staging",
    "description": "",
    "targets": [
        {
            "type": "stable",
            "bento_repository": "wf_service",
            "bento": "",
            "config": {
                "hpa_conf": {
                    "min_replicas": 2,
                    "max_replicas": 2
                },
                "resources": {
                    "requests": {
                        "cpu": "250m",
                        "memory": "200Mi",
                        "gpu": ""
                    },
                    "limits": {
                        "cpu": "500m",
                        "memory": "512Mi",
                        "gpu": ""
                    }
                },
                "envs": [],
                "runners": {
                    "wf_model": {
                        "resources": {
                            "requests": {
                                "cpu": "400m",
                                "memory": "512Mi"
                            },
                            "limits": {
                                "cpu": "500m",
                                "memory": "1024Mi"
                            }
                        },
                        "hpa_conf": {
                            "min_replicas": 2,
                            "max_replicas": 2
                        },
                        "envs": [],
                        "enable_stealing_traffic_debug_mode": false,
                        "enable_debug_mode": false,
                        "enable_debug_pod_receive_production_traffic": false,
                        "bento_deployment_overrides": {}
                    }
                },
                "enable_ingress": true
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

    # Log the update
    logger -p info "BentoML staging deployment updated to version $VERSION from $CURRENT_VERSION"
else
    # Log the non-update
    logger -p info "BentoML staging deployment not updated. Current version is the same as new version."
fi
