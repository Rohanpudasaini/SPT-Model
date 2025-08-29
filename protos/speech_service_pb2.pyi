from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TranscribeAudioRequest(_message.Message):
    __slots__ = ("audio_data", "language", "sample_rate")
    AUDIO_DATA_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    audio_data: bytes
    language: str
    sample_rate: int
    def __init__(self, audio_data: _Optional[bytes] = ..., language: _Optional[str] = ..., sample_rate: _Optional[int] = ...) -> None: ...

class TranscribeAudioResponse(_message.Message):
    __slots__ = ("transcription", "success", "error_message")
    TRANSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    transcription: str
    success: bool
    error_message: str
    def __init__(self, transcription: _Optional[str] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class MergeTranscriptionsRequest(_message.Message):
    __slots__ = ("transcriptions", "language")
    TRANSCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    transcriptions: _containers.RepeatedScalarFieldContainer[str]
    language: str
    def __init__(self, transcriptions: _Optional[_Iterable[str]] = ..., language: _Optional[str] = ...) -> None: ...

class MergeTranscriptionsResponse(_message.Message):
    __slots__ = ("merged_text", "success", "error_message")
    MERGED_TEXT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    merged_text: str
    success: bool
    error_message: str
    def __init__(self, merged_text: _Optional[str] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class ProcessIntentRequest(_message.Message):
    __slots__ = ("text", "confidence_threshold")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    text: str
    confidence_threshold: float
    def __init__(self, text: _Optional[str] = ..., confidence_threshold: _Optional[float] = ...) -> None: ...

class ProcessIntentResponse(_message.Message):
    __slots__ = ("action", "message", "form_data", "entities", "confidence", "success", "error_message")
    class FormDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    action: str
    message: str
    form_data: _containers.ScalarMap[str, str]
    entities: _containers.RepeatedCompositeFieldContainer[Entity]
    confidence: float
    success: bool
    error_message: str
    def __init__(self, action: _Optional[str] = ..., message: _Optional[str] = ..., form_data: _Optional[_Mapping[str, str]] = ..., entities: _Optional[_Iterable[_Union[Entity, _Mapping]]] = ..., confidence: _Optional[float] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class Entity(_message.Message):
    __slots__ = ("entity", "value", "confidence", "start", "end")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    entity: str
    value: str
    confidence: float
    start: int
    end: int
    def __init__(self, entity: _Optional[str] = ..., value: _Optional[str] = ..., confidence: _Optional[float] = ..., start: _Optional[int] = ..., end: _Optional[int] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("healthy", "status", "version", "loaded_models")
    HEALTHY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    LOADED_MODELS_FIELD_NUMBER: _ClassVar[int]
    healthy: bool
    status: str
    version: str
    loaded_models: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, healthy: bool = ..., status: _Optional[str] = ..., version: _Optional[str] = ..., loaded_models: _Optional[_Iterable[str]] = ...) -> None: ...
