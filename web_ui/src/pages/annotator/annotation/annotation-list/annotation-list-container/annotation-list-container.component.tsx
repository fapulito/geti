// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { DOMAIN } from '../../../../../core/projects/core.interface';
import { useAnnotatorMode } from '../../../hooks/use-annotator-mode';
import { useLocalAnnotations } from '../../../hooks/use-local-annotations.hooks';
import { useLocalPredictions } from '../../../hooks/use-local-predictions.hooks';
import { useAnnotationScene } from '../../../providers/annotation-scene-provider/annotation-scene-provider.component';
import { useTaskChain } from '../../../providers/task-chain-provider/task-chain-provider.component';
import { useTask } from '../../../providers/task-provider/task-provider.component';
import { PaneList } from '../../pane-list.component';
import { AnnotationListThumbnailGrid } from '../annotation-list-thumbnail-grid/annotation-list-thumbnail-grid.component';
import { AnnotationList } from '../annotation-list.component';
import { AnnotationActions } from './annotation-actions.component';
import { AnnotationListActions } from './annotation-list-actions.component';

export const AnnotationListContainer = (): JSX.Element => {
    const { predictions, isFetching } = useLocalPredictions();
    const localAnnotations = useLocalAnnotations();
    const { isActiveLearningMode } = useAnnotatorMode();
    const { isTaskChainDomainSelected } = useTask();
    const { inputs: inputAnnotations } = useTaskChain();
    const { unselectAnnotation, selectAnnotation, annotations } = useAnnotationScene();

    const isTaskChainSelectedSegmentation = isTaskChainDomainSelected(DOMAIN.SEGMENTATION);
    const isTaskChainSelectedClassification = isTaskChainDomainSelected(DOMAIN.CLASSIFICATION);
    const selectedAnnotation = annotations.find(({ isSelected }) => isSelected);

    const finalAnnotations = isActiveLearningMode
        ? localAnnotations
        : predictions.map((current) => ({ ...current, isSelected: current.id === selectedAnnotation?.id }));

    const handleSelectAnnotation = (annotationId: string) => (isSelected: boolean) => {
        if (isSelected) {
            selectAnnotation(annotationId);
        } else {
            unselectAnnotation(annotationId);
        }
    };

    if (isTaskChainSelectedClassification) {
        return (
            <AnnotationListThumbnailGrid annotations={inputAnnotations} onSelectAnnotation={handleSelectAnnotation} />
        );
    }

    return (
        <PaneList
            thumbnailGrid={
                isTaskChainSelectedSegmentation && (
                    <AnnotationListThumbnailGrid
                        annotations={inputAnnotations}
                        onSelectAnnotation={handleSelectAnnotation}
                    />
                )
            }
            listActions={
                <AnnotationActions isTaskChainSelectedClassification={isTaskChainSelectedClassification}>
                    {isActiveLearningMode ? <AnnotationListActions /> : null}
                </AnnotationActions>
            }
            itemsList={
                <AnnotationList
                    annotations={finalAnnotations}
                    isLoading={!isActiveLearningMode && isFetching}
                    isDragDisabled={!isActiveLearningMode}
                />
            }
        />
    );
};
