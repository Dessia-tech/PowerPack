
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import numpy as npy
import math
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy import interpolate

from powerpack.electrical import Cell, CellRC, Cell2RC, PowerPackElectricSimulator, \
            CombinationPowerProfile, CellManagementSystem, CellElectricSimulator
from typing import TypeVar, List
from dataclasses import dataclass
from dessia_common import DessiaObject, dict_merge
import inspect

@dataclass
class Usecase:
    minimum: float
    maximum: float

@dataclass
class Limits:
    charge: Usecase
    discharge: Usecase

try:
    _open_source = False
    import powerpack.optimization.electrical_protected as opt
except ModuleNotFoundError:
    _open_source = True



class ElecBatteryOptimizer(opt.ElecBatteryOptimizer if not _open_source else DessiaObject):
    """
    Defines of the module optimizer

    :param cell: electrical cell object
    :type cell: powerpack.electrical.Cell
    :param limits_voltage_module: Dictionnary define the voltage limit on the modules
    :type limits_voltage_module: {'charge': {'minimum': value, 'maximum': value},
                                  'discharge': {'minimum': value, 'maximum': value}}
    :param limits_current_module: Dictionnary define the current limit on the modules
    :type limits_current_module: {'charge': {'minimum': value, 'maximum': value},
                                  'discharge': {'minimum': value, 'maximum': value}}
    :param limits_voltage_battery: Dictionnary define the voltage limit on the battery
    :type limits_voltage_battery: {'charge': {'minimum': value, 'maximum': value},
                                   'discharge': {'minimum': value, 'maximum': value}}
    :param limits_current_battery: Dictionnary define the current limit on the battery
    :type limits_current_battery: {'charge': {'minimum': value, 'maximum': value},
                                   'discharge': {'minimum': value, 'maximum': value}}
    :param search_number_cells: List define the minimum and maximum of cells on a module
    :param search_number_modules: List define the minimum and maximum of modules on a battery
    :param combination_profils: list of power profile object to define input power
    :type combination_profils: [powerpack.electrical.CombinationPowerProfile]
    :param powerpack_electric_simulators: result of the current optimization store as powerpack electric simulation object
    :type powerpack_electric_simulators: [powerpack.electrical.PowerPackElectricSimulator]

    :Example:

    >>> import powerpack.electrical as elec
    >>> limits_voltage_module = {'charge': {'minimum': 1, 'maximum': 100},
                                 'discharge': {'minimum': 1, 'maximum': 120}}
    >>> limits_current_module = {'charge': {'minimum': 0, 'maximum': 100},
                                 'discharge': {'minimum': -100, 'maximum': 0}}
    >>> limits_voltage_battery = {'charge': {'minimum': 0, 'maximum': 500},
                                  'discharge': {'minimum': 0, 'maximum': 500}}
    >>> limits_current_battery = {'charge': {'minimum': 0, 'maximum': 1000},
                                  'discharge': {'minimum': -1000, 'maximum': 0}}
    >>> ebo = elec.ElecBatteryOptimizer(elec.cells.CELL1_2RC,
                                        limits_voltage_module,
                                        limits_current_module,
                                        limits_voltage_battery,
                                        limits_current_battery,
                                        search_number_cells = [2, 60],
                                        search_number_modules = [2, 30],
                                        combination_profils = [comb_profile_load,
                                                               comb_profile_wltp,
                                                               comb_profile_end])
    """
    _standalone_in_db = True
    _jsonschema = dict_merge(DessiaObject.base_jsonschema(), {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.PowerPackElectricSimulator Base Schema",
        "required": ['cell', 'limits_voltage_module', 'limits_current_module',
                     'limits_voltage_battery', 'limits_current_battery',
                     'search_number_cells', 'search_number_modules', 'combination_profils'],
        "properties": {
            'cell': {
                "type" : "object",
                "title" : "Cell",
                "classes" : ["powerpack.electrical.Cell",
                             "powerpack.electrical.CellRC",
                             "powerpack.electrical.Cell2RC"],
                "description" : "Cell",
                "editable" : True,
                "order" : 1},
            "limits_voltage_module": {
                "type": "object",
                "title" : "Module Voltage Limititations",
                "description" : "Limits voltage module",
                "editable" : True,
                "order" : 2,
                "properties": {
                    "charge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        },
                    "discharge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        }
                    },
                "required": [ "charge", "discharge" ]
                },
            "limits_current_module": {
                "type": "object",
                "title" : "Module Current Limititations",
                "description" : "Limits current module",
                "editable" : True,
                "order" : 3,
                "properties": {
                    "charge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "A"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        },
                    "discharge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "unit": "A"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        }
                    },
                "required": [ "charge", "discharge" ]
                },
            "limits_voltage_battery": {
                "type": "object",
                "title" : "Battery Voltage Limititations",
                "description" : "Limits voltage battery",
                "editable" : True,
                "order" : 4,
                "properties": {
                    "charge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        },
                    "discharge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "V"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        }
                    },
                "required": [ "charge", "discharge" ]
                },
            "limits_current_battery": {
                "type": "object",
                "title" : "Battery Current Limititations",
                "description" : "Limits current battery",
                "editable" : True,
                "order" : 5,
                "properties": {
                    "charge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "unit": "A"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        },
                    "discharge": {
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "unit": "A"
                                }
                            },
                        "required": ['minimum', 'maximum'],
                        }
                    },
                "required": [ "charge", "discharge" ]
                },
            'search_number_cells': {
                'type': 'array',
                "title" : "Number of Cells searched",
                "description" : "Minimium/maximum cells number",
                "editable" : True,
                "order" : 6,
                'items':{
                    'type': 'number',
                    "editable" : True,
                    'minimum': 0
                    },
                "minItems": 2,
                "maxItems": 2
                },
            'search_number_modules': {
                'type': 'array',
                "title" : "Number of Modules searched",
                "description" : "Minimium/maximum modules number",
                "editable" : True,
                "order" : 7,
                'items':{
                    'type': 'number',
                    "editable" : True,
                    'minimum': 0
                    },
                "minItems": 2,
                "maxItems": 2
                },
            'combination_profils': {
                'type': 'array',
                "title" : "Combination profiles",
                "description" : "Combination profiles",
                "editable" : True,
                "order" : 8,
                'items': {
                    "type" : "object",
                    "editable" : True,
                    "classes" : ["powerpack.electrical.CombinationPowerProfile"]
                    }
                },
            'powerpack_electric_simulators': {
                'type': 'array',
                "title" : "Powerpack Electric Simulators",
                "description" : "Battery simulation solutions",
                "editable" : False,
                "order" : 9,
                'items': {
                    "type" : "object",
                    "editable" : True,
                    "classes" : ["powerpack.electrical.PowerPackElectricSimulator"]
                    }
                }
             }
         })

    _allowed_methods = ['Optimize']

    def __init__(self, cell:TypeVar('Cells', Cell, CellRC, Cell2RC),
                 limits_voltage_module:Limits, limits_current_module:Limits,
                 limits_voltage_battery:Limits, limits_current_battery:Limits,
                 search_number_cells:List[int], search_number_modules:List[int],
                 combination_profils:List[CombinationPowerProfile],
                 powerpack_electric_simulators:List[PowerPackElectricSimulator]=None,
                 name:str=''):
        self.cell = cell
        self.search_number_cells = search_number_cells
        self.search_number_modules = search_number_modules
        self.limits_voltage_module = limits_voltage_module
        self.limits_current_module = limits_current_module
        self.limits_voltage_battery = limits_voltage_battery
        self.limits_current_battery = limits_current_battery
        self.combination_profils = combination_profils

        if powerpack_electric_simulators is not None:
            self.powerpack_electric_simulators = powerpack_electric_simulators
        else:
            self.powerpack_electric_simulators = []
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = (self.cell == other.cell
                 and self.limits_voltage_module == other.limits_voltage_module
                 and self.limits_current_module == other.limits_current_module
                 and self.limits_voltage_battery == other.limits_voltage_battery
                 and self.limits_current_battery == other.limits_current_battery
                 and self.search_number_cells == other.search_number_cells
                 and self.search_number_modules == other.search_number_modules)
        for combination_profil, other_combination_profil in zip(self.combination_profils, other.combination_profils):
            equal = equal and combination_profil == other_combination_profil
        if len(self.powerpack_electric_simulators) == len(other.powerpack_electric_simulators):
            if (self.powerpack_electric_simulators != []) and (other.powerpack_electric_simulators != []):
                for powerpack_electric_simulator, other_powerpack_electric_simulator in zip(self.powerpack_electric_simulators, other.powerpack_electric_simulators):
                    equal = equal and powerpack_electric_simulator == other_powerpack_electric_simulator
            elif (self.powerpack_electric_simulators == []) and (other.powerpack_electric_simulators == []):
                pass
        else:
            equal = False
        return equal

    def __hash__(self):
        hash_cell = hash(self.cell)
        hash_lim = 0
        for usecase, val_limit in self.limits_voltage_module.items():
            for minmax, val in val_limit.items():
                hash_lim += abs(int(val) % 1e4)
        for usecase, val_limit in self.limits_current_module.items():
            for minmax, val in val_limit.items():
                hash_lim += abs(int(val) % 1e4)
        for usecase, val_limit in self.limits_voltage_battery.items():
            for minmax, val in val_limit.items():
                hash_lim += abs(int(val) % 1e4)
        for usecase, val_limit in self.limits_current_battery.items():
            for minmax, val in val_limit.items():
                hash_lim += abs(int(val) % 1e4)
        hash_lim += hash(int(sum(self.search_number_cells)) % 3e5)
        hash_lim += hash(int(sum(self.search_number_modules)) % 4e5)
        hash_sol = 0
        if self.powerpack_electric_simulators != []:
            for powerpack_electric_simulator in self.powerpack_electric_simulators:
                hash_sol += hash(powerpack_electric_simulator)

        return int(hash_cell + hash_lim + hash_sol)

    def _display_angular(self):
        displays = [cp._display_angular() for cp in self.combination_profils]
        cell_displays = self.cell._display_angular()
        displays.extend(cell_displays)
        return displays

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'limits_voltage_module' : self.limits_voltage_module,
                      'limits_current_module' : self.limits_current_module,
                      'limits_voltage_battery' : self.limits_voltage_battery,
                      'limits_current_battery' : self.limits_current_battery,
                      'search_number_cells' : self.search_number_cells,
                      'search_number_modules' : self.search_number_modules,
                      'cell' : self.cell.to_dict()})
        if self.combination_profils is not None:
            dict_['combination_profils'] = []
            for combination_profil in self.combination_profils:
                dict_['combination_profils'].append(combination_profil.Dict())
        if self.powerpack_electric_simulators != []:
            dict_['powerpack_electric_simulators'] = []
            for powerpack_electric_simulator in self.powerpack_electric_simulators:
                dict_['powerpack_electric_simulators'].append(powerpack_electric_simulator.Dict())
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an ElecBatteryOptimizer object

        :param dict_: ElecBatteryOptimizer dictionnary generate with the Dict method
        """
        cell = Cell.dict_to_object(dict_['cell'])

        combination_profils = []
        for combination_profil in dict_['combination_profils']:
            combination_profils.append(CombinationPowerProfile.DictToObject(combination_profil))

        powerpack_electric_simulators = None
        if 'powerpack_electric_simulators' in dict_:
            if dict_['powerpack_electric_simulators'] is not None and len(dict_['powerpack_electric_simulators']) > 0:
                powerpack_electric_simulators = []
                for powerpack_electric_simulator in dict_['powerpack_electric_simulators']:
                    powerpack_electric_simulators.append(PowerPackElectricSimulator.DictToObject(powerpack_electric_simulator))

        optimizer = cls(cell = cell,
                        limits_voltage_module = dict_['limits_voltage_module'],
                        limits_current_module = dict_['limits_current_module'],
                        limits_voltage_battery = dict_['limits_voltage_battery'],
                        limits_current_battery = dict_['limits_current_battery'],
                        search_number_cells = dict_['search_number_cells'],
                        search_number_modules = dict_['search_number_modules'],
                        combination_profils = combination_profils,
                        powerpack_electric_simulators = powerpack_electric_simulators,
                        name=dict_['name'])
        return optimizer

class ElecModuleOptimizer(opt.ElecModuleOptimizer if not _open_source else DessiaObject):
    """
    Defines of the module optimizer

    :param cell: Cell object from cells catalog
    :type cell: Cell
    :param limits_voltage_module: Dictionnary define the voltage limit on the modules
    :type limits_voltage_module: {'charge': {'minimum': value, 'maximum': value},
                                  'discharge': {'minimum': value, 'maximum': value}}
    :param limits_current_module: Dictionnary define the current limit on the modules
    :type limits_current_module: {'charge': {'minimum': value, 'maximum': value},
                                  'discharge': {'minimum': value, 'maximum': value}}
    :param search_number_cells: List define the minimum and maximum of cells on a module
    :param search_voltage: A dictionnary that define in the charge and discharge mode
                           the minimum and maximum module voltage to search
    :type search_voltage: {'charge': {'minimum':value, 'maximum': value},
                           'discharge': {'minimum':value, 'maximum': value}}
    :param search_current: A dictionnary that define in the charge and discharge mode
                           the minimum and maximum module current to search
    :type search_current: {'charge': {'minimum':value, 'maximum': value},
                           'discharge': {'minimum':value, 'maximum': value}}

    :Example:

    >>> C1 = cells.CELL1
    >>> O1 = ElecModuleOptimizer(cell=C1,
                                            limits_voltage_module={'charge': {'minimum': 1,
                                                                              'maximum': 40},
                                                                   'discharge': {'minimum': 1,
                                                                                   'maximum': 35}},
                                            limits_current_module={'charge': {'minimum': 0,
                                                                              'maximum': 300},
                                                                   'discharge': {'minimum': -350,
                                                                                 'maximum': 0}},
                                            search_voltage={'charge': {'minimum':20,
                                                                       'maximum': 40},
                                                            'discharge': {'minimum':20,
                                                                          'maximum': 40}},
                                            search_current={'charge': {'minimum':4,
                                                                       'maximum': 10},
                                                            'discharge': {'minimum':4,
                                                                          'maximum': 10}},
                                            search_number_cells=[5, 20])
    >>>
    >>> module_combinations = O1.Combination()
    """
    def __init__(self,
                 cell,
                 limits_voltage_module,
                 limits_current_module,
                 search_number_cells,
                 search_voltage,
                 search_current):

        self.cell = cell
        self.search_number_cells = search_number_cells
        self.search_voltage = search_voltage
        self.search_current = search_current
        self.limits_voltage_module = limits_voltage_module
        self.limits_current_module = limits_current_module


class CellIdentify(opt.CellIdentify if not _open_source else DessiaObject):
    def __init__(self, cell, combination_profils, combination_evolutions):
        self.cell = cell
        self.combination_profils = combination_profils
        self.combination_evolutions = combination_evolutions
        self.cms = CellManagementSystem(cell=self.cell)
        self.cell_elec_simulator = CellElectricSimulator(self.cms, combination_profils)

