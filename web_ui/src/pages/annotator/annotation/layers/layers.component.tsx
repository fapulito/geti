// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { isClassificationDomain, isKeypointDetection } from '../../../../core/projects/domains';
import { hasEqualId } from '../../../../shared/utils';
import { useAnnotatorMode } from '../../hooks/use-annotator-mode';
import {
    useExplanationOpacity,
    usePrediction,
} from '../../providers/prediction-provider/prediction-provider.component';
import { useROI } from '../../providers/region-of-interest-provider/region-of-interest-provider.component';
import { getGlobalAnnotations } from '../../providers/task-chain-provider/utils';
import { useTask } from '../../providers/task-provider/task-provider.component';
import { areAnnotationsIdentical } from '../../utils';
import { ShapeLabel } from '../labels/shape-label.component';
import { Layer } from './layer.component';
import { LayersProps } from './utils';

export const Layers = ({
    annotations: userAnnotations,
    annotationsFilter,
    showLabelOptions,
    ...props
}: LayersProps) => {
    const { tasks, selectedTask, isTaskChainDomainSelected } = useTask();

    const task = selectedTask ?? tasks[0];
    const [selectedAnnotation] = userAnnotations;
    const isClassification = isClassificationDomain(task.domain);

    const { roi } = useROI();
    const { isActiveLearningMode } = useAnnotatorMode();
    const { predictionAnnotations } = usePrediction();
    const { showOverlapAnnotations } = useExplanationOpacity();

    const taskChainClassificationFilter =
        isClassification && isTaskChainDomainSelected(task.domain) ? hasEqualId(selectedAnnotation?.id) : undefined;

    const filteredAnnotations = annotationsFilter(userAnnotations);
    const filteredPredictions = annotationsFilter(predictionAnnotations, taskChainClassificationFilter);

    const annotationsByMode = isActiveLearningMode ? filteredAnnotations : filteredPredictions;
    const predictionModeShowsAnnotations = !isActiveLearningMode && showOverlapAnnotations;

    const isPredictionModeAndShowsAnnotations =
        predictionModeShowsAnnotations && !areAnnotationsIdentical(filteredAnnotations, filteredPredictions);

    return (
        <>
            {predictionModeShowsAnnotations && isClassification ? (
                <></>
            ) : (
                <Layer
                    width={props.width}
                    height={props.height}
                    selectedTask={selectedTask}
                    hideLabels={props.hideLabels}
                    isPredictionMode={!isActiveLearningMode}
                    globalAnnotations={getGlobalAnnotations(annotationsByMode, roi, selectedTask)}
                    removeBackground={isPredictionModeAndShowsAnnotations}
                    annotations={annotationsByMode}
                    renderLabel={(annotation) => (
                        <ShapeLabel
                            showOptions={showLabelOptions && isActiveLearningMode}
                            annotation={annotation}
                            areLabelsInteractive={props.areLabelsInteractive}
                            annotationToolContext={props.annotationToolContext}
                        />
                    )}
                />
            )}

            {isPredictionModeAndShowsAnnotations && (
                <Layer
                    width={props.width}
                    height={props.height}
                    isOverlap={!isClassification}
                    isPredictionMode={false}
                    selectedTask={selectedTask}
                    globalAnnotations={getGlobalAnnotations(filteredAnnotations, roi, selectedTask)}
                    removeBackground={isPredictionModeAndShowsAnnotations && !isKeypointDetection(task.domain)}
                    annotations={filteredAnnotations}
                    renderLabel={(annotation) => (
                        <ShapeLabel
                            showOptions={false}
                            annotation={annotation}
                            isOverlap={!isClassification}
                            areLabelsInteractive={props.areLabelsInteractive}
                            annotationToolContext={props.annotationToolContext}
                        />
                    )}
                />
            )}
        </>
    );
};
