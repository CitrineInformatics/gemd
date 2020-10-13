from gemd.entity.attribute.base_attribute import BaseAttribute
from gemd.entity.template import PropertyTemplate

from typing import Type


class Property(BaseAttribute):
    """
    Property of a material, measured in a MeasurementRun or specified in a MaterialSpec.

    Properties are characteristics of a material that could be measured, e.g. chemical composition,
     density, yield strength.

    """

    typ = "property"

    @staticmethod
    def _template_type() -> Type:
        return PropertyTemplate
