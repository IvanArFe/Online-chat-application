# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04grpc\"\x07\n\x05\x45mpty\"7\n\x04Note\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x10\n\x08receiver\x18\x03 \x01(\t\",\n\x08UserPair\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x10\n\x08receiver\x18\x02 \x01(\t2]\n\nChatServer\x12*\n\nChatStream\x12\x0e.grpc.UserPair\x1a\n.grpc.Note0\x01\x12#\n\x08SendNote\x12\n.grpc.Note\x1a\x0b.grpc.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_EMPTY']._serialized_start=20
  _globals['_EMPTY']._serialized_end=27
  _globals['_NOTE']._serialized_start=29
  _globals['_NOTE']._serialized_end=84
  _globals['_USERPAIR']._serialized_start=86
  _globals['_USERPAIR']._serialized_end=130
  _globals['_CHATSERVER']._serialized_start=132
  _globals['_CHATSERVER']._serialized_end=225
# @@protoc_insertion_point(module_scope)
