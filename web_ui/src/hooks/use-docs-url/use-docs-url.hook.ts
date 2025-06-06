// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { useDeploymentConfigQuery } from '../../core/services/use-deployment-config-query.hook';

export const useDocsUrl = () => {
    const { data } = useDeploymentConfigQuery();

    return data?.docsUrl ?? '';
};
