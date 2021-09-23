"""A unique id that stands in for a data object."""
import uuid
from warnings import warn

from gemd.entity.dict_serializable import DictSerializable


class LinkByUID(DictSerializable):
    """
    Link object, which replaces pointers to other entities before serialization and writing.

    Parameters
    ----------
    scope: str
        The scope of the unique identifier. Scopes are case-insensitive.
    id: str
        The unique identifier.

    """

    typ = "link_by_uid"

    def __init__(self, scope, id):
        # TODO: parse to make sure it's valid
        self.scope = scope
        self.id = id

    def __repr__(self):
        return str({"scope": self.scope, "id": self.id})

    @classmethod
    def from_entity(cls, entity, name=None, *, scope=None):
        """
        Create LinkByUID from in-memory object.

        - If there exists an id with scope (default 'auto'), the LinkByUID object will be built
          with that scope.
        - If there is no id with scope, an arbitrary scope-id pair will be chosen.
        - If the object has no uids, the object will be mutated to include a uid (UUID4) with the
          chosen scope and the LinkByUID object will be built with that scope and id.

        Parameters
        ----------
        entity: BaseEntity
            The entity to substitute with a LinkByUID
        name: str, optional (Deprecated)
            The desired scope of the id.
        scope: str, optional
            The desired scope of the id.

        Returns
        -------
        LinkByUID
            A link object that references `entity` through its scope and id.

        """
        if name is None:
            if scope is None:
                scope = "auto"  # set default
        elif scope is None:
            warn("The positional argument 'name' is deprecated.  When selecting a default scope, "
                 "use the 'scope' keyword argument.", DeprecationWarning)
            scope = name
        else:
            if scope is not None:
                raise ValueError("Specify the 'name' parameter or 'scope' parameter, not both.")

        if scope in entity.uids:
            uid = entity.uids[scope]
        else:
            if not entity.uids:
                entity.add_uid(scope, str(uuid.uuid4()))
            scope, uid = next((s, i) for s, i in entity.uids.items())
        return LinkByUID(scope, uid)
