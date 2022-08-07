"""A DigitalOcean Python Pulumi program"""

import pulumi
import pulumi_digitalocean as do
from typing import Type

control_plane_node_count: int = 1
worker_node_count: int = 2
region: str = "nyc"

control_plane_nodes: list[Type[do.Droplet]]  = []
worker_nodes: list[Type[do.Droplet]] = []


bootstrap_control_plane = """#!/bin/bash
    sudo yum update
"""
bootstrap_workers = """#!/bin/bash
    sudo yum update
"""

## Create SSH Keys
default_key = do.SshKey(
    "default", lambda p: open(p).read()("/Users/praveen/do_test_keys/id_rsa.pub")
)

## Provision Control Plane node(s)
for idx, droplet in enumerate(range(0, control_plane_nodes)):
    instance_name = f"control-plane-node-{idx+1}"
    name_tag = do.Tag(instance_name)
    droplet = do.Droplet(
        instance_name,
        image="rockylinux-8-4-x64",
        region=region,
        ssh_keys=[default_key.fingerprint],
        size="s-1vcpu-2gb",
        tags=[name_tag.id],
        user_data=bootstrap_control_plane,
    )
    control_plane_nodes.append(droplet)

## Provision Worker Nodes
for idx, droplet in enumerate(range(0, worker_nodes)):
    instance_name = f"worker-node-{idx+1}"
    name_tag = do.Tag(instance_name)
    droplet = do.Droplet(
        instance_name,
        image="rockylinux-8-4-x64",
        region=region,
        size="s-1vcpu-1gb",
        ssh_keys=[default_key.fingerprint],
        tags=[name_tag.id],
        user_data=bootstrap_workers,
    )
    worker_nodes.append(droplet)

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

for node in (control_plane_nodes + worker_nodes):
    pulumi.export("ip_address", node.ipv4_address)

pulumi.export("endpoint", lb.ip)