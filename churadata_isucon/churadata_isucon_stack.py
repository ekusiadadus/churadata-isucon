from os import getenv
from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct


class ChuradataIsuconStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            id="vpc",
            vpc_name="ChuraDATA ISUCON",
            cidr="192.168.0.0/16",
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC),
            ],
        )

        security_group = ec2.SecurityGroup(
            self,
            id="sg",
            vpc=vpc,
            allow_all_outbound=True,
        )
        security_group.add_ingress_rule(
            peer=security_group,
            connection=ec2.Port.all_traffic(),
        )
        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(getenv("ALLOWED_CIDR", "0.0.0.0/0")),
            connection=ec2.Port.tcp(22),
        )

        instance_spec = [
            ("bench", "192.168.0.10", "c4.xlarge"),
            # ("app-1", "192.168.0.11", "c5.large"),
            # ("app-2", "192.168.0.12", "c5.large"),
            # ("app-3", "192.168.0.13", "c5.large"),
        ]

        for (i_name, i_addr, i_type) in instance_spec:
            user_data = ec2.UserData.for_linux(shebang="#cloud-config")
            user_data.add_commands(
                f"fqdn: churadata-isucon-{i_name}",
                "system_info:",
                "  default_user:",
                "    name: isucon",
            )
            ec2.Instance(
                self,
                id=f"ec2-{i_name}",
                instance_name=f"ChuraDATA ISUCON / {i_name}",
                instance_type=ec2.InstanceType(i_type),
                machine_image=ec2.MachineImage.generic_linux({"ap-northeast-1": "ami-0796be4f4814fc3d5"}),
                vpc=vpc,
                security_group=security_group,
                block_devices=[
                    ec2.BlockDevice(
                        device_name="/dev/xvda",
                        volume=ec2.BlockDeviceVolume.ebs(20, volume_type=ec2.EbsDeviceVolumeType.GP3),
                    )
                ],
                key_name=getenv("KEY_NAME"),
                private_ip_address=i_addr,
                user_data=user_data,
            )

        # TODO: EIP 指定
        # TODO: /etc/hosts 追記 (or 置換)
        # TODO: 証明書インストール
        # TODO: ベンチマークスクリプトをインストール
