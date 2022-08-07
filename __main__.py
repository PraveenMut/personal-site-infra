"""A DigitalOcean Python Pulumi program"""

import pulumi
import pulumi_digitalocean as do

control_plane_nodes = 1
worker_nodes = 2
region = "nyc"

bootstrap_control_plane = ""
bootstrap_workers = ""

## Create SSH Keys
default_key = do.SshKey(
    "default", lambda p: open(p).read()("/Users/pxm021/do_test_keys/id_rsa.pub")
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
