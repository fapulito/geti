# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE
import logging
from copy import copy
from typing import Any, cast

import cv2
import numpy as np
from bson import ObjectId
from geti_types import ID
from iai_core.entities.annotation import Annotation
from iai_core.entities.dataset_item import DatasetItem
from iai_core.entities.label import Label
from iai_core.entities.model import Model
from iai_core.entities.scored_label import ScoredLabel
from iai_core.entities.shapes import Point, Polygon
from iai_core.utils.shape_factory import ShapeFactory

from jobs_common_extras.evaluation.utils.helpers import is_model_legacy_otx_version

logger = logging.getLogger(__name__)

Contour = list[tuple[float, float]]
ContourInternal = list[tuple[float, float] | None]
Mask = np.ndarray[Any, np.dtype[np.uint8]]


def create_hard_prediction_from_soft_prediction(
    soft_prediction: np.ndarray, soft_threshold: float, blur_strength: int = 5
) -> np.ndarray:
    """
    Creates a hard prediction containing the final label index per pixel.

    :param soft_prediction: Output from segmentation network. Assumes floating point values, between 0.0 and 1.0.
        Can be a 2d-array of shape (height, width) or per-class segmentation logits of shape (height, width, n_classes)
    :param soft_threshold: minimum class confidence for each pixel.
        The higher the value, the more strict the segmentation is (usually set to 0.5)
    :param blur_strength: The higher the value, the smoother the segmentation output will be, but less accurate
    :return: numpy array of the hard prediction
    """
    soft_prediction_blurred = cv2.blur(soft_prediction, (blur_strength, blur_strength))
    if len(soft_prediction.shape) == 3:
        # Apply threshold to filter out `unconfident` predictions, then get max along
        # class dimension
        soft_prediction_blurred[soft_prediction_blurred < soft_threshold] = 0
        hard_prediction = np.argmax(soft_prediction_blurred, axis=2)
    elif len(soft_prediction.shape) == 2:
        # In the binary case, simply apply threshold
        hard_prediction = soft_prediction_blurred > soft_threshold
    else:
        raise ValueError(
            f"Invalid prediction input of shape {soft_prediction.shape}. Expected either a 2D or 3D array."
        )
    return hard_prediction


def get_subcontours(contour: Contour) -> list[Contour]:
    """
    Splits contour into sub-contours that do not have self intersections.

    :param contour: the contour to split
    :return: list of sub-contours
    """

    def find_loops(points: ContourInternal) -> list:
        """For each consecutive pair of equivalent rows in the input matrix returns their indices."""
        _, inverse, count = np.unique(points, axis=0, return_inverse=True, return_counts=True)  # type: ignore
        duplicates = np.where(count > 1)[0]
        indices = []
        for x in duplicates:
            y = np.nonzero(inverse == x)[0]
            for i, _ in enumerate(y[:-1]):
                indices.append(y[i : i + 2])
        return indices

    base_contour = cast("ContourInternal", copy(contour))

    # Make sure that contour is closed.
    if not np.array_equal(base_contour[0], base_contour[-1]):  # type: ignore
        base_contour.append(base_contour[0])

    subcontours: list[Contour] = []
    loops = sorted(find_loops(base_contour), key=lambda x: x[0], reverse=True)
    for loop in loops:
        i, j = loop
        subcontour = base_contour[i:j]
        subcontour = [x for x in subcontour if x is not None]
        subcontours.append(cast("Contour", subcontour))
        base_contour[i:j] = [None] * (j - i)

    return [i for i in subcontours if len(i) > 2]


def create_annotation_from_segmentation_map(
    hard_prediction: np.ndarray, soft_prediction: np.ndarray, label_map: dict
) -> list[Annotation]:
    """
    Creates polygons from the soft predictions.

    Note: background label will be ignored and not be converted to polygons.

    :param hard_prediction: hard prediction containing the final label index per pixel.
        See function `create_hard_prediction_from_soft_prediction`.
    :param soft_prediction: soft prediction with shape H x W x N_labels,
            where soft_prediction[:, :, 0] is the soft prediction for
            background. If soft_prediction is of H x W shape, it is
            assumed that this soft prediction will be applied for all
            labels.
    :param label_map: dictionary mapping labels to an index. It is assumed
            that the first item in the dictionary corresponds to the
            background label and will therefore be ignored.
    :return: list of annotations with polygons
    """
    # pylint: disable=too-many-locals
    height, width = hard_prediction.shape[:2]
    img_class = hard_prediction.swapaxes(0, 1)

    # pylint: disable=too-many-nested-blocks
    annotations: list[Annotation] = []
    for label_index, label in label_map.items():
        # Skip background
        if label_index == 0:
            continue

        # obtain current label soft prediction
        if len(soft_prediction.shape) == 3:
            current_label_soft_prediction = soft_prediction[:, :, label_index]
        else:
            current_label_soft_prediction = soft_prediction

        obj_group = img_class == label_index
        label_index_map = (obj_group.T.astype(int) * 255).astype(np.uint8)

        # Contour retrieval mode CCOMP (Connected components) creates a two-level
        # hierarchy of contours
        contours, hierarchies = cv2.findContours(label_index_map, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

        if hierarchies is not None:
            for contour, hierarchy in zip(contours, hierarchies[0]):
                if len(contour) <= 2 or cv2.contourArea(contour) < 1.0:
                    continue

                if hierarchy[3] == -1:
                    # In this case a contour does not represent a hole
                    _contour = [(point[0][0], point[0][1]) for point in contour]

                    # Split contour into subcontours that do not have self intersections.
                    subcontours = get_subcontours(_contour)
                    for subcontour in subcontours:
                        # compute probability of the shape
                        mask = np.zeros(hard_prediction.shape, dtype=np.uint8)
                        cv2.drawContours(
                            mask,
                            [np.asarray([[[x, y]] for x, y in subcontour])],
                            contourIdx=-1,
                            color=(1,),
                            thickness=-1,
                        )
                        probability = cv2.mean(current_label_soft_prediction, mask)[0]

                        # convert the list of points to a closed polygon
                        points = [Point(x=x / (width - 1), y=y / (height - 1)) for x, y in subcontour]
                        polygon = Polygon(points=points)

                        if polygon.get_area() > 0:
                            # Contour is a closed polygon with area > 0
                            annotations.append(
                                Annotation(
                                    shape=polygon,
                                    labels=[
                                        ScoredLabel(
                                            label_id=label.id_,
                                            is_empty=label.is_empty,
                                            probability=probability,
                                        )
                                    ],
                                    id_=ID(ObjectId()),
                                )
                            )
                        else:
                            # Contour is a closed polygon with area == 0
                            logger.warning(
                                "The geometry of the segmentation map you are converting "
                                "is not fully supported. Polygons with a area of zero "
                                "will be removed.",
                            )
                else:
                    # If contour hierarchy[3] != -1 then contour has a parent and
                    # therefore is a hole
                    # Do not allow holes in segmentation masks to be filled silently,
                    # but trigger warning instead
                    logger.warning(
                        "The geometry of the segmentation map you are converting is "
                        "not fully supported. A hole was found and will be filled.",
                    )
    return annotations


def mask_from_dataset_item(dataset_item: DatasetItem, labels: list[Label]) -> np.ndarray:
    """Creates a mask from dataset item.

    The mask will be two dimensional, and the value of each pixel matches the class index with offset 1. The background
    class index is zero. labels[0] matches pixel value 1, etc. The class index is
    determined based on the order of 'labels'.

    :param dataset_item: Item to make mask for
    :param labels: The labels to use for creating the mask. The order of the labels determines the class index.
    :return: numpy array of mask
    """
    return mask_from_annotation(dataset_item.get_annotations(), labels, dataset_item.width, dataset_item.height)


def mask_from_annotation(annotations: list[Annotation], labels: list[Label], width: int, height: int) -> np.ndarray:
    """
    Generate a segmentation mask of a numpy image, and a list of shapes.

    The mask is will be two dimensional and the value of each pixel matches the class
    index with offset 1. The background class index is zero. labels[0] matches pixel
    value 1, etc. The class index is determined based on the order of `labels`:

    :param annotations: List of annotations to plot in mask
    :param labels: List of labels. The index position of the label determines the class number in the segmentation mask.
    :param width: Width of the mask
    :param height: Height of the mask
    :return: 2d numpy array of mask
    """

    mask = np.zeros(shape=(height, width), dtype=np.uint8)
    label_ids = [label.id_ for label in labels]
    for annotation in annotations:
        shape = annotation.shape
        if not isinstance(shape, Polygon):
            shape = ShapeFactory.shape_as_polygon(annotation.shape)
        known_labels = [
            label for label in annotation.get_labels() if isinstance(label, ScoredLabel) and label.id_ in label_ids
        ]
        if len(known_labels) == 0:
            # Skip unknown shapes
            continue

        label_to_compare = known_labels[0].label_id

        class_idx = label_ids.index(label_to_compare) + 1
        contour = []
        for point in shape.points:
            contour.append([int(point.x * width), int(point.y * height)])

        mask = cast(
            "Mask",
            cv2.drawContours(mask, [np.asarray([contour])], 0, (class_idx, class_idx, class_idx), -1),
        )

    return np.expand_dims(mask, axis=2)


def get_legacy_instance_segmentation_inferencer_configuration(model: Model) -> dict:
    """
    Get legacy OTX (version < 2.0) instance segmentation configuration from the model.

    :param model: (Geti) Model to get the instance segmentation configuration from
    :return: dict representing the instance segmentation configuration
    """
    if not is_model_legacy_otx_version(model):
        logger.warning(f"Model {model.id_} is not a legacy OTX model. Skipping legacy segmentation configuration.")
        return {}

    postprocessing = model.configuration.configurable_parameters.postprocessing  # type: ignore

    output_config: dict = {}
    output_config["use_ellipse_shapes"] = postprocessing.use_ellipse_shapes

    logger.info(f"Instance segmentation inferencer configuration: {output_config}")
    return output_config
