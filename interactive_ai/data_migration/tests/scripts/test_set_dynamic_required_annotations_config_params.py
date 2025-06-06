# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

from copy import deepcopy
from unittest.mock import patch
from uuid import UUID, uuid4

import mongomock
import pytest
from bson import ObjectId
from bson.binary import UUID_SUBTYPE, Binary, UuidRepresentation
from pymongo import MongoClient

from migration.scripts.set_dynamic_required_annotations_config_params import (
    SetDynamicRequiredAnnotationsConfigParamsMigration,
)


@pytest.fixture
def fxt_organization_id():
    yield uuid4()


@pytest.fixture
def fxt_workspace_id():
    yield uuid4()


@pytest.fixture
def fxt_project_ids():
    yield ObjectId(), ObjectId()  # 2 projects


@pytest.fixture
def fxt_configs_before_upgrade(fxt_organization_id, fxt_workspace_id, fxt_project_ids):
    """
    List of documents present in the database BEFORE upgrading project #0
    """
    yield [
        # document in project #0 without the new parameters -> expected that it is updated
        {
            "_id": ObjectId(),
            "organization_id": fxt_organization_id,
            "workspace_id": fxt_workspace_id,
            "project_id": fxt_project_ids[0],
            "entity_identifier": {
                "component": "DATASET_COUNTER",
                "task_id": "",
                "type": "COMPONENT_PARAMETERS",
            },
            "data": {
                "type": "CONFIGURABLE_PARAMETERS",
                "header": "Annotation requirements",
                "description": "Specify the number of required annotations for a task",
                "other_parameter": {"key1": "value1"},
            },
        },
        # document in project #0 with the new parameters -> expected that it is NOT updated
        {
            "_id": ObjectId(),
            "organization_id": fxt_organization_id,
            "workspace_id": fxt_workspace_id,
            "project_id": fxt_project_ids[0],
            "entity_identifier": {
                "component": "DATASET_COUNTER",
                "task_id": "",
                "type": "COMPONENT_PARAMETERS",
            },
            "data": {
                "type": "CONFIGURABLE_PARAMETERS",
                "header": "Annotation requirements",
                "description": "Specify the number of required annotations for a task",
                "other_parameter": {"key1": "value1"},
                "use_dynamic_required_annotations": {"existing_key": "existing_value"},
                "required_images_auto_training_dynamic": {"existing_key": "existing_value"},
            },
        },
        # document in project #0 relative to a different component -> expected that it is NOT updated
        {
            "_id": ObjectId(),
            "organization_id": fxt_organization_id,
            "workspace_id": fxt_workspace_id,
            "project_id": fxt_project_ids[0],
            "entity_identifier": {
                "component": "PIPELINE_DATASET_MANAGER",
                "task_id": "",
                "type": "COMPONENT_PARAMETERS",
            },
            "data": {
                "type": "CONFIGURABLE_PARAMETERS",
                "header": "Dataset management",
                "description": "Specify parameters to control how datasets are managed in the system.",
                "other_parameter": {"key1": "value1"},
            },
        },
        # document from another project -> expected that it is NOT updated
        {
            "_id": ObjectId(),
            "organization_id": fxt_organization_id,
            "workspace_id": fxt_workspace_id,
            "project_id": fxt_project_ids[1],
            "entity_identifier": {
                "component": "DATASET_COUNTER",
                "task_id": "",
                "type": "COMPONENT_PARAMETERS",
            },
            "data": {
                "type": "CONFIGURABLE_PARAMETERS",
                "header": "Annotation requirements",
                "description": "Specify the number of required annotations for a task",
                "other_parameter": {"key1": "value1"},
            },
        },
    ]


@pytest.fixture
def fxt_configs_after_upgrade(fxt_configs_before_upgrade):
    """
    List of documents present in the database AFTER upgrading project #0
    """
    docs_after_upgrade = deepcopy(fxt_configs_before_upgrade)
    docs_after_upgrade[0]["data"].update(
        {
            "use_dynamic_required_annotations": {
                "value": True,
                "default_value": True,
                "description": "Only applicable if auto-training is on. Set this parameter on to let the system "
                "dynamically compute the number of required annotations between training "
                "rounds based on model performance and training dataset size.",
                "header": "Dynamic required annotations",
                "warning": None,
                "editable": True,
                "visible_in_ui": True,
                "affects_outcome_of": "NONE",
                "ui_rules": {
                    "operator": "AND",
                    "action": "DISABLE_EDITING",
                    "type": "UI_RULES",
                    "rules": [],
                },
                "type": "BOOLEAN",
                "auto_hpo_state": "not_possible",
                "auto_hpo_value": None,
            },
            "required_images_auto_training_dynamic": {
                "value": 12,
                "default_value": 12,
                "description": "An optimal minimum number of images required for auto-training, "
                "calculated based on model performance and dataset size",
                "header": "Dynamic minimum number of images required for auto-training",
                "warning": None,
                "editable": False,
                "visible_in_ui": False,
                "affects_outcome_of": "NONE",
                "ui_rules": {
                    "operator": "AND",
                    "action": "DISABLE_EDITING",
                    "type": "UI_RULES",
                    "rules": [],
                },
                "type": "INTEGER",
                "auto_hpo_state": "not_possible",
                "auto_hpo_value": None,
                "min_value": 3,
                "max_value": 10000,
            },
        }
    )
    yield docs_after_upgrade


@pytest.fixture(autouse=True)
def fxt_mongo_uuid(monkeypatch):
    def side_effect_mongo_mock_from_uuid(uuid: UUID, uuid_representation=UuidRepresentation.STANDARD):
        """Override (Mock) the bson.binary.Binary.from_uuid function to work for mongomock
        Code is copy pasted from the original function,
        but `uuid_representation` is ignored and only code parts as if
        uuid_representation == UuidRepresentation.STANDARD are used
        """
        if not isinstance(uuid, UUID):
            raise TypeError("uuid must be an instance of uuid.UUID")

        subtype = UUID_SUBTYPE
        payload = uuid.bytes

        return Binary(payload, subtype)

    with patch.object(Binary, "from_uuid", side_effect=side_effect_mongo_mock_from_uuid):
        yield


class TestDynamicRequiredAnnotationsConfigParamsMigration:
    def test_set_dynamic_required_annotations_config_params_upgrade(
        self,
        fxt_organization_id,
        fxt_workspace_id,
        fxt_project_ids,
        fxt_configs_before_upgrade,
        fxt_configs_after_upgrade,
    ) -> None:
        mock_db = mongomock.MongoClient(uuidRepresentation="standard").db
        config_params_collection = mock_db.create_collection("configurable_parameters")

        config_params_collection.insert_many(fxt_configs_before_upgrade)

        project_to_upgrade_id = fxt_project_ids[0]

        with patch.object(MongoClient, "get_database", return_value=mock_db):
            SetDynamicRequiredAnnotationsConfigParamsMigration.upgrade_project(
                organization_id=str(fxt_organization_id),
                workspace_id=str(fxt_workspace_id),
                project_id=str(project_to_upgrade_id),
            )

        actual_configs_after_upgrade = list(config_params_collection.find())
        actual_configs_after_upgrade.sort(key=lambda doc: doc["_id"])
        fxt_configs_after_upgrade.sort(key=lambda doc: doc["_id"])

        assert actual_configs_after_upgrade == fxt_configs_after_upgrade
