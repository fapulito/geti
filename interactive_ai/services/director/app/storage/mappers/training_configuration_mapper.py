# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

from geti_configuration_tools.hyperparameters import Hyperparameters
from geti_configuration_tools.training_configuration import GlobalParameters, TrainingConfiguration

from iai_core.repos.mappers.mongodb_mapper_interface import IMapperSimple
from iai_core.repos.mappers.mongodb_mappers.id_mapper import IDToMongo


class TrainingConfigurationToMongo(IMapperSimple[TrainingConfiguration, dict]):
    """MongoDB mapper for `TrainingConfiguration` entities"""

    @staticmethod
    def forward(instance: TrainingConfiguration) -> dict:
        doc = {
            "_id": IDToMongo.forward(instance.id_),
            "task_id": IDToMongo.forward(instance.task_id),
            "global_parameters": instance.global_parameters.model_dump(),
            "hyperparameters": instance.hyperparameters.model_dump(),
        }
        if instance.model_manifest_id:
            doc["model_manifest_id"] = instance.model_manifest_id
        return doc

    @staticmethod
    def backward(instance: dict) -> TrainingConfiguration:
        return TrainingConfiguration(
            id_=IDToMongo.backward(instance["_id"]),
            task_id=IDToMongo.backward(instance["task_id"]),
            model_manifest_id=instance.get("model_manifest_id"),
            global_parameters=GlobalParameters.model_validate(instance["global_parameters"]),
            hyperparameters=Hyperparameters.model_validate(instance["hyperparameters"]),
        )
