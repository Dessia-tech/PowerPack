#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:54:34 2019

@author: jezequel
"""
from powerpack import cells, power_profile, electrical, thermal, mechanical
from powerpack.optimization import electrical as eo
from powerpack.optimization import thermal as to
from powerpack.optimization import mechanical as mo
from dessia_common import workflow as wf

import numpy as npy


# =============================================================================
# Thermal specification
# =============================================================================

nb_discret = 4
evol_soc = electrical.Evolution(evolution=list(npy.linspace(0, 1, nb_discret)))

soc_charger = electrical.Evolution(evolution=[0, 0.2, 0.5, 1])
current_charger = electrical.Evolution(evolution=[60, 60, 30, 10])
ce_charger = electrical.CombinationEvolution(evolution1=[soc_charger],
                                       evolution2=[current_charger],
                                       title1='Soc',
                                       title2='Current')
se_charger = electrical.SpecsEvolution(temperature=298.15,
                                 charge=ce_charger,
                                 title='Current')
cce_charger = electrical.CombinationSpecsEvolution(specs_evolutions=[se_charger],
                                             title='Current')

evol_temperature = electrical.Evolution(evolution = [270, 290, 310, 330])
evol_thermal_trans1 = electrical.Evolution(evolution = [0.1, 0.5, 1, 1.5])
evol_thermal_trans2 = electrical.Evolution(evolution = [0.2, 0.6, 1.1, 1.6])
evol_thermal_trans3 = electrical.Evolution(evolution = [0.3, 0.7, 1.2, 1.7])

thermal_transfert1 = electrical.CombinationEvolution(evolution1 = [evol_temperature],
                                               evolution2 = [evol_thermal_trans1],
                                               name = 'thermal transfert dir1',
                                               title1 = 'Temperature',
                                               title2 = 'Thermal transfert')
thermal_transfert2 = electrical.CombinationEvolution(evolution1 = [evol_temperature],
                                               evolution2 = [evol_thermal_trans2],
                                               name = 'thermal transfert dir2',
                                               title1 = 'Temperature',
                                               title2 = 'Thermal transfert')
thermal_transfert3 = electrical.CombinationEvolution(evolution1 = [evol_temperature],
                                               evolution2 = [evol_thermal_trans3],
                                               name = 'thermal transfert dir3',
                                               title1 = 'Temperature',
                                               title2 = 'Thermal transfert')

# =============================================================================
# Cell definition
# =============================================================================

Cell2 = cells.CELL1_S

# =============================================================================
# Vehicle specs
# =============================================================================
VEHICLE_SPECS = {'SCx' : 1.4,
                 'Crr' : 0.01,
                 'mass' : 1200,
                 'powertrain_efficiency' : 0.7,
                 'charge_efficiency' : 0.6}

# =============================================================================
# Electrical Specs
# =============================================================================

limits_voltage_module = {'charge': {'minimum': 1, 'maximum': 100},
                         'discharge': {'minimum': 1, 'maximum': 100}}
limits_current_module = {'charge': {'minimum': 0, 'maximum': 100},
                         'discharge': {'minimum': -200, 'maximum': 0}}


limits_voltage_battery = {'charge': {'minimum': 0, 'maximum': 1000},
                          'discharge': {'minimum': 0, 'maximum': 500}}
limits_current_battery = {'charge': {'minimum': 0, 'maximum': 1000},
                          'discharge': {'minimum': -500, 'maximum': 0}}


# =============================================================================
# Electrical Optimizer
# =============================================================================
POWER_PROFILE1, TIME1 = power_profile.WltpProfile(VEHICLE_SPECS, (1, ))
t_wltp1 = electrical.Evolution(list(TIME1))
p_wltp1 = electrical.Evolution(list(POWER_PROFILE1))

POWER_PROFILE2, TIME2 = power_profile.WltpProfile(VEHICLE_SPECS, (2, ))
t_wltp2 = electrical.Evolution(list(TIME2))
p_wltp2 = electrical.Evolution(list(POWER_PROFILE2))

POWER_PROFILE3, TIME3 = power_profile.WltpProfile(VEHICLE_SPECS, (3, ))
t_wltp3 = electrical.Evolution(list(TIME3))
p_wltp3 = electrical.Evolution(list(POWER_PROFILE3))
t_load = electrical.Evolution(list(range(10)))
p_load = electrical.Evolution([1e5]*10)
t_end = electrical.Evolution(list(range(10)))
p_end = electrical.Evolution([-2e4]*10)

ce_end = electrical.CombinationEvolution(evolution1=[t_end],
                              evolution2=[p_end],
                              name='End Profile')
ce_wltp1 = electrical.CombinationEvolution(evolution1=[t_wltp1],
                                evolution2=[p_wltp1],
                                 name='WLTP1 profile')
ce_wltp2 = electrical.CombinationEvolution(evolution1=[t_wltp2],
                                evolution2=[p_wltp2],
                                name='WLTP2 profile')
ce_wltp3 = electrical.CombinationEvolution(evolution1=[t_wltp3],
                                evolution2=[p_wltp3],
                                name='WLTP3 profile')
ce_load = electrical.CombinationEvolution(evolution1=[t_load],
                               evolution2=[p_load],
                               name='Load Profile')


load_bat = electrical.PowerProfile(soc_init=0.05*59.5*3600,
                        combination_evolutions=[ce_load],
                        loop=True,
                        soc_end=0.95*59.5*3600,
                        use_selection=True,
                        name='Load profile')
end_bat = electrical.PowerProfile(combination_evolutions=[ce_end],
                       loop=False,
                       power_accuracy=0.05,
                       soc_init=0.2*59.5*3600,
                       name='End profile')
wltp_bat = electrical.PowerProfile(combination_evolutions=[ce_wltp2],
                        loop=True,
                        power_accuracy=0.05,
                        soc_init=0.95*59.5*3600,
                        max_loop=50,
                        soc_end=0.2*59.5*3600,
                        use_selection=True,
                        name='WLTP profile')

comb_profile_wltp = electrical.CombinationPowerProfile([wltp_bat], name='wltp_profil')
comb_profile_load = electrical.CombinationPowerProfile([load_bat], name='load_profil')
comb_profile_end = electrical.CombinationPowerProfile([end_bat], name='end_soc_profil')

# =============================================================================
# Electrical Optimizer
# =============================================================================

input_values = {}
blocks = []
block_ebo = wf.InstanciateModel(eo.ElecBatteryOptimizer, name='ElecBatteryOptimizer')
optimize_ebo = wf.ModelMethod(eo.ElecBatteryOptimizer, 'Optimize',  name='Optimize-ElecBatteryOptimizer')
attribute_selection_ebo = wf.ModelAttribute('powerpack_electric_simulators')


blocks.extend([block_ebo, optimize_ebo, attribute_selection_ebo])
pipes = [wf.Pipe(block_ebo.outputs[0], optimize_ebo.inputs[0]),
         wf.Pipe(optimize_ebo.outputs[1], attribute_selection_ebo.inputs[0])
         ]

# =============================================================================
# Thermal specs
# =============================================================================
altitude = 0.1
evol_power1 = electrical.Evolution(evolution = list(npy.linspace(0, 5., 10)))
evol_power2 = electrical.Evolution(evolution = list(npy.linspace(0, 6., 10)))
evol_h_min1 = electrical.Evolution(evolution = [0 + 0.3*1e1*p/(p + 0.1)/2. for p in npy.linspace(0, 1, 10)])
evol_h_max2 = electrical.Evolution(evolution = [altitude + 0.3*1e1*p/(p + 0.1)/2. for p in npy.linspace(0, 1, 10)])

ce_cooling1_min = electrical.CombinationEvolution(evolution1 = [evol_power1],
        evolution2 = [evol_h_min1], name='Min', title1='power', title2='h')
ce_cooling1_max = electrical.CombinationEvolution(evolution1 = [evol_power2],
        evolution2 = [evol_h_max2], name='Max', title1='power', title2='h')
sc1 = thermal.SpecsCooling(internal_parameter = 273, thermal_transfer_coefficient_min = ce_cooling1_min,
                     thermal_transfer_coefficient_max = ce_cooling1_max,
                     name='Cooling1', title = 'Cooling')
csc1 = thermal.CombinationSpecsCooling(specs_coolings = [sc1])
cc1 = thermal.CoolingComponent(csc1, thermal_capacity = 0.1, coeff_a_price = 0.4,
                               coeff_b_price = 1)

altitude = 10
evol_power1 = electrical.Evolution(evolution = list(npy.linspace(0, 50., 10)))
evol_power2 = electrical.Evolution(evolution = list(npy.linspace(0, 60., 10)))
evol_h_min1 = electrical.Evolution(evolution = [0 + 0.3*1e1*p/(p + 0.1)/2. for p in npy.linspace(0, 1, 10)])
evol_h_max2 = electrical.Evolution(evolution = [altitude + 0.3*1e1*p/(p + 0.1)/2. for p in npy.linspace(0, 1, 10)])

ce_cooling2_min = electrical.CombinationEvolution(evolution1 = [evol_power1],
        evolution2 = [evol_h_min1], name='Min', title1='power', title2='h')
ce_cooling2_max = electrical.CombinationEvolution(evolution1 = [evol_power2],
        evolution2 = [evol_h_max2], name='Max', title1='power', title2='h')
sc2 = thermal.SpecsCooling(internal_parameter = 273, thermal_transfer_coefficient_min = ce_cooling2_min,
                     thermal_transfer_coefficient_max = ce_cooling2_max,
                     name='Cooling1', title = 'Cooling')
csc2 = thermal.CombinationSpecsCooling(specs_coolings = [sc2])
cc2 = thermal.CoolingComponent(csc2, thermal_capacity = 0.1, coeff_a_price = 0.4,
                               coeff_b_price = 1)

altitude = 1e7
evol_power1 = electrical.Evolution(evolution = list(npy.linspace(0, 1e4, 10)))
evol_power2 = electrical.Evolution(evolution = list(npy.linspace(0, 2e4, 10)))
evol_h_min1 = electrical.Evolution(evolution = [0 + 0.3*1e1*p/(p + 0.1)/2. for p in npy.linspace(0, 1, 10)])
evol_h_max2 = electrical.Evolution(evolution = [altitude + 0.3*1e1*p/(p + 0.1)/2. for p in npy.linspace(0, 1, 10)])

ce_cooling3_min = electrical.CombinationEvolution(evolution1 = [evol_power1],
        evolution2 = [evol_h_min1], name='Min', title1='power', title2='h')
ce_cooling3_max = electrical.CombinationEvolution(evolution1 = [evol_power2],
        evolution2 = [evol_h_max2], name='Max', title1='power', title2='h')
sc3 = thermal.SpecsCooling(internal_parameter = 273, thermal_transfer_coefficient_min = ce_cooling3_min,
                     thermal_transfer_coefficient_max = ce_cooling3_max,
                     name='Cooling1', title = 'Cooling')
csc3 = thermal.CombinationSpecsCooling(specs_coolings = [sc3])
cc3 = thermal.CoolingComponent(csc3, thermal_capacity = 0.1, coeff_a_price = 0.4,
                               coeff_b_price = 1)

catalog1 = thermal.CoolingCatalog(cooling_components = [cc1, cc2, cc3])

print("===== QTBO =====")
block_qtbo = wf.InstanciateModel(to.QuickThermalBatteryOptimizer,  name='QuickThermalBatteryOptimizer')
optimize_qtbo = wf.ModelMethod(to.QuickThermalBatteryOptimizer, 'Optimize', name='Optimize-QuickThermalBatteryOptimizer')
attribute_selection_qtbo = wf.ModelAttribute('powerpack_thermal_simulators')

blocks.extend([block_qtbo, optimize_qtbo, attribute_selection_qtbo,])
pipes.extend([wf.Pipe(attribute_selection_ebo.outputs[0], block_qtbo.inputs[0]),
              wf.Pipe(block_qtbo.outputs[0], optimize_qtbo.inputs[0]),
              wf.Pipe(optimize_qtbo.outputs[1], attribute_selection_qtbo.inputs[0]),
              ])

# =============================================================================
# Mechanical specs
# =============================================================================

pack_size = (2.3, 1.4, 0.32)

bounds_grids = (3, 3)

rails_specs = {'transversal' : .010, 'longitudinal' : .005}
rail_numbers = (2, 2)

longitudinal_tolerances = [{'minus' : 1, 'plus' : 1}, {'minus' : 0.5, 'plus' : 1.5},
          {'minus' : 0.5, 'plus' : 1.5}, {'minus' : 0.5, 'plus' : 1.5}]
transversal_tolerances = [{'minus' : 0.7, 'plus' : 1.3}, {'minus' : 1, 'plus' : 1},
         {'minus' : 0.7, 'plus' : 1.3}]

cp_thickness = 0.015
module_gap = 0.005

# =============================================================================
# Mechanical Optimizer
# =============================================================================

print("===== GBO =====")
block_gbo = wf.InstanciateModel(mo.GenerativeBatteryOptimizer, name='GenerativeBatteryOptimizer')
optimize_gbo = wf.ModelMethod(mo.GenerativeBatteryOptimizer, 'Optimize', name='Optimize-GenerativeBatteryOptimizer')
attribute_selection_gbo = wf.ModelAttribute('powerpack_mechanical_simulators')

filters = [{'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.analysis.electric_range', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.analysis.load_time', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.analysis.number_cells', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.analysis.number_modules', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.analysis.voltage_max', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.analysis.current_max', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.bms.number_module_serie', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.bms.number_module_parallel', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.bms.battery.mms.number_cell_serie', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.powerpack_electric_simulator.bms.battery.mms.number_cell_parallel', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.analysis.cooling_price', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.analysis.cooling_surface', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.analysis.grid_0', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.analysis.grid_1', 'operator' : 'gt', 'bound' : 0},
           {'attribute' : 'powerpack_thermal_simulator.analysis.grid_2', 'operator' : 'gt', 'bound' : 0},
           ]

filter_sort_gbo = wf.Filter(filters)


blocks.extend([block_gbo, optimize_gbo, attribute_selection_gbo, filter_sort_gbo])
pipes.extend([wf.Pipe(attribute_selection_qtbo.outputs[0], block_gbo.inputs[8]),
              wf.Pipe(block_gbo.outputs[0], optimize_gbo.inputs[0]),
              wf.Pipe(optimize_gbo.outputs[1], attribute_selection_gbo.inputs[0]),
              wf.Pipe(attribute_selection_gbo.outputs[0], filter_sort_gbo.inputs[0])
              ])

workflow_complete_battery = wf.Workflow(blocks, pipes, filter_sort_gbo.outputs[0])

input_values = {workflow_complete_battery.index(block_ebo.inputs[0]): Cell2,
                workflow_complete_battery.index(block_ebo.inputs[1]): limits_voltage_module,
                workflow_complete_battery.index(block_ebo.inputs[2]): limits_current_module,
                workflow_complete_battery.index(block_ebo.inputs[3]): limits_voltage_battery,
                workflow_complete_battery.index(block_ebo.inputs[4]): limits_current_battery,
                workflow_complete_battery.index(block_ebo.inputs[5]): [6, 50],
                workflow_complete_battery.index(block_ebo.inputs[6]): [25, 50],
                workflow_complete_battery.index(block_ebo.inputs[7]): [comb_profile_load,
                                      comb_profile_wltp,
                                      comb_profile_end],
                workflow_complete_battery.index(optimize_ebo.inputs[1]): 20,
                workflow_complete_battery.index(optimize_ebo.inputs[2]): [420, 500]}

input_values.update({workflow_complete_battery.index(block_qtbo.inputs[1]): catalog1,
                     workflow_complete_battery.index(block_qtbo.inputs[2]): 280,
                     workflow_complete_battery.index(block_qtbo.inputs[3]): 350,
                     workflow_complete_battery.index(block_qtbo.inputs[4]): 280,
                     workflow_complete_battery.index(block_qtbo.inputs[5]): 200,
                     workflow_complete_battery.index(optimize_qtbo.inputs[1]): 20})

input_values.update({workflow_complete_battery.index(block_gbo.inputs[0]) : bounds_grids,
                     workflow_complete_battery.index(block_gbo.inputs[1]) : pack_size,
                     workflow_complete_battery.index(block_gbo.inputs[2]) : cp_thickness,
                     workflow_complete_battery.index(block_gbo.inputs[3]) : module_gap,
                     workflow_complete_battery.index(block_gbo.inputs[4]) : rails_specs,
                     workflow_complete_battery.index(block_gbo.inputs[5]) : rail_numbers,
                     workflow_complete_battery.index(block_gbo.inputs[6]) : longitudinal_tolerances,
                     workflow_complete_battery.index(block_gbo.inputs[7]) : transversal_tolerances,
                     workflow_complete_battery.index(block_gbo.inputs[9]) : True,
                     workflow_complete_battery.index(optimize_gbo.inputs[1]): 50})

# workflow_complete_battery_run = workflow_complete_battery.run(input_values)

