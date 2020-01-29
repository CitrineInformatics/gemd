"""Demo representing Strehlow & Cook bandgap data with data concepts."""
from taurus.entity.util import make_instance

from taurus.entity.object.process_spec import ProcessSpec
from taurus.entity.object.material_spec import MaterialSpec
from taurus.entity.object.measurement_spec import MeasurementSpec

from taurus.entity.template.process_template import ProcessTemplate
from taurus.entity.template.material_template import MaterialTemplate
from taurus.entity.template.measurement_template import MeasurementTemplate

from taurus.entity.attribute.property import Property
from taurus.entity.template.property_template import PropertyTemplate
from taurus.entity.attribute.property_and_conditions import PropertyAndConditions
from taurus.entity.attribute.condition import Condition
from taurus.entity.template.condition_template import ConditionTemplate

from taurus.entity.bounds.categorical_bounds import CategoricalBounds
from taurus.entity.value.nominal_categorical import NominalCategorical

from taurus.entity.bounds.composition_bounds import CompositionBounds
from taurus.entity.value.empirical_formula import EmpiricalFormula

from taurus.entity.value.normal_real import NormalReal
from taurus.entity.value.nominal_real import NominalReal
from taurus.entity.value.uniform_real import UniformReal
from taurus.entity.bounds.real_bounds import RealBounds


# For now, module constant, though likely this should get promoted to a package level
DEMO_SCOPE = 'citrine-demo-sac'
FULL_TABLE = "strehlow_and_cook.pif"
SMALL_TABLE = "strehlow_and_cook_small.pif"


def import_table(filename=SMALL_TABLE):
    """Return the deserialized JSON table."""
    import pkg_resources
    import json
    resource = pkg_resources.resource_stream("taurus.demo", filename)
    content = bytearray()
    for line in resource:
        content += line
    table = json.loads(content.decode())

    return table


def _fingerprint(row):
    """Generate a string-based fingerprint to characterize row diversity."""
    return ''.join(map(lambda x: str(type(x)), row))


def minimal_subset(table):
    """Transform an incoming table into the minimal example that reflects full diversity."""
    seen = set()
    smaller = []
    for row in table:
        mask = _fingerprint(row)
        if mask not in seen:  # this is a novel shape
            smaller.append(row)
            seen.add(mask)

    return smaller


def formula_latex(old):
    """Transform a formula into one with LaTeX markup."""
    import re
    return re.sub(r"(?<=[A-Za-z])([\d\.]+)(?=[A-Za-z]|$)", r"$_{\1}$", formula_clean(old))


def formula_clean(old):
    """Transform a formula into a cleaner version."""
    import re
    return re.sub(r"(?<=[A-Za-z])1(?=[A-Za-z]|$)", '', old)


def make_templates():
    """Build all templates needed for the table."""
    tmpl = dict()

    # Attribute Templates
    attribute_feed = {
        "Formula": [PropertyTemplate,
                    CompositionBounds(components=EmpiricalFormula.all_elements())],
        "Crystallinity": [ConditionTemplate,
                          CategoricalBounds(
                              ['Amorphous', 'Polycrystalline', 'Single crystalline']
                          )],
        "Color": [PropertyTemplate,
                  CategoricalBounds(
                      ['Amber', 'Black', 'Blue', 'Bluish', 'Bronze', 'Brown', 'Brown-Black',
                       'Copper-Red', 'Dark Brown', 'Dark Gray', 'Dark Green', 'Dark Red', 'Gray',
                       'Light Gray', 'Ocher', 'Orange', 'Orange-Red', 'Pale Yellow', 'Red',
                       'Red-Yellow', 'Violet', 'White', 'Yellow', 'Yellow-Orange', 'Yellow-White']
                  )],
        "Band gap": [PropertyTemplate,
                     RealBounds(lower_bound=0.001, upper_bound=100, default_units='eV')],
        "Temperature": [ConditionTemplate,
                        RealBounds(lower_bound=1, upper_bound=1000, default_units='K')],
        "Temperature derivative of band gap": [PropertyTemplate,
                                               RealBounds(lower_bound=-0.01, upper_bound=0.01,
                                                          default_units='eV/K')],
        "Lasing": [PropertyTemplate,
                   CategoricalBounds(['True', 'False'])],
        "Cathodoluminescence": [PropertyTemplate,
                                CategoricalBounds(['True', 'False'])],
        "Mechanical luminescence": [PropertyTemplate,
                                    CategoricalBounds(['True', 'False'])],
        "Photoluminescence": [PropertyTemplate,
                              CategoricalBounds(['True', 'False'])],
        "Electroluminescence": [PropertyTemplate,
                                CategoricalBounds(['True', 'False'])],
        "Thermoluminescence": [PropertyTemplate,
                               CategoricalBounds(['True', 'False'])],
        "Morphology": [ConditionTemplate,
                       CategoricalBounds(['Thin Film', 'Bulk'])],
        "Electric field polarization": [ConditionTemplate,
                                        CategoricalBounds(['Parallel to A axis',
                                                           'Parallel to B axis',
                                                           'Parallel to C axis',
                                                           'Perpendicular to B axis',
                                                           'Perpendicular to C axis'])],
        "Phase": [ConditionTemplate,
                  CategoricalBounds(['A', 'B', 'B1', 'B2', 'Cubic', 'Fused quartz', 'Hexagonal',
                                     'Natural diamond', 'Orthorhombic', 'Rutile', 'Sapphire',
                                     'Synthetic quartz', 'Tetragonal', 'Trigonal'])],
        "Transition": [ConditionTemplate,
                       CategoricalBounds(['Direct', 'Excitonic', 'G1 to X1', 'G15 to G1',
                                          'G15 to X1', 'G25 to G1', 'G25 to G12', 'G25 to G15',
                                          'G6 to G8', 'G8 to G6+', 'Indirect', 'L6+ to L6-'])]
    }
    for (name, (typ, bounds)) in attribute_feed.items():
        assert name not in tmpl
        tmpl[name] = typ(name=name,
                         bounds=bounds,
                         uids={DEMO_SCOPE + '-template': name},
                         tags=['citrine::demo::template::attribute']
                         )

    # Object Templates
    object_feed = {
        "Sample preparation": [
            ProcessTemplate,
            dict()
        ],
        "Chemical": [
            MaterialTemplate,
            {"properties": [tmpl["Formula"]]}
        ],
        "Band gap measurement": [
            MeasurementTemplate,
            {"properties": [tmpl["Band gap"],
                            tmpl["Temperature derivative of band gap"],
                            tmpl["Color"],
                            tmpl["Lasing"],
                            tmpl["Cathodoluminescence"],
                            tmpl["Mechanical luminescence"],
                            tmpl["Photoluminescence"],
                            tmpl["Electroluminescence"],
                            tmpl["Thermoluminescence"]
                            ],
             "conditions": [tmpl["Temperature"],
                            tmpl["Crystallinity"],
                            tmpl["Morphology"],
                            tmpl["Electric field polarization"],
                            tmpl["Phase"],
                            tmpl["Transition"]
                            ]
             }
        ],
    }
    for (name, (typ, kw_args)) in object_feed.items():
        assert name not in tmpl
        tmpl[name] = typ(name=name,
                         uids={DEMO_SCOPE + '-template': name},
                         tags=['citrine::demo::template::object'],
                         **kw_args)

    return tmpl


def make_strehlow_objects(table=None):
    """Make a table with Strehlow & Cook data."""
    tmpl = make_templates()

    if table is None:
        table = import_table()

    # Specs
    msr_spec = MeasurementSpec(name='Band gap',
                               template=tmpl["Band gap measurement"]
                               )

    def real_mapper(prop):
        """Mapping methods for RealBounds."""
        if 'uncertainty' in prop['scalars'][0]:
            val = NormalReal(mean=float(prop['scalars'][0]['value']),
                             units=prop['units'],
                             std=float(prop['scalars'][0]['uncertainty'])
                             )
        else:
            val = NominalReal(nominal=float(prop['scalars'][0]['value']),
                              units=prop['units']
                              )
        return val

    content_map = {
        RealBounds: real_mapper,
        CategoricalBounds: lambda prop: NominalCategorical(category=prop['scalars'][0]['value']),
        type(None): lambda bnd: 'Label'
    }

    compounds = []
    for row in table:
        spec = MaterialSpec(name=formula_latex(row['chemicalFormula']),
                            template=tmpl["Chemical"],
                            process=ProcessSpec(name="Sample preparation",
                                                template=tmpl["Sample preparation"]
                                                )
                            )
        run = make_instance(spec)
        compounds.append(run)

        if '.' not in row['chemicalFormula']:
            spec.properties.append(
                PropertyAndConditions(
                    property=Property(name=spec.template.properties[0][0].name,
                                      value=EmpiricalFormula(
                                          formula=formula_clean(row['chemicalFormula'])),
                                      template=spec.template.properties[0][0])
                ))

        msr = make_instance(msr_spec)
        msr.material = run

        for prop in row['properties']:
            template = tmpl[prop['name']]
            if type(template) == PropertyTemplate:
                msr.properties.append(
                    Property(name=template.name,
                             template=template,
                             value=content_map[type(template.bounds)](prop)
                             ))
            elif type(template) == ConditionTemplate:
                msr.conditions.append(
                    Condition(name=template.name,
                              template=template,
                              value=content_map[type(template.bounds)](prop)
                              ))

            for cond in prop.get('conditions', []):
                template = tmpl[cond['name']]
                if type(template) == PropertyTemplate:
                    msr.properties.append(
                        Property(name=template.name,
                                 template=template,
                                 value=content_map[type(template.bounds)](cond)
                                 ))
                elif type(template) == ConditionTemplate:
                    msr.conditions.append(
                        Condition(name=template.name,
                                  template=template,
                                  value=content_map[type(template.bounds)](cond)
                                  ))
    return compounds


def make_strehlow_table(compounds):
    """
    Headers and content for the output of make_strehlow_objects.

    Note that this is supposed to be mimicking the transformation of a set of Material Histories
    into a Training Table, and as such we are missing the column definition component of the query
    that created this particular result set.

    :param compounds: a list of MaterialRun objects from the make_strehlow_objects method
    :return:
    """
    # Stash templates in convenience variables
    for comp in compounds:
        if comp.spec.properties:
            chem_tmpl = comp.spec.properties[0].property.template
            break

    chem_mat_tmpl = compounds[0].spec.template

    tmpl = dict()

    properties = compounds[0].measurements[0].spec.template.properties
    conditions = compounds[0].measurements[0].spec.template.conditions
    parameters = compounds[0].measurements[0].spec.template.parameters
    for attr in (properties + conditions + parameters):
        tmpl[attr[0].name] = attr[0]

    # Consider how to specify relevant data pathing here
    output = {'headers': [], 'content': []}

    # "Chemical" is supposed to be the unifying characterization of all the root elements of the
    # Material Histories, but that can't be the spec name because the spec is Compound specific --
    # that's where the chemical is defined
    output['headers'].append(
        {'name': [chem_mat_tmpl.name,
                  "Display name"  # It would be good to derive this from the structure somehow
                  ],
         'primitive': True
         }
    )
    output['headers'].append(
        {'name': [chem_mat_tmpl.name,
                  chem_tmpl.name
                  ],
         'primitive': False,
         'bounds': CompositionBounds()
         }
    )
    terms = ["Band gap", "Temperature derivative of band gap", "Temperature", "Color",
             "Lasing", "Cathodoluminescence", "Mechanical luminescence", "Photoluminescence",
             "Electroluminescence", "Thermoluminescence", "Transition",
             "Electric field polarization", "Crystallinity", "Morphology", "Phase"]

    for term in terms:
        output['headers'].append(
            {'name': [chem_mat_tmpl.name,
                      term
                      ],
             'primitive': False,
             'bounds': tmpl[term].bounds
             }
        )

    for comp in compounds:
        row = [comp.spec.name]
        x = list(filter(lambda y: y.name == chem_tmpl.name, comp.spec.properties))
        if x:
            row.append(x[0].value)
        else:
            row.append(None)

        for term in terms:
            x = list(filter(lambda y: y.name == term,
                            comp.measurements[0].properties + comp.measurements[0].conditions))
            if x:
                row.append(x[0].value)
            else:
                row.append(None)

        output['content'].append(row)

    return output


def make_display_table(structured):
    """Generate a Display Table from a passed Structured Table."""
    table = [[]]
    header_map = {
        RealBounds: lambda bnd: 'Mean({})'.format(bnd.default_units),
        CategoricalBounds: lambda bnd: 'Category',
        CompositionBounds: lambda bnd: 'Formula',
        type(None): lambda bnd: 'Label'
    }
    for column in structured['headers']:
        bounds = column.get('bounds', None)
        table[0].append('~'.join(column['name'] + [header_map[type(bounds)](bounds)]))

    i_bandgap = list(filter(lambda i: 'Band gap' in table[0][i], range(len(table[0]))))
    assert i_bandgap, "Band gap was not found"
    i_bandgap = i_bandgap[0]
    column = structured['headers'][i_bandgap]
    table[0].insert(
        i_bandgap + 1,
        '~'.join(column['name'] + ['Std Deviation({})'.format(column['bounds'].default_units)])
    )

    content_map = {
        NominalReal: lambda x: x.nominal,
        NormalReal: lambda x: x.mean,
        UniformReal: lambda x: 0.5 * (x.lower_bound + x.upper_bound),
        NominalCategorical: lambda x: x.category,
        EmpiricalFormula: lambda x: x.formula,
        str: lambda x: x,
        type(None): lambda x: ''
    }
    uncert_map = {
        NominalReal: lambda x: '',
        NormalReal: lambda x: x.std,
        UniformReal: lambda x: 0.29 * (x.upper_bound - x.lower_bound),
        type(None): lambda x: ''
    }
    for row in structured['content']:
        table.append([])
        for element in row:
            table[-1].append(content_map[type(element)](element))

        # And insert band gap
        table[-1].insert(i_bandgap + 1, uncert_map[type(row[i_bandgap])](row[i_bandgap]))

    return table


if __name__ == "__main__":
    """
    When run as a script, this will clobber the SMALL_TABLE file with a newly-generated
    minimal subset input table.
    """
    import os.path
    import json

    imported_table = import_table(FULL_TABLE)
    full_compounds = make_strehlow_objects(imported_table)
    full_table = make_strehlow_table(full_compounds)
    small_table = minimal_subset(full_table['content'])
    todo = set(_fingerprint(x) for x in small_table)
    print('Total number of prototypes: {}'.format(len(small_table)))

    reduced_list = []
    for (raw, clean) in zip(imported_table, full_table['content']):
        fp = _fingerprint(clean)
        if fp in todo:
            reduced_list.append(raw)
            todo.remove(fp)
            if not todo:
                break

    with open(os.path.join(os.path.dirname(__file__), SMALL_TABLE), 'w') as f:
        json.dump(reduced_list, f, indent=2)

    print("\n\nJSON -- Training table")
    import taurus.client.json_encoder as je
    print(json.dumps(json.loads(je.dumps(full_table))[1], indent=2))

    print("\n\nCSV -- Display table")
    display = make_display_table(full_table)
    for row in display:
        print(','.join(map(lambda x: str(x), row)))
