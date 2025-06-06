# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import os
import tempfile
from collections.abc import Sequence

import cv2
import pytest
from _pytest.fixtures import FixtureRequest
from geti_types import VideoFrameIdentifier
from iai_core.entities.annotation import AnnotationScene, AnnotationSceneKind
from iai_core.entities.label import Label
from iai_core.entities.media import MediaPreprocessing, MediaPreprocessingStatus, VideoExtensions
from iai_core.entities.project import Project
from iai_core.entities.video import Video
from iai_core.repos import AnnotationSceneRepo, AnnotationSceneStateRepo, LabelSchemaRepo, VideoRepo
from iai_core.utils.annotation_scene_state_helper import AnnotationSceneStateHelper

from tests.fixtures.values import DummyValues


@pytest.fixture
def fxt_random_annotated_video_factory(request: FixtureRequest, fxt_random_annotated_image_factory):
    """
    This is a fixture to create and save a random video with annotations. Both video
    and annotations are stored in their respective repositories, and removed after
    the test.

    The factory generates shapes that are either 'rectangle', 'ellipse' or 'triangle'
    on a white background. The shapes to be generated are deduced from the labels
    in the project. If the project labels do not match the shape names, all three
    sorts of random shapes are generated.
    """

    def _video_factory(
        project: Project,
        width: int = 480,
        height: int = 360,
        number_of_frames: int = 150,
        labels: Sequence[Label] | None = None,
    ) -> tuple[Video, list[AnnotationScene], float, int, int, int, str]:
        """
        generate a random video that is 150 frames at 30 fps. Video contains random
        shapes on white background

        :param project: Project that the Video will added to
        :param width: Width of the video
        :param height: Height of the video
        :param number_of_frames: Amount of frames to generate
        :param labels: Labels to create annotations on the frames. If not provided,
            the schema is loaded from the DB.
        :return: Tuple(Video entity, list of AnnotationScene entities)
        """
        if labels is None:
            label_schema_repo = LabelSchemaRepo(project.identifier)
            project_schema = label_schema_repo.get_latest()
            project_labels = project_schema.get_labels(include_empty=True)
        else:
            project_labels = list(labels)
        dataset_storage = project.get_training_dataset_storage()
        ann_scene_repo = AnnotationSceneRepo(dataset_storage.identifier)
        ann_scene_state_repo = AnnotationSceneStateRepo(dataset_storage.identifier)
        video_repo: VideoRepo = VideoRepo(dataset_storage.identifier)
        # Generate a video path using video id and an extension
        video_id = VideoRepo.generate_id()
        video_path = os.path.join(tempfile.gettempdir(), f"{video_id}.mp4")
        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        fps = 30.0
        video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

        annotations_per_frame = []  # List with list of annotations

        # Generate frames
        for i in range(number_of_frames):
            img, annotations = fxt_random_annotated_image_factory(
                image_width=width,
                image_height=height,
                labels=project_labels,
                min_size=15,
            )
            annotations_per_frame.append(annotations)
            video_writer.write(img)
        video_writer.release()

        # Generate video
        filename = video_repo.binary_repo.save(data_source=video_path, dst_file_name=video_path)
        size = video_repo.binary_repo.get_object_size(video_path)
        request.addfinalizer(lambda: video_repo.binary_repo.delete_by_filename(filename=filename))

        # Remove input binary after save
        if os.path.exists(video_path):
            os.remove(video_path)

        _, extension = os.path.splitext(filename)
        try:
            video_extension = VideoExtensions[extension[1:].upper()]
        except KeyError:
            video_extension = VideoExtensions.MP4

        video = Video(
            name="Generated video",
            stride=1,
            creation_date=DummyValues.CREATION_DATE,
            id=video_id,
            uploader_id="",
            fps=fps,
            width=width,
            height=height,
            total_frames=number_of_frames,
            size=size,
            extension=video_extension,
            preprocessing=MediaPreprocessing(status=MediaPreprocessingStatus.FINISHED),
        )
        video_repo.save(video)
        request.addfinalizer(lambda: video_repo.delete_by_id(video.id_))

        # Generate annotations
        annotation_scenes = []
        for i, annotations in enumerate(annotations_per_frame):
            annotation_scene = AnnotationScene(
                kind=AnnotationSceneKind.ANNOTATION,
                media_identifier=VideoFrameIdentifier(video_id=video.id_, frame_index=i),
                media_height=video.height,
                media_width=video.width,
                id_=AnnotationSceneRepo.generate_id(),
                last_annotator_id=DummyValues.CREATOR_NAME,
                creation_date=DummyValues.CREATION_DATE,
                annotations=annotations,
            )
            annotation_scenes.append(annotation_scene)
            ann_scene_repo.save(annotation_scene)
            request.addfinalizer(lambda: ann_scene_repo.delete_by_id(annotation_scene.id_))
            media_state = AnnotationSceneStateHelper.compute_annotation_scene_state(
                project=project,
                annotation_scene=annotation_scene,
            )
            ann_scene_state_repo.save(media_state)
            request.addfinalizer(lambda: ann_scene_state_repo.delete_by_id(media_state.id_))
        return (
            video,
            annotation_scenes,
            fps,
            width,
            height,
            number_of_frames,
            str(video_repo.binary_repo.get_path_or_presigned_url(filename)),
        )

    return _video_factory
