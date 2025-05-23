// Copyright (C) 2022-2025 Intel Corporation
// LIMITED EDGE SOFTWARE DISTRIBUTION LICENSE

// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.36.6
// 	protoc        v3.12.4
// source: user_common.proto

package pb

import (
	timestamp "github.com/golang/protobuf/ptypes/timestamp"
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
	unsafe "unsafe"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type UserData struct {
	state                  protoimpl.MessageState `protogen:"open.v1"`
	Id                     string                 `protobuf:"bytes,1,opt,name=id,proto3" json:"id,omitempty"`
	FirstName              string                 `protobuf:"bytes,2,opt,name=first_name,json=firstName,proto3" json:"first_name,omitempty"`
	SecondName             string                 `protobuf:"bytes,3,opt,name=second_name,json=secondName,proto3" json:"second_name,omitempty"`
	Email                  string                 `protobuf:"bytes,4,opt,name=email,proto3" json:"email,omitempty"`
	ExternalId             string                 `protobuf:"bytes,5,opt,name=external_id,json=externalId,proto3" json:"external_id,omitempty"`
	Country                string                 `protobuf:"bytes,6,opt,name=country,proto3" json:"country,omitempty"`
	Status                 string                 `protobuf:"bytes,7,opt,name=status,proto3" json:"status,omitempty"`
	OrganizationId         string                 `protobuf:"bytes,8,opt,name=organization_id,json=organizationId,proto3" json:"organization_id,omitempty"`
	OrganizationStatus     string                 `protobuf:"bytes,9,opt,name=organization_status,json=organizationStatus,proto3" json:"organization_status,omitempty"`
	Roles                  []*UserRole            `protobuf:"bytes,10,rep,name=roles,proto3" json:"roles,omitempty"`
	LastSuccessfulLogin    *timestamp.Timestamp   `protobuf:"bytes,11,opt,name=last_successful_login,json=lastSuccessfulLogin,proto3" json:"last_successful_login,omitempty"`
	CurrentSuccessfulLogin *timestamp.Timestamp   `protobuf:"bytes,12,opt,name=current_successful_login,json=currentSuccessfulLogin,proto3" json:"current_successful_login,omitempty"`
	CreatedAt              *timestamp.Timestamp   `protobuf:"bytes,13,opt,name=created_at,json=createdAt,proto3" json:"created_at,omitempty"`
	CreatedBy              string                 `protobuf:"bytes,14,opt,name=created_by,json=createdBy,proto3" json:"created_by,omitempty"`
	ModifiedAt             *timestamp.Timestamp   `protobuf:"bytes,15,opt,name=modified_at,json=modifiedAt,proto3" json:"modified_at,omitempty"`
	ModifiedBy             string                 `protobuf:"bytes,16,opt,name=modified_by,json=modifiedBy,proto3" json:"modified_by,omitempty"`
	TelemetryConsent       *string                `protobuf:"bytes,17,opt,name=telemetry_consent,json=telemetryConsent,proto3,oneof" json:"telemetry_consent,omitempty"`
	TelemetryConsentAt     *timestamp.Timestamp   `protobuf:"bytes,18,opt,name=telemetry_consent_at,json=telemetryConsentAt,proto3" json:"telemetry_consent_at,omitempty"`
	UserConsent            *string                `protobuf:"bytes,19,opt,name=user_consent,json=userConsent,proto3,oneof" json:"user_consent,omitempty"`
	UserConsentAt          *timestamp.Timestamp   `protobuf:"bytes,20,opt,name=user_consent_at,json=userConsentAt,proto3" json:"user_consent_at,omitempty"`
	PresignedUrl           string                 `protobuf:"bytes,21,opt,name=presigned_url,json=presignedUrl,proto3" json:"presigned_url,omitempty"`
	LastLogoutDate         *timestamp.Timestamp   `protobuf:"bytes,22,opt,name=last_logout_date,json=lastLogoutDate,proto3" json:"last_logout_date,omitempty"`
	unknownFields          protoimpl.UnknownFields
	sizeCache              protoimpl.SizeCache
}

func (x *UserData) Reset() {
	*x = UserData{}
	mi := &file_user_common_proto_msgTypes[0]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *UserData) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*UserData) ProtoMessage() {}

func (x *UserData) ProtoReflect() protoreflect.Message {
	mi := &file_user_common_proto_msgTypes[0]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use UserData.ProtoReflect.Descriptor instead.
func (*UserData) Descriptor() ([]byte, []int) {
	return file_user_common_proto_rawDescGZIP(), []int{0}
}

func (x *UserData) GetId() string {
	if x != nil {
		return x.Id
	}
	return ""
}

func (x *UserData) GetFirstName() string {
	if x != nil {
		return x.FirstName
	}
	return ""
}

func (x *UserData) GetSecondName() string {
	if x != nil {
		return x.SecondName
	}
	return ""
}

func (x *UserData) GetEmail() string {
	if x != nil {
		return x.Email
	}
	return ""
}

func (x *UserData) GetExternalId() string {
	if x != nil {
		return x.ExternalId
	}
	return ""
}

func (x *UserData) GetCountry() string {
	if x != nil {
		return x.Country
	}
	return ""
}

func (x *UserData) GetStatus() string {
	if x != nil {
		return x.Status
	}
	return ""
}

func (x *UserData) GetOrganizationId() string {
	if x != nil {
		return x.OrganizationId
	}
	return ""
}

func (x *UserData) GetOrganizationStatus() string {
	if x != nil {
		return x.OrganizationStatus
	}
	return ""
}

func (x *UserData) GetRoles() []*UserRole {
	if x != nil {
		return x.Roles
	}
	return nil
}

func (x *UserData) GetLastSuccessfulLogin() *timestamp.Timestamp {
	if x != nil {
		return x.LastSuccessfulLogin
	}
	return nil
}

func (x *UserData) GetCurrentSuccessfulLogin() *timestamp.Timestamp {
	if x != nil {
		return x.CurrentSuccessfulLogin
	}
	return nil
}

func (x *UserData) GetCreatedAt() *timestamp.Timestamp {
	if x != nil {
		return x.CreatedAt
	}
	return nil
}

func (x *UserData) GetCreatedBy() string {
	if x != nil {
		return x.CreatedBy
	}
	return ""
}

func (x *UserData) GetModifiedAt() *timestamp.Timestamp {
	if x != nil {
		return x.ModifiedAt
	}
	return nil
}

func (x *UserData) GetModifiedBy() string {
	if x != nil {
		return x.ModifiedBy
	}
	return ""
}

func (x *UserData) GetTelemetryConsent() string {
	if x != nil && x.TelemetryConsent != nil {
		return *x.TelemetryConsent
	}
	return ""
}

func (x *UserData) GetTelemetryConsentAt() *timestamp.Timestamp {
	if x != nil {
		return x.TelemetryConsentAt
	}
	return nil
}

func (x *UserData) GetUserConsent() string {
	if x != nil && x.UserConsent != nil {
		return *x.UserConsent
	}
	return ""
}

func (x *UserData) GetUserConsentAt() *timestamp.Timestamp {
	if x != nil {
		return x.UserConsentAt
	}
	return nil
}

func (x *UserData) GetPresignedUrl() string {
	if x != nil {
		return x.PresignedUrl
	}
	return ""
}

func (x *UserData) GetLastLogoutDate() *timestamp.Timestamp {
	if x != nil {
		return x.LastLogoutDate
	}
	return nil
}

type UserRole struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Role          string                 `protobuf:"bytes,1,opt,name=role,proto3" json:"role,omitempty"`
	ResourceType  string                 `protobuf:"bytes,2,opt,name=resource_type,json=resourceType,proto3" json:"resource_type,omitempty"`
	ResourceId    string                 `protobuf:"bytes,3,opt,name=resource_id,json=resourceId,proto3" json:"resource_id,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *UserRole) Reset() {
	*x = UserRole{}
	mi := &file_user_common_proto_msgTypes[1]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *UserRole) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*UserRole) ProtoMessage() {}

func (x *UserRole) ProtoReflect() protoreflect.Message {
	mi := &file_user_common_proto_msgTypes[1]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use UserRole.ProtoReflect.Descriptor instead.
func (*UserRole) Descriptor() ([]byte, []int) {
	return file_user_common_proto_rawDescGZIP(), []int{1}
}

func (x *UserRole) GetRole() string {
	if x != nil {
		return x.Role
	}
	return ""
}

func (x *UserRole) GetResourceType() string {
	if x != nil {
		return x.ResourceType
	}
	return ""
}

func (x *UserRole) GetResourceId() string {
	if x != nil {
		return x.ResourceId
	}
	return ""
}

type UserRoleOperation struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Role          *UserRole              `protobuf:"bytes,1,opt,name=role,proto3" json:"role,omitempty"`
	Operation     string                 `protobuf:"bytes,2,opt,name=operation,proto3" json:"operation,omitempty"` // CREATE, DELETE, TOUCH
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *UserRoleOperation) Reset() {
	*x = UserRoleOperation{}
	mi := &file_user_common_proto_msgTypes[2]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *UserRoleOperation) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*UserRoleOperation) ProtoMessage() {}

func (x *UserRoleOperation) ProtoReflect() protoreflect.Message {
	mi := &file_user_common_proto_msgTypes[2]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use UserRoleOperation.ProtoReflect.Descriptor instead.
func (*UserRoleOperation) Descriptor() ([]byte, []int) {
	return file_user_common_proto_rawDescGZIP(), []int{2}
}

func (x *UserRoleOperation) GetRole() *UserRole {
	if x != nil {
		return x.Role
	}
	return nil
}

func (x *UserRoleOperation) GetOperation() string {
	if x != nil {
		return x.Operation
	}
	return ""
}

type UserInvitationRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	User          *UserData              `protobuf:"bytes,1,opt,name=user,proto3" json:"user,omitempty"`
	Roles         []*UserRoleOperation   `protobuf:"bytes,2,rep,name=roles,proto3" json:"roles,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *UserInvitationRequest) Reset() {
	*x = UserInvitationRequest{}
	mi := &file_user_common_proto_msgTypes[3]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *UserInvitationRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*UserInvitationRequest) ProtoMessage() {}

func (x *UserInvitationRequest) ProtoReflect() protoreflect.Message {
	mi := &file_user_common_proto_msgTypes[3]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use UserInvitationRequest.ProtoReflect.Descriptor instead.
func (*UserInvitationRequest) Descriptor() ([]byte, []int) {
	return file_user_common_proto_rawDescGZIP(), []int{3}
}

func (x *UserInvitationRequest) GetUser() *UserData {
	if x != nil {
		return x.User
	}
	return nil
}

func (x *UserInvitationRequest) GetRoles() []*UserRoleOperation {
	if x != nil {
		return x.Roles
	}
	return nil
}

var File_user_common_proto protoreflect.FileDescriptor

const file_user_common_proto_rawDesc = "" +
	"\n" +
	"\x11user_common.proto\x12\vuser_common\x1a\x1fgoogle/protobuf/timestamp.proto\"\xa6\b\n" +
	"\bUserData\x12\x0e\n" +
	"\x02id\x18\x01 \x01(\tR\x02id\x12\x1d\n" +
	"\n" +
	"first_name\x18\x02 \x01(\tR\tfirstName\x12\x1f\n" +
	"\vsecond_name\x18\x03 \x01(\tR\n" +
	"secondName\x12\x14\n" +
	"\x05email\x18\x04 \x01(\tR\x05email\x12\x1f\n" +
	"\vexternal_id\x18\x05 \x01(\tR\n" +
	"externalId\x12\x18\n" +
	"\acountry\x18\x06 \x01(\tR\acountry\x12\x16\n" +
	"\x06status\x18\a \x01(\tR\x06status\x12'\n" +
	"\x0forganization_id\x18\b \x01(\tR\x0eorganizationId\x12/\n" +
	"\x13organization_status\x18\t \x01(\tR\x12organizationStatus\x12+\n" +
	"\x05roles\x18\n" +
	" \x03(\v2\x15.user_common.UserRoleR\x05roles\x12N\n" +
	"\x15last_successful_login\x18\v \x01(\v2\x1a.google.protobuf.TimestampR\x13lastSuccessfulLogin\x12T\n" +
	"\x18current_successful_login\x18\f \x01(\v2\x1a.google.protobuf.TimestampR\x16currentSuccessfulLogin\x129\n" +
	"\n" +
	"created_at\x18\r \x01(\v2\x1a.google.protobuf.TimestampR\tcreatedAt\x12\x1d\n" +
	"\n" +
	"created_by\x18\x0e \x01(\tR\tcreatedBy\x12;\n" +
	"\vmodified_at\x18\x0f \x01(\v2\x1a.google.protobuf.TimestampR\n" +
	"modifiedAt\x12\x1f\n" +
	"\vmodified_by\x18\x10 \x01(\tR\n" +
	"modifiedBy\x120\n" +
	"\x11telemetry_consent\x18\x11 \x01(\tH\x00R\x10telemetryConsent\x88\x01\x01\x12L\n" +
	"\x14telemetry_consent_at\x18\x12 \x01(\v2\x1a.google.protobuf.TimestampR\x12telemetryConsentAt\x12&\n" +
	"\fuser_consent\x18\x13 \x01(\tH\x01R\vuserConsent\x88\x01\x01\x12B\n" +
	"\x0fuser_consent_at\x18\x14 \x01(\v2\x1a.google.protobuf.TimestampR\ruserConsentAt\x12#\n" +
	"\rpresigned_url\x18\x15 \x01(\tR\fpresignedUrl\x12D\n" +
	"\x10last_logout_date\x18\x16 \x01(\v2\x1a.google.protobuf.TimestampR\x0elastLogoutDateB\x14\n" +
	"\x12_telemetry_consentB\x0f\n" +
	"\r_user_consent\"d\n" +
	"\bUserRole\x12\x12\n" +
	"\x04role\x18\x01 \x01(\tR\x04role\x12#\n" +
	"\rresource_type\x18\x02 \x01(\tR\fresourceType\x12\x1f\n" +
	"\vresource_id\x18\x03 \x01(\tR\n" +
	"resourceId\"\\\n" +
	"\x11UserRoleOperation\x12)\n" +
	"\x04role\x18\x01 \x01(\v2\x15.user_common.UserRoleR\x04role\x12\x1c\n" +
	"\toperation\x18\x02 \x01(\tR\toperation\"x\n" +
	"\x15UserInvitationRequest\x12)\n" +
	"\x04user\x18\x01 \x01(\v2\x15.user_common.UserDataR\x04user\x124\n" +
	"\x05roles\x18\x02 \x03(\v2\x1e.user_common.UserRoleOperationR\x05rolesB\"Z geti.com/account_service_grpc/pbb\x06proto3"

var (
	file_user_common_proto_rawDescOnce sync.Once
	file_user_common_proto_rawDescData []byte
)

func file_user_common_proto_rawDescGZIP() []byte {
	file_user_common_proto_rawDescOnce.Do(func() {
		file_user_common_proto_rawDescData = protoimpl.X.CompressGZIP(unsafe.Slice(unsafe.StringData(file_user_common_proto_rawDesc), len(file_user_common_proto_rawDesc)))
	})
	return file_user_common_proto_rawDescData
}

var file_user_common_proto_msgTypes = make([]protoimpl.MessageInfo, 4)
var file_user_common_proto_goTypes = []any{
	(*UserData)(nil),              // 0: user_common.UserData
	(*UserRole)(nil),              // 1: user_common.UserRole
	(*UserRoleOperation)(nil),     // 2: user_common.UserRoleOperation
	(*UserInvitationRequest)(nil), // 3: user_common.UserInvitationRequest
	(*timestamp.Timestamp)(nil),   // 4: google.protobuf.Timestamp
}
var file_user_common_proto_depIdxs = []int32{
	1,  // 0: user_common.UserData.roles:type_name -> user_common.UserRole
	4,  // 1: user_common.UserData.last_successful_login:type_name -> google.protobuf.Timestamp
	4,  // 2: user_common.UserData.current_successful_login:type_name -> google.protobuf.Timestamp
	4,  // 3: user_common.UserData.created_at:type_name -> google.protobuf.Timestamp
	4,  // 4: user_common.UserData.modified_at:type_name -> google.protobuf.Timestamp
	4,  // 5: user_common.UserData.telemetry_consent_at:type_name -> google.protobuf.Timestamp
	4,  // 6: user_common.UserData.user_consent_at:type_name -> google.protobuf.Timestamp
	4,  // 7: user_common.UserData.last_logout_date:type_name -> google.protobuf.Timestamp
	1,  // 8: user_common.UserRoleOperation.role:type_name -> user_common.UserRole
	0,  // 9: user_common.UserInvitationRequest.user:type_name -> user_common.UserData
	2,  // 10: user_common.UserInvitationRequest.roles:type_name -> user_common.UserRoleOperation
	11, // [11:11] is the sub-list for method output_type
	11, // [11:11] is the sub-list for method input_type
	11, // [11:11] is the sub-list for extension type_name
	11, // [11:11] is the sub-list for extension extendee
	0,  // [0:11] is the sub-list for field type_name
}

func init() { file_user_common_proto_init() }
func file_user_common_proto_init() {
	if File_user_common_proto != nil {
		return
	}
	file_user_common_proto_msgTypes[0].OneofWrappers = []any{}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: unsafe.Slice(unsafe.StringData(file_user_common_proto_rawDesc), len(file_user_common_proto_rawDesc)),
			NumEnums:      0,
			NumMessages:   4,
			NumExtensions: 0,
			NumServices:   0,
		},
		GoTypes:           file_user_common_proto_goTypes,
		DependencyIndexes: file_user_common_proto_depIdxs,
		MessageInfos:      file_user_common_proto_msgTypes,
	}.Build()
	File_user_common_proto = out.File
	file_user_common_proto_goTypes = nil
	file_user_common_proto_depIdxs = nil
}
