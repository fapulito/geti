// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import '@wessberg/pointer-events';

import { fireEvent, render, screen } from '@testing-library/react';

import { Anchor } from './anchor.component';

describe('anchor', (): void => {
    const properties = {
        x: 10,
        y: 10,
        angle: 0,
        size: 10,
        zoom: 1,
        label: 'test-label',
        cursor: 'nw-resize',
        onComplete: jest.fn(),
        moveAnchorTo: jest.fn(),
    };

    it('calls moveAnchorTo when clicked upon and moved', () => {
        const moveAnchorCallback = jest.fn();
        render(
            <svg>
                <Anchor {...properties} moveAnchorTo={moveAnchorCallback}>
                    <rect></rect>
                </Anchor>
            </svg>
        );
        const anchorActor = screen.getByLabelText(properties.label);
        fireEvent.pointerDown(anchorActor);
        fireEvent.pointerMove(anchorActor, { clientX: 10, clientY: 10 });
        expect(moveAnchorCallback).toBeCalledTimes(1);
    });

    it('calls onComplete when clicked and released', () => {
        const onCompleteCallback = jest.fn();
        render(
            <svg>
                <Anchor {...properties} onComplete={onCompleteCallback}>
                    <rect></rect>
                </Anchor>
            </svg>
        );
        const anchorActor = screen.getByLabelText(properties.label);
        fireEvent.pointerDown(anchorActor);
        fireEvent.pointerMove(anchorActor, { clientX: 10, clientY: 10 });
        fireEvent.pointerUp(anchorActor);
        expect(onCompleteCallback).toBeCalledTimes(1);
    });
});
