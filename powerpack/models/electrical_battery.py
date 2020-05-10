#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 15:08:32 2018

@author: jezequel
"""
import numpy as npy
import matplotlib.pyplot as plt
from powerpack import cells, power_profile, electrical, thermal, mechanical
from powerpack.electrical import Evolution, CombinationEvolution,\
                                 SpecsEvolution, CombinationSpecsEvolution,\
                                 Cell, CellRC, Cell2RC
import dessia_common as dc
from volmdlr import plot_data

# =============================================================================
# Electrical specs 2
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

# =============================================================================
# Cell definition
# =============================================================================
Cell1 = Cell(rated_capacity=30*3600,
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

cms1 = electrical.CellManagementSystem(cell = Cell1)

number_cell_serie = 8
number_cell_parallel = 4

m1 = electrical.ElecModule(cms = cms1, number_cell_serie = number_cell_serie, number_cell_parallel = number_cell_parallel)

mms1 = electrical.ModuleManagementSystem(module = m1,
                                         limits_voltage = {'charge': {'minimum': 1, 'maximum': 100},
                                                  'discharge': {'minimum': 1, 'maximum': 100}},
                                         limits_current = {'charge': {'minimum': 0, 'maximum': 300},
                                                      'discharge': {'minimum': -300, 'maximum': 0}})

number_module_serie = 4
number_module_parallel = 6
b1 = electrical.ElecBattery(mms = mms1, number_module_serie = number_module_serie, number_module_parallel = number_module_parallel)

bms1 = electrical.BatteryManagementSystem(battery = b1,
                                          limits_voltage = {'charge': {'minimum': 0, 'maximum': 1000},
                                                            'discharge': {'minimum': 0, 'maximum': 600}},
                                          limits_current = {'charge': {'minimum': 0, 'maximum': 2000},
                                                            'discharge': {'minimum': -500, 'maximum': 0}})

# plots = b1.concept_plot_data()
# pdg = plot_data.plot_d3(plots[0])

VEHICLE_SPECS = {'SCx' : 1,
                 'Crr' : 0.01,
                 'mass' : 1300,
                 'powertrain_efficiency' : 0.7,
                 'charge_efficiency' : 0.5}

POWER_PROFILE, TIME = power_profile.WltpProfile(VEHICLE_SPECS, (1, ))
t_wltp = electrical.Evolution(list(TIME), name='t_wltp')
p_wltp = electrical.Evolution(list(POWER_PROFILE))
t_load = electrical.Evolution(list(range(10)))
p_load = electrical.Evolution([1e5]*10)
t_end = electrical.Evolution(list(range(10)))
p_end = electrical.Evolution([-2e4]*10)

ce_end = electrical.CombinationEvolution(evolution1 = [t_end],
                                        evolution2 = [p_end])
ce_wltp = electrical.CombinationEvolution(evolution1 = [t_wltp],
                                        evolution2 = [p_wltp])
ce_load = electrical.CombinationEvolution(evolution1 = [t_load],
                                        evolution2 = [p_load])


load_bat = electrical.PowerProfile(soc_init = 0.05*180000, combination_evolutions = [ce_load],
                                   loop = True, soc_end = 0.95*180000,
                                  charger = True)
end_bat = electrical.PowerProfile(combination_evolutions = [ce_end],  loop = False,
                                  power_accuracy = 0.2, soc_init = 0.1*180000)
wltp_bat = electrical.PowerProfile(combination_evolutions = [ce_wltp],  loop = True,
                                  power_accuracy = 0.2, soc_init = 0.95*180000,
                                  max_loop = 1,
                                  soc_end = 0.1*180000, use_selection = False)

comb_profile_wltp = electrical.CombinationPowerProfile([wltp_bat], name='wltp_profil')
comb_profile_load = electrical.CombinationPowerProfile([load_bat], name='load_profil')
comb_profile_end = electrical.CombinationPowerProfile([end_bat], name='end_soc_profil')

power_pack_electric_simulator = electrical.PowerPackElectricSimulator(bms = bms1,
                  combination_profils = [comb_profile_load, comb_profile_wltp, comb_profile_end],
                  battery_results = [electrical.ElecBatteryResult()]*3,
                  module_results = [electrical.ElecModuleResult()]*3,
                  cell_results = [electrical.CellResult()]*3)

# valid_profil = power_pack_electric_simulator.Simulate()
