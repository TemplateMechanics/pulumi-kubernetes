from dataclass_wizard import YAMLWizard, asdict
from typing import Dict, Any, Sequence ,Optional, List
from dataclasses import dataclass, field
@dataclass
class ObjectMetaArgs:
    name: Optional[str] = None
    namespace: Optional[str] = None
    labels: Optional[dict[str, str]] = None
    annotations: Optional[dict[str, str]] = None
@dataclass
class ConfigMapInitArgs:
    data: Optional[Dict[str, str]] = None
    metadata: Optional[ObjectMetaArgs] = None
    namespace: Optional[str] = None
    immutable: Optional[bool] = None
    string_data: Optional[Dict[str, str]] = None
    type: Optional[str] = None
@dataclass
class ConfigMaps:
    name: Optional[str] = None
    api_version: Optional[str] = None
    kind: Optional[str] = None
    id: Optional[str] = None
    args: Optional[ConfigMapInitArgs] = None
### https://www.pulumi.com/registry/packages/kubernetes/api-docs/core/v1/configmap/ ###
@dataclass
class SecretInitArgs:
    data: Optional[Dict[str, str]] = None
    metadata: Optional[ObjectMetaArgs] = None
    namespace: Optional[str] = None
    immutable: Optional[bool] = None
    string_data: Optional[Dict[str, str]] = None
    type: Optional[str] = None
@dataclass
class Secrets:
    name: Optional[str] = None
    api_version: Optional[str] = None
    kind: Optional[str] = None
    id: Optional[str] = None
    args: Optional[SecretInitArgs] = None
    # metadata: Optional[ObjectMetaArgs] = None
### https://www.pulumi.com/registry/packages/kubernetes/api-docs/core/v1/secret/ ###
@dataclass
class NamespaceSpecArgs:
    finalizers: Optional[List[str]] = None
@dataclass
class NamespaceInitArgs:
    string_data: Optional[Dict[str, str]] = None
    metadata: Optional[ObjectMetaArgs] = None
    immutable: Optional[bool] = None
    type: Optional[str] = None
    spec: Optional[Dict[str, NamespaceSpecArgs]] = None
@dataclass
class Namespaces:
    name: Optional[str] = None
    api_version: Optional[str] = None
    kind: Optional[str] = None
    id: Optional[str] = None
    args: Optional[NamespaceInitArgs] = None
    metadata: Optional[ObjectMetaArgs] = None
### https://www.pulumi.com/registry/packages/kubernetes/api-docs/core/v1/namespace/ ###
@dataclass
class Kubernetes:
    namespaces: Optional[List[Namespaces]]
    secrets: Optional[List[Secrets]]
    configmaps: Optional[List[ConfigMaps]]
### https://www.pulumi.com/registry/packages/kubernetes/api-docs/ ###
@dataclass
class Environment:
    name: str
    location: Optional[str] = None
    project: Optional[str] = None
    kubernetes: Optional[Kubernetes] = None
@dataclass
class Service:
    name: str
    environments: List[Environment]
@dataclass
class Team:
    name: str
    services: List[Service]
@dataclass
class Config(YAMLWizard):
    teams: List[Team]
### Base Config ###