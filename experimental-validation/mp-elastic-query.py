# query materials project for all structures with our space groups and compositions
from mp_api.client import MPRester

mp_ids = ["mp-7088", "mp-10196", "mp-1217106", "mp-1224388", "mp-1220515", "mp-2318", "mp-1220726", "mp-1221488", "mp-1221498", "mp-1221473", "mp-1221525", "mp-1216471", "mp-1008632", "mp-1216472", "mp-1008625", "mp-29941", "mp-1226378", "mp-1221793"]

with MPRester() as mpr:
    data = mpr.elasticity.search(material_ids=mp_ids)
    for d in data:
        print(d.formula_pretty)
        print(d.shear_modulus)
        print(d.bulk_modulus)
        print(d.debye_temperature)

        

        doc = mpr.materials.summary.search(material_ids=[d.material_id])
        print(doc[0].energy_above_hull)

        print("\n")

