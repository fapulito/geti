"""
Implements crop task
"""

# Copyright (C) 2022-2025 Intel Corporation
# LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

from iai_core.entities.dataset_item import DatasetItem
from iai_core.entities.datasets import Dataset
from iai_core.entities.label import Label
from iai_core.entities.subset import Subset
from iai_core.entities.task_environment import TaskEnvironment
from iai_core.repos import DatasetRepo


class CropTask:
    """
    Creates a cropped dataset based on the shapes containing labels of the
    previous task. If the previous task has no labels, the result will be empty.

    Note: for crop tasks, the task_environment.label_schema points to the
        LabelSchema of the previous task, not this one (which has NullLabelSchema).

    :param task_environment: TaskEnvironment defining the crop task configuration
    """

    task_environment: TaskEnvironment

    def __init__(self, task_environment: TaskEnvironment) -> None:
        self.task_environment = task_environment
        self.previous_task_labels = None

    def _get_labels_from_previous_task(self) -> list[Label]:
        """
        Get the list of labels associated with the previous task.

        :return: list of labels from the previous task
        """
        return self.task_environment.get_labels(include_empty=False)

    def infer(
        self,
        dataset: Dataset,
        subset: Subset | None = None,
    ) -> Dataset:
        """
        Crop the specified dataset, creating a dataset for the next task.

        :param dataset: Dataset to crop
        :param subset: Subset to set for the dataset items, if None the items will inherit the subset from the parent
        dataset item
        :return: Dataset for the next task
        """
        result_dataset = Dataset(
            label_schema_id=dataset.label_schema_id,
            id=DatasetRepo.generate_id(),
            purpose=dataset.purpose,
        )

        prev_task_labels: list[Label] = self._get_labels_from_previous_task()

        # Iterate dataset
        for item in dataset:
            for annotation in item.get_rois_containing_labels(labels=prev_task_labels):
                # Build a dataset item for the next task from the annotation of prev one
                new_item = DatasetItem(
                    media=item.media,
                    annotation_scene=item.annotation_scene,
                    roi=annotation,
                    subset=item.subset if subset is None else subset,
                    id_=DatasetRepo.generate_id(),
                )
                result_dataset.append(new_item)

        return result_dataset
