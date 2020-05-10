#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 11:49:33 2019

@author: jezequel
"""
from copy import copy
import numpy as npy
from powerpack import __version__
from powerpack.thermal import PowerPackThermalSimulator
from powerpack.mechanical import PowerPackMechanicalSimulator
from typing import List
from dataclasses import dataclass
from dessia_common import DessiaObject

try:
    open_source = False
    import powerpack.optimization.mechanical_protected as opt
except:
    open_source = True

@dataclass
class RailSpecs:
    longitunal:float
    transversal:float

@dataclass
class Tolerance:
    minus:float
    plus:float

class GenerativeBatteryOptimizer(opt.GenerativeBatteryOptimizer if not open_source else dc.DessiaObject):
    """
    Defines a generative battery designer for mechanical

    :param pack_size: Tuple that represent pack structure size constraints in global frame
    :type size: (x, y, z) m
    :param cp_thickness: Thickness of cooling_plates
    :type cp_thickness: m
    :param module_gap: Gap between modules defined by process needs
    :type module_gap: m
    :param rails_specs: Rails widths
    :type rails_specs: {'transversal' : [width_n, width_m,...],
                        'longitudinal' : [width_i, width_j, width_k,...]
    :param longitudinal_tolerances: List indicating tolerance on rails x positions.
                   Indices are x coordinates of cases.
    :type longitudinal_tolerances: {0 : (1, 1), 1 : (0.8, 1.2), 2 : (0.7, 1.7)}
    :param transversal_tolerances: List indicating tolerance on rails y positions
    :type transversal_tolerances: {0 : (0.5, 1.5), 1 : (1, 1)}
    :param elec_battery: ElecBattery object representing electrical circuit
    :type elec_battery: ElecBattery()
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.MechModule Base Schema",
        "required": ["bounds_grids", "pack_size", "cp_thickness", "module_gap",
                     "rail_specs", "n_lr", "n_tr", "longitudinal_tolerances", "transversal_tolerances",
                     "powerpack_thermal_simulators", "allow_empty_grid"],
        "properties": {
            'bounds_grids' : {
                'type' : 'array',
                "title" : "Grids Bounds",
                'order' : 1,
                "minItems": 2,
                "maxItems": 2,
                'examples' : [(3, 3)],
                "editable" : True,
                "description" : "Number of module in grid in each direction",
                'items' : {
                    'type' : 'number',
                    'step' : 1,
                    'minimum' : 1
                    }
                },
            'pack_size' : {
                'type' : 'array',
                "title" : "Pack Size",
                'order' : 2,
                "minItems": 3,
                "maxItems": 3,
                "editable" : True,
                'examples' : [(2, 1.4, .160)],
                "description" : "Maximum size of pack",
                'items' : {
                    'type' : 'number',
                    "editable" : True,
                    'step' : "any",
                    'minimum' : 0,
                    'unit' : 'm'
                    }
                },
            'cp_thickness' : {
                "type" : "number",
                "title" : "Cooling Plates Thickness",
                "order" : 3,
                "editable" : True,
                "examples" : [0.005],
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "description" : "Cooling plates thickness"
                },
            'module_gap' : {
                "type" : "number",
                "title" : "Module Gap",
                "order" : 4,
                "editable" : True,
                "examples" : [0.005],
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "description" : "Gap between modules"
                },
            'rail_specs' : {
                'order' : 5,
                'type' : 'object',
                "title" : "Rails Specifications",
                'editable' : True,
                'properties' : {
                    'longitudinal' : {
                        'type' : 'number',
                        'editable' : True,
                        'examples' : [0.010],
                        'step' : 0.0001,
                        'unit' : 'm',
                        'description' : 'Width of longitudinal rails'
                        },
                    'transversal' : {
                        'type' : 'number',
                        'editable' : True,
                        'examples' : [0.010],
                        'step' : 0.0001,
                        'unit' : 'm',
                        'description' : 'Width of transversal rails'
                        }
                    }
                },
            'n_lr' : {
                'type' : 'number',
                "title" : "Number of Longitudinal Rails",
                'order' : 6,
                "editable" : True,
                "description" : "Number of longitudinal rails",
                "step" : 1,
                "minimum" : 0,
                "examples" : [2]
                },
            'n_tr' : {
                'type' : 'number',
                "title" : "Number of Transversal Rails",
                'order' : 7,
                "editable" : True,
                "description" : "Number of transversal rails",
                "step" : 1,
                "minimum" : 0,
                "examples" : [3]
                },
            'longitudinal_tolerances' : {
                'type' : 'array',
                "title" : "Logitudinal Tolerances",
                'order' : 8,
                'editable' : True,
                'description' : 'x tolerance on rails position',
                'items': {
                    'type' : 'object',
                    'editable' : True,
                    'description' : 'x tolerance on rails position',
                    'properties' : {
                        'minus' : {
                            'type' : 'number',
                            "editable" : True,
                            'step' : 0.01,
                            'minimum' : 0,
                            'maximum' : 1
                            },
                        'plus' :
                            {
                            'type' : 'number',
                            "editable" : True,
                            'step' : 0.01,
                            'minimum' : 1
                            }
                        }
                    }
                },
            'transversal_tolerances' : {
                'type' : 'array',
                "title" : "Transversal Tolerances",
                'order' : 9,
                'editable' : True,
                'description' : 'y tolerance on rails position',
                'items': {
                    'type' : 'object',
                    'editable' : True,
                    'description' : 'x tolerance on rails position',
                    'properties' : {
                        'minus' : {
                            'type' : 'number',
                            "editable" : True,
                            'step' : 0.01,
                            'minimum' : 0,
                            'maximum' : 1
                            },
                        'plus' : {
                            'type' : 'number',
                            "editable" : True,
                            'step' : 0.01,
                            'minimum' : 1
                            }
                        }
                    }
                },
            'powerpack_thermal_simulators' : {
                'type' : 'array',
                "title" : "Powerpack Thermal Simulators",
                'order' : 10,
                'editable' : True,
                'description' : 'List of viable thermal battery simulations',
                'items' : {
                    'type' : 'object',
                    "editable" : True,
                    'classes' : ['powerpack.thermal.PowerPackThermalSimulator']
                    }
                },
            'powerpack_mechanical_simulators' : {
                'type' : 'array',
                "title" : "Powerpack Mechanical Simulators",
                'order' : 11,
                'editable' : False,
                'description' : 'List of simulation powerpack mechanichal',
                'items' : {
                    'type' : 'object',
                    "editable" : False,
                    'classes' : ['powerpack.mechanical.PowerPackMechanicalSimulator']
                    }
                },
            'allow_empty_grid' : {
                'type' : 'boolean',
                "title" : "Allow Empty Grid",
                'order' : 12,
                'examples' : [True, False],
                'editable' : True,
                'description' : 'Wether empty cases should be allowed or not'
                }
            }
        }
    _allowed_methods = ['Optimize']
    def __init__(self,
                 bounds_grids:List[float],
                 pack_size:List[float],
                 cp_thickness:float,
                 module_gap:float,
                 rail_specs:RailSpecs,
                 rail_number:List[int],
                 longitudinal_tolerances:List[Tolerance],
                 transversal_tolerances:List[Tolerance],
                 powerpack_thermal_simulators:List[PowerPackThermalSimulator],
                 allow_empty_grid:bool=None,
                 powerpack_mechanical_simulators:List[PowerPackMechanicalSimulator]=None):
        self.bounds_grids = bounds_grids
        self.pack_size = pack_size
        self.cp_thickness = cp_thickness
        self.module_gap = module_gap
        self.rail_specs = rail_specs
        self.n_lr, self.n_tr = rail_number
        self.longitudinal_tolerances = longitudinal_tolerances
        self.transversal_tolerances = transversal_tolerances
        self.powerpack_thermal_simulators = powerpack_thermal_simulators
        if allow_empty_grid is None:
            self.allow_empty_grid = True
        else:
            self.allow_empty_grid = allow_empty_grid

        if powerpack_mechanical_simulators is None:
            self.powerpack_mechanical_simulators = []
        else:
            self.powerpack_mechanical_simulators = powerpack_mechanical_simulators

    def __eq__(self, other):
        equal = (npy.allclose(self.bounds_grids,other.bounds_grids)
                 and npy.allclose(self.pack_size,other.pack_size)
                 and self.cp_thickness == other.cp_thickness
                 and self.module_gap == other.module_gap
                 and self.rail_specs == other.rail_specs
                 and self.n_lr == other.n_lr
                 and self.n_tr == other.n_tr
                 and self.longitudinal_tolerances == other.longitudinal_tolerances
                 and self.transversal_tolerances == other.transversal_tolerances
                 and self.allow_empty_grid == other.allow_empty_grid)

        if len(self.powerpack_thermal_simulators) == len(other.powerpack_thermal_simulators):
            for powerpack_thermal_simulator, other_powerpack_thermal_simulator in zip(self.powerpack_thermal_simulators, other.powerpack_thermal_simulators):
                equal = (equal and powerpack_thermal_simulator == other_powerpack_thermal_simulator)
        else:
            equal = False
        if len(self.powerpack_mechanical_simulators) == len(other.powerpack_mechanical_simulators):
            if len(self.powerpack_mechanical_simulators) > 0:
                for powerpack_mechanical_simulator, other_powerpack_mechanical_simulator in zip(self.powerpack_mechanical_simulators, other.powerpack_mechanical_simulators):
                    equal = (equal and powerpack_mechanical_simulator == other_powerpack_mechanical_simulator)
        else:
            equal = False
        return equal

    def __hash__(self):
        # Proposition, see if ok of if it needs more
        li_hash = int(hash(sum(self.pack_size)) % 1e5)
        li_hash += int(hash(sum(self.bounds_grids)) % 1e5)
        li_hash += int(hash(self.module_gap) % 1e5)
        li_hash += int(hash(self.cp_thickness) % 1e5)
        for powerpack_thermal_simulator in self.powerpack_thermal_simulators:
            li_hash += hash(powerpack_thermal_simulator)
        return li_hash

    def Dict(self):
        dict_ = self.__dict__.copy()
        dict_['powerpack_thermal_simulators'] = [pts.Dict() for pts in self.powerpack_thermal_simulators]
        if self.powerpack_mechanical_simulators != []:
            dict_['powerpack_mechanical_simulators'] = [mb.Dict() for mb in self.powerpack_mechanical_simulators]
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        longitudinal_tolerances = [a for a in dict_['longitudinal_tolerances']]
        transversal_tolerances = [b for b in dict_['transversal_tolerances']]
        bounds_grids = dict_['bounds_grids']
        pack_size = dict_['pack_size']
        cp_thickness = dict_['cp_thickness']
        module_gap = dict_['module_gap']
        rail_specs = dict_['rail_specs']
        rail_number = (dict_['n_lr'], dict_['n_tr'])
        powerpack_thermal_simulators = [PowerPackThermalSimulator.DictToObject(d)\
                          for d in dict_['powerpack_thermal_simulators']]
        powerpack_mechanical_simulators = None
        if 'powerpack_mechanical_simulators' in dict_:
            if len(dict_['powerpack_mechanical_simulators']) > 0:
                powerpack_mechanical_simulators = [PowerPackMechanicalSimulator.DictToObject(d)\
                          for d in dict_['powerpack_mechanical_simulators']]
        allow_empty_grid = None
        if 'allow_empty_grid' in dict_:
            allow_empty_grid = dict_['allow_empty_grid']

        gbo = cls(bounds_grids=bounds_grids,
                  pack_size=pack_size,
                  cp_thickness=cp_thickness,
                  module_gap=module_gap,
                  rail_specs=rail_specs,
                  rail_number=rail_number,
                  longitudinal_tolerances=longitudinal_tolerances,
                  transversal_tolerances=transversal_tolerances,
                  powerpack_thermal_simulators=powerpack_thermal_simulators,
                  allow_empty_grid=allow_empty_grid,
                  powerpack_mechanical_simulators=powerpack_mechanical_simulators)
        return gbo

