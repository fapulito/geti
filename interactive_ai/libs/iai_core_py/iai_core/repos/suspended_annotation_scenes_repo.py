# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

"""
This module implements the repository for the list of suspended annotation scenes
"""

from collections.abc import Callable

from pymongo.command_cursor import CommandCursor
from pymongo.cursor import Cursor

from iai_core.entities.suspended_scenes import (
    NullSuspendedAnnotationScenesDescriptor,
    SuspendedAnnotationScenesDescriptor,
)
from iai_core.repos.base import DatasetStorageBasedSessionRepo
from iai_core.repos.mappers.cursor_iterator import CursorIterator
from iai_core.repos.mappers.mongodb_mappers.suspended_scenes_mapper import SuspendedAnnotationScenesDescriptorToMongo

from geti_types import DatasetStorageIdentifier, Session


class SuspendedAnnotationScenesRepo(DatasetStorageBasedSessionRepo[SuspendedAnnotationScenesDescriptor]):
    """
    Repository to persist ActiveScore entities in the database.

    :param dataset_storage_identifier: Identifier of the dataset_storage
    :param session: Session object; if not provided, it is loaded through the context variable CTX_SESSION_VAR
    """

    def __init__(
        self,
        dataset_storage_identifier: DatasetStorageIdentifier,
        session: Session | None = None,
    ) -> None:
        super().__init__(
            collection_name="suspended_annotation_scenes",
            session=session,
            dataset_storage_identifier=dataset_storage_identifier,
        )

    @property
    def forward_map(self) -> Callable[[SuspendedAnnotationScenesDescriptor], dict]:
        return SuspendedAnnotationScenesDescriptorToMongo.forward

    @property
    def backward_map(self) -> Callable[[dict], SuspendedAnnotationScenesDescriptor]:
        return SuspendedAnnotationScenesDescriptorToMongo.backward

    @property
    def null_object(self) -> NullSuspendedAnnotationScenesDescriptor:
        return NullSuspendedAnnotationScenesDescriptor()

    @property
    def cursor_wrapper(self) -> Callable[[Cursor | CommandCursor], CursorIterator]:
        return lambda mongo_cursor: CursorIterator(
            cursor=mongo_cursor,
            mapper=SuspendedAnnotationScenesDescriptorToMongo,
            parameter=None,
        )
