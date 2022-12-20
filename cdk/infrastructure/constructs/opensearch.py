from aws_cdk import RemovalPolicy
from aws_cdk import Tags

from constructs import Construct

from aws_cdk.aws_ec2 import SubnetSelection
from aws_cdk.aws_ec2 import SubnetType

from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.aws_iam import Effect
from aws_cdk.aws_iam import AnyPrincipal

from aws_cdk.aws_opensearchservice import CapacityConfig
from aws_cdk.aws_opensearchservice import Domain
from aws_cdk.aws_opensearchservice import EngineVersion
from aws_cdk.aws_opensearchservice import EbsOptions
from aws_cdk.aws_opensearchservice import LoggingOptions
from aws_cdk.aws_opensearchservice import ZoneAwarenessConfig

from infrastructure.config import Config

from infrastructure.constructs.existing.types import ExistingResources

from infrastructure.constructs.alarms.opensearch import OpensearchAlarmsProps
from infrastructure.constructs.alarms.opensearch import OpensearchAlarms

from typing import Any

from dataclasses import dataclass


@dataclass
class OpensearchProps:
    config: Config
    existing_resources: ExistingResources
    capacity: CapacityConfig
    volume_size: int
    subnet_selection: SubnetSelection = SubnetSelection(
        availability_zones=['us-west-2a'],
        subnet_type=SubnetType.PRIVATE_ISOLATED
    )
    zone_awareness: ZoneAwarenessConfig = ZoneAwarenessConfig(
        enabled=False,
    )


class Opensearch(Construct):

    domain: Domain
    props: OpensearchProps
    url: str

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            *,
            props: OpensearchProps,
            **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.props = props
        self._define_domain()
        self._define_log_removal_policy()
        self._allow_access_to_domain()
        self._add_tags_to_domain()
        self._define_url()
        self._add_alarms()

    def _define_domain(self) -> None:
        self.domain = Domain(
            self,
            'Domain',
            version=EngineVersion.OPENSEARCH_1_2,
            capacity=self.props.capacity,
            ebs=EbsOptions(
                volume_size=self.props.volume_size,
            ),
            logging=LoggingOptions(
                app_log_enabled=True,
                slow_index_log_enabled=True,
                slow_search_log_enabled=True,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            vpc=self.props.existing_resources.network.vpc,
            vpc_subnets=[
                self.props.subnet_selection
            ],
            zone_awareness=self.props.zone_awareness,
            advanced_options={
                'indices.query.bool.max_clause_count': '8096'
            }
        )

    def _define_log_removal_policy(self) -> None:
        if self.domain.app_log_group:
            self.domain.app_log_group.apply_removal_policy(
                RemovalPolicy.DESTROY
            )
        if self.domain.slow_index_log_group:
            self.domain.slow_index_log_group.apply_removal_policy(
                RemovalPolicy.DESTROY
            )
        if self.domain.slow_search_log_group:
            self.domain.slow_search_log_group.apply_removal_policy(
                RemovalPolicy.DESTROY
            )

    def _allow_access_to_domain(self) -> None:
        # Access controlled by VPC security groups.
        unsigned_access_policy = PolicyStatement(
            effect=Effect.ALLOW,
            actions=[
                'es:ESHttp*',
            ],
            principals=[
                AnyPrincipal()
            ],
            resources=[
                f'{self.domain.domain_arn}/*'
            ]
        )
        self.domain.add_access_policies(
            unsigned_access_policy
        )

    def _add_tags_to_domain(self) -> None:
        Tags.of(self.domain).add(
            'branch',
            self.props.config.branch,
        )

    def _define_url(self) -> None:
        self.url = f'https://{self.domain.domain_endpoint}'

    def _add_alarms(self) -> None:
        OpensearchAlarms(
            self,
            'OpensearchAlarms',
            props=OpensearchAlarmsProps(
                existing_resources=self.props.existing_resources,
                domain=self.domain,
                volume_size=self.props.volume_size,
            ),
        )