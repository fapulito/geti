# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE
from __future__ import annotations

import logging
import math
import operator
from datetime import datetime
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any

from communication.rest_views.media_identifier_rest_views import MediaIdentifierRESTViews
from communication.rest_views.scored_label_rest_views import ScoredLabelRESTViews

from geti_telemetry_tools import unified_tracing
from geti_types import ID
from iai_core.entities.annotation import Annotation, AnnotationScene, AnnotationSceneKind
from iai_core.entities.shapes import Ellipse, Keypoint, Point, Polygon, Rectangle
from iai_core.repos import AnnotationSceneRepo

if TYPE_CHECKING:
    from collections.abc import Sequence

    from entities.video_annotation_properties import VideoAnnotationProperties

    from geti_types import MediaIdentifierEntity
    from iai_core.entities.annotation_scene_state import AnnotationSceneState, AnnotationState
    from iai_core.entities.label import Label
    from iai_core.entities.shapes import Shape


ANNOTATIONS = "annotations"
ANNOTATION_STATE_PER_TASK = "annotation_state_per_task"
TO_REVISIT = "to_revisit"
LABELS_TO_REVISIT = "labels_to_revisit"
LABELS_TO_REVISIT_FULL_SCENE = "labels_to_revisit_full_scene"
HEIGHT = "height"
ID_ = "id"
KIND = "kind"
LABELS = "labels"
MEDIA_IDENTIFIER = "media_identifier"
MODIFIED = "modified"
POINTS = "points"
SHAPE = "shape"
TYPE = "type"
WIDTH = "width"
X = "x"
Y = "y"
ANGLE = "angle"
IS_VISIBLE = "is_visible"

logger = logging.getLogger(__name__)


class RestShapeType(IntEnum):
    ELLIPSE = auto()
    RECTANGLE = auto()
    POLYGON = auto()
    ROTATED_RECTANGLE = auto()
    KEYPOINT = auto()


class AnnotationRevisitState:
    """
    This class holds various properties related to the AnnotationSceneState which are
    extracted from the REST representation of an AnnotationScene

    :param labels_to_revisit_full_scene: List of label ID's (as strings) to revisit
        for the full annotation scene to which this AnnotationRevisitState applies
    :param labels_to_revisit_per_annotation: Nested list of label ID's to revisit for
        each annotation in the scene. Each entry in the outermost list corresponds to
        the list of labels that need to be revisited for a single annotation
    :param annotations: List of annotations in the annotation scene to which this
        AnnotationRevisitState applies. This list should have the same length as
        `labels_to_revisit_per_annotation`, and be sorted such that each annotation
        and the list of labels to revisit for it should have the same index.
    """

    def __init__(
        self,
        labels_to_revisit_full_scene: Sequence[str] | None = None,
        labels_to_revisit_per_annotation: Sequence[set[ID]] | None = None,
        annotations: Sequence[Annotation] | None = None,
    ) -> None:
        self.labels_to_revisit_full_scene: set[ID] = (
            {ID(label_id) for label_id in labels_to_revisit_full_scene}
            if labels_to_revisit_full_scene is not None
            else set()
        )
        self._labels_to_revisit_per_annotation: list[set[ID]] = (
            list(labels_to_revisit_per_annotation) if labels_to_revisit_per_annotation is not None else []
        )
        self._annotations: list[Annotation] = list(annotations) if annotations is not None else []

        if len(self._annotations) != len(self._labels_to_revisit_per_annotation):
            raise ValueError("The lists of annotations and labels to revisit per annotation must be of equal length.")

    def append_labels_to_revisit_for_annotation(self, annotation: Annotation, labels_to_revisit: Sequence[str]) -> None:
        """
        This method adds the information regarding which labels to revisit for a
        specific annotation to the existing mapping of annotations and to-revisit
        labels

        :param annotation: Annotation instance for which the labels should be revisited
        :param labels_to_revisit: List of label ID's that should be revisited for the
            annotation
        """
        self._annotations.append(annotation)
        self._labels_to_revisit_per_annotation.append({ID(label_id) for label_id in labels_to_revisit})

    @property
    def labels_to_revisit_per_annotation(self) -> dict[ID, set[ID]]:
        """
        Returns the mapping of annotation ID to the list of label ids to revisit for
        that particular annotation

        NOTE: This method assumes that the annotations for the annotation scene to
        which this AnnotationRevisitState applies have all been saved to the repository,
        and hence all have a unique ID. It will raise a ValueError if this is not the
        case.

        :raises ValueError: If the AnnotationRevisitState contains annotations with
            duplicate (or empty) database ID's.
        :return: Dictionary containing annotation ID's as keys and lists of label ID's
            as values
        """
        annotation_ids = [annotation.id_ for annotation in self._annotations]
        if len(annotation_ids) != len(set(annotation_ids)):
            raise ValueError(
                f"Duplicate annotation ID's found in REST request data for annotation list: '{self._annotations}'."
            )
        return dict(zip(annotation_ids, self._labels_to_revisit_per_annotation))


class AnnotationRESTViews:
    """
    This class maps Annotation entities to REST View (and vice versa)
    """

    @staticmethod
    def generate_full_box_rest(media_height: int, media_width: int) -> dict:
        return AnnotationRESTViews.rectangle_shape_to_rest(Rectangle.generate_full_box(), media_height, media_width)

    @staticmethod
    def rectangle_shape_to_rest(rectangle_shape: Rectangle, media_height: int, media_width: int) -> dict:
        """
        Returns the REST representation of a rectangle.

        :param rectangle_shape: the input rectangle to be represented in REST
        :return: the REST representation of a rectangle.
        """
        return {
            TYPE: RestShapeType.RECTANGLE.name,
            X: round(rectangle_shape.x1 * media_width),
            Y: round(rectangle_shape.y1 * media_height),
            WIDTH: round(rectangle_shape.width * media_width),
            HEIGHT: round(rectangle_shape.height * media_height),
        }

    @staticmethod
    def __rectangle_shape_from_rest(
        rectangle_data: dict,
        media_height: int,
        media_width: int,
        modification_date: datetime | None = None,
    ) -> Rectangle:
        """
        Deserializes a rectangle from a REST representation

        :param rectangle_data: the REST representation of a rectangle
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :return: deserialized Rectangle object
        """
        x = float(rectangle_data[X]) / media_width
        y = float(rectangle_data[Y]) / media_height
        width = float(rectangle_data[WIDTH]) / media_width
        height = float(rectangle_data[HEIGHT]) / media_height

        return Rectangle(x1=x, y1=y, x2=x + width, y2=y + height, modification_date=modification_date)

    @staticmethod
    def ellipse_shape_to_rest(ellipse_shape: Ellipse, media_height: int, media_width: int) -> dict:
        """
        Returns the REST representation of an ellipse

        REST representation of the ellipse is now a bounding box encapsulating the ellipse.
        (x,y) denotes the top-left point of the bounding box.
        (width, height) denotes the width and height of the bounding box.
        All values are expressed in the pixel coordinate system.

        :return: the REST representation of an ellipse
        """
        return {
            TYPE: RestShapeType.ELLIPSE.name,
            X: round(ellipse_shape.x1 * media_width),  # the x origin of the encapsulating rectangle
            Y: round(ellipse_shape.y1 * media_height),  # the y origin of the encapsulating rectangle
            WIDTH: round(ellipse_shape.width * media_width),
            HEIGHT: round(ellipse_shape.height * media_height),
        }

    @staticmethod
    def __ellipse_shape_from_rest(
        ellipse_data: dict,
        media_height: int,
        media_width: int,
        modification_date: datetime | None = None,
    ) -> Ellipse:
        """
        Deserializes an ellipse from a REST representation

        :param ellipse_data: the REST representation of an ellipse
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :return: deserialized Ellipse object
        """
        x1 = float(ellipse_data[X]) / media_width
        y1 = float(ellipse_data[Y]) / media_height
        width = float(ellipse_data[WIDTH]) / media_width
        height = float(ellipse_data[HEIGHT]) / media_height

        return Ellipse(
            x1=x1,
            y1=y1,
            x2=x1 + width,
            y2=y1 + height,
            modification_date=modification_date,
        )

    @staticmethod
    def point_to_rest(point: Point, media_height: int, media_width: int) -> dict:
        """
        Returns the REST representation of a Point.

        :param point: the point to be represented in REST
        :return: the REST representation of a point
        """
        return {
            X: round(point.x * media_width),
            Y: round(point.y * media_height),
        }

    @staticmethod
    def _polygon_shape_to_rest(polygon_shape: Polygon, media_height: int, media_width: int) -> dict:
        """
        Returns the REST representation of a polygon

        :param polygon_shape: the polygon to be represented in REST
        :return: the REST representation of a polygon
        """
        return {
            TYPE: RestShapeType.POLYGON.name,
            POINTS: [AnnotationRESTViews.point_to_rest(p, media_height, media_width) for p in polygon_shape.points],
        }

    @staticmethod
    def __polygon_shape_from_rest(
        polygon_data: dict,
        media_height: int,
        media_width: int,
        modification_date: datetime | None = None,
    ) -> Polygon:
        """
        Deserializes a polygon from a REST representation

        :param polygon_data: the REST representation of a polygon
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :return: deserialized Polygon object
        """
        points = polygon_data[POINTS]

        return Polygon(
            points=[Point(x=float(p[X]) / media_width, y=float(p[Y]) / media_height) for p in points],
            modification_date=modification_date,
        )

    @staticmethod
    def keypoint_shape_to_rest(
        keypoint_shape: Keypoint,
        media_height: int,
        media_width: int,
    ) -> dict:
        """
        Returns the REST representation of a keypoint.

        :param keypoint_shape: the keypoint to be represented in REST
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :return: the REST representation of a keypoint
        """
        return {
            TYPE: RestShapeType.KEYPOINT.name,
            X: round(keypoint_shape.x * media_width),
            Y: round(keypoint_shape.y * media_height),
            IS_VISIBLE: keypoint_shape.is_visible,
        }

    @staticmethod
    def __keypoint_shape_from_rest(
        keypoint_data: dict,
        media_height: int,
        media_width: int,
        modification_date: datetime | None = None,
    ) -> Keypoint:
        """
        Deserializes a keypoint from a REST representation

        :param keypoint_data: the REST representation of a polygon
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :return: deserialized Keypoint object
        """
        return Keypoint(
            x=keypoint_data[X] / media_width,
            y=keypoint_data[Y] / media_height,
            is_visible=keypoint_data[IS_VISIBLE],
            modification_date=modification_date,
        )

    @staticmethod
    def rotated_rectangle_shape_to_rest(rotated_rectangle: Polygon, media_height: int, media_width: int) -> dict:
        """
        Returns the REST representation of a rotated rectangle.

        :param rotated_rectangle: the rotated rectangle to be represented in REST
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :raises: ValueError if the input polygon does not have 4 points
        :return: the REST representation of a polygon
        """
        if len(rotated_rectangle.points) != 4:
            raise ValueError("A rotated rectangle must have exactly 4 points.")

        for p in rotated_rectangle.points:
            p.x *= media_width
            p.y *= media_height

        x_max_coord = max(rotated_rectangle.points, key=operator.attrgetter("x"))
        x_min_coord = min(rotated_rectangle.points, key=operator.attrgetter("x"))
        y_max_coord = max(rotated_rectangle.points, key=operator.attrgetter("y"))
        y_min_coord = min(rotated_rectangle.points, key=operator.attrgetter("y"))

        x_center = (x_max_coord.x + x_min_coord.x) / 2
        y_center = (y_max_coord.y + y_min_coord.y) / 2

        height = math.sqrt((y_max_coord.y - x_max_coord.y) ** 2 + (x_max_coord.x - y_max_coord.x) ** 2)
        width = math.sqrt((x_max_coord.y - y_min_coord.y) ** 2 + (y_min_coord.x - x_max_coord.x) ** 2)

        delta_y = rotated_rectangle.points[2].y - rotated_rectangle.points[1].y
        delta_x = rotated_rectangle.points[2].x - rotated_rectangle.points[1].x

        angle = math.atan2(delta_y, delta_x)
        while angle < 0.0:
            angle += math.pi * 2
        angle *= 180 / math.pi
        angle += 90
        if angle >= 360:
            angle -= 360
        if 270 < angle < 360 or 90 < angle < 180:
            height, width = width, height

        angle_rounded = round(angle, 3)  # rounding to avoid floating-point error
        if angle_rounded in (0, 360):
            width = rotated_rectangle.points[0].x - rotated_rectangle.points[1].x
            height = rotated_rectangle.points[1].y - rotated_rectangle.points[2].y
        elif angle_rounded == 90:
            width = rotated_rectangle.points[0].y - rotated_rectangle.points[1].y
            height = rotated_rectangle.points[2].x - rotated_rectangle.points[1].x
        elif angle_rounded == 180:
            width = rotated_rectangle.points[1].x - rotated_rectangle.points[0].x
            height = rotated_rectangle.points[2].y - rotated_rectangle.points[1].y
        elif angle_rounded == 270:
            width = rotated_rectangle.points[2].y - rotated_rectangle.points[3].y
            height = rotated_rectangle.points[1].x - rotated_rectangle.points[2].x

        return {
            TYPE: RestShapeType.ROTATED_RECTANGLE.name,
            X: round(x_center, 4),
            Y: round(y_center, 4),
            WIDTH: round(width, 4),
            HEIGHT: round(height, 4),
            ANGLE: round(angle, 4),
        }

    @staticmethod
    def rotated_rectangle_shape_from_rest(
        rotated_rectangle_data: dict,
        media_height: int,
        media_width: int,
        modification_date: datetime | None = None,
    ) -> Polygon:
        """
        Deserializes a rotated rectangle from a REST representation. Orientation should
        be re applied between points 2 and 3 pointing outwards as seen below.
                            0 --- 1
                            |     |
                            3 --- 2
                               |
                               v
        :param rotated_rectangle_data: the REST representation of a rotated rectangle
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :param modification_date: The data of when the modification took place
        :return: deserialized Rotated Rectangle object
        """
        x_center = float(rotated_rectangle_data[X])
        y_center = float(rotated_rectangle_data[Y])
        width = float(rotated_rectangle_data[WIDTH])
        height = float(rotated_rectangle_data[HEIGHT])
        angle = math.radians(rotated_rectangle_data[ANGLE])

        points = [
            Point(
                x_center + (width / 2 * math.cos(angle)) - (height / 2 * math.sin(angle)),
                y_center + (width / 2 * math.sin(angle)) + (height / 2 * math.cos(angle)),
            ),
            Point(
                x_center - (width / 2 * math.cos(angle)) - (height / 2 * math.sin(angle)),
                y_center - (width / 2 * math.sin(angle)) + (height / 2 * math.cos(angle)),
            ),
            Point(
                x_center - (width / 2 * math.cos(angle)) + (height / 2 * math.sin(angle)),
                y_center - (width / 2 * math.sin(angle)) - (height / 2 * math.cos(angle)),
            ),
            Point(
                x_center + (width / 2 * math.cos(angle)) + (height / 2 * math.sin(angle)),
                y_center + (width / 2 * math.sin(angle)) - (height / 2 * math.cos(angle)),
            ),
        ]
        points = [Point(p.x / media_width, p.y / media_height) for p in points]
        return Polygon(
            points=points,
            modification_date=modification_date,
        )

    @staticmethod
    def rest_rectangle_to_rest_rotated_rectangle(rectangle_data: dict) -> dict:
        """
        Converts a REST representation of a rectangle into a REST representation of a rotated rectangle
        The angle is set to 0.

        :return: REST representation of a rotated rectangle
        """
        x_center = (rectangle_data[X] + rectangle_data[WIDTH]) / 2
        y_center = (rectangle_data[Y] + rectangle_data[HEIGHT]) / 2
        width = rectangle_data[WIDTH]
        height = rectangle_data[HEIGHT]

        return {
            TYPE: RestShapeType.ROTATED_RECTANGLE.name,
            X: round(x_center, 4),
            Y: round(y_center, 4),
            WIDTH: round(width, 4),
            HEIGHT: round(height, 4),
            ANGLE: 0,
        }

    @staticmethod
    def annotation_to_rest(
        annotation: Annotation,
        media_height: int,
        media_width: int,
        annotation_scene_state: AnnotationSceneState | None = None,
        label_only: bool = False,
        is_rotated_detection: bool = False,
        deleted_label_ids: Sequence[ID] | None = None,
    ) -> dict:
        """
        Serialize an Annotation to a REST representation

        :param annotation: the input annotation to be represented in REST
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :param annotation_scene_state: AnnotationSceneState representing the state of
            the annotation scene from which the annotation originates. If left as
            None, the field `labels_to_revisit` will not be added to the response
        :param label_only: if set to true, do not return the shape of the annotation
        :param is_rotated_detection: if set to true a polygon needs to be converted to
        a rotated rectangle representation in the rest api
        :param deleted_label_ids: deleted label ids to filter out
        :return: REST representation of an Annotation
        """
        deleted_label_ids = [] if deleted_label_ids is None else deleted_label_ids

        labels = annotation.get_labels(include_empty=True)
        if not labels:
            logger.warning(f"Annotation {annotation.id_} has no labels")

        rest_labels = [
            ScoredLabelRESTViews.scored_label_to_rest(label) for label in labels if label.id_ not in deleted_label_ids
        ]

        result: dict[str, Any] = {
            ID_: str(annotation.id_),
            MODIFIED: annotation.shape.modification_date.isoformat(),  # type: ignore
            LABELS: rest_labels,
        }

        if annotation_scene_state is not None:
            result.update(
                {
                    LABELS_TO_REVISIT: [
                        str(label_id)
                        for label_id in annotation_scene_state.labels_to_revisit_per_annotation[annotation.id_]
                    ]
                }
            )
        if not label_only:
            if isinstance(annotation.shape, Ellipse):
                shape = AnnotationRESTViews.ellipse_shape_to_rest(annotation.shape, media_height, media_width)
            elif isinstance(annotation.shape, Rectangle):
                shape = AnnotationRESTViews.rectangle_shape_to_rest(annotation.shape, media_height, media_width)
            elif isinstance(annotation.shape, Polygon):
                if not is_rotated_detection:
                    shape = AnnotationRESTViews._polygon_shape_to_rest(annotation.shape, media_height, media_width)
                else:
                    shape = AnnotationRESTViews.rotated_rectangle_shape_to_rest(
                        annotation.shape, media_height, media_width
                    )
            elif isinstance(annotation.shape, Keypoint):
                shape = AnnotationRESTViews.keypoint_shape_to_rest(annotation.shape, media_height, media_width)
            else:
                raise ValueError(f"Shape {annotation.shape.__class__.__name__} is not supported (yet)")
            result[SHAPE] = shape
        return result

    @staticmethod
    def annotation_from_rest(
        data: dict, label_per_id: dict[ID, Label], media_height: int, media_width: int
    ) -> Annotation:
        """
        Deserialize an Annotation from a REST representation

        :param data: REST representation of an Annotation
        :param label_per_id: dictionary containing the labels mapped to their IDs
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :return: deserialized Annotation object
        """
        annotation_id = data.get(ID_)
        date_string = data.get(MODIFIED)
        modification_date = datetime.fromisoformat(date_string) if date_string else None

        shape = AnnotationRESTViews.shape_from_rest(data[SHAPE], media_height, media_width, modification_date)

        labels_data = data.get(LABELS)

        labels = [
            ScoredLabelRESTViews.scored_label_from_rest(scored_label_data=data, label=label_per_id[ID(data[ID_])])
            for data in labels_data  # type: ignore
        ]

        return Annotation(shape=shape, labels=labels, id_=annotation_id)  # type: ignore[arg-type]

    @staticmethod
    def shape_from_rest(
        data: dict,
        media_height: int,
        media_width: int,
        modification_date: datetime | None = None,
    ) -> Shape | Keypoint:
        """
        Deserialize a Rectangle, Ellipse, Polygon, or Keypoint shape from its rest view.

        :param data: REST view of the shape
        :param media_height: The height in pixels of the media
        :param media_width: The width in pixels of the media
        :param modification_date: Modification date of the shape
        :return: Rectangle, Ellipse, Polygon, Keypoint shape object
        """
        shape_type = data[TYPE]

        shape: Shape | Keypoint
        if shape_type == RestShapeType.ELLIPSE.name:
            shape = AnnotationRESTViews.__ellipse_shape_from_rest(data, media_height, media_width, modification_date)
        elif shape_type == RestShapeType.RECTANGLE.name:
            shape = AnnotationRESTViews.__rectangle_shape_from_rest(data, media_height, media_width, modification_date)
        elif shape_type == RestShapeType.POLYGON.name:
            shape = AnnotationRESTViews.__polygon_shape_from_rest(data, media_height, media_width, modification_date)
        elif shape_type == RestShapeType.ROTATED_RECTANGLE.name:
            shape = AnnotationRESTViews.rotated_rectangle_shape_from_rest(
                data, media_height, media_width, modification_date
            )
        elif shape_type == RestShapeType.KEYPOINT.name:
            shape = AnnotationRESTViews.__keypoint_shape_from_rest(data, media_height, media_width, modification_date)
        else:
            raise ValueError(f"Shape of kind {shape_type} is not supported (yet)")
        return shape

    @staticmethod
    def __per_task_annotation_states_to_rest(
        annotation_states_per_task: dict[ID, AnnotationState],
        tasks_to_revisit: list[ID],
    ) -> list[dict[str, str]]:
        """
        Returns the REST representation of the per-task (aggregated) annotation states

        :param annotation_states_per_task: Dictionary containing the ID's of all
            tasks in the project as keys, and the corresponding AnnotationState for
            the tasks as values
        :param tasks_to_revisit: List of ID's of those tasks that need revisiting of
            the annotations, as a consequence of a label schema change
        :return: List of dictionaries. Each dictionary corresponds to the annotation
            state for a single task in the project. The dictionary contains the
            following keys:
                - 'task_id', the ID of the task
                - 'state', the annotation state of the task
        """
        task_states: list[dict[str, str]] = []
        for task_id, task_annotation_state in annotation_states_per_task.items():
            state_rest_dict = {"task_id": str(task_id)}
            if task_id in tasks_to_revisit:
                state_rest_dict.update({"state": TO_REVISIT})
            else:
                state_rest_dict.update({"state": str(task_annotation_state).lower()})
            task_states.append(state_rest_dict)
        return task_states

    @staticmethod
    @unified_tracing
    def media_2d_annotation_to_rest(
        annotation_scene: AnnotationScene,
        annotation_scene_state: AnnotationSceneState | None = None,
        tasks_to_revisit: list[ID] | None = None,
        label_only: bool = False,
        is_rotated_detection: bool = False,
        deleted_label_ids: Sequence[ID] | None = None,
        is_ephemeral: bool = False,
    ) -> dict:
        """
        Returns the REST representation of an Annotation.

        :param annotation_scene: the input annotation to be represented in REST
        :param annotation_scene_state: the annotation state for the annotation
        :param tasks_to_revisit: List of ID's of the tasks for which revisiting the
            annotation is needed due to a label schema change
        :param label_only: if set to true, do not return the shape
        :param is_rotated_detection: if the task is rotated detection
        :param is_ephemeral: if set to true, skip rest mapping of media identifier
        :param deleted_label_ids: deleted labels to filter out
        :raises ValueError: if annotation does not belong to an Image
        :return: the REST representation of annotation.
        """
        if deleted_label_ids is None:
            deleted_label_ids = []

        result: dict[str, Any] = {
            KIND: str(annotation_scene.kind).lower(),
            MODIFIED: annotation_scene.creation_date.isoformat(),
        }

        # Skip DB dependant items
        if not is_ephemeral:
            result[MEDIA_IDENTIFIER] = MediaIdentifierRESTViews.media_identifier_to_rest(
                annotation_scene.media_identifier
            )
            result[ID_] = str(annotation_scene.id_)

        if annotation_scene.kind != AnnotationSceneKind.ANNOTATION:
            # Prediction case. annotation_scene_state should always be None
            annotation_scene_state = None
        else:
            # Annotation case.
            if annotation_scene_state is None or tasks_to_revisit is None:
                raise ValueError(
                    f"Cannot convert {annotation_scene} to REST: Either its "
                    f"AnnotationSceneState or the list of tasks to revisit is missing."
                )
            result[LABELS_TO_REVISIT_FULL_SCENE] = [
                str(label_id) for label_id in annotation_scene_state.labels_to_revisit_full_scene
            ]
            result[ANNOTATION_STATE_PER_TASK] = AnnotationRESTViews.__per_task_annotation_states_to_rest(
                annotation_states_per_task=annotation_scene_state.state_per_task,
                tasks_to_revisit=tasks_to_revisit,
            )

        result[ANNOTATIONS] = [
            AnnotationRESTViews.annotation_to_rest(
                annotation,
                media_height=annotation_scene.media_height,
                media_width=annotation_scene.media_width,
                annotation_scene_state=annotation_scene_state,
                label_only=label_only,
                is_rotated_detection=is_rotated_detection,
                deleted_label_ids=deleted_label_ids,
            )
            for annotation in annotation_scene.annotations
        ]

        return result

    @staticmethod
    @unified_tracing
    def media_2d_annotation_from_rest(  # noqa: PLR0913
        annotation_dict: dict,
        label_per_id: dict[ID, Label],
        kind: AnnotationSceneKind,
        last_annotator_id: str,
        media_identifier: MediaIdentifierEntity,
        media_height: int,
        media_width: int,
        annotation_scene_id: ID | None = None,
    ) -> tuple[AnnotationScene, AnnotationRevisitState]:
        """
        Deserializes a media 2d annotation from a REST message and makes sure that the annotation is valid.

        :param annotation_dict: the REST representation of the annotation scene
        :param label_per_id: dictionary containing the labels mapped to their IDs
        :param kind: the annotation kind of the returned annotation object. See :class:`AnnotationKind`
        :param last_annotator_id: the name or id of the editor.
        :param media_identifier: Media identifier for which the annotation scene was made
        :param media_height: Height in pixels of the media
        :param media_width: Width in pixels of the media
        :param annotation_scene_id: the id of the annotation object. Optional, do not assign for new annotation.
        :return: deserialized media 2d annotation
        """
        labels_to_revisit_full_scene = annotation_dict.get(LABELS_TO_REVISIT_FULL_SCENE)
        annotation_revisit_state = AnnotationRevisitState(labels_to_revisit_full_scene=labels_to_revisit_full_scene)
        annotations: list[Annotation] = []
        for shape in annotation_dict[ANNOTATIONS]:
            annotation = AnnotationRESTViews.annotation_from_rest(shape, label_per_id, media_height, media_width)
            labels_to_revisit_for_annotation = shape.get(LABELS_TO_REVISIT, [])
            if labels_to_revisit_for_annotation:
                annotation_revisit_state.append_labels_to_revisit_for_annotation(
                    annotation=annotation,
                    labels_to_revisit=labels_to_revisit_for_annotation,
                )
            annotations.append(annotation)
        ephemeral = False
        if annotation_scene_id is None:
            annotation_scene_id = AnnotationSceneRepo.generate_id()
            ephemeral = True
        annotation_scene = AnnotationScene(
            kind=kind,
            media_identifier=media_identifier,
            media_height=media_height,
            media_width=media_width,
            id_=annotation_scene_id,
            last_annotator_id=last_annotator_id,
            annotations=annotations,
            ephemeral=ephemeral,
        )
        return annotation_scene, annotation_revisit_state

    @staticmethod
    def get_label_ids_from_rest(annotation_dict: dict) -> set[ID]:
        """
        Get all the label IDs from the annotation REST view.

        :param annotation_dict: REST representation of the annotation scene
        :return: a set of the label IDs contained in the annotation REST
        """
        annotations = annotation_dict[ANNOTATIONS]
        # Flatten the list of labels contained in each annotation
        return {label_dict[ID_] for anno_dict in annotations for label_dict in anno_dict.get(LABELS, [])}

    @staticmethod
    @unified_tracing
    def media_2d_annotations_to_rest(
        annotation_scenes: Sequence[AnnotationScene],
        annotation_scene_states: Sequence[AnnotationSceneState],
        tasks_to_revisit_per_scene: Sequence[list[ID]],
        annotation_properties: VideoAnnotationProperties,
        label_only: bool = False,
        is_rotated_detection: bool = False,
        deleted_label_ids: Sequence[ID] | None = None,
    ) -> dict[str, Any]:
        """
        Returns the REST representation of a list of annotation scenes, used for video annotations.

        :param annotation_scenes: List of annotation scenes to be represented in REST
        :param annotation_scene_states: the annotation states for the annotation scenes
        :param tasks_to_revisit_per_scene: For each annotation scene, list of ID's of the tasks for which
         revisiting the annotation is needed due to a label schema change
        :param label_only: if set to true, do not return the shape
        :param is_rotated_detection: if the task is rotated detection
        :param deleted_label_ids: deleted labels to filter out
        :param annotation_properties: video properties of this rest view
        :raises ValueError: if annotation does not belong to an Image
        :return: the REST representation of annotation.
        """
        return {
            "video_annotations": [
                AnnotationRESTViews.media_2d_annotation_to_rest(
                    annotation_scene,
                    label_only=label_only,
                    annotation_scene_state=annotation_scene_state,
                    tasks_to_revisit=tasks_to_revisit,
                    is_rotated_detection=is_rotated_detection,
                    deleted_label_ids=deleted_label_ids,
                )
                for annotation_scene, annotation_scene_state, tasks_to_revisit in zip(
                    annotation_scenes,
                    annotation_scene_states,
                    tasks_to_revisit_per_scene,
                )
            ],
            "video_annotation_properties": AnnotationRESTViews.video_annotation_properties_to_rest(
                video_annotation_properties=annotation_properties
            ),
        }

    @staticmethod
    @unified_tracing
    def video_annotation_properties_to_rest(
        video_annotation_properties: VideoAnnotationProperties,
    ) -> dict[str, Any]:
        """
        Return a dict with the rest representation for the video annotation properties.

        :param video_annotation_properties: the pagination properties to be represented in REST
        :return: the REST representation of the video annotation properties
        """
        return {
            "total_count": video_annotation_properties.total_count,
            "start_frame": video_annotation_properties.start_frame,
            "end_frame": video_annotation_properties.end_frame,
            "total_requested_count": video_annotation_properties.total_requested_count,
            "requested_start_frame": video_annotation_properties.requested_start_frame,
            "requested_end_frame": video_annotation_properties.requested_end_frame,
        }
