"""A DigitalOcean Python Pulumi program"""

import pulumi
import pulumi_digitalocean as do
from typing import Type
from os import getenv

control_plane_node_count: int = 1
worker_node_count: int = 2
region: str = "nyc3"

control_plane_nodes: list[Type[do.Droplet]]  = []
worker_nodes: list[Type[do.Droplet]] = []

ssh_public_key = getenv('SSH_PUB_KEY')

## Create SSH Keys
default_key = do.SshKey(
    "default", ssh_public_key
)

## Provision Control Plane node(s)
for d in range(0, control_plane_node_count):
    instance_name = f"control-plane-node-{d}"
    name_tag = do.Tag(instance_name)
    cp_droplet = do.Droplet(
        instance_name,
        image="rockylinux-8-4-x64",
        region=region,
        ssh_keys=[default_key.fingerprint],
        size="s-1vcpu-2gb",
        tags=[name_tag.id],
    )
    control_plane_nodes.append(cp_droplet)

## Provision Worker Nodes
for d in range(0, worker_node_count):
    instance_name = f"worker-node-{d}"
    name_tag = do.Tag(instance_name)
    worker_droplet = do.Droplet(
        instance_name,
        image="rockylinux-8-4-x64",
        region=region,
        size="s-1vcpu-1gb",
        ssh_keys=[default_key.fingerprint],
        tags=[name_tag.id],
    )
    worker_nodes.append(worker_droplet)

# Provision a LB with TLS termination for the rancher cluster.
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

for idx, node in enumerate((control_plane_nodes + worker_nodes)):
    pulumi.export(f"ip_address-${idx}", node.ipv4_address)
