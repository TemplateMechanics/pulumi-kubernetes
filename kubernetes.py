import config
import dataclasses
from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod
import re
from collections.abc import Iterable
import uuid
import secrets
import string
from automapper import mapper

import pulumi
from pulumi_kubernetes import core, meta

pulumiConfig : pulumi.Config = pulumi.Config()

@dataclass
class BuildContext:
    team: str
    service: str
    environment: str
    location: str
    project: str
    app_labels: dict[str, str]

    resource_cache: dict = field(init=False, repr=False, default_factory=dict)

    async def add_resource_to_cache(self, name: str, resource: pulumi.CustomResource):
        self.resource_cache[name] = resource

    async def get_resource_from_cache(self, name: str) -> pulumi.CustomResource:
        if name in self.resource_cache:
            return self.resource_cache[name]

        return None

    def get_default_resource_name(self, unique_identifier: str) -> str:
        return f"{self.team}-{self.service}-{self.environment}-{unique_identifier}"

    def get_default_resource_name_clean(self, unique_identifier: str) -> str:
        return self.get_default_resource_name(unique_identifier).replace("-", "")
    
    def generate_password(length=16):
        all_characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(all_characters) for _ in range(length))
        return password

# region Resources
class BaseResource(ABC):

    def __init__(self, name: str, context: BuildContext):
        self.name = name
        self.context = context

    @abstractmethod
    async def find(self, id: Optional[str] = None) -> pulumi.CustomResource:
        pass

    @abstractmethod
    async def create(self, args: any) -> pulumi.CustomResource:
        pass

    async def getResourceValue(self, baseResource : pulumi.CustomResource, outputChain : str) -> Optional[str]:
        outputs = outputChain.split("->")
                
        if baseResource is None:
            return None      
        
        # loop through nested output parameters until we get to the last resource
        for outputName in outputs[:-1]:
            baseResource = getattr(baseResource, outputName)
            if baseResource is None:
                return None
    
        return getattr(baseResource, outputs[-1] )

    async def replaceValue(self, args : any, propertyName : str, value : str | pulumi.Output[any]) -> str:
        newValue : str = value
        m = re.search(r"Resource (.+),\s?(.+)", value)
        if m is not None:
            resource = await self.context.get_resource_from_cache(m.group(1))
            newValue = await self.getResourceValue(resource, m.group(2)) or newValue            
        else:
            m = re.search(r"Secret (.+)", value)
            if m is not None:
                secret = pulumiConfig.require_secret(m.group(1))
                newValue = secret or value

        if value != newValue:
            setattr(args, propertyName, newValue)

    async def replaceInputArgs(self, args: any):
        properties = [a for a in dir(args) if not a.startswith('__') and not callable(getattr(args, a))]
        for property in properties:
            value = getattr(args, property)
            if value is not None:

                # loop iterables
                if (isinstance(value, Iterable)):
                    for item in value:
                        await self.replaceInputArgs(item)

                # deep replace on all child dataclasses
                if (dataclasses.is_dataclass(value)):
                    await self.replaceInputArgs(value)

                # only replace values for strings
                if isinstance(value, str):
                    await self.replaceValue(args, property, value)

    async def build(self, id: Optional[str] = None, args: Optional[any] = None) -> None:
        if id is not None:
            try:
                resource_group = await self.find(id)
            except Exception as e:
                pulumi.log.warn(f"Failed to find existing resource group with id {id}: {e}")
                return

        if args is not None:
            await self.replaceInputArgs(args);
            resource_group = await self.create(args)

        await self.context.add_resource_to_cache(self.name, resource_group)

class Namespaces(BaseResource):

    def __init__(self, name: str, context: BuildContext):
        super().__init__(name, context)

    async def find(self, id: Optional[str] = None) -> Optional[core.v1.Namespace]:
        if not id:
            return None

        return core.v1.Namespace.get(self.context.get_default_resource_name(self.name), id)
    
    async def create(self, args: config.NamespaceInitArgs) -> core.v1.Namespace:
        # args.name = self.context.get_default_resource_name(self.name)
        args.app_labels = self.context.app_labels
        namespace_init_args = mapper.to(core.v1.NamespaceInitArgs).map(args, use_deepcopy=False, skip_none_values=True)
        return core.v1.Namespace(self.context.get_default_resource_name(self.name), args=namespace_init_args)

#endregion

class ResourceBuilder:

    def __init__(self, context: BuildContext):
        self.context = context
        self.app_labels = context.app_labels

    async def build(self, config: config.Kubernetes):
        await self.build_namespaces(config.namespaces)
    
    async def build_namespaces(self, configs: Optional[list[config.Namespaces]] = None):
        if configs is None:
            return

        for config in configs:
            namespaces = Namespaces(config.name, self.context)
            await namespaces.build(config.id, config.args)

# app_labels = { "app": "nginx" }

# deployment = Deployment(
#     "nginx",
#     spec=DeploymentSpecArgs(
#         selector=LabelSelectorArgs(match_labels=app_labels),
#         replicas=1,
#         template=PodTemplateSpecArgs(
#             metadata=ObjectMetaArgs(labels=app_labels),
#             spec=PodSpecArgs(containers=[ContainerArgs(name="nginx", image="nginx")])
#         ),
#     ))

# pulumi.export("name", deployment.metadata["name"])