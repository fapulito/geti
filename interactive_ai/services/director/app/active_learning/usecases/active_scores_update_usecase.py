# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

"""This module contains the ActiveScoresUpdate use case"""

import logging
from collections.abc import Sequence

from active_learning.interactors import ActiveMapper

from geti_fastapi_tools.exceptions import DatasetStorageNotFoundException
from geti_telemetry_tools import unified_tracing
from geti_types import ID, DatasetStorageIdentifier, MediaIdentifierEntity, ProjectIdentifier
from iai_core.entities.dataset_storage import NullDatasetStorage
from iai_core.repos import DatasetStorageRepo

logger = logging.getLogger(__name__)


class ActiveScoresUpdateUseCase:
    """Use case to update the active scores at task or project level."""

    @staticmethod
    @unified_tracing
    def _is_training_dataset_storage(
        dataset_storage_identifier: DatasetStorageIdentifier,
    ) -> bool:
        """
        Check whether the dataset storage is used for training

        :param dataset_storage_identifier: Identifier of the storage containing the dataset.
        :return: True if the dataset storage is used for training. Otherwise, False.
        :raises: DatasetStorageNotFoundException if the dataset storage is not found.
        """
        project_identifier = ProjectIdentifier(
            workspace_id=dataset_storage_identifier.workspace_id,
            project_id=dataset_storage_identifier.project_id,
        )
        ds_repo = DatasetStorageRepo(project_identifier)
        dataset_storage = ds_repo.get_by_id(dataset_storage_identifier.dataset_storage_id)
        if isinstance(dataset_storage, NullDatasetStorage):
            logger.warning("Could not find dataset storage: %s", dataset_storage_identifier)
            raise DatasetStorageNotFoundException(dataset_storage_id=dataset_storage_identifier.dataset_storage_id)
        return dataset_storage.use_for_training

    @staticmethod
    def on_output_datasets_and_metadata_created(  # noqa: PLR0913
        workspace_id: ID,
        project_id: ID,
        dataset_storage_id: ID,
        task_node_id: ID,
        model_storage_id: ID,
        model_id: ID,
        annotated_dataset_id: ID,
        train_dataset_with_predictions_id: ID,
        unannotated_dataset_with_predictions_id: ID,
        asynchronous: bool = False,
    ) -> None:
        """
        Handler to be called when predictions and AL metadata become available for
        training and unannotated data as a result of inference for a task.

        It submits a request to the ActiveMapper to update (synchronously or not)
        the active scores for the affected media.

        :param workspace_id: ID of the workspace containing the project
        :param project_id: ID of the project containing the datasets
        :param dataset_storage_id: ID of the storage containing the datasets
        :param task_node_id: ID of the task node on which inference was executed
        :param model_storage_id: ID of the storage containing the model used
            to generate the predictions
        :param model_id: IDs of the model used to generate the predictions
        :param annotated_dataset_id: ID of the user annotated dataset on which
            the task was trained
        :param train_dataset_with_predictions_id: ID of the dataset containing
            predictions generated by the trained model on the training dataset
            (training subset only)
        :param unannotated_dataset_with_predictions_id: ID of the dataset containing
            predictions generated by the trained model on unlabeled data
        :param asynchronous: If True, execute the handler asynchronously in
            a separate thread; this makes the function non-blocking
        """
        if asynchronous:
            ActiveMapper().update_active_scores_async(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                task_node_id=task_node_id,
                model_storage_id=model_storage_id,
                model_id=model_id,
                annotated_dataset_id=annotated_dataset_id,
                train_dataset_with_predictions_id=train_dataset_with_predictions_id,
                unannotated_dataset_with_predictions_id=unannotated_dataset_with_predictions_id,
            )
        else:
            ActiveMapper.update_active_scores(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                task_node_id=task_node_id,
                model_storage_id=model_storage_id,
                model_id=model_id,
                annotated_dataset_id=annotated_dataset_id,
                train_dataset_with_predictions_id=train_dataset_with_predictions_id,
                unannotated_dataset_with_predictions_id=unannotated_dataset_with_predictions_id,
            )

    @staticmethod
    def on_media_uploaded(
        workspace_id: ID,
        project_id: ID,
        dataset_storage_id: ID,
        media_identifiers: Sequence[MediaIdentifierEntity],
        asynchronous: bool = False,
    ) -> None:
        """
        Handler to be called when a new media is uploaded to a project.

        :param workspace_id: ID of the workspace containing the project
        :param project_id: ID of the project containing the media
        :param dataset_storage_id: ID of the dataset storage containing the media
        :param media_identifiers: Identifiers of the newly uploaded media
        :param asynchronous: If True, execute the handler asynchronously in
            a separate thread; this makes the function non-blocking
        """
        dataset_storage_identifier = DatasetStorageIdentifier(
            workspace_id=workspace_id,
            project_id=project_id,
            dataset_storage_id=dataset_storage_id,
        )
        if not ActiveScoresUpdateUseCase._is_training_dataset_storage(
            dataset_storage_identifier=dataset_storage_identifier
        ):
            return  # no active learning on secondary dataset storages

        if asynchronous:
            ActiveMapper().init_active_scores_async(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                media_identifiers=media_identifiers,
            )
        else:
            ActiveMapper.init_active_scores(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                media_identifiers=media_identifiers,
            )

    @staticmethod
    def on_media_deleted(
        workspace_id: ID,
        project_id: ID,
        dataset_storage_id: ID,
        media_identifiers: Sequence[MediaIdentifierEntity],
        asynchronous: bool = False,
    ) -> None:
        """
        Handler to be called when media are deleted from a project.

        :param workspace_id: ID of the workspace containing the project
        :param project_id: ID of the project containing the media
        :param dataset_storage_id: ID of the dataset storage containing the media
        :param media_identifiers: Identifiers of the deleted media
        :param asynchronous: If True, execute the handler asynchronously in
            a separate thread; this makes the function non-blocking
        """
        dataset_storage_identifier = DatasetStorageIdentifier(
            workspace_id=workspace_id,
            project_id=project_id,
            dataset_storage_id=dataset_storage_id,
        )
        if not ActiveScoresUpdateUseCase._is_training_dataset_storage(
            dataset_storage_identifier=dataset_storage_identifier
        ):
            return  # no active learning on secondary dataset storages

        if asynchronous:
            ActiveMapper().remove_media_async(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                media_identifiers=media_identifiers,
            )
        else:
            ActiveMapper.remove_media(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                media_identifiers=media_identifiers,
            )

    @staticmethod
    def on_project_deleted(
        workspace_id: ID,
        project_id: ID,
        dataset_storage_id: ID,
        asynchronous: bool = False,
    ) -> None:
        """
        Handler to be called when a project is deleted.

        :param workspace_id: ID of the workspace containing the project
        :param project_id: ID of the project containing the media
        :param dataset_storage_id: ID of the dataset storage containing the media
        :param asynchronous: If True, execute the handler asynchronously in
            a separate thread; this makes the function non-blocking
        """
        if asynchronous:
            ActiveMapper().remove_media_async(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                media_identifiers=None,  # all media
            )
        else:
            ActiveMapper.remove_media(
                workspace_id=workspace_id,
                project_id=project_id,
                dataset_storage_id=dataset_storage_id,
                media_identifiers=None,  # all media
            )
