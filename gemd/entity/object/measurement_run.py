from gemd.entity.attribute import Property, Condition, Parameter
from gemd.entity.object.base_object import BaseObject
from gemd.entity.object.has_spec import HasSpec
from gemd.entity.object.has_conditions import HasConditions
from gemd.entity.object.has_properties import HasProperties
from gemd.entity.object.has_parameters import HasParameters
from gemd.entity.object.has_source import HasSource
from gemd.entity.source.performed_source import PerformedSource
from gemd.entity.link_by_uid import LinkByUID
from gemd.entity.file_link import FileLink

from typing import Union, Optional, Type, Collection, Mapping


class MeasurementRun(BaseObject, HasSpec, HasConditions, HasProperties, HasParameters, HasSource):
    """
    A measurement run.

    This contains a link to the material the measurement is performed on, as well as links to
    any properties, conditions, and parameters.

    Parameters
    ----------
    name: str, required
        Name of the measurement run.
    uids: Map[str, str], optional
        A collection of
        `unique IDs <https://citrineinformatics.github.io/gemd-documentation/
        specification/unique-identifiers/>`_.
    tags: List[str], optional
        `Tags <https://citrineinformatics.github.io/gemd-documentation/specification/tags/>`_
        are hierarchical strings that store information about an entity. They can be used
        for filtering and discoverability.
    notes: str, optional
        Long-form notes about the measurement run.
    conditions: List[:class:`Condition <gemd.entity.attribute.condition.Condition>`], optional
        Conditions under which this measurement run occurs.
    parameters: List[:class:`Parameter <gemd.entity.attribute.parameter.Parameter>`], optional
        Parameters of this measurement run.
    properties: List[:class:`Property <gemd.entity.attribute.property.Property>`], optional
        Properties that are measured during this measurement run.
    spec: :class:`MeasurementSpec <gemd.entity.object.measurement_spec.MeasurementSpec>`
        The measurement specification of which this is an instance.
    material: :class:`MaterialRun <gemd.entity.object.material_run.MaterialRun>`
        The material run being measured.
    spec: :class:`MaterialSpec <gemd.entity.object.material_spec.MaterialSpec>`
        The material specification of which this is an instance.
    file_links: List[:class:`FileLink <gemd.entity.file_link.FileLink>`], optional
        Links to associated files, with resource paths into the files API.
    source: :class:`PerformedSource\
    <gemd.entity.source.performed_source.PerformedSource>`, optional
        Information about the person who performed the run and when.

    """

    typ = "measurement_run"

    def __init__(self, name: str, *,
                 spec: Union[BaseObject, LinkByUID, None] = None,
                 material: Union[BaseObject, LinkByUID, None] = None,
                 properties: Optional[Property] = None,
                 conditions: Optional[Condition] = None,
                 parameters: Optional[Parameter] = None,
                 uids: Optional[Mapping[str, str]] = None,
                 tags: Union[Collection[str], str, None] = None,
                 notes: Optional[str] = None,
                 file_links: Optional[Collection[FileLink]] = None,
                 source: Optional[PerformedSource] = None
                 ):
        BaseObject.__init__(self, name=name, uids=uids, tags=tags, notes=notes,
                            file_links=file_links)
        HasSpec.__init__(self, spec)
        HasProperties.__init__(self, properties)
        HasConditions.__init__(self, conditions)
        HasParameters.__init__(self, parameters)
        HasSource.__init__(self, source)

        self._spec = None
        self.spec = spec
        self._material = None
        self.material = material

    @property
    def material(self):
        """Get the material."""
        return self._material

    @material.setter
    def material(self, value):
        from gemd.entity.object import MaterialRun
        from gemd.entity.link_by_uid import LinkByUID
        if isinstance(self._material, MaterialRun):
            # This could throw an exception if it's not in the list, but then something else broke
            self._material.measurements.remove(self)

        if value is None or isinstance(value, (MaterialRun, LinkByUID)):
            self._material = value
            if isinstance(value, MaterialRun):
                value.measurements.append(self)
        else:
            raise TypeError("material must be a MaterialRun or LinkByUID: {}".format(value))

    @staticmethod
    def _spec_type() -> Type:
        """Get the expected type of spec for this object (property of child)."""
        from gemd.entity.object import MeasurementSpec
        return MeasurementSpec
