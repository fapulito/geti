// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { useState } from 'react';

import { Button } from '@geti/ui';
import { isEmpty } from 'lodash-es';

import { ModelGroupsAlgorithmDetails } from '../../../../../core/models/models.interface';
import { CreditBalanceTrainDialog } from './credit-balance-train-dialog.component';

interface TrainModelProps {
    models: ModelGroupsAlgorithmDetails[];
}

export const TrainModel = ({ models }: TrainModelProps): JSX.Element => {
    const hasModels = !isEmpty(models);
    const [isTrainingDialogOpen, setIsTrainingDialogOpen] = useState<boolean>(false);

    return (
        <>
            <Button
                id={'train-new-model-button-id'}
                data-testid={'train-new-model-button-id'}
                variant={'accent'}
                onPress={() => setIsTrainingDialogOpen(true)}
            >
                Train {!hasModels ? 'new' : ''} model
            </Button>
            <CreditBalanceTrainDialog isOpen={isTrainingDialogOpen} onClose={() => setIsTrainingDialogOpen(false)} />
        </>
    );
};
