"""Pydantic models for Yhteentoimivuusalusta data structures."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, HttpUrl


class Language(str, Enum):
    """Supported languages."""

    FI = "fi"
    EN = "en"
    SV = "sv"


class Status(str, Enum):
    """Resource status values."""

    DRAFT = "DRAFT"
    VALID = "VALID"
    DEPRECATED = "DEPRECATED"
    INCOMPLETE = "INCOMPLETE"
    SUGGESTED = "SUGGESTED"


class LocalizedString(BaseModel):
    """Multi-language string."""

    model_config = ConfigDict(extra="ignore")

    fi: str | None = None
    en: str | None = None
    sv: str | None = None

    def get(self, lang: Language | str = Language.FI) -> str | None:
        """Get string in specified language with fallback."""
        lang_str = lang.value if isinstance(lang, Language) else lang
        value = getattr(self, lang_str, None)
        if value:
            return value
        # Fallback order: fi -> en -> sv
        return self.fi or self.en or self.sv


class Term(BaseModel):
    """Represents a term in a vocabulary."""

    model_config = ConfigDict(extra="ignore")

    label: str
    language: Language
    status: str = "PREFERRED"  # PREFERRED, ACCEPTABLE, NOT_RECOMMENDED, etc.
    scope: str | None = None


class Concept(BaseModel):
    """Represents a concept in a vocabulary."""

    model_config = ConfigDict(extra="ignore")

    id: str
    uri: HttpUrl | str
    vocabulary_id: str
    preferred_label: LocalizedString
    definition: LocalizedString | None = None
    terms: list[Term] = []
    status: Status = Status.VALID
    broader: list[str] = []
    narrower: list[str] = []
    related: list[str] = []
    created: datetime | None = None
    modified: datetime | None = None


class Vocabulary(BaseModel):
    """Represents a vocabulary/terminology."""

    model_config = ConfigDict(extra="ignore")

    id: str
    uri: HttpUrl | str
    label: LocalizedString
    description: LocalizedString | None = None
    domain: list[str] = []
    organization: str | None = None
    concept_count: int = 0
    status: Status = Status.VALID
    languages: list[Language] = []


class DataModelProperty(BaseModel):
    """Represents a property in a data model class."""

    model_config = ConfigDict(extra="ignore")

    id: str
    label: LocalizedString
    description: LocalizedString | None = None
    data_type: str | None = None
    min_count: int = 0
    max_count: int | None = None
    vocabulary_reference: str | None = None


class DataModelAssociation(BaseModel):
    """Represents an association between classes."""

    model_config = ConfigDict(extra="ignore")

    id: str
    label: LocalizedString
    target_class: str
    min_count: int = 0
    max_count: int | None = None


class DataModelClass(BaseModel):
    """Represents a class in a data model."""

    model_config = ConfigDict(extra="ignore")

    id: str
    uri: HttpUrl | str
    label: LocalizedString
    description: LocalizedString | None = None
    is_abstract: bool = False
    parent_class: str | None = None
    properties: list[DataModelProperty] = []
    associations: list[DataModelAssociation] = []
    vocabulary_references: list[dict[str, Any]] = []


class DataModel(BaseModel):
    """Represents a data model."""

    model_config = ConfigDict(extra="ignore")

    id: str
    uri: HttpUrl | str
    type: str  # PROFILE or LIBRARY
    status: Status = Status.VALID
    label: LocalizedString
    description: LocalizedString | None = None
    domain: list[str] = []
    version: str | None = None
    classes: list[DataModelClass] = []


class Code(BaseModel):
    """Represents a code in a code list."""

    model_config = ConfigDict(extra="ignore")

    code: str
    uri: HttpUrl | str
    label: LocalizedString
    definition: LocalizedString | None = None
    status: Status = Status.VALID
    broader_code: str | None = None
    order: int | None = None


class CodeScheme(BaseModel):
    """Represents a code list."""

    model_config = ConfigDict(extra="ignore")

    id: str
    registry: str
    uri: HttpUrl | str
    label: LocalizedString
    description: LocalizedString | None = None
    version: str | None = None
    code_count: int = 0
    codes: list[Code] = []
