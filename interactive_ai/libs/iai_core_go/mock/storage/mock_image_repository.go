// Code generated by mockery. DO NOT EDIT.

package storage

import (
	context "context"
	image "image"

	entities "geti.com/iai_core/entities"

	io "io"

	mock "github.com/stretchr/testify/mock"
)

// MockImageRepository is an autogenerated mock type for the ImageRepository type
type MockImageRepository struct {
	mock.Mock
}

type MockImageRepository_Expecter struct {
	mock *mock.Mock
}

func (_m *MockImageRepository) EXPECT() *MockImageRepository_Expecter {
	return &MockImageRepository_Expecter{mock: &_m.Mock}
}

// LoadImageByID provides a mock function with given fields: ctx, imageID
func (_m *MockImageRepository) LoadImageByID(ctx context.Context, imageID *entities.FullImageID) (io.ReadCloser, *entities.ObjectMetadata, error) {
	ret := _m.Called(ctx, imageID)

	if len(ret) == 0 {
		panic("no return value specified for LoadImageByID")
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

// MockImageRepository_LoadImageByID_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'LoadImageByID'
type MockImageRepository_LoadImageByID_Call struct {
	*mock.Call
}

// LoadImageByID is a helper method to define mock.On call
//   - ctx context.Context
//   - imageID *entities.FullImageID
func (_e *MockImageRepository_Expecter) LoadImageByID(ctx interface{}, imageID interface{}) *MockImageRepository_LoadImageByID_Call {
	return &MockImageRepository_LoadImageByID_Call{Call: _e.mock.On("LoadImageByID", ctx, imageID)}
}

func (_c *MockImageRepository_LoadImageByID_Call) Run(run func(ctx context.Context, imageID *entities.FullImageID)) *MockImageRepository_LoadImageByID_Call {
	_c.Call.Run(func(args mock.Arguments) {
		run(args[0].(context.Context), args[1].(*entities.FullImageID))
	})
	return _c
}

func (_c *MockImageRepository_LoadImageByID_Call) Return(_a0 io.ReadCloser, _a1 *entities.ObjectMetadata, _a2 error) *MockImageRepository_LoadImageByID_Call {
	_c.Call.Return(_a0, _a1, _a2)
	return _c
}

func (_c *MockImageRepository_LoadImageByID_Call) RunAndReturn(run func(context.Context, *entities.FullImageID) (io.ReadCloser, *entities.ObjectMetadata, error)) *MockImageRepository_LoadImageByID_Call {
	_c.Call.Return(run)
	return _c
}

// LoadThumbnailByID provides a mock function with given fields: ctx, imageID
func (_m *MockImageRepository) LoadThumbnailByID(ctx context.Context, imageID *entities.FullImageID) (io.ReadCloser, *entities.ObjectMetadata, error) {
	ret := _m.Called(ctx, imageID)

	if len(ret) == 0 {
		panic("no return value specified for LoadThumbnailByID")
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

// MockImageRepository_LoadThumbnailByID_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'LoadThumbnailByID'
type MockImageRepository_LoadThumbnailByID_Call struct {
	*mock.Call
}

// LoadThumbnailByID is a helper method to define mock.On call
//   - ctx context.Context
//   - imageID *entities.FullImageID
func (_e *MockImageRepository_Expecter) LoadThumbnailByID(ctx interface{}, imageID interface{}) *MockImageRepository_LoadThumbnailByID_Call {
	return &MockImageRepository_LoadThumbnailByID_Call{Call: _e.mock.On("LoadThumbnailByID", ctx, imageID)}
}

func (_c *MockImageRepository_LoadThumbnailByID_Call) Run(run func(ctx context.Context, imageID *entities.FullImageID)) *MockImageRepository_LoadThumbnailByID_Call {
	_c.Call.Run(func(args mock.Arguments) {
		run(args[0].(context.Context), args[1].(*entities.FullImageID))
	})
	return _c
}

func (_c *MockImageRepository_LoadThumbnailByID_Call) Return(_a0 io.ReadCloser, _a1 *entities.ObjectMetadata, _a2 error) *MockImageRepository_LoadThumbnailByID_Call {
	_c.Call.Return(_a0, _a1, _a2)
	return _c
}

func (_c *MockImageRepository_LoadThumbnailByID_Call) RunAndReturn(run func(context.Context, *entities.FullImageID) (io.ReadCloser, *entities.ObjectMetadata, error)) *MockImageRepository_LoadThumbnailByID_Call {
	_c.Call.Return(run)
	return _c
}

// SaveThumbnail provides a mock function with given fields: ctx, imageID, thumbnail
func (_m *MockImageRepository) SaveThumbnail(ctx context.Context, imageID *entities.FullImageID, thumbnail image.Image) error {
	ret := _m.Called(ctx, imageID, thumbnail)

	if len(ret) == 0 {
		panic("no return value specified for SaveThumbnail")
	}

	var r0 error
	if rf, ok := ret.Get(0).(func(context.Context, *entities.FullImageID, image.Image) error); ok {
		r0 = rf(ctx, imageID, thumbnail)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// MockImageRepository_SaveThumbnail_Call is a *mock.Call that shadows Run/Return methods with type explicit version for method 'SaveThumbnail'
type MockImageRepository_SaveThumbnail_Call struct {
	*mock.Call
}

// SaveThumbnail is a helper method to define mock.On call
//   - ctx context.Context
//   - imageID *entities.FullImageID
//   - thumbnail image.Image
func (_e *MockImageRepository_Expecter) SaveThumbnail(ctx interface{}, imageID interface{}, thumbnail interface{}) *MockImageRepository_SaveThumbnail_Call {
	return &MockImageRepository_SaveThumbnail_Call{Call: _e.mock.On("SaveThumbnail", ctx, imageID, thumbnail)}
}

func (_c *MockImageRepository_SaveThumbnail_Call) Run(run func(ctx context.Context, imageID *entities.FullImageID, thumbnail image.Image)) *MockImageRepository_SaveThumbnail_Call {
	_c.Call.Run(func(args mock.Arguments) {
		run(args[0].(context.Context), args[1].(*entities.FullImageID), args[2].(image.Image))
	})
	return _c
}

func (_c *MockImageRepository_SaveThumbnail_Call) Return(_a0 error) *MockImageRepository_SaveThumbnail_Call {
	_c.Call.Return(_a0)
	return _c
}

func (_c *MockImageRepository_SaveThumbnail_Call) RunAndReturn(run func(context.Context, *entities.FullImageID, image.Image) error) *MockImageRepository_SaveThumbnail_Call {
	_c.Call.Return(run)
	return _c
}

// NewMockImageRepository creates a new instance of MockImageRepository. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
// The first argument is typically a *testing.T value.
func NewMockImageRepository(t interface {
	mock.TestingT
	Cleanup(func())
}) *MockImageRepository {
	mock := &MockImageRepository{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
