#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
from powerpack.electrical import PowerPackElectricSimulator
from powerpack.thermal import PowerPackThermalSimulator, CoolingCatalog
from powerpack.mechanical import PowerPackMechanicalSimulator
from typing import List
from dessia_common import DessiaObject

try:
    open_source = False
    import powerpack.optimization.thermal_protected as opt
except:
    open_source = True

class QuickThermalBatteryOptimizer(opt.QuickThermalBatteryOptimizer if not open_source else DessiaObject):
    """
    Defines a thermal battery optimizer

    :param powerpack_electric_simulators: list of PowerPackElectricSimulator
    :type powerpack_electric_simulators: [powerpack.electrical.PowerPackElectricSimulator]
    :param cooling_catalog: cooling catalogue
    :type cooling_catalog: powerpack.thermal.CoolingCatalog
    :param module_temperature_init: initial module temperature
    :type module_temperature_init: K
    :param module_temperature_max: maximum module temperature
    :type module_temperature_max: K
    :param cooling_temperature: cooling temperature
    :type cooling_temperature: K
    :param dtime_power: time step smoothing
    :type dtime_power: s
    :param powerpack_thermal_simulators: list of output
    :type powerpack_thermal_simulators: [powerpack.thermal.PowerPackThermalSimulator]

    :Example:

    >>> import powerpack.electrical as elec
    >>> catalog1 = thermal.CoolingCatalog(cooling_components = [cc1, cc2, cc3])
    >>> ebt = thermal.ThermalBatteryOptimizer(powerpack_electric_simulators, catalog1,
                                              module_temperature_max = 330,
                                              cooling_temperature = 290,
                                              module_temperature_init = 290)
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.ThermalBatteryOptimizer Base Schema",
        "required": ['powerpack_electric_simulators', 'cooling_catalog',
                     'module_temperature_init', 'module_temperature_max',
                     'cooling_temperature'],
        "properties": {
            'powerpack_electric_simulators': {
               "type": "array",
               "title" : "Powerpack Electrical Simulators",
               "order": 1,
               "editable": True,
               "description": "List of powerpack electric simulator to optimize",
               "items" : {
                   "type" : "object",
                   "classes" : ["powerpack.electrical.PowerPackElectricSimulator"]
                   },
               },
            "cooling_catalog" : {
                "type" : "object",
                "title" : "Cooling Catalog",
                "classes" : ["powerpack.thermal.CoolingCatalog"],
                "order" : 2,
                "editable" : True,
                "description" : "Cooling component catalog"
                },
            "module_temperature_init" : {
                "type" : "number",
                "title" : "Initial Module Temperature",
                "order" : 4,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "module_temperature_max" : {
                "type" : "number",
                "title" : "Maximum Module Temperature",
                "order" : 5,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "cooling_temperature" : {
                "type" : "number",
                "title" : "Cooling Temperature",
                "order" : 6,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "dtime_power" : {
                "type" : "number",
                "title" : "Dtime Power",
                "order" : 7,
                "step" : 1,
                "minimum" : 0,
                "unit" : "s",
                "editable": True,
                "examples" : [100]
                },
            'powerpack_thermal_simulators': {
               "type": "array",
               "title" : "PowerPack Thermal Simulators",
               "order": 8,
               "editable": False,
               "description": "Thermal Battery solutions",
               "items" : {
                   "type" : "object",
                   "classes" : ["powerpack.thermal.PowerPackThermalSimulator"]
                   },
               },
            }
        }

    _allowed_methods = ['Optimize']

    def __init__(self, powerpack_electric_simulators:List[PowerPackElectricSimulator],
                 cooling_catalog:CoolingCatalog,
                 module_temperature_init:float,
                 module_temperature_max:float,
                 cooling_temperature:float,
                 dtime_power:float=None,
                 powerpack_thermal_simulators:List[PowerPackThermalSimulator]=None):
        self.powerpack_electric_simulators = powerpack_electric_simulators
        self.cooling_catalog = cooling_catalog
        self.module_temperature_init = module_temperature_init
        self.module_temperature_max = module_temperature_max
        self.cooling_temperature = cooling_temperature
        if dtime_power is None:
            self.dtime_power = 100
        else:
            self.dtime_power = dtime_power

        if powerpack_thermal_simulators is None:
            self.powerpack_thermal_simulators = []
        else:
            self.powerpack_thermal_simulators = powerpack_thermal_simulators

    def __eq__(self, other):
        equal = (self.cooling_catalog == other.cooling_catalog
                 and self.module_temperature_init == other.module_temperature_init
                 and self.module_temperature_max == other.module_temperature_max
                 and self.cooling_temperature == other.cooling_temperature
                 and self.dtime_power == other.dtime_power)
        if len(self.powerpack_electric_simulators) == len(other.powerpack_electric_simulators):
            for powerpack_electric_simulator, other_powerpack_electric_simulator in zip(self.powerpack_electric_simulators, other.powerpack_electric_simulators):
                equal = (equal and powerpack_electric_simulator == other_powerpack_electric_simulator)
        else:
            equal = False
        if len(self.powerpack_thermal_simulators) == len(other.powerpack_thermal_simulators):
            if len(self.powerpack_thermal_simulators) > 0:
                for powerpack_thermal_simulator, other_powerpack_thermal_simulator in zip(self.powerpack_thermal_simulators, other.powerpack_thermal_simulators):
                    equal = (equal and powerpack_thermal_simulator == other_powerpack_thermal_simulator)
        else:
            equal = False
        return equal

    def __hash__(self):
        li_hash = 0
        for powerpack_electric_simulator in self.powerpack_electric_simulators:
            li_hash += hash(powerpack_electric_simulator)
        if self.powerpack_thermal_simulators != []:
            for powerpack_thermal_simulator in self.powerpack_thermal_simulators:
                li_hash += hash(powerpack_thermal_simulator)
        li_hash += hash(self.cooling_catalog)
        return int(li_hash % 1.0023e6)

    def Dict(self):
        """
        Export dictionary
        """
        d={}
        d['cooling_catalog'] = self.cooling_catalog.Dict()
        d['module_temperature_init'] = self.module_temperature_init
        d['module_temperature_max'] = self.module_temperature_max
        d['cooling_temperature'] = self.cooling_temperature
        d['dtime_power'] = self.dtime_power
        d['powerpack_electric_simulators'] = []
        for powerpack_electric_simulator in self.powerpack_electric_simulators:
            d['powerpack_electric_simulators'].append(powerpack_electric_simulator.Dict())
        if self.powerpack_thermal_simulators != []:
            d['powerpack_thermal_simulators'] = []
            for powerpack_thermal_simulator in self.powerpack_thermal_simulators:
                d['powerpack_thermal_simulators'].append(powerpack_thermal_simulator.Dict())
        return d

    @classmethod
    def DictToObject(cls, d):
        powerpack_electric_simulators = []
        for powerpack_electric_simulator in d['powerpack_electric_simulators']:
            powerpack_electric_simulators.append(PowerPackElectricSimulator.DictToObject(powerpack_electric_simulator))
        powerpack_thermal_simulators = None
        if 'powerpack_thermal_simulators' in d:
            if len(d['powerpack_thermal_simulators']) > 0:
                powerpack_thermal_simulators = []
                for powerpack_thermal_simulator in d['powerpack_thermal_simulators']:
                    powerpack_thermal_simulators.append(PowerPackThermalSimulator.DictToObject(powerpack_thermal_simulator))
        dtime_power = None
        if 'dtime_power' in d:
            dtime_power = d['dtime_power']
        specs = cls(cooling_catalog = CoolingCatalog.DictToObject(d['cooling_catalog']),
                    module_temperature_init = d['module_temperature_init'],
                    module_temperature_max = d['module_temperature_max'],
                    cooling_temperature = d['cooling_temperature'],
                    dtime_power = dtime_power,
                    powerpack_electric_simulators = powerpack_electric_simulators)#,
#                    powerpack_thermal_simulators = powerpack_thermal_simulators)
        specs.powerpack_thermal_simulators = powerpack_thermal_simulators
        return specs

class ThermalBatteryOptimizer(opt.ThermalBatteryOptimizer if not open_source else DessiaObject):
    """
    Defines a thermal battery optimizer

    :param powerpack_mechanical_simulators: list of PowerPackMechanicalSimulator
    :type powerpack_mechanical_simulators: [powerpack.mechanical.PowerPackMechanicalSimulator]
    :param module_temperature_init: initial module temperature
    :type module_temperature_init: K
    :param module_temperature_max: maximum module temperature
    :type module_temperature_max: K
    :param cooling_temperature: cooling temperature
    :type cooling_temperature: K
    :param dtime_power: time step smoothing
    :type dtime_power: s
    :param powerpack_thermal_simulators: list of output
    :type powerpack_thermal_simulators: [powerpack.thermal.PowerPackThermalSimulator]

    :Example:

    >>> import powerpack.electrical as elec
    >>> ebt = thermal.ThermalBatteryOptimizer(powerpack_electric_simulators,
                                              module_temperature_max = 330,
                                              cooling_temperature = 290,
                                              module_temperature_init = 290)
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.ThermalBatteryOptimizer Base Schema",
        "required": ['powerpack_mechanical_simulators',
                     'module_temperature_init', 'module_temperature_max',
                     'cooling_temperature'],
        "properties": {
            'powerpack_mechanical_simulators': {
               "type": "array",
               "title" : "Powerpack Mechanical Simulators",
               "order": 1,
               "editable": True,
               "description": "List of powerpack electric simulator to optimize",
               "items" : {
                   "type" : "object",
                   "classes" : ["powerpack.mechanical.PowerPackMechanicalSimulator"]
                   },
               },
            "module_temperature_init" : {
                "type" : "number",
                "title" : "Initial Module Temperature",
                "order" : 4,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "module_temperature_max" : {
                "type" : "number",
                "title" : "Maximum Module Temperature",
                "order" : 5,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "cooling_temperature" : {
                "type" : "number",
                "title" : "Cooling Temperature",
                "order" : 6,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "dtime_power" : {
                "type" : "number",
                "title" : "Dtime Power",
                "order" : 7,
                "step" : 1,
                "minimum" : 0,
                "unit" : "s",
                "editable": True,
                "examples" : [100]
                },
            'powerpack_thermal_simulators': {
               "type": "array",
               "title" : "Powerpack Thermal Siumulators",
               "order": 8,
               "editable": False,
               "description": "Thermal Battery solutions",
               "items" : {
                   "type" : "object",
                   "classes" : ["powerpack.thermal.PowerPackThermalSimulator"]
                   },
               },
            }
        }
    _allowed_methods = ['Optimize']

    def __init__(self, powerpack_mechanical_simulators:List[PowerPackMechanicalSimulator],
                 module_temperature_init:float,
                 module_temperature_max:float,
                 cooling_temperature:float,
                 dtime_power:float=None,
                 powerpack_thermal_simulators:List[PowerPackThermalSimulator]=None):
        self.powerpack_mechanical_simulators = powerpack_mechanical_simulators
        self.module_temperature_init = module_temperature_init
        self.module_temperature_max = module_temperature_max
        self.cooling_temperature = cooling_temperature
        if dtime_power is None:
            self.dtime_power = 100
        else:
            self.dtime_power = dtime_power

        if powerpack_thermal_simulators is None:
            self.powerpack_thermal_simulators = []
        else:
            self.powerpack_thermal_simulators = powerpack_thermal_simulators

    def __eq__(self, other):
        equal = (self.module_temperature_init == other.module_temperature_init
                 and self.module_temperature_max == other.module_temperature_max
                 and self.cooling_temperature == other.cooling_temperature
                 and self.dtime_power == other.dtime_power)
        if len(self.powerpack_mechanical_simulators) == len(other.powerpack_mechanical_simulators):
            for powerpack_mechanical_simulator, other_powerpack_mechanical_simulator in zip(self.powerpack_mechanical_simulators, other.powerpack_mechanical_simulators):
                equal = (equal and powerpack_mechanical_simulator == other_powerpack_mechanical_simulator)
        else:
            equal = False
        if len(self.powerpack_thermal_simulators) == len(other.powerpack_thermal_simulators):
            if len(self.powerpack_thermal_simulators) > 0:
                for powerpack_thermal_simulator, other_powerpack_thermal_simulator in zip(self.powerpack_thermal_simulators, other.powerpack_thermal_simulators):
                    equal = (equal and powerpack_thermal_simulator == other_powerpack_thermal_simulator)
        else:
            equal = False
        return equal

    def __hash__(self):
        li_hash = 0
        for powerpack_mechanical_simulator in self.powerpack_mechanical_simulators:
            li_hash += hash(powerpack_mechanical_simulator)
        if self.powerpack_thermal_simulators != []:
            for powerpack_thermal_simulator in self.powerpack_thermal_simulators:
                li_hash += hash(powerpack_thermal_simulator)
        return int(li_hash % 1.0023e6)

    def Dict(self):
        """
        Export dictionary
        """
        d={}
        d['module_temperature_init'] = self.module_temperature_init
        d['module_temperature_max'] = self.module_temperature_max
        d['cooling_temperature'] = self.cooling_temperature
        d['dtime_power'] = self.dtime_power
        d['powerpack_mechanical_simulators'] = []
        for powerpack_mechanical_simulator in self.powerpack_mechanical_simulators:
            d['powerpack_mechanical_simulators'].append(powerpack_mechanical_simulator.Dict())
        if self.powerpack_thermal_simulators != []:
            d['powerpack_thermal_simulators'] = []
            for powerpack_thermal_simulator in self.powerpack_thermal_simulators:
                d['powerpack_thermal_simulators'].append(powerpack_thermal_simulator.Dict())
        return d

    @classmethod
    def DictToObject(cls, d):
        powerpack_mechanical_simulators = []
        for powerpack_mechanical_simulator in d['powerpack_mechanical_simulators']:
            powerpack_mechanical_simulators.append(PowerPackMechanicalSimulator.DictToObject(powerpack_mechanical_simulator))
        powerpack_thermal_simulators = None
        if 'powerpack_thermal_simulators' in d:
            if d['powerpack_thermal_simulators'] is not None:
                powerpack_thermal_simulators = []
                for powerpack_thermal_simulator in d['powerpack_thermal_simulators']:
                    powerpack_thermal_simulators.append(PowerPackThermalSimulator.DictToObject(powerpack_thermal_simulator))
        dtime_power = None
        if 'dtime_power' in d:
            dtime_power = d['dtime_power']
        specs = cls(module_temperature_init = d['module_temperature_init'],
                    module_temperature_max = d['module_temperature_max'],
                    cooling_temperature = d['cooling_temperature'],
                    dtime_power=dtime_power,
                    powerpack_mechanical_simulators = powerpack_mechanical_simulators,
                    powerpack_thermal_simulators = powerpack_thermal_simulators)
        return specs