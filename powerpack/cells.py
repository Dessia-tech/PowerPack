"""
Cells catalog
"""
import numpy as npy
from powerpack.electrical import Evolution, CombinationEvolution,\
                                 SpecsEvolution, CombinationSpecsEvolution,\
                                 Cell, CellRC, Cell2RC

# =============================================================================
# Cell
# =============================================================================
sample = npy.linspace(0, 1, 100)
evol_soc = Evolution(evolution=list(sample), name='evol_soc')
evol_ocv25deg_charge = Evolution(evolution=[(0.97 + 3.1*soc) for soc in sample],
                                 name='evol_ocv25deg_charge')
evol_ocv25deg_discharge = Evolution(evolution=[(1.3 + 3.9*soc) for soc in sample],
                                    name='evol_ocv25deg_discharge')
evol_ocv40deg_charge = Evolution(evolution=[(0.85 + 3.6*soc) for soc in sample],
                                 name='evol_ocv40deg_charge')
evol_ocv40deg_discharge = Evolution(evolution=[(1.3 + 3.2*soc) for soc in sample],
                                    name='evol_ocv40deg_discharge')

ce_ocv25deg_charge = CombinationEvolution(evolution1=[evol_soc],
                                          evolution2=[evol_ocv25deg_charge],
                                          name='ce_ocv25deg_charge',
                                          title1='Soc',
                                          title2='OCV')
ce_ocv25deg_discharge = CombinationEvolution(evolution1=[evol_soc],
                                             evolution2=[evol_ocv25deg_discharge],
                                             name='ce_ocv25deg_discharge',
                                             title1='Soc',
                                             title2='OCV')
ce_ocv40deg_charge = CombinationEvolution(evolution1=[evol_soc],
                                          evolution2=[evol_ocv40deg_charge],
                                          name='ce_ocv40deg_charge',
                                          title1='Soc',
                                          title2='OCV')
ce_ocv40deg_discharge = CombinationEvolution(evolution1=[evol_soc],
                                             evolution2=[evol_ocv40deg_discharge],
                                             name='ce_ocv40deg_discharge',
                                             title1='Soc',
                                             title2='OCV')
se_ocv25deg = SpecsEvolution(temperature=298.15,
                             charge=ce_ocv25deg_charge,
                             discharge=ce_ocv25deg_discharge,
                             name='se_ocv25deg',
                             title='OCV')
se_ocv40deg = SpecsEvolution(temperature=313.15,
                             charge=ce_ocv40deg_charge,
                             discharge=ce_ocv40deg_discharge,
                             name='se_ocv40deg',
                             title='OCV')
cse_ocv = CombinationSpecsEvolution(specs_evolutions=[se_ocv25deg, se_ocv40deg],
                                    name='cse_ocv',
                                    title='OCV')

evol_rint25deg_charge = Evolution(evolution=[(0.006*(soc**(2)) - 0.007*soc + 0.005)\
                                             for soc in sample],
                                  name='evol_rint25deg_charge')
evol_rint25deg_discharge = Evolution(evolution=[(0.002*(max(0.001, soc)**(-0.6)))\
                                                for soc in sample],
                                     name='evol_rint25deg_discharge')
evol_rint40deg_charge = Evolution(evolution=[(0.004*(soc**(2)) - 0.005*soc + 0.004)\
                                             for soc in sample],
                                  name='evol_rint40deg_charge')
evol_rint40deg_discharge = Evolution(evolution=[(0.002*(max(0.001, soc)**(-0.2)))\
                                                for soc in sample],
                                     name='evol_rint40deg_discharge')

ce_rint25deg_charge = CombinationEvolution(evolution1=[evol_soc],
                                           evolution2=[evol_rint25deg_charge],
                                           name='ce_rint25deg_charge',
                                           title1='Soc',
                                           title2='Rint')
ce_rint25deg_discharge = CombinationEvolution(evolution1=[evol_soc],
                                              evolution2=[evol_rint25deg_discharge],
                                              name='ce_rint25deg_discharge',
                                              title1='Soc',
                                              title2='Rint')
ce_rint40deg_charge = CombinationEvolution(evolution1=[evol_soc],
                                           evolution2=[evol_rint40deg_charge],
                                           name='ce_rint40deg_charge',
                                           title1='Soc',
                                           title2='Rint')
ce_rint40deg_discharge = CombinationEvolution(evolution1=[evol_soc],
                                              evolution2=[evol_rint40deg_discharge],
                                              name='ce_rint40deg_discharge',
                                              title1='Soc',
                                              title2='Rint')
se_rint25deg = SpecsEvolution(temperature=298.15,
                              charge=ce_rint25deg_charge,
                              discharge=ce_rint25deg_discharge,
                              name='se_rint25deg',
                              title='Rint')
se_rint40deg = SpecsEvolution(temperature=313.15,
                              charge=ce_rint40deg_charge,
                              discharge=ce_rint40deg_discharge,
                              name='se_rint40deg',
                              title='Rint')
cse_rint = CombinationSpecsEvolution(specs_evolutions=[se_rint25deg, se_rint40deg],
                                     name='cse_rint',
                                     title='Rint')

soc_charger = Evolution(evolution=[0, .2, .5, 1],
                        name='soc_charger')
current_charger = Evolution(evolution=[60, 60, 30, 10],
                            name='current_charger')
ce_charger = CombinationEvolution(evolution1=[soc_charger],
                                  evolution2=[current_charger],
                                  name='ce_charger',
                                  title1='Soc',
                                  title2='Current')
se_charger = SpecsEvolution(temperature=298.15,
                            charge=ce_charger,
                            name='se_charger',
                            title='Current')
cce_charger = CombinationSpecsEvolution(specs_evolutions=[se_charger],
                                        name='cce_charger',
                                        title='Current')

evol_temperature = Evolution(evolution=[270, 290, 310, 330])
evol_thermal_trans1 = Evolution(evolution=[0.1, 0.5, 1, 1.5])
evol_thermal_trans2 = Evolution(evolution=[0.2, 0.6, 1.1, 1.6])
evol_thermal_trans3 = Evolution(evolution=[0.3, 0.7, 1.2, 1.7])

thermal_transfert1 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans1],
                                          name='thermal transfert dir1',
                                          title1='Temperature',
                                          title2='Thermal transfert')
thermal_transfert2 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans2],
                                          name='thermal transfert dir2',
                                          title1='Temperature',
                                          title2='Thermal transfert')
thermal_transfert3 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans3],
                                          name='thermal transfert dir3',
                                          title1='Temperature',
                                          title2='Thermal transfert')

CELL1_S = Cell(rated_capacity=30*3600,
               ocv_specs=cse_ocv,
               rint_specs=cse_rint,
               limits_voltage={'charge': {'minimum': 1, 'maximum': 10},
                               'discharge': {'minimum': 1, 'maximum': 12}},
               limits_current={'charge': {'minimum': 0, 'maximum': 50},
                               'discharge': {'minimum': -50, 'maximum': 0}},
               limits_soc={'minimum': 0.005, 'maximum': 0.95},
               charge_specs=cce_charger,
               size=(.03, .15, .103),
               mass=1,
               thermal_transfert_specs=[thermal_transfert1, thermal_transfert2, thermal_transfert3],
               name='CELL1_S')

# =============================================================================
# Cell RC
# =============================================================================
evol_soc = Evolution(evolution=[.01, .05, .1, .15, .2, .25, .3,
                                .35, .4, .45, .5, .55, .6, .65,
                                .7, .75, .8, .85, .9, .95],
                     name='evol_soc')
evol_rint1_charge = Evolution(evolution=[.02, .003, .0015, .00155, .00137,
                                         .00135, .0013, .0012, .00118,
                                         .00115, .00111, .001, .0009,
                                         .00085, .00083, .00081, .0008,
                                         .00075, .00073, .0007],
                              name='evol_rint1_charge')
evol_rint1_discharge = Evolution(evolution=[.02, .003, .0015, .00155, .00137,
                                         .00135, .0013, .0012, .00118,
                                         .00115, .00111, .001, .0009,
                                         .00085, .00083, .00081, .0008,
                                         .00075, .00073, .0007],
                                 name='evol_rint1_discharge')
evol_c1_charge = Evolution(evolution=[200, 500, 15000, 15645, 16255, 16882,
                                      17500, 18120, 18710, 19400, 20020,
                                      20720, 21320, 21830, 22650, 23146,
                                      23742, 24365, 25125, 25042],
                           name='evol_c1_charge')
evol_c1_discharge = Evolution(evolution=[200, 500, 15000, 15645, 16255, 16882,
                                      17500, 18120, 18710, 19400, 20020,
                                      20720, 21320, 21830, 22650, 23146,
                                      23742, 24365, 25125, 25042],
                              name='evol_c1_discharge')

ce_rint1_charge = CombinationEvolution(evolution1=[evol_soc],
                                       evolution2=[evol_rint1_charge],
                                       name='ce_rint1_charge',
                                       title1='Soc',
                                       title2='Rint1')
ce_rint1_discharge = CombinationEvolution(evolution1=[evol_soc],
                                          evolution2=[evol_rint1_discharge],
                                          name='ce_rint1_discharge',
                                          title1='Soc',
                                          title2='Rint1')
ce_c1_charge = CombinationEvolution(evolution1=[evol_soc],
                                    evolution2=[evol_c1_charge],
                                    name='ce_c1_charge',
                                    title1='Soc',
                                    title2='C1')
ce_c1_discharge = CombinationEvolution(evolution1=[evol_soc],
                                       evolution2=[evol_c1_discharge],
                                       name='ce_c1_discharge',
                                       title1='Soc',
                                       title2='C1')

se_rint1 = SpecsEvolution(temperature=298.15,
                          charge=ce_rint1_charge,
                          discharge=ce_rint1_discharge,
                          name='se_rint1',
                          title='Rint1')
se_c1 = SpecsEvolution(temperature=298.15,
                       charge=ce_c1_charge,
                       discharge=ce_c1_discharge,
                       name='se_c1',
                       title='C1')

cse_rint1 = CombinationSpecsEvolution(specs_evolutions=[se_rint1],
                                      name='cse_rint1',
                                      title='Rint1')
cse_C1 = CombinationSpecsEvolution(specs_evolutions=[se_c1],
                                   name='cse_C1',
                                   title='C1')

evol_temperature = Evolution(evolution=[270, 290, 310, 330])
evol_thermal_trans1 = Evolution(evolution=[0.1, 0.5, 1, 1.5])
evol_thermal_trans2 = Evolution(evolution=[0.2, 0.6, 1.1, 1.6])
evol_thermal_trans3 = Evolution(evolution=[0.3, 0.7, 1.2, 1.7])

thermal_transfert1 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans1],
                                          name='thermal transfert dir1',
                                          title1='Temperature',
                                          title2='Thermal transfert')
thermal_transfert2 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans2],
                                          name='thermal transfert dir2',
                                          title1='Temperature',
                                          title2='Thermal transfert')
thermal_transfert3 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans3],
                                          name='thermal transfert dir3',
                                          title1='Temperature',
                                          title2='Thermal transfert')

CELL1_RC = CellRC(rated_capacity=50*3600,
                  ocv_specs=cse_ocv,
                  rint_specs=cse_rint,
                  rint1_specs=cse_rint1,
                  c1_specs=cse_C1,
                  limits_voltage={'charge': {'minimum': 1, 'maximum': 8},
                                  'discharge': {'minimum': 1, 'maximum': 7}},
                  limits_current={'charge': {'minimum': 0, 'maximum': 10},
                                  'discharge': {'minimum': -15, 'maximum': 0}},
                  limits_soc={'minimum': 0.005, 'maximum': 0.95},
                  charge_specs=cce_charger,
                  size=(.03, .15, .103),
                  mass=1,
                  thermal_transfert_specs=[thermal_transfert1, thermal_transfert2, thermal_transfert3],
                  name='CELL1_RC')

# =============================================================================
# Cell 2RC
# =============================================================================
evol_soc = Evolution(evolution=[.01, .05, .1, .15, .2, .25, .3,
                                .35, .4, .45, .5, .55, .6, .65,
                                .7, .75, .8, .85, .9, .95],
                     name='evol_soc')
evol_rint2_charge = Evolution(evolution=[.01002, .0015, .001, .00095, .00094, .00091,
                                         .00091, .00089, .00085, .00082, .00081,
                                         .00082, .00085, .00082, .00085, .00089,
                                         .0008, .00075, .00072, .00071],
                              name='evol_rint2_charge')
evol_rint2_discharge = Evolution(evolution=[.01001, .0014, .00105, .00095, .00094, .00091,
                                         .00091, .00089, .00085, .00082, .00081,
                                         .00082, .00085, .00082, .00085, .00089,
                                         .0008, .00075, .00072, .00071],
                                 name='evol_rint2_discharge')
evol_c2_charge = Evolution(evolution=[15000, 100000, 240000, 246900, 243760,
                                      240645, 237514, 234398, 231300, 228254,
                                      225456, 221987, 218457, 215972, 212527,
                                      209678, 206276, 203741, 200794, 200589],
                           name='evol_c2_charge')
evol_c2_discharge = Evolution(evolution=[15000, 100000, 240000, 246900, 243760,
                                      240645, 237514, 234398, 231300, 228254,
                                      225456, 221987, 218457, 215972, 212527,
                                      209678, 206276, 203741, 200794, 200589],
                              name='evol_c2_discharge')

ce_rint2_charge = CombinationEvolution(evolution1=[evol_soc],
                                       evolution2=[evol_rint2_charge],
                                       name='ce_rint2_charge',
                                       title1='Soc',
                                       title2='Rint2')
ce_rint2_discharge = CombinationEvolution(evolution1=[evol_soc],
                                          evolution2=[evol_rint2_discharge],
                                          name='ce_rint2_discharge',
                                          title1='Soc',
                                          title2='Rint2')
ce_c2_charge = CombinationEvolution(evolution1=[evol_soc],
                                    evolution2=[evol_c2_charge],
                                    name='ce_c2_charge',
                                    title1='Soc',
                                    title2='C2')
ce_c2_discharge = CombinationEvolution(evolution1=[evol_soc],
                                       evolution2=[evol_c2_discharge],
                                       name='ce_c2_discharge',
                                       title1='Soc',
                                       title2='C2')
se_rint2 = SpecsEvolution(temperature=298.15,
                          charge=ce_rint2_charge,
                          discharge=ce_rint2_discharge,
                          name='se_rint2',
                          title='Rint2')
se_c2 = SpecsEvolution(temperature=298.15,
                       charge=ce_c2_charge,
                       discharge=ce_c2_discharge,
                       name='se_c2',
                       title='C2')
cse_rint2 = CombinationSpecsEvolution(specs_evolutions=[se_rint2],
                                      name='cse_rint2',
                                      title='Rint2')
cse_C2 = CombinationSpecsEvolution(specs_evolutions=[se_c2],
                                   name='cse_C2',
                                   title='C2')

evol_temperature = Evolution(evolution=[270, 290, 310, 330])
evol_thermal_trans1 = Evolution(evolution=[0.1, 0.5, 1, 1.5])
evol_thermal_trans2 = Evolution(evolution=[0.2, 0.6, 1.1, 1.6])
evol_thermal_trans3 = Evolution(evolution=[0.3, 0.7, 1.2, 1.7])

thermal_transfert1 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans1],
                                          name='thermal transfert dir1',
                                          title1='Temperature',
                                          title2='Thermal transfert')
thermal_transfert2 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans2],
                                          name='thermal transfert dir2',
                                          title1='Temperature',
                                          title2='Thermal transfert')
thermal_transfert3 = CombinationEvolution(evolution1=[evol_temperature],
                                          evolution2=[evol_thermal_trans3],
                                          name='thermal transfert dir3',
                                          title1='Temperature',
                                          title2='Thermal transfert')

CELL1_2RC = Cell2RC(rated_capacity=50*3600,
                    ocv_specs=cse_ocv,
                    rint_specs=cse_rint,
                    rint1_specs=cse_rint1,
                    c1_specs=cse_C1,
                    rint2_specs=cse_rint2,
                    c2_specs=cse_C2,
                    limits_voltage={'charge': {'minimum': 1, 'maximum': 8},
                                    'discharge': {'minimum': 1, 'maximum': 7}},
                    limits_current={'charge': {'minimum': 0, 'maximum': 10},
                                    'discharge': {'minimum': -15, 'maximum': 0}},
                    limits_soc={'minimum': 0.005, 'maximum': 0.95},
                    charge_specs=cce_charger,
                    size=(.03, .15, .103),
                    mass=1,
                    thermal_transfert_specs=[thermal_transfert1, thermal_transfert2, thermal_transfert3],
                    name='CELL1_2RC')
d = CELL1_S.to_dict()
obj1 = Cell.dict_to_object(d)

d = CELL1_RC.to_dict()
obj2 = Cell.dict_to_object(d)

d = CELL1_2RC.to_dict()
obj3 = Cell.dict_to_object(d)
