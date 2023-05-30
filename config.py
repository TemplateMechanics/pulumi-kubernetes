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
class SecretInitArgs:
    data: Optional[Dict[str, str]] = None
    immutable: Optional[bool] = None
    metadata: Optional[Dict[str, ObjectMetaArgs]] = None
    string_data: Optional[Dict[str, str]] = None
    type: Optional[str] = None
@dataclass
class Secrets:
    name: str
    id: Optional[str] = None
    args: Optional[SecretInitArgs] = None
### https://www.pulumi.com/registry/packages/kubernetes/api-docs/core/v1/secret/ ###
@dataclass
class ObjectMetaArgs:
    name: Optional[str] = None
    namespace: Optional[str] = None
    labels: Optional[dict[str, str]] = None
    annotations: Optional[dict[str, str]] = None
@dataclass
class NamespaceSpecArgs:
    finalizers: Optional[List[str]] = None
@dataclass
class NamespaceInitArgs:
    metadata: Optional[Dict[str, ObjectMetaArgs]] = None
    spec: Optional[Dict[str, NamespaceSpecArgs]] = None
@dataclass
class Namespaces:
    name: str
    id: Optional[str] = None
    args: Optional[NamespaceInitArgs] = None
### https://www.pulumi.com/registry/packages/kubernetes/api-docs/core/v1/namespace/ ###
@dataclass
class Kubernetes:
    namespaces: Optional[List[Namespaces]]
    secrets: Optional[List[Secrets]]
### https://www.pulumi.com/registry/packages/kubernetes/api-docs/ ###
@dataclass
class Environment:
    name: str
    app_labels: Optional[dict[str, str]] = None
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