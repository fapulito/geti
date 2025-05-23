// Code generated by mockery. DO NOT EDIT.

package usecase

import (
	context "context"
	io "io"

	entities "geti.com/iai_core/entities"

	mock "github.com/stretchr/testify/mock"
)

// MockIGetOrCreateThumbnail is an autogenerated mock type for the IGetOrCreateThumbnail type
type MockIGetOrCreateThumbnail struct {
	mock.Mock
}

type MockIGetOrCreateThumbnail_Expecter struct {
	mock *mock.Mock
}

func (_m *MockIGetOrCreateThumbnail) EXPECT() *MockIGetOrCreateThumbnail_Expecter {
	return &MockIGetOrCreateThumbnail_Expecter{mock: &_m.Mock}
}

// Execute provides a mock function with given fields: ctx, imageID
func (_m *MockIGetOrCreateThumbnail) Execute(ctx context.Context, imageID *entities.FullImageID) (io.ReadCloser, *entities.ObjectMetadata, error) {
	ret := _m.Called(ctx, imageID)

	if len(ret) == 0 {
		panic("no return value specified for Execute")
	}

	var r0 io.ReadCloser
	var r1 *entities.ObjectMetadata
	var r2 error
	if rf, ok := ret.Get(0).(func(context.Context, *entities.FullImageID) (io.ReadCloser, *entities.ObjectMetadata, error)); ok {
		return rf(ctx, imageID)
	}
	if rf, ok := ret.Get(0).(func(context.Context, *entities.FullImageID) io.ReadCloser); ok {
		r0 = rf(ctx, imageID)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).(io.ReadCloser)
		}
	}

	if rf, ok := ret.Get(1).(func(context.Context, *entities.FullImageID) *entities.ObjectMetadata); ok {
		r1 = rf(ctx, imageID)
	} else {
		if ret.Get(1) != nil {
			r1 = ret.Get(1).(*entities.ObjectMetadata)
		}
	}

	if rf, ok := ret.Get(2).(func(context.Context, *entities.FullImageID) error); ok {
		r2 = rf(ctx, imageID)
	} else {
		r2 = ret.Error(2)
	}

	return r0, r1, r2
}

// MockIGetOrCreateThumbnail_Execute_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'Execute'
type MockIGetOrCreateThumbnail_Execute_Call struct {
	*mock.Call
}

// Execute is a helper method to define mock.On call
//   - ctx context.Context
//   - imageID *entities.FullImageID
func (_e *MockIGetOrCreateThumbnail_Expecter) Execute(ctx interface{}, imageID interface{}) *MockIGetOrCreateThumbnail_Execute_Call {
	return &MockIGetOrCreateThumbnail_Execute_Call{Call: _e.mock.On("Execute", ctx, imageID)}
}

func (_c *MockIGetOrCreateThumbnail_Execute_Call) Run(run func(ctx context.Context, imageID *entities.FullImageID)) *MockIGetOrCreateThumbnail_Execute_Call {
	_c.Call.Run(func(args mock.Arguments) {
		run(args[0].(context.Context), args[1].(*entities.FullImageID))
	})
	return _c
}

func (_c *MockIGetOrCreateThumbnail_Execute_Call) Return(_a0 io.ReadCloser, _a1 *entities.ObjectMetadata, _a2 error) *MockIGetOrCreateThumbnail_Execute_Call {
	_c.Call.Return(_a0, _a1, _a2)
	return _c
}

func (_c *MockIGetOrCreateThumbnail_Execute_Call) RunAndReturn(run func(context.Context, *entities.FullImageID) (io.ReadCloser, *entities.ObjectMetadata, error)) *MockIGetOrCreateThumbnail_Execute_Call {
	_c.Call.Return(run)
	return _c
}

// NewMockIGetOrCreateThumbnail creates a new instance of MockIGetOrCreateThumbnail. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
// The first argument is typically a *testing.T value.
func NewMockIGetOrCreateThumbnail(t interface {
	mock.TestingT
	Cleanup(func())
}) *MockIGetOrCreateThumbnail {
	mock := &MockIGetOrCreateThumbnail{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
