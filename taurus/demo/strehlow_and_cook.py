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

from taurus.entity.bounds.categorical_bounds import CategoricalBounds
from taurus.entity.value.nominal_categorical import NominalCategorical

from taurus.entity.bounds.composition_bounds import CompositionBounds
from taurus.entity.value.empirical_formula import EmpiricalFormula

from taurus.entity.value.normal_real import NormalReal
from taurus.entity.value.nominal_real import NominalReal
from taurus.entity.bounds.real_bounds import RealBounds


# For now, module constant, though likely this should get promoted to a package level
DEMO_SCOPE = 'citrine-demo-sac'


def import_table():
    """Return the deserialized JSON table."""
    import pkg_resources
    import json
    resource = pkg_resources.resource_stream("taurus.demo", "strehlow_and_cook.pif")
    table = json.load(resource)

    return table


def minimal_subset(table):
    """Transform an incoming table into the minimal example that reflects full diversity."""
    seen = set()
    smaller = []
    for row in table:
        mask = ''.join(map(lambda x: str(type(x)), row))
        if mask not in seen:  # this is a novel shape
            smaller.append(row)
            seen.add(mask)

    return smaller


def make_strehlow_objects(table=None):
    """Make a table with Strehlow & Cook data."""
    # Construct templates
    chem_tmpl = PropertyTemplate(
        name="Formula",
        bounds=CompositionBounds(components=EmpiricalFormula.all_elements()),
    )
    cryst_tmpl = PropertyTemplate(
        name="Crystallinity",
        bounds=CategoricalBounds(['Amorphous', 'Polycrystalline', 'Single crystalline']),
    )
    color_tmpl = PropertyTemplate(
        name="Color",
        bounds=CategoricalBounds(
            ['Amber', 'Black', 'Blue', 'Bluish', 'Bronze', 'Brown', 'Brown-Black', 'Copper-Red',
             'Dark Brown', 'Dark Gray', 'Dark Green', 'Dark Red', 'Gray', 'Light Gray', 'Ocher',
             'Orange', 'Orange-Red', 'Pale Yellow', 'Red', 'Red-Yellow', 'Violet', 'White',
             'Yellow', 'Yellow-Orange', 'Yellow-White'
             ]),
    )
    band_tmpl = PropertyTemplate(
        name="Band gap",
        bounds=RealBounds(lower_bound=0, upper_bound=100, default_units='eV'),
    )
    proc_tmpl = ProcessTemplate(name='Sample preparation')

    chem_mat_tmpl = MaterialTemplate(name='Chemical',
                                     properties=[chem_tmpl]
                                     )
    cryst_msr_tmpl = MeasurementTemplate(name='Crystal description',
                                         properties=[cryst_tmpl]
                                         )
    color_msr_tmpl = MeasurementTemplate(name='Color description',
                                         properties=[color_tmpl]
                                         )
    band_msr_tmpl = MeasurementTemplate(name='Band gap measurement',
                                        properties=[band_tmpl]
                                        )

    if table is None:
        table = [["Bi$_{2}$Te$_{3}$", "Bi2Te3", 0.153, None, "Single crystalline", None],
                 ["DyN", "DyN", 2.1, None, None, None],
                 ["InAs", "InAs", 0.404, None, "Single crystalline", "Dark Gray"],
                 ["CaS", "CaS", 6.0, 0.2, "Polycrystalline", None],
                 ["Rb$_{3}$Sb", "Rb3Sb", 1.7, 0.1, None, None],
                 ["CeN", "CeN", 0.7, None, None, "Bronze"],
                 ["BaI", "BaI", None, None, None, None],
                 ["CoF$_{2}$", "CoF2", None, None, "Polycrystalline", None],
                 ["B$_{2}$Se$_{3}$", "B2Se3", None, None, None, "Orange"],
                 ["Mg$_{3}$As$_{2}$", "Mg3As2", 2.55, 0.35, "Polycrystalline", "Brown"],
                 ["Bi$_{0.85}$Sb$_{0.15}$", None, 0.01, None, "Single crystalline", None],
                 ["CoTe$_{1.88}$", None, 0.2, None, None, None]]

    # Specs
    cryst_msr_spec = MeasurementSpec(name='Crystallinity',
                                     template=cryst_msr_tmpl
                                     )

    color_msr_spec = MeasurementSpec(name='Color',
                                     template=color_msr_tmpl
                                     )

    band_msr_spec = MeasurementSpec(name='Band gap',
                                    template=band_msr_tmpl
                                    )

    compounds = []
    for row in table:
        spec = MaterialSpec(name=row['chemicalFormula'],
                            template=chem_mat_tmpl,
                            process=ProcessSpec(name='Literature source',
                                                template=proc_tmpl
                                                )
                            )
        run = make_instance(spec)
        compounds.append(run)

        if '.' not in row['chemicalFormula']:
            spec.properties.append(
                PropertyAndConditions(
                    property=Property(name=chem_tmpl.name,
                                      value=EmpiricalFormula(formula=row['chemicalFormula']),
                                      template=chem_tmpl)
                ))

        for prop in filter(lambda x:'Band gap' == x['name'], row['properties']):
            band_meas = make_instance(band_msr_spec)
            band_meas.material = run
            if 'uncertainty' in prop['scalars'][0]:
                val = NormalReal(mean=float(prop['scalars'][0]['value']),
                                 units=prop['units'],
                                 std=float(prop['scalars'][0]['uncertainty'])
                                 )
            else:
                val = NominalReal(nominal=float(prop['scalars'][0]['value']),
                                  units=prop['units']
                                  )
            band_meas.properties.append(Property(name=cryst_msr_tmpl.name, value=val))

        for prop in filter(lambda x: 'Crystallinity' == x['name'], row['properties']):
            cryst_msr = make_instance(cryst_msr_spec)
            cryst_msr.material = run
            val = NominalCategorical(category=prop['scalars'][0]['value'])
            cryst_msr.properties.append(Property(name=cryst_msr_tmpl.name, value=val))

        for prop in filter(lambda x: 'Color' == x['name'], row['properties']):
            color_msr = make_instance(color_msr_spec)
            color_msr.material = run
            val = NominalCategorical(category=prop['scalars'][0]['value'])
            color_msr.properties.append(Property(name=color_msr_tmpl.name, value=val))

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

    for comp in compounds:
        if len(comp.measurements) == 3:  # Full list
            band_msr = comp.measurements[0].spec
            cryst_msr = comp.measurements[1].spec
            color_msr = comp.measurements[2].spec
            break

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
    output['headers'].append(
        {'name': [chem_mat_tmpl.name,
                  band_msr.name,
                  band_msr.template.properties[0][0].name
                  ],
         'primitive': False,
         'bounds': band_msr.template.properties[0][0].bounds
         }
    )
    output['headers'].append(
        {'name': [chem_mat_tmpl.name,
                  cryst_msr.name,
                  cryst_msr.template.properties[0][0].name
                  ],
         'primitive': False,
         'bounds': cryst_msr.template.properties[0][0].bounds
         }
    )
    output['headers'].append(
        {'name': [chem_mat_tmpl.name,
                  color_msr.name,
                  color_msr.template.properties[0][0].name
                  ],
         'primitive': False,
         'bounds': color_msr.template.properties[0][0].bounds
         }
    )

    for comp in compounds:
        row = [comp.spec.name]
        x = list(filter(lambda y: y.name == chem_tmpl.name, comp.spec.properties))
        if x:
            row.append(x[0].value)
        else:
            row.append(None)

        x = list(filter(lambda y: y.name == band_msr.name, comp.measurements))
        if x:
            row.append(x[0].properties[0].value)
        else:
            row.append(None)

        x = list(filter(lambda y: y.name == cryst_msr.name, comp.measurements))
        if x:
            row.append(x[0].properties[0].value)
        else:
            row.append(None)

        x = list(filter(lambda y: y.name == color_msr.name, comp.measurements))
        if x:
            row.append(x[0].properties[0].value)
        else:
            row.append(None)

        output['content'].append(row)

    return output


if __name__ == "__main__":
    import taurus.client.json_encoder as je
    import json

    # Whether to use the full data set.
    # If `False` a minimal, predefined subset of compounds will be used.
    use_full_table = True

    if use_full_table:
        imported_table = import_table()
    else:
        imported_table = None

    compounds = make_strehlow_objects(imported_table)
    sac_tbl = make_strehlow_table(compounds)

    # Look at each different combination of Value types in a S&C record
    smaller = minimal_subset(sac_tbl['content'])
    for row in smaller:
        print(row[0])
    print('Total number of prototypes: {}'.format(len(smaller)))

    print("\n\nJSON -- Training table")
    print(json.dumps(json.loads(je.dumps(sac_tbl))[1], indent=2))

    print("\n\nCSV -- Display table")
    header = list(map(lambda x: '~'.join(x['name']), sac_tbl['headers']))
    header.insert(2, header[2])
    header[0] += '~Label'
    header[1] += '~Formula'
    header[2] += '~Mean ({})'.format('eV')  # .format(sac_tbl['headers'][2]['bounds'].default_units
    header[3] += '~Std deviation ({})'.format('eV')
    header[4] += '~Category'
    header[5] += '~Category'

    print(','.join(header))

    for comp in sac_tbl['content']:
        row = [comp[0]]

        if comp[1] is None:
            row.append('')
        else:
            row.append(comp[1].formula)

        if comp[2] is None:
            row.extend(['', ''])
        elif isinstance(comp[2], NominalReal):
            row.extend([str(comp[2].nominal), ''])
        else:
            row.extend([str(comp[2].mean), str(comp[2].std)])

        if comp[3] is None:
            row.append('')
        else:
            row.append(comp[3].category)

        if comp[4] is None:
            row.append('')
        else:
            row.append(comp[4].category)

        print(','.join(row))
