// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { Dispatch, MutableRefObject, SetStateAction, useEffect } from 'react';

import { ChartData, Colors } from '../../chart.interface';
import { CustomTooltipWrapper } from '../../custom-tooltip-wrapper/custom-tooltip-wrapper.component';

interface CustomTooltipChartProps {
    payload?: {
        value: number | string;
    }[];
    active?: boolean;
    label?: string;
    prevHoveredLabel: MutableRefObject<string | null>;
    defaultColors: Colors[];
    setLabelColors: Dispatch<SetStateAction<Colors[]>>;
    data: ChartData[];
    displayMessage: (props: { value?: number | string; label?: string }) => JSX.Element;
}

export const CustomTooltipChart = ({
    active,
    payload,
    label,
    prevHoveredLabel,
    defaultColors,
    setLabelColors,
    data,
    displayMessage,
}: CustomTooltipChartProps): JSX.Element | null => {
    const value =
        payload && payload.length
            ? typeof payload[0].value === 'number'
                ? Math.round(payload[0].value * 100) / 100
                : payload[0].value
            : '';

    useEffect(() => {
        if (active && label && prevHoveredLabel.current !== label) {
            const currentIndex = data.findIndex((element) => element.name === label);

            setLabelColors(() =>
                defaultColors.map((prevColor, index) => {
                    if (index !== currentIndex) {
                        return {
                            color: prevColor.fadedColor,
                            fadedColor: prevColor.color,
                        };
                    }

                    return prevColor;
                })
            );

            prevHoveredLabel.current = label;
        }
        if (!active && prevHoveredLabel.current) {
            setLabelColors(defaultColors);
            prevHoveredLabel.current = null;
        }
    }, [active, label, data, defaultColors, prevHoveredLabel, setLabelColors]);

    if (active && payload && payload.length) {
        return <CustomTooltipWrapper>{displayMessage({ label, value })}</CustomTooltipWrapper>;
    }

    return null;
};
