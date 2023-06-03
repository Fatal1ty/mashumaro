from dataclasses import dataclass
from datetime import date

from typing_extensions import Literal

from mashumaro import DataClassDictMixin

DT_STR = "2022-05-30"
DT_DATE = date(2022, 5, 30)

X_STR_1 = {"x": DT_STR, "type": "str_1"}
X_STR_12 = {"x": DT_STR, "type": "str_12"}
X_DATE_12 = {"x": DT_STR, "type": "date_12"}
X_DATE_1 = {"x": DT_STR, "type": "date_1"}
X_STR_21 = {"x": DT_STR, "type": "str_21"}
X_DATE_22 = {"x": DT_STR, "type": "date_22"}


@dataclass
class BaseVariant(DataClassDictMixin):
    pass


@dataclass
class VariantStr1(BaseVariant):
    x: str
    type: Literal["str_1"] = "str_1"


@dataclass
class VariantDate1(BaseVariant):
    x: date
    type: Literal["date_1"] = "date_1"


@dataclass
class VariantStr12(VariantStr1):
    x: str
    type: Literal["str_12"] = "str_12"


@dataclass
class VariantDate12(VariantStr1):
    x: date
    type: Literal["date_12"] = "date_12"


@dataclass
class VariantStr21(VariantDate1):
    x: str
    type: Literal["str_21"] = "str_21"


@dataclass
class VariantDate22(VariantDate1):
    x: date
    type: Literal["date_22"] = "date_22"
