"""A DigitalOcean Python Pulumi program"""

import pulumi
import pulumi_digitalocean as do

control_plane_nodes = 1
worker_nodes = 2
region = "nyc"

bootstrap_control_plane = ""
bootstrap_workers = ""

## Provision Control Plane node(s)
for idx, droplet in enumerate(range(0, control_plane_nodes)):
    instance_name = f"control-plane-node-{idx+1}"
    name_tag = do.Tag(instance_name)
    droplet = do.Droplet(
        instance_name,
        image="",
        region=region,
        size="2gb",
        tags=[name_tag.id],
        user_data=bootstrap_control_plane,
    )

## Provision Worker Nodes
for idx, droplet in enumerate(range(0, worker_nodes)):
    instance_name = f"worker-node-{idx+1}"
    name_tag = do.Tag(instance_name)
    droplet = do.Droplet(
        instance_name,
        image="",
        region=region,
        size="2gb",
        tags=[name_tag.id],
        user_data=bootstrap_workers,
    )

## Provision a LB with TLS termination for the rancher cluster.
lb = do.LoadBalancer(
    "public",
    droplet_tag="external-lb",
    forwarding_rules=[
        do.LoadBalancerForwardingRuleArgs(
            entry_port=443,
            entry_protocol="https",
            target_port="",
            target_protocol="https",
        )
    ],
    healthcheck=do.LoadBalancerHealthcheckArgs(
        port=443,
        protocol="https",
    ),
    region=region,
)

pulumi.export("endpoint", lb.ip)
