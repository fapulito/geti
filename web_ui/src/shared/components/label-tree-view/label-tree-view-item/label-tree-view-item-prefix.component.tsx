// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { ActionButton, View } from '@geti/ui';
import { ChevronDownSmallLight, ChevronRightSmallLight } from '@geti/ui/icons';

interface LabelTreeViewItemPrefixProps {
    isOpen: boolean;
    onOpenClickHandler: () => void;
    childrenLength: number;
}

export const LabelTreeViewItemPrefix = ({
    isOpen,
    onOpenClickHandler,
    childrenLength,
}: LabelTreeViewItemPrefixProps): JSX.Element => {
    return childrenLength > 0 ? (
        <ActionButton id='toggle-label-item' data-testid='toggle-label-item' isQuiet onPress={onOpenClickHandler}>
            {isOpen ? <ChevronDownSmallLight /> : <ChevronRightSmallLight />}
        </ActionButton>
    ) : (
        <View width={'16px'} height={'16px'} />
    );
};
