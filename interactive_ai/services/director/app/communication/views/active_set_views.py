# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import logging
from typing import Any

from geti_fastapi_tools.exceptions import InvalidMediaException
from geti_telemetry_tools import unified_tracing
from geti_types import (
    CTX_SESSION_VAR,
    ID,
    DatasetStorageIdentifier,
    MediaIdentifierEntity,
    MediaType,
    VideoFrameIdentifier,
    VideoIdentifier,
)
from iai_core.entities.image import Image
from iai_core.entities.video import Video
from iai_core.entities.video_annotation_statistics import VideoAnnotationStatistics
from iai_core.utils.annotation_scene_state_helper import AnnotationStatePerTask

logger = logging.getLogger(__name__)


class ActiveSetRESTViews:
    @staticmethod
    @unified_tracing
    def active_set_to_rest(
        dataset_storage_identifier: DatasetStorageIdentifier,
        media_entities_data: dict[MediaIdentifierEntity, Image | Video],
        annotation_scene_states: dict[MediaIdentifierEntity, AnnotationStatePerTask],
    ) -> list[dict]:
        """
        Returns the REST representation of an active set.
        The active set can contain both images and video frames.
        For images, the ImageRESTView is used while video frames are grouped by video.
        We keep track of the videos in the rest view, and combine video frames originated
        from the same video in video_rest['active_frames'].

        :param dataset_storage_identifier: Identifier of the dataset storage where
            the media are stored
        :param media_entities_data: The media entities associated with the media identifiers,
            represented as a dictionary that maps the media identifiers to the media entity
        :param annotation_scene_states: Annotation state per task for each media identifier
        :return: REST representation of an active set
        :raises: WorkspaceNotFoundException if the workspace does not exist
            InvalidMediaException if the media type is unsupported
        """
        rest_views = []
        # Keep track of the existing videos and active frames in active dataset
        existing_videos: dict[ID, list[int]] = {}

        for media_identifier, media_entity in media_entities_data.items():
            if media_identifier.media_type is MediaType.IMAGE:
                annotation_state_per_task = annotation_scene_states.get(media_identifier, {})
                rest_view = ActiveSetRESTViews.media_to_rest(
                    media=media_entity,
                    media_identifier=media_identifier,
                    dataset_storage_identifier=dataset_storage_identifier,
                    annotation_state_per_task=annotation_state_per_task,
                )
                rest_view["dataset_id"] = str(dataset_storage_identifier.dataset_storage_id)
                rest_views.append(rest_view)
            elif media_identifier.media_type is MediaType.VIDEO_FRAME:
                if media_identifier.media_id not in existing_videos:
                    # use the media_id to get the video identifier
                    video_identifier = VideoIdentifier(media_identifier.media_id)
                    annotation_state_per_task = annotation_scene_states.get(video_identifier, {})
                    video_rest = ActiveSetRESTViews.media_to_rest(
                        media=media_entity,
                        media_identifier=media_entity.media_identifier,
                        dataset_storage_identifier=dataset_storage_identifier,
                        annotation_state_per_task=annotation_state_per_task,
                    )
                    frame_list: list[int] = []
                    # We reference the frame list, so we don't have to look for it later
                    video_rest["active_frames"] = frame_list
                    video_rest["dataset_id"] = str(dataset_storage_identifier.dataset_storage_id)
                    rest_views.append(video_rest)
                    existing_videos[media_identifier.media_id] = frame_list
                else:
                    frame_list = existing_videos[media_identifier.media_id]

                # We can directly add the video frame index to the frame list reference
                frame_list.append(media_identifier.frame_index)  # type: ignore[attr-defined]
            else:
                raise InvalidMediaException(
                    f"Got unsupported media type `{str(type(media_identifier))}` "
                    f"for MediaIdentifierRESTViews.active_dataset_to_rest"
                )

        return rest_views

    @staticmethod
    def _get_media_information(
        base_url: str,
        media: Image | Video,
        frame_index: int | None,
    ) -> dict[str, Any]:
        display_type = "stream" if isinstance(media, Video) and frame_index is None else "full"
        media_information = {
            "height": media.height,
            "width": media.width,
            "display_url": f"{base_url}/display/{display_type}",
        }

        if frame_index is None:
            media_information["size"] = media.size
            # Note that video frames do not have the "extension" field
            if isinstance(media, Video):
                media_information.update(
                    {
                        "frame_count": media.total_frames,
                        "frame_stride": media.stride,
                        "frame_rate": media.fps,
                        "duration": media.duration,
                    }
                )
            if media.extension is not None:
                media_information["extension"] = media.extension.value

        return media_information

    @staticmethod
    def _get_base_url(
        dataset_storage_identifier: DatasetStorageIdentifier,
        media: Image | Video,
        frame_index: int | None,
    ) -> str:
        session = CTX_SESSION_VAR.get()
        base_url = (
            f"/api/v1/organizations/{str(session.organization_id)}/workspaces/{str(dataset_storage_identifier.workspace_id)}"
            f"/projects/{str(dataset_storage_identifier.project_id)}/datasets/{str(dataset_storage_identifier.dataset_storage_id)}"
            f"/media/{media.media_identifier.media_type.value}s/{str(media.id_)}"
        )
        if frame_index is not None:
            base_url += f"/frames/{frame_index}"

        return base_url

    @staticmethod
    def _get_annotation_state_per_task_rest_view(
        annotation_state_per_task: AnnotationStatePerTask | None,
    ) -> list[dict[str, Any]]:
        if annotation_state_per_task is None:
            return []
        return [
            {
                "task_id": task_id,
                "state": (annotation_state.name.lower() if annotation_state is not None else None),
            }
            for task_id, annotation_state in annotation_state_per_task.items()
        ]

    @staticmethod
    def media_to_rest(
        media: Image | Video,
        media_identifier: MediaIdentifierEntity,
        dataset_storage_identifier: DatasetStorageIdentifier,
        annotation_state_per_task: AnnotationStatePerTask | None,
        video_annotation_statistics: VideoAnnotationStatistics | None = None,
    ) -> dict[str, Any]:
        """
        Transform media entity and identifier to a REST view

        :param media: Image or Video entity
        :param media_identifier: MediaIdentifierEntity to be transformed
            Note that media identifier is redundant in most cases as Image and Video have a media
            identifier. However, for video frames we need both the Video and the VideoFrameIdentifier.
        :param dataset_storage_identifier: Identifier of the dataset storage where the media is stored
        :annotation_state_per_task: dict indicating for each task id the current annotation state.
        """
        frame_index: int | None = None
        if isinstance(media_identifier, VideoFrameIdentifier):
            frame_index = media_identifier.frame_index

        base_url = ActiveSetRESTViews._get_base_url(
            dataset_storage_identifier=dataset_storage_identifier,
            media=media,
            frame_index=frame_index,
        )
        name = media.name
        id_key = "id"
        if frame_index is not None:
            name += f"_{frame_index}"
            id_key = "video_id"

        rest_view: dict[str, Any] = {
            id_key: str(media.id_),
            "name": name,
            "type": media_identifier.media_type.value,
            "media_information": ActiveSetRESTViews._get_media_information(
                base_url=base_url, media=media, frame_index=frame_index
            ),
            "annotation_state_per_task": ActiveSetRESTViews._get_annotation_state_per_task_rest_view(
                annotation_state_per_task
            ),
            "upload_time": media.creation_date.isoformat(),
            "uploader_id": media.uploader_id,
            "thumbnail": f"{base_url}/display/thumb",
            "preprocessing": {"status": media.preprocessing.status.value},
        }

        if frame_index is not None:
            rest_view["frame_index"] = frame_index
        if media.preprocessing.message is not None:
            rest_view["preprocessing"]["message"] = media.preprocessing.message

        if video_annotation_statistics is not None:
            rest_view["annotation_statistics"] = {
                "annotated": video_annotation_statistics.annotated,
                "partially_annotated": video_annotation_statistics.partially_annotated,
                "unannotated": video_annotation_statistics.unannotated,
            }

        return rest_view
