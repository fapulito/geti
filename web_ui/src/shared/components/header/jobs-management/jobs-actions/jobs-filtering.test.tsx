// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

import { fireEvent, screen, waitFor } from '@testing-library/react';

import { JobType } from '../../../../../core/jobs/jobs.const';
import { createInMemoryProjectService } from '../../../../../core/projects/services/in-memory-project-service';
import { useUsers } from '../../../../../core/users/hook/use-users.hook';
import { User } from '../../../../../core/users/users.interface';
import { getMockedProject } from '../../../../../test-utils/mocked-items-factory/mocked-project';
import { getMockedUser } from '../../../../../test-utils/mocked-items-factory/mocked-users';
import { projectRender as render } from '../../../../../test-utils/project-provider-render';
import { FiltersType } from './jobs-dialog.interface';
import { JobsFiltering } from './jobs-filtering.component';

const mockedProject = getMockedProject({});

jest.mock('../../../../../core/users/hook/use-users.hook', () => ({
    ...jest.requireActual('../../../../../core/users/hook/use-users.hook'),
    useUsers: jest.fn(() => ({
        useGetUsersQuery: () => {
            return {
                users: [],
                isLoading: false,
                isError: false,
                totalCount: 0,
                totalMatchedCount: 0,
                getNextPage: async () => {
                    // noop
                },
            };
        },
    })),
}));

interface AppProps extends FiltersType {
    users: User[];
}

describe('jobs filtering', (): void => {
    const mockedUser = getMockedUser();
    const mockOnChange = jest.fn();

    let clientHeightSpy: jest.MockInstance<number, []>;
    let scrollHeightSpy: jest.MockInstance<number, []>;

    beforeEach(() => {
        scrollHeightSpy = jest.spyOn(window.HTMLElement.prototype, 'scrollHeight', 'get').mockImplementation(() => 32);
        clientHeightSpy = jest
            .spyOn(window.HTMLElement.prototype, 'clientHeight', 'get')
            .mockImplementationOnce((): number => 0)
            .mockImplementation(function (): number {
                // @ts-expect-error use of this
                return this.getAttribute('role') === 'listbox' ? 150 : 40;
            });
    });

    afterEach(() => {
        clientHeightSpy.mockRestore();
        scrollHeightSpy.mockRestore();
        jest.spyOn(window.HTMLElement.prototype, 'clientHeight', 'get').mockImplementation((): number => 1000);

        jest.clearAllMocks();
    });

    const App = ({ projectId, userId, jobTypes, users }: AppProps): JSX.Element => {
        // @ts-expect-error we only mock useGetUsersQuery
        jest.mocked(useUsers).mockImplementation(() => ({
            useGetUsersQuery: () => {
                return {
                    users,
                    isLoading: false,
                    isError: false,
                    totalCount: users.length,
                    totalMatchedCount: users.length,
                    getNextPage: async () => {
                        // noop
                    },
                };
            },
        }));

        return (
            <JobsFiltering
                values={{
                    projectId,
                    userId,
                    jobTypes: jobTypes === undefined ? [] : jobTypes,
                }}
                onChange={mockOnChange}
            />
        );
    };

    const renderComponent = async (
        projectId?: string,
        userId?: string,
        jobTypes: JobType[] = [],
        users: User[] = []
    ): Promise<void> => {
        const projectService = createInMemoryProjectService();
        projectService.getProjects = jest.fn(async () => {
            const projects = [mockedProject, { ...mockedProject, id: '222222', name: 'Test project 2' }];
            return {
                projects,
                nextPage: null,
            };
        });
        await render(<App projectId={projectId} userId={userId} jobTypes={jobTypes} users={users} />, {
            services: { projectService },
        });
    };

    it('should properly render base component', async (): Promise<void> => {
        await renderComponent();
        expect(screen.getByLabelText(/filter project/)).toHaveTextContent('All projects');
        expect(screen.getByLabelText(/filter user/)).toHaveTextContent('All users');
        expect(screen.getByLabelText(/filter job type/)).toHaveTextContent('All job types');
    });

    it('should populate project filter with projectId if defined', async (): Promise<void> => {
        await renderComponent('222222', '3');

        await waitFor(() => {
            expect(screen.getByLabelText(/filter project/)).toHaveTextContent('Test project 2');
        });
    });

    it('should populate user filter with userId if defined', async (): Promise<void> => {
        const users = [
            mockedUser,
            { ...mockedUser, id: '2', email: 'admin2@example.com', firstName: 'Administrator 2' },
        ];

        await renderComponent(undefined, '2', undefined, users);
        expect(screen.getByLabelText(/filter user/)).toHaveTextContent('admin2@example.com');
    });

    it('should populate job type filter with jobTypes if defined', async (): Promise<void> => {
        await renderComponent(undefined, undefined, [JobType.OPTIMIZATION_POT]);
        expect(screen.getByLabelText(/filter job type/)).toHaveTextContent('Optimize');
    });

    it('should reset user filter with "All users" if selected before user is not present in collection anymore', async (): Promise<void> => {
        const users = [
            mockedUser,
            { ...mockedUser, id: '2', email: 'admin2@example.com', firstName: 'Administrator 2' },
        ];

        await renderComponent(undefined, undefined, undefined, users);
        expect(screen.getByLabelText(/filter user/)).toHaveTextContent('All users');
    });

    it('should properly render suggestion panel for project filter', async (): Promise<void> => {
        await renderComponent();

        fireEvent.click(screen.getByRole('button', { name: /filter project/ }));

        expect(await screen.findByRole('option', { name: 'All projects' })).toHaveAttribute('data-key', '');
        expect(screen.getByRole('option', { name: 'Test project 1' })).toHaveAttribute('data-key', '111111');
        expect(screen.getByRole('option', { name: 'Test project 2' })).toHaveAttribute('data-key', '222222');
    });

    it('should properly render suggestion panel for user filter', async (): Promise<void> => {
        const users = [
            mockedUser,
            { ...mockedUser, id: '2', email: 'admin2@example.com', firstName: 'Administrator 2' },
            { ...mockedUser, id: '3', email: 'admin3@example.com', firstName: 'Administrator 3' },
        ];

        await renderComponent(undefined, undefined, undefined, users);

        fireEvent.click(screen.getByRole('button', { name: /filter user/ }));

        expect(screen.getByRole('option', { name: 'All users' })).toHaveAttribute('data-key', '');
        expect(screen.getByRole('option', { name: 'test@intel.com' })).toHaveAttribute('data-key', 'user-1-id');
        expect(screen.getByRole('option', { name: 'admin2@example.com' })).toHaveAttribute('data-key', '2');
        expect(screen.getByRole('option', { name: 'admin3@example.com' })).toHaveAttribute('data-key', '3');
    });

    it('should properly render suggestion panel for job type filter', async (): Promise<void> => {
        await renderComponent();

        fireEvent.click(screen.getByRole('button', { name: /filter job type/ }));

        expect(screen.getByRole('option', { name: 'All job types' })).toHaveAttribute('data-key', 'all');
        expect(screen.getByRole('option', { name: 'Train' })).toHaveAttribute('data-key', 'train');
        expect(screen.getByRole('option', { name: 'Test' })).toHaveAttribute('data-key', 'test');
        expect(screen.getByRole('option', { name: 'Optimize' })).toHaveAttribute('data-key', 'optimize');
    });

    it.each([
        {
            filterName: /filter project/,
            filterValue: 'Test project 2',
            changedValues: {
                projectId: '222222',
            },
        },
        {
            filterName: /filter user/,
            filterValue: 'admin3@example.com',
            changedValues: {
                userId: '3',
            },
        },
        {
            filterName: /filter job type/,
            filterValue: 'Optimize',
            changedValues: {
                jobTypes: ['optimize_pot'],
            },
        },
    ])(
        `should trigger onChange event with selected filter `,
        async ({ filterName, filterValue, changedValues }): Promise<void> => {
            const users = [
                mockedUser,
                { ...mockedUser, id: '2', email: 'admin2@example.com', firstName: 'Administrator 2' },
                { ...mockedUser, id: '3', email: 'admin3@example.com', firstName: 'Administrator 3' },
            ];

            await renderComponent(undefined, undefined, undefined, users);

            fireEvent.click(screen.getByRole('button', { name: filterName }));
            fireEvent.click(await screen.findByRole('option', { name: filterValue }));
            const defaultValues = {
                userId: undefined,
                jobTypes: [],
                projectId: undefined,
            };
            const expected = { ...defaultValues, ...changedValues };
            expect(mockOnChange).toHaveBeenNthCalledWith(1, expect.objectContaining(expected));
        }
    );
});
