// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { Flex, View } from '@geti/ui';
import { MoreMenu } from '@geti/ui/icons';
import { AnimatePresence, motion } from 'framer-motion';

import { DATASET_NAME_MAX_WIDTH } from '../../../pages/project-details/components/project-dataset/utils';
import { ANIMATION_PARAMETERS } from '../../animation-parameters/animation-parameters';
import { TruncatedText } from '../truncated-text/truncated-text.component';

import classes from './custom-tab-item.module.scss';

export interface CustomTabItemProps {
    name: string;
    isMoreIconVisible: boolean;
}

export const CustomTabItem = ({ name, isMoreIconVisible }: CustomTabItemProps): JSX.Element => {
    return (
        <Flex
            alignItems={'center'}
            gap={'size-50'}
            UNSAFE_className={!isMoreIconVisible ? classes.customTabItemContainer : undefined}
        >
            <View maxWidth={DATASET_NAME_MAX_WIDTH}>
                <TruncatedText
                    aria-label={name}
                    data-testid='dataset-name'
                    UNSAFE_className={isMoreIconVisible ? classes.customTabItemName : undefined}
                >
                    {name}
                </TruncatedText>
            </View>
            <View width={'size-200'} height={'size-200'}>
                <AnimatePresence>
                    {isMoreIconVisible && (
                        <motion.div variants={ANIMATION_PARAMETERS.FADE_ITEM} animate={'visible'} initial={'hidden'}>
                            <MoreMenu />
                        </motion.div>
                    )}
                </AnimatePresence>
            </View>
        </Flex>
    );
};
