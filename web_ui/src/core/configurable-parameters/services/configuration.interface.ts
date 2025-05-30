// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

interface ParameterBase {
    key: string;
    name: string;
    description: string;
}

interface NumberParameter extends ParameterBase {
    type: 'int' | 'float';
    value: number;
    minValue: number;
    maxValue: number;
    defaultValue: number;
}

interface BoolParameter extends ParameterBase {
    type: 'bool';
    value: boolean;
    defaultValue: boolean;
}

interface EnumParameter extends ParameterBase {
    type: 'enum';
    value: string;
    defaultValue: string;
    allowedValues: string[];
}

export interface StaticParameter extends ParameterBase {
    value: number | string | boolean;
}

export type ConfigurationParameter = BoolParameter | NumberParameter | EnumParameter;

interface ProjectConfigurationTaskConfigsTraining {
    constraints: ConfigurationParameter[];
}

interface ProjectConfigurationTaskConfigs {
    taskId: string;
    training: ProjectConfigurationTaskConfigsTraining;
    autoTraining: ConfigurationParameter[];
    predictions: ConfigurationParameter[];
}

type KeyValueParameter = Pick<ConfigurationParameter, 'key' | 'value'>;

export interface ProjectConfigurationUploadPayload {
    training?: {
        constraints: KeyValueParameter[];
    };
    autoTraining?: KeyValueParameter[];
    predictions?: KeyValueParameter[];
}

export interface ProjectConfiguration {
    taskConfigs: ProjectConfigurationTaskConfigs[];
}

export interface TrainingConfiguration {
    datasetPreparation?: Record<string, ConfigurationParameter[]>;
    training?: ConfigurationParameter[];
    evaluation?: ConfigurationParameter[];
    advancedConfiguration?: StaticParameter[];
}

export interface TrainingConfigurationUpdatePayload {
    datasetPreparation?: Record<string, KeyValueParameter[]>;
    training?: KeyValueParameter[];
    evaluation?: KeyValueParameter[];
    advancedConfiguration?: KeyValueParameter[];
}
