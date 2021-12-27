"""For entities that have properties."""
from gemd.entity.attribute.property import Property
from gemd.entity.setters import validate_list


class HasProperties(object):
    """Mixin-trait for entities that include properties.

    Parameters
    ----------
    properties: List[:class:`Property <gemd.entity.attribute.property.Property>`]
        A list of properties associated with this entity

    """

    def __init__(self, properties):
        self._properties = None
        self.properties = properties

    @property
    def properties(self):
        """Get a list of the properties."""
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Set the list of properties."""
        self._properties = validate_list(properties, Property)

    def all_dependencies(self):
        """Return a set of all immediate dependencies (no recursion)."""
        return {prop.template for prop in self.properties if prop.template is not None}
