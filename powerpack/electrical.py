import matplotlib.pyplot as plt
import numpy as npy
from scipy import interpolate
from dessia_common import DessiaObject, dict_merge
from copy import deepcopy
import volmdlr as vm
from volmdlr import primitives3D
import math

class ElecAnalysis(DessiaObject):
    _standalone_in_db = True
    _jsonschema = {
        "definitions": { },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.ElecAnalysis Base Schema",
        "required": [],
        "properties": {
            'electric_range': {
                "type": "number",
                "title" : "Electric Range",
                "examples": [1],
                "editable": False,
                "description": "Electric Range",
                },
            'load_time': {
                "type": "number",
                "title" : "Load Time",
                "examples": [1],
                "editable": False,
                "description": "Load Time",
                },
            'number_cells': {
                "type": "number",
                "title" : "Cell Number",
                "examples": [1],
                "editable": False,
                "description": "Cell Number",
                },
            'number_modules': {
                "type": "number",
                "title" : "Module Number",
                "examples": [1],
                "editable": False,
                "description": "Module Number",
                },
            'voltage_max': {
                "type": "number",
                "title" : "voltage max",
                "examples": [1],
                "editable": False,
                "description": "voltage max",
                },
            'voltage_min': {
                "type": "number",
                "title" : "voltage min",
                "examples": [1],
                "editable": False,
                "description": "voltage min",
                },
            'voltage_mean': {
                "type": "number",
                "title" : "voltage mean",
                "examples": [1],
                "editable": False,
                "description": "voltage mean",
                },
            'current_max': {
                "type": "number",
                "title" : "current max",
                "examples": [1],
                "editable": False,
                "description": "current max",
                },
            'current_min': {
                "type": "number",
                "title" : "current min",
                "examples": [1],
                "editable": False,
                "description": "current min",
                },
            'current_mean': {
                "type": "number",
                "title" : "current mean",
                "examples": [1],
                "editable": False,
                "description": "current mean",
                },
            }
        }

    def __init__(self, electric_range=None, load_time=None,
                 number_cells=None, number_modules=None,
                 voltage_max=None, voltage_min=None, voltage_mean=None,
                 current_max=None, current_min=None, current_mean=None,
                 name=''):
        self.electric_range = electric_range
        self.load_time = load_time
        self.number_cells = number_cells
        self.number_modules = number_modules
        self.voltage_max = voltage_max
        self.voltage_min = voltage_min
        self.voltage_mean = voltage_mean
        self.current_max = current_max
        self.current_min = current_min
        self.current_mean = current_mean

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equa = (self.electric_range == other.electric_range
                and self.load_time == other.load_time
                and self.number_cells == other.number_cells
                and self.number_modules == other.number_modules
                and self.voltage_max == other.voltage_max
                and self.voltage_min == other.voltage_min
                and self.voltage_mean == other.voltage_mean
                and self.current_max == other.current_max
                and self.current_min == other.current_min
                and self.current_mean == other.current_mean)
        return equa

    def __hash__(self):
        li_hash = int(self.electric_range) + int(self.number_cells) + int(self.voltage_max) + int(self.current_max)
        return li_hash

    def to_dict(self):
        """
        Export object in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'electric_range' : self.electric_range,
                      'load_time' : self.load_time,
                      'number_cells' : self.number_cells,
                      'number_modules' : self.number_modules,
                      'voltage_max' : self.voltage_max,
                      'voltage_min' : self.voltage_min,
                      'voltage_mean' : self.voltage_mean,
                      'current_max' : self.current_max,
                      'current_min' : self.current_min,
                      'current_mean' : self.current_mean})
        return dict_

    @classmethod
    def dict_to_object(cls, dict_):
        """
        Generate an Evolution object

        :param dict_: Evolution dictionnary generate with the Dict method
        """
        if dict_ != None:
            electric_range = None
            if 'electric_range' in dict_:
                if dict_['electric_range'] is not None:
                    electric_range = dict_['electric_range']
            load_time = None
            if 'load_time' in dict_:
                if dict_['load_time'] is not None:
                    load_time = dict_['load_time']
            number_cells = None
            if 'number_cells' in dict_:
                if dict_['number_cells'] is not None:
                    number_cells = dict_['number_cells']
            number_modules = None
            if 'number_modules' in dict_:
                if dict_['number_modules'] is not None:
                    number_modules = dict_['number_modules']
            voltage_max = None
            if 'voltage_max' in dict_:
                if dict_['voltage_max'] is not None:
                    voltage_max = dict_['voltage_max']
            voltage_min = None
            if 'voltage_min' in dict_:
                if dict_['voltage_min'] is not None:
                    voltage_min = dict_['voltage_min']
            voltage_mean = None
            if 'voltage_mean' in dict_:
                if dict_['voltage_mean'] is not None:
                    voltage_mean = dict_['voltage_mean']
            current_max = None
            if 'current_max' in dict_:
                if dict_['current_max'] is not None:
                    current_max = dict_['current_max']
            current_min = None
            if 'current_min' in dict_:
                if dict_['current_min'] is not None:
                    current_min = dict_['current_min']
            current_mean = None
            if 'current_mean' in dict_:
                if dict_['current_mean'] is not None:
                    current_mean = dict_['current_mean']
            return cls(electric_range=electric_range, load_time=load_time,
                       number_cells=number_cells, number_modules=number_modules,
                       voltage_max=voltage_max, voltage_min=voltage_min,
                       voltage_mean=voltage_mean,
                       current_max=current_max, current_min=current_min,
                       current_mean=current_mean,
                       name=dict_['name'])
        return ElecAnalysis()


class Evolution(DessiaObject):
    """
    Defines a generic evolution

    :param evolution: float list
    :type evolution: list

    :Example:

    >>> import dessia_common as dc
    >>> import powerpack.optimization.electrical as elec
    >>> evol = elec.Evolution(evolution = [0, 0.2, 0.4, 0.6, 0.8, 1])
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": { },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.Evolution Base Schema",
        "required": ["evolution"],
        "properties": {
            "evolution": {
                "type": "array",
                "title" : "Evolution",
                "items": {
                    "type": "number",
                    "editable" : True,
                    "step" : 0.001,
                    },
                "editable": True,
                "description": "Evolution",
                "order": 1
                }
            }
        }

    def __init__(self, evolution=None, name=''):
        # TODO Why None?
        if evolution is None:
            evolution = []
        self.evolution = evolution

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        return self.evolution == other.evolution

    def __hash__(self):
        li_hash = int(hash(tuple(self.evolution)) % 1e8)
        return li_hash

    def _display_angular(self):
        if self.name == '':
            label = 'Evolution'
        else:
            label = self.name
        displays = [{'angular_component': 'graph',
                      'x_label': 'increment',
                      'show_table': True,
                      'datasets': [
                          {
                              'label': label,
                              'color': None,
                              'values': [{'x': x, 'y': y} \
                                         for x, y \
                                         in enumerate(self.evolution)]
                          },
                      ]
                      }]
        return displays

    def Copy(self):
        """
        Returns a copy of a Evolution object
        """
        evol = Evolution(self.evolution)
        return evol

    def update(self, evolution):
        """
        Update the evolution list
        """
        self.evolution = evolution

    def Dict(self):
        """
        Export object in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        if self.evolution != []:
            dict_['evolution'] = self.evolution
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an Evolution object

        :param dict_: Evolution dictionnary generate with the Dict method
        """
        if dict_ != None:
            evolution = None
            if 'evolution' in dict_:
                if dict_['evolution'] is not None:
                    evolution = dict_['evolution']
            return cls(evolution=evolution, name=dict_['name'])
        return Evolution(name=dict_['name'])

class CombinationEvolution(DessiaObject):
    """
    Defines a combination of evolutions

    :param evolution1: list of Evolution object define the "1" axis
    :type evolution1: [powerpack.electrical.Evolution]
    :param evolution2: list of Evolution object define the "2" axis
    :type evolution2: [powerpack.electrical.Evolution]
    :param title1: title of the "1" axis
    :type title1: string
    :param title2: title of the "2" axis
    :type title2: string

    :Example:

    >>> import dessia_common as dc
    >>> import powerpack.optimization.electrical as elec
    >>> charge = elec.CombinationEvolution(evolution1 = [evol_soc1, evol_soc2],
                                           evolution2 = [evol_ocv1, evol_ocv2],
                                           title1 = 'Soc',
                                           title2 = 'OCV')
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.electrical.CombinationEvolution Base Schema",
        "required": ['evolution1', 'evolution2'],
        "properties": {
            'evolution1': {
                "type": "array",
                "title" : "Evolution x",
                "order": 3,
                "editable": True,
                "description": "X evolutions",
                "items" : {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.Evolution"]
                    },
                },
            'evolution2': {
                "type": "array",
                "title" : "Evolution y",
                "order": 4,
                "editable": True,
                "description": "Y evolutions",
                "items" : {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.Evolution"]
                    },
                },
            'title1': {
                "type": "string",
                "title" : "Title x",
                "default_value" : "x",
                "examples": ['Title1'],
                "editable": True,
                "description": "Title",
                "order": 1
                },
            'title2': {
                "type": "string",
                "title" : "Title y",
                "default_value" : "y",
                "examples": ['Title2'],
                "editable": True,
                "description": "Title",
                "order": 2
                }
            }
        }

    def __init__(self, evolution1, evolution2, title1='x', title2='y', name=''):

        self.evolution1 = evolution1
        self.evolution2 = evolution2

        self.GenereXY()

        self.title1 = title1
        self.title2 = title2

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = True
        if hasattr(self, 'evolution1'):
            for evol, other_evol in zip(self.evolution1, other.evolution1):
                equal = (equal and evol == other_evol)
        if hasattr(self, 'evolution2'):
            for evol, other_evol in zip(self.evolution2, other.evolution2):
                equal = (equal and evol == other_evol)
        return equal

    def __hash__(self):
        li_hash = 0
        for evol in self.evolution1:
            li_hash += hash(evol)
        for evol in self.evolution2:
            li_hash += hash(evol)
        return li_hash

    def _display_angular(self):
        displays = [{'angular_component': 'graph',
                      'x_label': self.title1,
                      'show_table': True,
                      'datasets': [
                          {
                              'label': self.title2,
                              'color': None,
                              'values': [{'x': x, 'y': y} \
                                         for x, y \
                                         in zip(self.x, self.y)]
                          },
                      ]
                      }]
        return displays

    def update(self, evol1, evol2):
        """
        Update the CombinationEvolution object

        :param evol1: list
        :param evol2: list
        """
        for evolution, ev1 in zip(self.evolution1, evol1):
            evolution.update(ev1)
        for evolution, ev2 in zip(self.evolution2, evol2):
            evolution.update(ev2)
        self.GenereXY()

    def Copy(self):
        """
        Returns a copy of a CombinationEvolution object
        """
        evol1 = []
        for ev in self.evolution1:
            evol1.append(ev.Copy())
        evol2 = []
        for ev in self.evolution2:
            evol2.append(ev.Copy())
        ce = CombinationEvolution(evol1, evol2, title1 = self.title1, title2 = self.title2)
        return ce

    def GenereXY(self):
        x, y = [], []
        for evol in self.evolution1:
            x = x + evol.evolution
        for evol in self.evolution2:
            y = y + evol.evolution
        self.x = x
        self.y = y

    def Dict(self):
        """
        Export object in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'evolution1' : [e.to_dict() for e in self.evolution1],
                      'evolution2' : [e.to_dict() for e in self.evolution2],
                      'title1' : self.title1,
                      'title2' : self.title2,
                      'x' : self.x,
                      'y' : self.y})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an CombinationEvolution object

        :param dict_: CombinationEvolution dictionnary generate with the Dict method
        """
        li_evolution1 = [Evolution.DictToObject(evolution1)\
                         for evolution1 in dict_['evolution1']]
        li_evolution2 = [Evolution.DictToObject(evolution2)\
                         for evolution2 in dict_['evolution2']]

        evol = cls(evolution1=li_evolution1,
                   evolution2=li_evolution2,
                   title1=dict_['title1'],
                   title2=dict_['title2'],
                   name=dict_['name'])
        return evol

class PowerProfile(DessiaObject):
    """
    Defines power profile specifications

    :param soc_init: initial soc of electrical cell
    :type soc_init: As
    :param combination_evolutions: list of CombinationEvolution define the power evolution
    :type combination_evolutions: [powerpack.electrical.CombinationEvolution]
    :param power_accuracy: exit condition based on power tracking accuracy
    :type power_accuracy: %
    :param loop: repeat of the combination_evolutions profile
    :type loop: boolean
    :param max_loop: exit condition based on maximum repeat number of the combination_evolutions profile
    :type max_loop: integer
    :param soc_end: exit condition based on final soc of electrical cell
    :type soc_end: As
    :param charger: use charge_specs of electrical cell
    :type charger: boolean
    :param use_selection: use the achievement status of the power profile to validate the PowerPackElectricSimulator simulation
    :type use_selection: boolean

    :Example:

    >>> import dessia_common as dc
    >>> import powerpack.optimization.electrical as elec
    >>> load_bat = elec.PowerProfile(soc_init = 0.05*180000,
                                combination_evolutions = [ce_load],
                                loop = True,
                                soc_end = 0.95*180000,
                                charger = True)
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.electrical.PowerProfile Base Schema",
        "required": ['soc_init', 'combination_evolutions'],
        "properties": {
            'combination_evolutions': {
                "type": "array",
                "title" : "Combinations evolutions",
                "order": 8,
                "editable": True,
                "description": "Combination evolutions",
                "items" : {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.CombinationEvolution"]
                    }
                },
            'soc_init': {
                "type": "number",
                "title" : "Initial SoC",
                'minimum': 0,
                "step" : 0.001,
                "examples": [0.1],
                "editable": True,
                "description": "Soc init",
                "unit": "%",
                "order": 1
                },
            'power_accuracy': {
                "type": "number",
                "title" : "Power Accuracy",
                'minimum': 0,
                'maximum': 2,
                "step" : 0.01,
                "examples": [0.2],
                "editable": True,
                "description": "Power accuracy",
                "unit": "%",
                "order": 3
                },
            'soc_end': {
                "type": "number",
                "title" : "Final SoC",
                'minimum': 0,
                "maximum" : 1,
                "step" : 0.01,
                "examples": [0.1],
                "editable": True,
                "description": "Soc end",
                "unit": "%",
                "order": 2
                },
            'max_loop': {
                "type": "number",
                "title" : "Max loop",
                "step" : 1,
                "examples": [10],
                "editable": True,
                "description": "Maximum number of loops",
                "order": 5
                },
            'loop': {
                "type": "boolean",
                "title" : "Loop",
                "default_value" : False,
                "editable": True,
                "description": "Loop",
                "order": 4
                },
            'charger': {
                "type": "boolean",
                "title" : "Charger",
                "default_value" : False,
                "editable": True,
                "description": "Charger",
                "order": 6
                },
            'use_selection': {
                "type": "boolean",
                "title" : "Use selection",
                "default_value" : True,
                "editable": True,
                "description": "Use selection",
                "order": 7
                },
            },
        }

    def __init__(self, soc_init, combination_evolutions, power_accuracy=None,
                 loop=False, max_loop=None, soc_end=None, charger=False,
                 use_selection=True, name=''):

        self.combination_evolutions = combination_evolutions

        evolutions, times = [], []
        for combination_evolution in combination_evolutions:
            evolutions = evolutions + combination_evolution.y
        last_val = 0
        for num, combination_evolution in enumerate(combination_evolutions):
            if num == 0:
                temp = [i + last_val for i in combination_evolution.x]
            else:
                delta_t = times[-1] - times[-2]
                temp = [i + last_val + delta_t for i in combination_evolution.x]
            times = times + temp
            last_val = times[-1]
        self.evolutions = evolutions
        self.times = times

        self.soc_init = soc_init
        self.power_accuracy = power_accuracy
        self.loop = loop
        self.max_loop = max_loop
        self.soc_end = soc_end
        # TODO: check name
        self.charger = charger
        self.use_selection = use_selection

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = (self.soc_init == other.soc_init
                 and self.power_accuracy == other.power_accuracy
                 and self.loop == other.loop
                 and self.max_loop == other.max_loop
                 and self.soc_end == other.soc_end
                 and self.charger == other.charger
                 and self.use_selection == other.use_selection)
        for ce, other_ce in zip(self.combination_evolutions, other.combination_evolutions):
            equal = equal and ce == other_ce
        return equal

    def __hash__(self):
        li_hash = 0
        for ce in self.combination_evolutions:
            li_hash += hash(ce)
        li_hash += hash(self.power_accuracy) + hash(self.charger)
        return li_hash

    def _display_angular(self):
        datasets = []
        for combination_evolution in self.combination_evolutions:
            datasets.append({
                            'label': combination_evolution.title2,
                            'color': None,
                            'values': [{'x': x, 'y': y} \
                                       for x, y \
                                       in zip(combination_evolution.x, combination_evolution.y)]
                            })
        displays = [{'angular_component': 'graph',
                      'x_label': 'Power Profile ' + self.name,
                      'show_table': False,
                      'datasets': datasets,
                      }]
        return displays

    def Dict(self):
        """
        Export object in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        combination_evolutions = [ce.to_dict() for ce in self.combination_evolutions]
        dict_.update({'soc_init' : self.soc_init,
                      'loop' : self.loop,
                      'charger' : self.charger,
                      'use_selection' : self.use_selection,
                      'combination_evolutions' : combination_evolutions})
        if self.power_accuracy is not None:
            dict_['power_accuracy'] = self.power_accuracy
        if self.max_loop is not None:
            dict_['max_loop'] = self.max_loop
        if self.soc_end is not None:
            dict_['soc_end'] = self.soc_end
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an PowerProfile object

        :param dict_: PowerProfile dictionnary generate with the Dict method
        """
        p_evol = [CombinationEvolution.dict_to_object(ce)\
                  for ce in dict_['combination_evolutions']]

        if 'power_accuracy' in dict_:
            power_accuracy = dict_['power_accuracy']
        else:
            power_accuracy = None

        if 'max_loop' in dict_:
            max_loop = dict_['max_loop']
        else:
            max_loop = None

        if 'soc_end' in dict_:
            soc_end = dict_['soc_end']
        else:
            soc_end = None

        profile = cls(combination_evolutions=p_evol, soc_init=dict_['soc_init'],
                      power_accuracy=power_accuracy, loop=dict_['loop'],
                      max_loop=max_loop, soc_end=soc_end, charger=dict_['charger'],
                      use_selection=dict_['use_selection'], name=dict_['name'])
        return profile

class CombinationPowerProfile(DessiaObject):
    """
    Defines power profile combination

    :param power_profiles: list of PowerProfile
    :type power_profiles: [powerpack.electrical.PowerProfile]

    :Example:

    >>> import dessia_common as dc
    >>> import powerpack.optimization.electrical as elec
    >>> comb_profile= elec.CombinationPowerProfile([wltp_bat])
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.electrical.CombinationPowerProfile Base Schema",
        "required": ['power_profiles'],
        "properties": {
            'power_profiles': {
                "type": "array",
                "title" : "Power profiles",
                "order": 1,
                "editable": True,
                "description": "Power profiles",
                "items" : {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.PowerProfile"]
                    },
                }
            }
        }

    def __init__(self, power_profiles, name=''):
        self.power_profiles = power_profiles

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = True
        for pp, other_pp in zip(self.power_profiles, other.power_profiles):
            equal = equal and pp == other_pp
        return equal

    def __hash__(self):
        li_hash = 0
        for pp in self.power_profiles:
            li_hash += int(hash(pp) % 34e4)
        li_hash
        return li_hash

    def _display_angular(self):
        displays= []
        for power_profile in self.power_profiles:
            displays.extend(power_profile._display_angular())
        return displays

    def Dict(self):
        """
        Export object in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_['power_profiles'] = [pp.to_dict() for pp in self.power_profiles]
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an CombinationPowerProfile object

        :param dict_: CombinationPowerProfile dictionnary generate with the Dict method
        """
        p_evol =[PowerProfile.DictToObject(power_profile)\
                 for power_profile in dict_['power_profiles']]
        return cls(power_profiles=p_evol, name=dict_['name'])

class SpecsEvolution(DessiaObject):
    """
    Defines specification evolutions for electric cell

    :param temperature: temperature of the current specification
    :type temperature: K
    :param charge: CombinationEvolution define the specification evolution in charge mode
    :type charge: powerpack.electrical.CombinationEvolution
    :param discharge: CombinationEvolution define the specification evolution in discharge mode
    :type discharge: powerpack.electrical.CombinationEvolution
    :param title: name of the "2" axis of the CombinationEvolution object
    :type title: string

    :Example:

    >>> import dessia_common as dc
    >>> import powerpack.optimization.electrical as elec
    >>> se_rint = elec.SpecsEvolution(temperature = 298.15,
                                      charge = ce_rint_charge,
                                      discharge = ce_rint_discharge,
                                      title = 'Rint')
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.electrical.SpecsEvolution Base Schema",
        "required": ['temperature', 'charge'],
        "properties": {
            'charge': {
                "type" : "object",
                "title" : "Charge",
                "classes" : ["powerpack.electrical.CombinationEvolution"],
                "description" : "Charge",
                "editable" : True,
                "order" : 3
                },
            'discharge': {
                "type" : "object",
                "title" : "Discharge",
                "classes" : ["powerpack.electrical.CombinationEvolution"],
                "description" : "Discharge",
                "editable" : True,
                "order" : 4
                },
            'temperature': {
                "type": "number",
                "title" : "Temperature",
                'minimum': 0,
                "step" : 0.001,
                "examples": [183],
                "editable": True,
                "description": "Temperature",
                "unit": "K",
                "order": 2
                },
            'title': {
                "type": "string",
                "title" : "Title",
                "examples": ['Title'],
                "editable": True,
                "description": "Title",
                "order": 1
                }
            }
        }

    def __init__(self, temperature, charge, discharge=None, title='', name=''):
        self.temperature = temperature
        self.charge = charge
        if discharge is not None:
            self.discharge = discharge
        else:
            evolution1 = Evolution()
            evolution2 = Evolution()
            self.discharge = CombinationEvolution(evolution1=[evolution1],
                                                  evolution2=[evolution2])
        self.title = title

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = self.charge == other.charge and self.discharge == other.discharge
        return equal

    def __hash__(self):
        li_hash = 0
        if self.charge is not None:
            li_hash += hash(self.charge)
        if self.discharge is not None:
            li_hash += hash(self.discharge)
        return li_hash

    # def _display_angular(self):
    #
    #
    #     displays = [{
    #         'angular_component': 'app-evolution2d-complex',
    #         'object_class': 'powerpack.electrical.SpecsEvolution',
    #         'evolution_x': [[['discharge', 'all'], ['evolution1', 'add'], ['evolution', 'all']],
    #                         [['charge', 'all'], ['evolution1', 'add'], ['evolution', 'all']]],
    #          'evolution_y': [[['discharge', 'all'], ['evolution2', 'add'], ['evolution', 'all']],
    #                          [['charge', 'all'], ['evolution2', 'add'], ['evolution', 'all']]],
    #          'cumul_x': False,
    #          'cumul_y': True,
    #          'label': [{'value': None, 'prefix': None, 'suffix': None, 'key': True}, {}, {}],
    #          'axe_x': [{'value': 'title1', 'prefix': None, 'suffix': None, 'key': False}, {}, {}],
    #          'axe_y': [{'value': 'title2', 'prefix': None, 'suffix': None, 'key': False}, {}, {}]
    #          }]
    #     return displays

    def _display_angular(self):
        displays = [{'angular_component': 'graph',
                      'x_label': 'Specs Evolution ' + self.name,
                      'show_table': False,
                      'datasets': [{
                                    'label': 'charge',
                                    'color': None,
                                    'values': [{'x': x, 'y': y} \
                                               for x, y \
                                               in zip(self.charge.x, self.charge.y)]
                                    },
                                    {
                                    'label': 'discharge',
                                    'color': None,
                                    'values': [{'x': x, 'y': y} \
                                                for x, y \
                                                in zip(self.discharge.x, self.discharge.y)]
                                    }
                      ],
                      }]
        return displays

    def Dict(self):
        """
        Export object in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'charge' : self.charge.Dict(),
                      'discharge' : self.discharge.Dict(),
                      'title' : self.title,
                      'temperature' : self.temperature})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an SpecsEvolution object

        :param dict_: SpecsEvolution dictionnary generate with the Dict method
        """
        if dict_['discharge'] is not None:
            evol = cls(temperature=dict_['temperature'],
                       charge=CombinationEvolution.DictToObject(dict_['charge']),
                       discharge=CombinationEvolution.DictToObject(dict_['discharge']),
                       title=dict_['title'],
                       name=dict_['name'])
        else:
            evol = cls(temperature=dict_['temperature'],
                       charge=CombinationEvolution.DictToObject(dict_['charge']),
                       title=dict_['title'],
                       name=dict_['name'])
        return evol


class CombinationSpecsEvolution(DessiaObject):
    """
    Defines specification evolutions  combination for electric cell

    :param specs_evolutions: SpecsEvolution list define the specification at several temperature
    :type specs_evolutions: [powerpack.electrical.SpecsEvolution]
    :param title: name of the "2" axis of the CombinationSpecsEvolution object
    :type title: string

    :Example:

    >>> import dessia_common as dc
    >>> import powerpack.optimization.electrical as elec
    >>> cse_rint = elec.CombinationSpecsEvolution(specs_evolutions = [se_rint25deg, se_rint40deg],
                                                  title = 'Rint')
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.electrical.CombinationSpecsEvolution Base Schema",
        "required": ['specs_evolutions'],
        "properties": {
            'specs_evolutions': {
                "type": "array",
                "title" : "Specification evolutions",
                "order": 2,
                "editable": True,
                "description": "Specification evolutions",
                "items": {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.SpecsEvolution"]
                    },
                },
            'title': {
                "type": "string",
                "title" : "Title",
                "examples": ['Title'],
                "editable": True,
                "description": "Title",
                "order": 1
                }
            }
        }

    def __init__(self, specs_evolutions, title='', name=''):

        self.specs_evolutions = specs_evolutions
        self.title = title
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_cell):
        equal = True
        for spec, other_spec in zip(self.specs_evolutions, other_cell.specs_evolutions):
            equal = (equal and spec == other_spec)
        return equal

    def __hash__(self):
        li_hash = 0
        for spec in self.specs_evolutions:
            li_hash += hash(spec)
        return li_hash

    def _display_angular(self):
        datasets= []
        for specs_evolution in self.specs_evolutions:
            datasets.extend([{
                            'label': 'charge' + ' Temp {}'.format(int(specs_evolution.temperature)),
                            'color': None,
                            'values': [{'x': x, 'y': y} \
                                       for x, y \
                                       in zip(specs_evolution.charge.x, specs_evolution.charge.y)]
                            },
                            {
                            'label': 'discharge' + ' Temp {}'.format(int(specs_evolution.temperature)),
                            'color': None,
                            'values': [{'x': x, 'y': y} \
                                        for x, y \
                                        in zip(specs_evolution.discharge.x, specs_evolution.discharge.y)]
                            }
                      ])

        displays= [{'angular_component': 'graph',
                  'x_label': 'Combination Specs Evolution ' + self.name,
                  'show_table': False,
                  'datasets': datasets}]
        return displays

    def Dict(self):
        """
        Export object in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'specs_evolutions' : [se.to_dict() for se in self.specs_evolutions],
                      'title' : self.title})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an CombinationSpecsEvolution object

        :param dict_: CombinationSpecsEvolution dictionnary generate with the Dict method
        """
        if dict_ != None:
            li_specs_evolution = [SpecsEvolution.dict_to_object(se)\
                                  for se in dict_['specs_evolutions']]
            return cls(specs_evolutions=li_specs_evolution,
                       title=dict_['title'],
                       name=dict_['name'])
        return CombinationSpecsEvolution()

class Cell(DessiaObject):
    """
    Defines an electric cell object

    :param rated_capacity: Cell capacity
    :type rated_capacity: As
    :param ocv_specs: CombinationSpecsEvolution object define the ocv evolution with the soc at several temperature
    :type ocv_specs: powerpack.electrical.CombinationSpecsEvolution
    :param rint_specs: CombinationSpecsEvolution object define the rint evolution with the soc at several temperature
    :type rint_specs: powerpack.electrical.CombinationSpecsEvolution
    :param limits_voltage: Dictionnary define the voltage limit
    :type limits_voltage: {'charge': {'minimum': value, 'maximum': value},
                           'discharge': {'minimum': value, 'maximum': value}}
    :param limits_current: Dictionnary define the current limit
    :type limits_current: {'charge': {'minimum': value, 'maximum': value},
                           'discharge': {'minimum': value, 'maximum': value}}
    :param limits_soc: Dictionnary define the soc limit
    :type limits_soc: {'minimum': value, 'maximum': value}
    :param charge_specs: CombinationSpecsEvolution object define the cell current evolution with the soc in charger mode
    :type charge_specs: powerpack.electrical.CombinationSpecsEvolution
    :param size: Tuple that represents size of cell in global frame
    :type size: (x, y, z) mm
    :param mass: Mass of cell
    :type mass: kg
    :param thermal_transfert_specs: list to define thermal transfert evolution vs cell temperature
    :type thermal_transfert_specs: [powerpack.electrical.CombinationEvolution]

    :Example:

    >>> import powerpack.electrical as elec
    >>> evol_soc = elec.Evolution(evolution = [0, 0.2, 0.4, 0.6, 0.8, 1])
    >>> evol_ocv_charge = elec.Evolution(evolution = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3])
    >>> ce_ocv_charge = elec.CombinationEvolution(evolution1 = [evol_soc],
                                                  evolution2 = [evol_ocv_charge],
                                                  title1 = 'Soc',
                                                  title2 = 'OCV')
    >>> evol_ocv_discharge = elec.Evolution(evolution = [0.85, 0.75, 0.65, 0.55, 0.45, 0.35])
    >>> ce_ocv_discharge = elec.CombinationEvolution(evolution1 = [evol_soc],
                                                     evolution2 = [evol_ocv_discharge],
                                                     title1 = 'Soc',
                                                     title2 = 'OCV')
    >>> se_ocv = elec.SpecsEvolution(temperature = 298.15,
                                     charge = ce_ocv_charge,
                                     discharge = ce_ocv_discharge,
                                     title = 'OCV')
    >>> cse_ocv = elec.CombinationSpecsEvolution(specs_evolutions = [se_ocv],
                                                 title = 'OCV')
    >>> evol_rint_charge = elec.Evolution(evolution = [0.08, 0.07, 0.06, 0.05, 0.04, 0.03])
    >>> ce_rint_charge = elec.CombinationEvolution(evolution1 = [evol_soc],
                                                  evolution2 = [evol_rint_charge],
                                                  title1 = 'Soc',
                                                  title2 = 'Rint')
    >>> evol_rint_discharge = elec.Evolution(evolution = [0.085, 0.075, 0.065, 0.055, 0.045, 0.035])
    >>> ce_rint_discharge = elec.CombinationEvolution(evolution1 = [evol_soc],
                                                     evolution2 = [evol_rint_discharge],
                                                     title1 = 'Soc',
                                                     title2 = 'Rint')
    >>> se_rint = elec.SpecsEvolution(temperature = 298.15,
                                     charge = ce_rint_charge,
                                     discharge = ce_rint_discharge,
                                     title = 'Rint')
    >>> cse_rint = elec.CombinationSpecsEvolution(specs_evolutions = [se_rint],
                                                 title = 'Rint')
    >>> soc_charger = elec.Evolution(evolution = [0, 0.2, 0.5, 1])
    >>> current_charger = elec.Evolution(evolution = [60, 60, 30, 10])
    >>> ce_charger = elec.CombinationEvolution(evolution1 = [soc_charger],
                                               evolution2 = [current_charger],
                                               title1 = 'Soc',
                                               title2 = 'Current')
    >>> se_charger = elec.SpecsEvolution(temperature = 298.15,
                                         charge = ce_charger,
                                         title = 'Current')
    >>> cce_charger = elec.CombinationSpecsEvolution(specs_evolutions = [se_charger],
                                                     title = 'Current')
    >>> evol_temperature = elec.Evolution(evolution = [270, 290, 310, 330])
    >>> evol_thermal_trans1 = elec.Evolution(evolution = [0.1, 0.5, 1, 1.5])
    >>> evol_thermal_trans2 = elec.Evolution(evolution = [0.2, 0.6, 1.1, 1.6])
    >>> evol_thermal_trans3 = elec.Evolution(evolution = [0.3, 0.7, 1.2, 1.7])
    >>> thermal_transfert1 = elec.CombinationEvolution(evolution1 = [evol_temperature],
                                               evolution2 = [evol_thermal_trans1],
                                               title1 = 'Temperature',
                                               title2 = 'Thermal transfert')
    >>> thermal_transfert2 = elec.CombinationEvolution(evolution1 = [evol_temperature],
                                               evolution2 = [evol_thermal_trans2],
                                               title1 = 'Temperature',
                                               title2 = 'Thermal transfert')
    >>> thermal_transfert3 = elec.CombinationEvolution(evolution1 = [evol_temperature],
                                               evolution2 = [evol_thermal_trans3],
                                               title1 = 'Temperature',
                                               title2 = 'Thermal transfert')
    >>> Cell1 = elec.Cell(rated_capacity=180000,
                          ocv_specs=cse_ocv,
                          rint_specs=cse_rint,
                          limits_voltage={'charge': {'minimum': 1, 'maximum': 6},
                                          'discharge': {'minimum': 1, 'maximum': 7}},
                          limits_current={'charge': {'minimum': 0, 'maximum': 10},
                                          'discharge': {'minimum': -15, 'maximum': 0}},
                          limits_soc={'minimum': 0.005, 'maximum': 0.95},
                          charge_specs=cce_charger,
                          size=(.0287, .1482, .1025),
                          mass=1,
                          thermal_transfert_specs = [thermal_transfert1, thermal_transfert2, thermal_transfert3])
    >>> Cell1.PlotSpecs()
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.Cell Base Schema",
        "required": ["rated_capacity", "ocv_specs", "rint_specs", "limits_voltage",
                     "limits_current", "limits_soc", "charge_specs", "size", "mass",
                     "thermal_transfert_specs"],
        "properties": {
            "rated_capacity" : {
                "type" : "number",
                "title" : "Rated capacity",
                "minimum" : 0,
                "examples" : [18000],
                "editable" : True,
                "description" : "Rated capacity",
                "step" : 1,
                "unit" : "Ah",
                "order" : 1
                },
            "ocv_specs" : {
                "type" : "object",
                "title" : "OCV Specifications",
                "classes" : ["powerpack.electrical.CombinationSpecsEvolution"],
                "unit" : "V",
                "description" : "OCV specification",
                "editable" : True,
                "order" : 2
                },
            "rint_specs" : {
                "type" : "object",
                "title" : "Internal Resistance Specifications",
                "classes" : ["powerpack.electrical.CombinationSpecsEvolution"],
                "unit" : "ohm",
                "description" : "Rint specification",
                "editable" : True,
                "order" : 3
                },
            "limits_voltage" : {
                # !!! Should we use limits dataclass here ?
                "type" : "object",
                "title" : "Voltage Limitations",
                "order" : 7,
                "required" : ["charge", "discharge"],
                "editable" : True,
                "properties" : {
                    "charge" : {
                        "type" : "object",
                        "editable" : True,
                        "properties" : {
                            "minimum" : {
                                "type" : "number",
                                "editable" : True,
                                "step" : 0.001,
                                "minimum" : 0,
                                "unit" : "V"
                                },
                            "maximum" : {
                                "type" : "number",
                                "editable" : True,
                                "step" : 0.001,
                                "minimum" : 0,
                                "unit" : "V"
                                }
                            }
                        },
                    "discharge" : {
                        "type" : "object",
                        "editable" : True,
                        "properties" : {
                            "minimum" : {
                                "type" : "number",
                                "editable" : True,
                                "step" : 0.001,
                                "minimum" : 0,
                                "unit" : "V"},
                            "maximum" : {
                                "type" : "number",
                                "editable" : True,
                                "step" : 0.001,
                                "minimum" : 0,
                                "unit" : "V"
                                }
                            }
                        }
                    }
                },
            "limits_current" : {
                "type" : "object",
                "title" : "Current Limitations",
                "order" : 8,
                "required" : ["charge", "discharge"],
                "editable" : True,
                "properties" : {
                    "charge" : {
                        "type" : "object",
                        "editable" : True,
                        "properties" : {
                            "minimum" : {
                                "type" : "number",
                                "editable" : True,
                                "step" : 0.001,
                                "minimum" : 0,
                                "unit" : "A"
                                },
                            "maximum" : {
                                "type" : "number",
                                "editable" : True,
                                "minimum" : 0,
                                "step" : 0.001,
                                "unit" : "A"
                                }
                            }
                        },
                    "discharge" : {
                        "type" : "object",
                        "editable" : True,
                        "properties" : {
                            "minimum" : {
                                "type" : "number",
                                "editable" : True,
                                "maximum" : 0,
                                "step" : 0.001,
                                "unit" : "A"
                                },
                            "maximum" : {
                                "type" : "number",
                                "editable" : True,
                                "step" : 0.001,
                                "maximum" : 0,
                                "unit" : "A"
                                }
                            }
                        }
                    }
                },
            "limits_soc" : {
                "type" : "object",
                "title" : "SoC Limitations",
                "order" : 6,
                "required" : ["minimum", "maximum"],
                "editable" : True,
                "properties" : {
                    "minimum" : {
                        "type" : "number",
                        "editable" : True,
                        "step" : 0.001,
                        "minimum" : 0,
                        "unit" : "%"
                        },
                    "maximum" : {
                        "type" : "number",
                        "editable" : True,
                        "step" : 0.001,
                        "minimum" : 0,
                        "unit" : "%"
                        }
                    }
                },
            "charge_specs" : {
                "type" : "object",
                "title" : "Charge Specifications",
                "classes" : ["powerpack.electrical.CombinationSpecsEvolution"],
                "unit" : "A",
                "description" : "Charger specification",
                "editable" : True,
                "order" : 9
                },
            "size" : {
                "type" : "array",
                "title" : "Cell Size",
                "order" : 4,
                "editable" : True,
                "items" : {
                    "type" : "number",
                    "editable" : True,
                    "step" : 0.0001,
                    "minimum" : 0,
                    "unit" : "m"
                    },
                "minItems" : 3,
                "maxItems" : 3
                },
            "mass" : {
                "type" : "number",
                "title" : "Cell Mass",
                "order" : 5,
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "kg",
                "editable" : True,
                "examples" : [1.200]
                },
            'thermal_transfert_specs': {
                "type": "array",
                "title" : "Thermal Transferts Specifications",
                "order": 10,
                "editable": True,
                "description": "Thermal transfert specifications",
                "items": {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.CombinationEvolution"]
                    },
                },
            }
        }

    def __init__(self, rated_capacity, ocv_specs, rint_specs,
                 limits_voltage, limits_current, limits_soc,
                 charge_specs, size, mass, thermal_transfert_specs, name=''):

        self.class_name = 'Cell'
        self.rated_capacity = rated_capacity
        self.limits_voltage = limits_voltage
        self.limits_current = limits_current
        self.limits_soc = limits_soc
        self.size = size
        self.mass = mass

        self.ocv_specs = ocv_specs
        self.rint_specs = rint_specs
        self.charge_specs = charge_specs
        self.thermal_transfert_specs = thermal_transfert_specs
        if self.__class__ is Cell:
            self.f_ocv, self.f_rint, self.f_charger, self.f_thermal_trans = self.genere_interpolate()

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_cell):
        equal = (npy.allclose(self.size,other_cell.size)
                 and self.mass == other_cell.mass
                 and self.rated_capacity == other_cell.rated_capacity
                 and self.ocv_specs == other_cell.ocv_specs
                 and self.rint_specs == other_cell.rint_specs
                 and self.charge_specs == other_cell.charge_specs)
        for (thermal_transfert_spec, other_thermal_transfert_spec) in zip(self.thermal_transfert_specs, other_cell.thermal_transfert_specs):
            equal = equal and thermal_transfert_spec == other_thermal_transfert_spec
        return equal

    def __hash__(self):
        # Proposition, see if ok of if it needs more
        size_hash = int(hash(sum(self.size)) % 1e5)
        mass_hash = int(hash(self.mass) % 87)
        capacity_hash = hash(self.rated_capacity % 9)
        specs_hash = hash(self.ocv_specs) + hash(self.rint_specs) + hash(self.charge_specs)
        hash_sum = int(size_hash + mass_hash + capacity_hash + specs_hash)
        return hash_sum

    def __setstate__(self, dict_):
        self.__dict__ = dict_
        self.f_ocv, self.f_rint, self.f_charger, self.f_thermal_trans = self.genere_interpolate()

    def __getstate__(self):
        dict_ = self.__dict__.copy()
        del dict_['f_ocv']
        del dict_['f_rint']
        del dict_['f_charger']
        del dict_['f_thermal_trans']
        return dict_

    def _display_angular(self):
        model = self.volmdlr_volume_model()
        displays = [{'angular_component': 'cad_viewer', 'data': model.babylon_data()}]
        displays += [{'angular_component': 'plot_data', 'data': self.concept_plot_data()[0]},
                     {'angular_component': 'plot_data', 'data': self.iso_plot_data()}]

        displays += self.ocv_specs._display_angular()
        displays += self.rint_specs._display_angular()
        return displays

    def genere_interpolate(self):
        f_ocv = {}
        for specs_evolution in self.ocv_specs.specs_evolutions:
            temperature = specs_evolution.temperature
            f_ocv[temperature] = {}
            charge = specs_evolution.charge
            discharge = specs_evolution.discharge
            if charge.x != [] and charge.y != []:
                f_ocv[temperature]['charge'] = interpolate.splrep(charge.x, charge.y)
            if discharge.x != [] and discharge.y != []:
                f_ocv[temperature]['discharge'] = interpolate.splrep(discharge.x, discharge.y)

        f_rint = {}
        for specs_evolution in self.rint_specs.specs_evolutions:
            temperature = specs_evolution.temperature
            f_rint[temperature] = {}
            charge = specs_evolution.charge
            discharge = specs_evolution.discharge
            if charge.x != [] and charge.y != []:
                f_rint[temperature]['charge'] = interpolate.splrep(charge.x, charge.y)
            if discharge.x != [] and discharge.y != []:
                f_rint[temperature]['discharge'] = interpolate.splrep(discharge.x, discharge.y)

        f_charger = {}
        for specs_evolution in self.charge_specs.specs_evolutions:
            temperature = specs_evolution.temperature
            charge = specs_evolution.charge
            if charge.x != [] and charge.y != []:
                f_charger[temperature] = interpolate.interp1d(charge.x, charge.y, fill_value="extrapolate")

        f_thermal_trans = []
        for thermal_transfert_spec in self.thermal_transfert_specs:
            temperature = thermal_transfert_spec.x
            thermal_transfer = thermal_transfert_spec.y
            f_thermal_trans.append(interpolate.splrep(temperature, thermal_transfer))

        return f_ocv, f_rint, f_charger, f_thermal_trans

    def Voltage(self, current, usecase, delta_t, temperature, internal_parameter_cell):
        """
        Define the voltage at the next time (t + delta_t). Update :math:`soc` and
        thermal_loss in the internal_parameter_cell object

        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param current: Current at time t + delta_t
        :type current: A
        :param usecase: String define the battery trend (charge or discharge)
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **voltage** Voltage at the time (t + delta_t)
        """
        soc_m = internal_parameter_cell.soc_m
        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint

        voltage = ocv + rint*current
        internal_parameter_cell.soc = soc_m + current*delta_t
        internal_parameter_cell.thermal_loss = rint*(current**2)

        return voltage

    def Ineq(self, usecase, delta_t, temperature, internal_parameter_cell):
        """
        Define the minimum and maximum current available at the time (t + delta_t) regards
        with cell limitation

        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param usecase: String define the battery trend (charge or discharge)
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **i_min, i_max** minimum and maximum current available at the time (t + delta_t)
        """
        soc_m = internal_parameter_cell.soc_m
        ocv = self.Eval(soc_m, temperature, usecase, self.ocv_specs, self.f_ocv)
        internal_parameter_cell.ocv = ocv
        rint = self.Eval(soc_m, temperature, usecase, self.rint_specs, self.f_rint)
        internal_parameter_cell.rint = rint

        i_min = max([self.limits_current[usecase]['minimum'],
                     (self.limits_soc['minimum']*self.rated_capacity - soc_m)/delta_t,
                     (self.limits_voltage[usecase]['minimum'] - ocv)/rint])
        i_max = min([self.limits_current[usecase]['maximum'],
                     (self.limits_soc['maximum']*self.rated_capacity - soc_m)/delta_t,
                     (self.limits_voltage[usecase]['maximum'] - ocv)/rint])

        return i_min, i_max

    def CurrentObjective(self, power, i_limits, u_limits, internal_parameter_cell):
        """
        Define the cell current to deliver a define power

        :param power: electrical cell power
        :type power: W
        :param i_limits: list define the minimum and maximum admissible current
        :type i_limits: list
        :param u_limits: list define the minimum and maximum admissible voltage
        :type u_limits: list
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **current** cell current
        """
        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint
        u0 = ocv

        return self.CurrentSearch(power, i_limits, u_limits, u0, rint)

    def CurrentSearch(self, power, i_limits, u_limits, u0, rint):

        (i_min, i_max) = i_limits
        (u_min, u_max) = u_limits
        p_min = rint*(i_min)**2 + u0*i_min
        p_max = rint*(i_max)**2 + u0*i_max

        discriminant = (u0**2 + 4*power*rint)
        if discriminant >= 0:
            i1 = (-u0 + discriminant**0.5)/(2*rint)
            i2 = (-u0 - discriminant**0.5)/(2*rint)
            if power < 0:
                if i1 < 0 and i1 >= i_min and i1 <= i_max:
                    i_optim = i1
                elif i2 < 0 and i2 >= i_min and i2 <= i_max:
                    i_optim = i2
                elif i2 > i_max:
                    i_optim = i_max
                elif i1 > i_max and i2 < i_min:
                    if p_max > 0:
                        i_optim = i_min
                    else:
                        if abs(power - p_max) < abs(power - p_min):
                            i_optim = i_max
                        else:
                            i_optim = i_min
                else:
                    i_optim = i_min
            else:
                if i1 < 0:
                    raise CurrentObjectiveError()
                else:
                    i_optim = min(i_max, i1)
                    i_optim = max(i_min, i_optim)
        else:
            power_update = -u0**2/(4*rint)# TODO: why unused?
            if power > 0:
                raise CurrentObjectiveError()
            else:
                i_optim = (-u0)/(2*rint)
                i_optim = min(i_max, i_optim)
                i_optim = max(i_min, i_optim)

        return i_optim

    def CurrentChargerEval(self, soc, temperature):

        list_temp = [specs_evolution.temperature for specs_evolution in self.charge_specs.specs_evolutions]
        temperature_interp_charge = list_temp[npy.argsort(abs(npy.array(list_temp) - temperature))[0]]
        i_max = float(self.f_charger[temperature_interp_charge](soc/self.rated_capacity))
        return i_max

    def Eval(self, soc, temperature, usecase, specs, f_specs):
        """
        Interpolation based on a CombinationSpecsEvolution object

        :param soc: Cell stage of charge
        :type soc: A.second
        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param usecase: string define the battery trend (charge or discharge)
        :param specs: CombinationSpecsEvolution object
        :type specs: powerpack.electrical.CombinationSpecsEvolution
        :param f_specs: CombinationSpecsEvolution interpolation define in the cell constructor

        """
        list_temp = [specs_evolution.temperature for specs_evolution in specs.specs_evolutions]
        temperature_interp = list_temp[npy.argsort(abs(npy.array(list_temp) - temperature))[0]]
        evaluate = float(interpolate.splev(soc/self.rated_capacity,
                                f_specs[temperature_interp][usecase]))
        return float(evaluate)

    def eval_thermal_transfer(self, temperature, face):
        """
        Interpolation of the thermal transfer

        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param face: face direction
        :type face: [0, 1, 2]

        """
        evaluate = float(interpolate.splev(temperature, self.f_thermal_trans[face]))
        return float(evaluate)

    def PlotSpecs(self, ax=None, temperature=298.15):
        """
        Plot cell specification

        :param ax: Current matplotlib graph
        :param temperature: Cell temperature
        :type temperature: Kelvin

        :returns: * **matplotlib graph1** Evolution of the ocv voltage versus the soc
                                          at a given temperature and in charge/discharge mode
                  * **matplotlib graph2** Evolution of the internal resistance versus the soc
                                          at a given temperature and in charge/discharge mode
        """
        if ax is None:
            fig = plt.figure()
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122, sharex=ax1)
        else:
            ax1, ax2 = ax

        soc = npy.linspace(0, self.rated_capacity, 100)
        ocv_charge = [self.Eval(s, temperature, 'charge', self.ocv_specs, self.f_ocv) for s in soc]
        ocv_discharge = [self.Eval(s, temperature, 'discharge', self.ocv_specs, self.f_ocv) for s in soc]

        b1, = ax1.plot(soc, ocv_charge, label='charge')
        b2, = ax1.plot(soc, ocv_discharge, label='discharge')
        ax1.set_xlabel('SoC')
        ax1.set_ylabel('Cell Voltage (V)')
        ax1.legend([b1, b2], ["charge", "discharge"], loc="upper left")

        rint_charge = [self.Eval(s, temperature, 'charge', self.rint_specs, self.f_rint) for s in soc]
        rint_discharge = [self.Eval(s, temperature, 'discharge', self.rint_specs, self.f_rint) for s in soc]

        b3, = ax2.plot(soc, rint_charge, label='charge')
        b4, = ax2.plot(soc, rint_discharge, label='discharge')
        ax2.set_xlabel('SoC')
        ax2.set_ylabel('Internal resistance (ohms)')
        ax2.legend([b3, b4], ["charge", "discharge"], loc="upper left")
        plt.show()

    def Volume(self):
        """
        Computes volume of the cell
        """
        volume = npy.prod(self.size)
        return volume

    def BasisDimensions(self, basis):
        vect_size_uvw = vm.Point3D(self.size)
        size_xyz = basis.OldCoordinates(vect_size_uvw)
        # Getting dimension of cells in (xm, ym, zm)
        return size_xyz

    def plot_data(self, frame=vm.OXYZ, stroke_width=1):
        """
        Displays a 2D representation of the cell (matplotlib)
        """

        size_xyz = self.BasisDimensions(vm.Basis3D(frame.u, frame.v, frame.w))
        plot_frame = vm.Frame3D(frame.origin,
                                size_xyz[0]*vm.X3D,
                                size_xyz[1]*vm.Y3D,
                                size_xyz[2]*vm.Z3D)

        # Projection
        block = primitives3D.Block(plot_frame)
        cell_2D = block.plot_data(vm.X3D, vm.Y3D, stroke_width=stroke_width)

        return cell_2D

    def iso_plot_data(self, frame=vm.OXYZ):
        wide = min(self.size)/2
        plot_datas = []
        plot_datas.extend(self.plot_data(frame))
        plot_datas.extend(self.plot_data(vm.Frame3D(frame.origin + vm.Point3D((0, self.size[1]/2 + self.size[2]/2 + wide, 0)), frame.u, frame.w, frame.v)))
        plot_datas.extend(self.plot_data(vm.Frame3D(frame.origin + vm.Point3D((self.size[0]/2 + self.size[2]/2 + wide, 0, 0)), frame.w, frame.v, frame.u)))
        return plot_datas

    def concept_plot_data(self, detail=True, p_init_global=vm.Point2D((0, 0)), p_end_global=vm.Point2D((1, 0)), color_box='blue'):
        blocks = [{0: [{'type': 'R', 'name': 'Rint'}, {'type': 'V', 'name': 'OCV'}]}]
        plot_datas, sup_y, inf_y = self.concept_plot_data_elem(detail, blocks, p_init_global, p_end_global, color_box)
        return plot_datas, sup_y, inf_y

    def concept_plot_data_elem(self, detail, blocks, p_init_global, p_end_global, color_box):
        delta_box = 0.05
        length_global = vm.LineSegment2D(p_init_global, p_end_global).Length()
        p_init = p_init_global.Translation(vm.Vector2D((delta_box*length_global, 0)), True)
        p_end = p_end_global.Translation(vm.Vector2D((-delta_box*length_global, 0)), True)
        length = vm.LineSegment2D(p_init, p_end).Length()

        nb_block = len(blocks)
        length_R = 0.4
        length_V = 0.1
        diam_point = length*0.005
        font_size = length*20
        p_block_init = p_init.copy()
        plot_datas = []
        sup_y = -npy.inf
        inf_y = npy.inf
        for block in blocks:
            nb_line = len(block.keys())
            if nb_line > 1:
                post_nd_init = 0.2
            else:
                post_nd_init = 0
            length_block = length/nb_block
            length_block_real = length_block - 2*post_nd_init*length_block
            p_block_init_real = p_block_init.Translation(vm.Vector2D((post_nd_init*length_block, 0)), True)
            p_block_end_real = p_block_init.Translation(vm.Vector2D(((1 - post_nd_init)*length_block, 0)), True)
            p_block_end = p_block_init.Translation(vm.Vector2D((length_block, 0)), True)
            plot_datas.append(vm.LineSegment2D(p_block_init, p_block_init_real).plot_data())
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_init.vector[0], p_block_init.vector[1])), diam_point).plot_data(color = 'black',
                              fill = 'black'))
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_init_real.vector[0], p_block_init_real.vector[1])), diam_point).plot_data(color = 'black',
                              fill = 'black'))
            for num_line, items_line in block.items():
                nb_elem = len(items_line)
                length_elem = length_block_real/(nb_elem)
                if nb_line > 1:
                    y_init = length_block_real/2.
                    pas_y = length_block_real/(nb_line - 1)
                else:
                    y_init, pas_y = 0, 0
                p_elem_past = p_block_init_real.Translation(vm.Vector2D((0, y_init - pas_y*num_line)), True)
                plot_datas.append(vm.LineSegment2D(p_block_init_real, p_elem_past).plot_data())
                for num_elem, elem in enumerate(items_line):
                    p_elem_current = p_elem_past.Translation(vm.Vector2D((length_elem, 0)), True)
                    if elem['type'] == 'R':
                        p_elem_middle = vm.Point2D.MiddlePoint(p_elem_past, p_elem_current)
                        p_elem_current_begin = p_elem_middle.Translation(vm.Vector2D((-length_elem*length_R/2, 0)), True)
                        p_elem_current_end = p_elem_middle.Translation(vm.Vector2D((length_elem*length_R/2, 0)), True)
                        length_elem_R = vm.LineSegment2D(p_elem_current_begin, p_elem_current_end).Length()
                        p1 = p_elem_current_begin.Translation(vm.Vector2D((0, length_elem_R/5)), True)
                        p2 = p1.Translation(vm.Vector2D((length_elem_R, 0)), True)
                        p3 = p2.Translation(vm.Vector2D((0, -2*length_elem_R/5)), True)
                        p4 = p3.Translation(vm.Vector2D((-length_elem_R, 0)), True)
                        plot_datas.append(vm.LineSegment2D(p_elem_current_begin, p1).plot_data())
                        plot_datas.append(vm.LineSegment2D(p1, p2).plot_data())
                        plot_datas.append(vm.LineSegment2D(p2, p3).plot_data())
                        plot_datas.append(vm.LineSegment2D(p3, p4).plot_data())
                        plot_datas.append(vm.LineSegment2D(p4, p_elem_current_begin).plot_data())

                        pt_data = {}
                        pt_data['type'] = 'text'
                        pt_data['label'] = elem['name']
                        pt_data['x_label'] = p_elem_middle.vector[0]
                        pt_data['y_label'] = p_elem_middle.vector[1]
                        pt_data['rot_label'] = 0
                        pt_data['baseline_shift'] = -0.5
                        pt_data['font_size'] = font_size
                        plot_datas.append(pt_data)

                        sup_y = max([p1.vector[1], p2.vector[1], sup_y])
                        inf_y = min([p3.vector[1], p4.vector[1], inf_y])

                    elif elem['type'] == 'V':
                        p_elem_middle = vm.Point2D.MiddlePoint(p_elem_past, p_elem_current)
                        p_elem_current_begin = p_elem_middle.Translation(vm.Vector2D((-length_elem*length_V/2, 0)), True)
                        p_elem_current_end = p_elem_middle.Translation(vm.Vector2D((length_elem*length_V/2, 0)), True)
                        length_elem_V = vm.LineSegment2D(p_elem_current_begin, p_elem_current_end).Length()
                        p1 = p_elem_current_begin.Translation(vm.Vector2D((0, length_elem_V)), True)
                        p2 = p1.Translation(vm.Vector2D((length_elem_V, 0)), True)
                        p3 = p2.Translation(vm.Vector2D((0, -2*length_elem_V)), True)
                        p4 = p3.Translation(vm.Vector2D((-length_elem_V, 0)), True)
                        plot_datas.append(vm.LineSegment2D(p_elem_current_begin, p1).plot_data())
                        plot_datas.append(vm.LineSegment2D(p2, p3).plot_data())
                        plot_datas.append(vm.LineSegment2D(p4, p_elem_current_begin).plot_data())

                        pt_data = {}
                        pt_data['type'] = 'text'
                        pt_data['label'] = elem['name']
                        pt_data['x_label'] = vm.Point2D.MiddlePoint(p3, p4).vector[0]
                        pt_data['y_label'] = vm.Point2D.MiddlePoint(p3, p4).vector[1]
                        pt_data['rot_label'] = 0
                        pt_data['baseline_shift'] = 0
                        pt_data['font_size'] = font_size
                        plot_datas.append(pt_data)

                        sup_y = max([p1.vector[1], p2.vector[1], sup_y])
                        inf_y = min([p3.vector[1], p4.vector[1], inf_y])

                    plot_datas.append(vm.LineSegment2D(p_elem_past, p_elem_current_begin).plot_data())
                    plot_datas.append(vm.LineSegment2D(p_elem_current_end, p_elem_current).plot_data())
                    p_elem_past = p_elem_current.copy()
                plot_datas.append(vm.LineSegment2D(p_elem_past, p_block_end_real).plot_data())
            plot_datas.append(vm.LineSegment2D(p_block_end_real, p_block_end).plot_data())
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_end_real.vector[0], p_block_end_real.vector[1])), diam_point).plot_data(color = 'black',
                         fill = 'black'))
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_end.vector[0], p_block_end.vector[1])), diam_point).plot_data(color = 'black',
                         fill = 'black'))
            p_block_init = p_block_end.copy()

        if not detail:
            plot_datas = []
            pt_data = {}
            pt_data['type'] = 'text'
            pt_data['label'] = self.class_name
            pt_data['x_label'] = vm.Point2D.MiddlePoint(p_init, p_end).vector[0]
            pt_data['y_label'] = vm.Point2D.MiddlePoint(p_init, p_end).vector[1]
            pt_data['rot_label'] = 0
            pt_data['baseline_shift'] = -0.5
            pt_data['font_size'] = font_size*10
            plot_datas.append(pt_data)

        p0_box = vm.Point2D.MiddlePoint(p_init_global, p_init)
        p1_box = vm.Point2D((p0_box.vector[0], sup_y + delta_box*length_global))
        p4_box = vm.Point2D((p0_box.vector[0], inf_y - delta_box*length_global))
        p21_box = vm.Point2D.MiddlePoint(p_end, p_end_global)
        p2_box = vm.Point2D((p21_box.vector[0], sup_y + delta_box*length_global))
        p3_box = vm.Point2D((p21_box.vector[0], inf_y - delta_box*length_global))
        plot_datas.append(vm.LineSegment2D(p4_box, p1_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p1_box, p2_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p2_box, p3_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p3_box, p4_box).plot_data(color=color_box))

        if detail:
            plot_datas.append(vm.LineSegment2D(p_init_global, p_init).plot_data())
            plot_datas.append(vm.LineSegment2D(p_end, p_end_global).plot_data())
        else:
            plot_datas.append(vm.LineSegment2D(p_init_global, p0_box).plot_data())
            plot_datas.append(vm.LineSegment2D(p21_box, p_end_global).plot_data())

        return plot_datas, sup_y + delta_box * length_global, inf_y - delta_box * length_global

    def CADContour(self):
        """
        Computes cell section for CAD Export
        """
        p0 = vm.Point2D((-self.size[1]/2, -self.size[2]/2))
        p1 = vm.Point2D((self.size[1]/2, -self.size[2]/2))
        p2 = vm.Point2D((self.size[1]/2, self.size[2]/2))
        p3 = vm.Point2D((self.size[1]*1/6, self.size[2]/2))
        p4 = vm.Point2D((self.size[1]*1/6, self.size[2]*2/5))
        p5 = vm.Point2D((-self.size[1]*1/6, self.size[2]*2/5))
        p6 = vm.Point2D((-self.size[1]*1/6, self.size[2]/2))
        p7 = vm.Point2D((-self.size[1]/2, self.size[2]/2))

        l0 = vm.LineSegment2D(p0, p1)
        l1 = vm.LineSegment2D(p1, p2)
        l2 = vm.LineSegment2D(p2, p3)
        l3 = vm.LineSegment2D(p3, p4)
        l4 = vm.LineSegment2D(p4, p5)
        l5 = vm.LineSegment2D(p5, p6)
        l6 = vm.LineSegment2D(p6, p7)
        l7 = vm.LineSegment2D(p7, p0)

        contour = vm.Contour2D([l0, l1, l2, l3, l4, l5, l6, l7])

        return contour

    def CADVolume(self, frame):
        """
        Computes cell volume for CAD Export

        :param Frame: Origin and base of the volume
        :type frame: volmdlr Frame Object

        :returns: List of ExtrudedProfile Objects
        """
        volume = primitives3D.ExtrudedProfile(frame.origin - frame.u*self.size[0]/2,
                                              frame.v,
                                              frame.w,
                                              self.CADContour(),
                                              [],
                                              frame.u*self.size[0],
                                              name='Cell')
        return [volume]

    # def CADExport(self,
    #               name='An_unnamed_cell',
    #               python_path='python',
    #               freecad_path='/usr/lib/freecad/lib/',
    #               export_types=('stl', 'fcstd')):
    #     """
    #     Export cell CAD file
    #     """
    #     frame = vm.Frame3D(vm.Point3D((0, 0, 0)), vm.Vector3D((1, 0, 0)), vm.Vector3D((0, 1, 0)), vm.Vector3D((0, 0, 1)))
    #     volumes = self.CADVolume(frame)
    #
    #     model = vm.VolumeModel(primitives=volumes, name='cell')
    #
    #     resp = model.FreeCADExport(fcstd_filepath=name,
    #                                python_path=python_path,
    #                                freecad_lib_path=freecad_path,
    #                                export_types=export_types)
    #
    #     return resp

    def volume_model(self):
        frame = vm.Frame3D(vm.Point3D((0, 0, 0)), vm.Vector3D((1, 0, 0)), vm.Vector3D((0, 1, 0)),
                           vm.Vector3D((0, 0, 1)))
        volumes = self.CADVolume(frame)
        model = vm.VolumeModel(volumes, self.name)

        return model

    def volmdlr_volume_model(self):
        model = self.volume_model()
        return model

    def Copy(self):
        """
        Returns a copy of a cell object
        """
        cell = Cell(self.rated_capacity, self.ocv_specs, self.rint_specs,
                    self.limits_voltage, self.limits_current, self.limits_soc,
                    self.charge_specs, self.size, self.mass,
                    self.thermal_transfert_specs)
        return cell

    def to_dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        thermal_transfert_specs = [s.to_dict() for s in self.thermal_transfert_specs]
        dict_.update({'rated_capacity' : self.rated_capacity,
                      'limits_voltage' : self.limits_voltage,
                      'limits_current' : self.limits_current,
                      'limits_soc' : self.limits_soc,
                      'mass' : self.mass,
                      'class_name' : self.class_name,
                      'size' : list(self.size),
                      'ocv_specs' : self.ocv_specs.Dict(),
                      'rint_specs' : self.rint_specs.Dict(),
                      'charge_specs' : self.charge_specs.Dict(),
                      'thermal_transfert_specs' : thermal_transfert_specs})
        return dict_

    @classmethod
    def dict_to_object(cls, dict_):
        """
        Generate a electrical cell

        :param dict_: electrical cell dictionnary generate with the Dict method
        """
        if dict_['class_name'] == 'Cell':
            thermal_transfert_specs = [CombinationEvolution.dict_to_object(spec)\
                                       for spec in dict_['thermal_transfert_specs']]
            cell = cls(rated_capacity=dict_['rated_capacity'],
                       ocv_specs=CombinationSpecsEvolution.DictToObject(dict_['ocv_specs']),
                       rint_specs=CombinationSpecsEvolution.DictToObject(dict_['rint_specs']),
                       limits_voltage=dict_['limits_voltage'],
                       limits_current=dict_['limits_current'],
                       limits_soc=dict_['limits_soc'],
                       charge_specs=CombinationSpecsEvolution.DictToObject(dict_['charge_specs']),
                       size=dict_['size'],
                       mass=dict_['mass'],
                       thermal_transfert_specs = thermal_transfert_specs,
                       name=dict_['name'])
        elif dict_['class_name'] == 'CellRC':
            cell = CellRC.dict_to_object(dict_)
        elif dict_['class_name'] == 'Cell2RC':
            cell = Cell2RC.dict_to_object(dict_)
        return cell

class CellRC(Cell):
    """
    Defines an electric cell RC object. This object inherits of the electric cell. Some new input are defined:

    :param rint1_specs: CombinationSpecsEvolution object define the rint1 evolution with the soc at several temperature
    :type rint1_specs: powerpack.electrical.CombinationSpecsEvolution
    :param c1_specs: CombinationSpecsEvolution object define the c1 evolution with the soc at several temperature
    :type c1_specs: powerpack.electrical.CombinationSpecsEvolution
    """
    _standalone_in_db = True
    _jsonschema = dict_merge(Cell._jsonschema, {
        "title" : "powerpack.electrical.CellRC Base Schema",
        "required": ['rint1_specs', 'c1_specs'],
        "properties": {
            "rint1_specs": {
                "type" : "object",
                "title" : "Rint1 Specifications",
                "classes" : ["powerpack.electrical.CombinationSpecsEvolution"],
                "unit" : "ohm",
                "description" : "Rint1 specification",
                "editable" : True,
                "order" : 11
                },
            "c1_specs": {
                "type" : "object",
                "title" : "C1 Specifications",
                "classes" : ["powerpack.electrical.CombinationSpecsEvolution"],
                "unit" : 'F',
                "description" : "C1 specification",
                "editable" : True,
                "order" : 12
                }
            }
        })

    def __init__(self, rated_capacity, ocv_specs, rint_specs, rint1_specs,
                 c1_specs, limits_voltage, limits_current, limits_soc,
                 charge_specs, size, mass, thermal_transfert_specs, name=''):
        Cell.__init__(self, rated_capacity=rated_capacity, ocv_specs=ocv_specs,
                      rint_specs=rint_specs, limits_voltage=limits_voltage,
                      limits_current=limits_current, limits_soc=limits_soc,
                      charge_specs=charge_specs, size=size, mass=mass,
                      thermal_transfert_specs = thermal_transfert_specs, name='')

        self.class_name = 'CellRC'
        self.rint1_specs = rint1_specs
        self.c1_specs = c1_specs

        if self.__class__ is CellRC:
            self.f_rint1, self.f_c1 = self.genere_interpolate()

    def __eq__(self, other_cell):
        equal = (Cell.__eq__(self, other_cell)
                 and self.rint1_specs == other_cell.rint1_specs
                 and self.c1_specs == other_cell.c1_specs)
        return equal

    def __hash__(self):
        cell_hash = Cell.__hash__(self)
        specs_hash = hash(self.rint1_specs) + hash(self.c1_specs)
        return int((cell_hash + specs_hash)%1e8)

    def __setstate__(self, dict_):
        self.__dict__ = dict_
        self.f_ocv, self.f_rint, self.f_charger, self.f_thermal_trans = Cell.genere_interpolate(self)
        self.f_rint1, self.f_c1 = self.genere_interpolate()

    def __getstate__(self):
        dict_ = self.__dict__.copy()
        del dict_['f_ocv']
        del dict_['f_rint']
        del dict_['f_charger']
        del dict_['f_thermal_trans']
        del dict_['f_rint1']
        del dict_['f_c1']
        return dict_

    def _display_angular(self):
        model = self.volmdlr_volume_model()
        displays = [{'angular_component': 'cad_viewer', 'data': model.babylon_data()}]
        displays += [{'angular_component': 'plot_data', 'data': self.concept_plot_data()[0]},
                     {'angular_component': 'plot_data', 'data': self.iso_plot_data()}]

        displays += self.ocv_specs._display_angular()
        displays += self.rint_specs._display_angular()
        displays += self.rint1_specs._display_angular()
        displays += self.c1_specs._display_angular()
        return displays

    def genere_interpolate(self):
        self.f_ocv, self.f_rint, self.f_charger, self.f_thermal_trans = Cell.genere_interpolate(self)
        f_rint1 = {}
        for specs_evolution in self.rint1_specs.specs_evolutions:
            temperature = specs_evolution.temperature
            f_rint1[temperature] = {}
            charge = specs_evolution.charge
            discharge = specs_evolution.discharge
            f_rint1[temperature]['charge'] = interpolate.splrep(charge.x, charge.y)
            f_rint1[temperature]['discharge'] = interpolate.splrep(discharge.x, discharge.y)

        f_c1 = {}
        for specs_evolution in self.c1_specs.specs_evolutions:
            temperature = specs_evolution.temperature
            f_c1[temperature] = {}
            charge = specs_evolution.charge
            discharge = specs_evolution.discharge
            f_c1[temperature]['charge'] = interpolate.splrep(charge.x, charge.y)
            f_c1[temperature]['discharge'] = interpolate.splrep(discharge.x, discharge.y)

        return f_rint1, f_c1

    def concept_plot_data(self, detail=True, p_init_global=vm.Point2D((0, 0)), p_end_global=vm.Point2D((1, 0)), color_box='blue'):
        blocks = [{0: [{'type': 'R', 'name': 'Rint'}, {'type': 'V', 'name': 'OCV'}]},
                 {0: [{'type': 'R', 'name': 'Rint1'}], 1: [{'type': 'V', 'name': 'C1'}]}]
        plot_datas, sup_y, inf_y = self.concept_plot_data_elem(detail, blocks, p_init_global, p_end_global, color_box)
        return plot_datas, sup_y, inf_y

    def Voltage(self, current, usecase, delta_t, temperature, internal_parameter_cell):
        """
        update :math:`soc`, temperature, current parameter and update :math:`ocv`, :math:`R_{int}`,
        thermal_loss, voltage and :math:`soc_p` parameters. :math:`soc_p` define the :math:`soc` at
        the next time (t + delta_t).

        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param current: Current at time t + delta_t
        :type current: A
        :param usecase: Global trend of the battery (charge or discharge)
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        """
        soc_m = internal_parameter_cell.soc_m
        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint
        rint1 = internal_parameter_cell.rint1
        c1 = internal_parameter_cell.c1

        current_rint1_m = internal_parameter_cell.current_rint1_m

        i_rint1 = math.exp(-delta_t/(rint1*c1))*current_rint1_m + (1 - math.exp(-delta_t/(rint1*c1)))*current
        i_rint1 = max(i_rint1, self.limits_current[usecase]['minimum'])
        i_rint1 = min(i_rint1, self.limits_current[usecase]['maximum'])
        u_rint1 = rint1*current_rint1_m

        voltage = ocv + rint*current + u_rint1
        internal_parameter_cell.soc = soc_m + current*delta_t + current_rint1_m*delta_t
        internal_parameter_cell.thermal_loss = rint*(current**2) + rint1*(current_rint1_m**2)
        internal_parameter_cell.current_rint1 = i_rint1

        return voltage

    def Current(self, voltage, usecase, delta_t, temperature, internal_parameter_cell):

        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint
        rint1 = internal_parameter_cell.rint1
        c1 = internal_parameter_cell.c1# TODO: why unused?
        current_rint1_m = internal_parameter_cell.current_rint1_m

        coeff1 = voltage - (ocv +  rint1*current_rint1_m)
        current = coeff1/rint

        return current

    def Ineq(self, usecase, delta_t, temperature, internal_parameter_cell):

        if internal_parameter_cell.current_rint1 is not None:
            internal_parameter_cell.current_rint1_m = internal_parameter_cell.current_rint1

        soc_m = internal_parameter_cell.soc_m
        ocv = self.Eval(soc_m, temperature, usecase, self.ocv_specs, self.f_ocv)
        internal_parameter_cell.ocv = ocv
        rint = self.Eval(soc_m, temperature, usecase, self.rint_specs, self.f_rint)
        internal_parameter_cell.rint = rint
        rint1 = self.Eval(soc_m, temperature, usecase, self.rint1_specs, self.f_rint1)
        internal_parameter_cell.rint1 = rint1
        c1 = self.Eval(soc_m, temperature, usecase, self.c1_specs, self.f_c1)
        internal_parameter_cell.c1 = c1

        u_min = self.limits_voltage[usecase]['minimum']
        i_min = self.Current(u_min, usecase, delta_t, temperature, internal_parameter_cell)
        u_max = self.limits_voltage[usecase]['maximum']
        i_max = self.Current(u_max, usecase, delta_t, temperature, internal_parameter_cell)

        i_min = max([self.limits_current[usecase]['minimum'],
                     (self.limits_soc['minimum']*self.rated_capacity - soc_m)/delta_t,
                     i_min])

        i_max = min([self.limits_current[usecase]['maximum'],
                     (self.limits_soc['maximum']*self.rated_capacity - soc_m)/delta_t,
                     i_max])

        return i_min, i_max

    def CurrentObjective(self, power, i_limits, u_limits, internal_parameter_cell):

        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint
        current_rint1_m = internal_parameter_cell.current_rint1_m
        rint1 = internal_parameter_cell.rint1
        u_rint1 = rint1*current_rint1_m

        u0 = ocv + u_rint1

        return self.CurrentSearch(power, i_limits, u_limits, u0, rint)

    def to_dict(self):
        """Export dictionary
        """
        dict_ = Cell.to_dict(self)
#        dict_['rated_capacity'] = self.rated_capacity
#        dict_['limits_voltage'] = self.limits_voltage
#        dict_['limits_current'] = self.limits_current
#        dict_['limits_soc'] = self.limits_soc
#        dict_['mass'] = self.mass
#        dict_['class_name'] = self.class_name
#        dict_['size'] = list(self.size)
#        dict_['ocv_specs'] = self.ocv_specs.Dict()
#        dict_['rint_specs'] = self.rint_specs.Dict()
#        dict_['charge_specs'] = self.charge_specs.Dict()
        dict_.update({'rint1_specs' : self.rint1_specs.Dict(),
                      'c1_specs' : self.c1_specs.Dict(),
                      'class_name' : self.class_name})
#        dict_['thermal_transfert_specs'] = []
#        for thermal_transfert_spec in self.thermal_transfert_specs:
#            dict_['thermal_transfert_specs'].append(thermal_transfert_spec.Dict())
        return dict_

    @classmethod
    def dict_to_object(cls, dict_):
        thermal_transfert_specs = [CombinationEvolution.dict_to_object(spec)\
                                   for spec in dict_['thermal_transfert_specs']]
        cell = cls(rated_capacity=dict_['rated_capacity'],
                   ocv_specs=CombinationSpecsEvolution.DictToObject(dict_['ocv_specs']),
                   rint_specs=CombinationSpecsEvolution.DictToObject(dict_['rint_specs']),
                   rint1_specs=CombinationSpecsEvolution.DictToObject(dict_['rint1_specs']),
                   c1_specs=CombinationSpecsEvolution.DictToObject(dict_['c1_specs']),
                   limits_voltage=dict_['limits_voltage'],
                   limits_current=dict_['limits_current'],
                   limits_soc=dict_['limits_soc'],
                   charge_specs=CombinationSpecsEvolution.DictToObject(dict_['charge_specs']),
                   size=dict_['size'],
                   mass=dict_['mass'],
                   thermal_transfert_specs=thermal_transfert_specs,
                   name=dict_['name'])
        return cell

class Cell2RC(CellRC):
    """
    Defines an electric cell double RC object. This object inherits of the electric simple RC cell and all previous function are available. Some new input are defined:

    :param rint2_specs: CombinationSpecsEvolution object define the rint2 evolution with the soc at several temperature
    :type rint2_specs: powerpack.electrical.CombinationSpecsEvolution
    :param c2_specs: CombinationSpecsEvolution object define the c2 evolution with the soc at several temperature
    :type c2_specs: powerpack.electrical.CombinationSpecsEvolution
    """
    _standalone_in_db = True
    _jsonschema = dict_merge(CellRC._jsonschema, {
        "title" : "powerpack.electrical.Cell2RC Base Schema",
        "required": ['rint2_specs', 'c2_specs'],
        "properties": {
            "rint2_specs": {
                "type" : "object",
                "title" : "Rint2 Specifications",
                "classes" : ["powerpack.electrical.CombinationSpecsEvolution"],
                "unit" : "ohm",
                "description" : "Rint2 specification",
                "editable" : True,
                "order" : 13
                },
            "c2_specs": {
                "type" : "object",
                "title" : "C2 Specifications",
                "classes" : ["powerpack.electrical.CombinationSpecsEvolution"],
                "unit" : 'F',
                "description" : "C2 specification",
                "editable" : True,
                "order" : 14
                }
            }
        })

    def __init__(self, rated_capacity, ocv_specs, rint_specs,
                 rint1_specs, c1_specs, rint2_specs, c2_specs,
                 limits_voltage, limits_current, limits_soc,
                 charge_specs, size, mass, thermal_transfert_specs, name=''):
        CellRC.__init__(self, rated_capacity=rated_capacity, ocv_specs=ocv_specs,
                        rint_specs=rint_specs, rint1_specs=rint1_specs,
                        c1_specs=c1_specs, limits_voltage=limits_voltage,
                        limits_current=limits_current, limits_soc=limits_soc,
                        charge_specs=charge_specs, size=size, mass=mass,
                        thermal_transfert_specs=thermal_transfert_specs, name=name)

        self.class_name = 'Cell2RC'

        self.rint2_specs = rint2_specs
        self.c2_specs = c2_specs
        if self.__class__ is Cell2RC:
            self.f_rint2, self.f_c2 = self.genere_interpolate()

    def __eq__(self, other_cell):
        equal = (CellRC.__eq__(self, other_cell)
                 and self.rint2_specs == other_cell.rint2_specs
                 and self.c2_specs == other_cell.c2_specs)
        return equal

    def __hash__(self):
        cell_hash = CellRC.__hash__(self)
        specs_hash = hash(self.rint2_specs) + hash(self.c2_specs)
        return cell_hash + specs_hash

    def __setstate__(self, dict_):
        self.__dict__ = dict_
        self.f_ocv, self.f_rint, self.f_charger, self.f_thermal_trans = Cell.genere_interpolate(self)
        self.f_rint1, self.f_c1 = CellRC.genere_interpolate(self)
        self.f_rint2, self.f_c2 = self.genere_interpolate()

    def __getstate__(self):
        dict_ = self.__dict__.copy()
        del dict_['f_ocv']
        del dict_['f_rint']
        del dict_['f_charger']
        del dict_['f_thermal_trans']
        del dict_['f_rint1']
        del dict_['f_c1']
        del dict_['f_rint2']
        del dict_['f_c2']
        return dict_

    def _display_angular(self):
        model = self.volmdlr_volume_model()
        displays = [{'angular_component': 'cad_viewer', 'data': model.babylon_data()}]
        displays += [{'angular_component': 'plot_data', 'data': self.concept_plot_data()[0]},
                     {'angular_component': 'plot_data', 'data': self.iso_plot_data()}]

        displays += self.ocv_specs._display_angular()
        displays += self.rint_specs._display_angular()
        displays += self.rint1_specs._display_angular()
        displays += self.c1_specs._display_angular()
        displays += self.rint2_specs._display_angular()
        displays += self.c2_specs._display_angular()
        return displays

    def genere_interpolate(self):
        self.f_rint1, self.f_c1 = CellRC.genere_interpolate(self)
        f_rint2 = {}
        for specs_evolution in self.rint2_specs.specs_evolutions:
            temperature = specs_evolution.temperature
            f_rint2[temperature] = {}
            charge = specs_evolution.charge
            discharge = specs_evolution.discharge
            f_rint2[temperature]['charge'] = interpolate.splrep(charge.x, charge.y)
            f_rint2[temperature]['discharge'] = interpolate.splrep(discharge.x, discharge.y)

        f_c2 = {}
        for specs_evolution in self.c2_specs.specs_evolutions:
            temperature = specs_evolution.temperature
            f_c2[temperature] = {}
            charge = specs_evolution.charge
            discharge = specs_evolution.discharge
            f_c2[temperature]['charge'] = interpolate.splrep(charge.x, charge.y)
            f_c2[temperature]['discharge'] = interpolate.splrep(discharge.x, discharge.y)

        return f_rint2, f_c2

    def concept_plot_data(self, detail=True, p_init_global=vm.Point2D((0, 0)), p_end_global=vm.Point2D((1, 0)), color_box='blue'):
        blocks = [{0: [{'type': 'R', 'name': 'Rint'}, {'type': 'V', 'name': 'OCV'}]},
                 {0: [{'type': 'R', 'name': 'Rint1'}], 1: [{'type': 'V', 'name': 'C1'}]},
                 {0: [{'type': 'R', 'name': 'Rint2'}], 1: [{'type': 'V', 'name': 'C2'}]}]
        plot_datas, sup_y, inf_y = self.concept_plot_data_elem(detail, blocks, p_init_global, p_end_global, color_box)
        return plot_datas, sup_y, inf_y

    def Voltage(self, current, usecase, delta_t, temperature, internal_parameter_cell):
        """
        update :math:`soc`, temperature, current parameter and update :math:`ocv`, :math:`R_{int}`,
        thermal_loss, voltage and :math:`soc_p` parameters. :math:`soc_p` define the :math:`soc` at
        the next time (t + delta_t).

        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param current: Current at time t + delta_t
        :type current: A
        :param usecase: Global trend of the battery (charge or discharge)
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        """
        soc_m = internal_parameter_cell.soc_m
        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint
        rint1 = internal_parameter_cell.rint1
        c1 = internal_parameter_cell.c1
        rint2 = internal_parameter_cell.rint2
        c2 = internal_parameter_cell.c2

        current_rint1_m = internal_parameter_cell.current_rint1_m
        current_rint2_m = internal_parameter_cell.current_rint2_m

        i_rint1 = math.exp(-delta_t/(rint1*c1))*current_rint1_m \
                + (1 - math.exp(-delta_t/(rint1*c1)))*current
        i_rint1 = max(i_rint1, self.limits_current[usecase]['minimum'])
        i_rint1 = min(i_rint1, self.limits_current[usecase]['maximum'])
        u_rint1 = rint1*current_rint1_m
        i_rint2 = math.exp(-delta_t/(rint2*c2))*current_rint2_m \
                + (1 - math.exp(-delta_t/(rint2*c2)))*current
        i_rint2 = max(i_rint2, self.limits_current[usecase]['minimum'])
        i_rint2 = min(i_rint2, self.limits_current[usecase]['maximum'])
        u_rint2 = rint2*current_rint2_m

        voltage = ocv + rint*current + u_rint1 + u_rint2

        internal_parameter_cell.soc = soc_m + current*delta_t + current_rint1_m*delta_t + current_rint2_m*delta_t
        internal_parameter_cell.thermal_loss = rint*(current**2) + rint1*(current_rint1_m**2) + rint2*(current_rint2_m**2)
        internal_parameter_cell.current_rint1 = i_rint1
        internal_parameter_cell.current_rint2 = i_rint2

        return voltage

    def Current(self, voltage, usecase, delta_t, temperature, internal_parameter_cell):

        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint
        rint1 = internal_parameter_cell.rint1
        current_rint1_m = internal_parameter_cell.current_rint1_m
        rint2 = internal_parameter_cell.rint2
        current_rint2_m = internal_parameter_cell.current_rint2_m

        coeff1 = voltage - (ocv + rint1*current_rint1_m + rint2*current_rint2_m)
        current = coeff1/rint

        return current

    def Ineq(self, usecase, delta_t, temperature, internal_parameter_cell):

        if internal_parameter_cell.current_rint1 is not None:
            internal_parameter_cell.current_rint1_m = internal_parameter_cell.current_rint1
        if internal_parameter_cell.current_rint2 is not None:
            internal_parameter_cell.current_rint2_m = internal_parameter_cell.current_rint2

        soc_m = internal_parameter_cell.soc_m
        ocv = self.Eval(soc_m, temperature, usecase, self.ocv_specs, self.f_ocv)
        internal_parameter_cell.ocv = ocv
        rint = self.Eval(soc_m, temperature, usecase, self.rint_specs, self.f_rint)
        internal_parameter_cell.rint = rint
        rint1 = self.Eval(soc_m, temperature, usecase, self.rint1_specs, self.f_rint1)
        internal_parameter_cell.rint1 = rint1
        c1 = self.Eval(soc_m, temperature, usecase, self.c1_specs, self.f_c1)
        internal_parameter_cell.c1 = c1
        rint2 = self.Eval(soc_m, temperature, usecase, self.rint2_specs, self.f_rint2)
        internal_parameter_cell.rint2 = rint2
        c2 = self.Eval(soc_m, temperature, usecase, self.c2_specs, self.f_c2)
        internal_parameter_cell.c2 = c2

        u_min = self.limits_voltage[usecase]['minimum']
        i_min = self.Current(u_min, usecase, delta_t, temperature, internal_parameter_cell)
        u_max = self.limits_voltage[usecase]['maximum']
        i_max = self.Current(u_max, usecase, delta_t, temperature, internal_parameter_cell)

        i_min = max([self.limits_current[usecase]['minimum'],
                     (self.limits_soc['minimum']*self.rated_capacity - soc_m)/delta_t,
                     i_min])

        i_max = min([self.limits_current[usecase]['maximum'],
                     (self.limits_soc['maximum']*self.rated_capacity - soc_m)/delta_t,
                     i_max])

        return i_min, i_max

    def CurrentObjective(self, power, i_limits, u_limits, internal_parameter_cell):

        ocv = internal_parameter_cell.ocv
        rint = internal_parameter_cell.rint
        current_rint1_m = internal_parameter_cell.current_rint1_m
        rint1 = internal_parameter_cell.rint1
        u_rint1 = rint1*current_rint1_m
        current_rint2_m = internal_parameter_cell.current_rint2_m
        rint2 = internal_parameter_cell.rint2
        u_rint2 = rint2*current_rint2_m

        u0 = ocv + u_rint1 + u_rint2

        return self.CurrentSearch(power, i_limits, u_limits, u0, rint)

    def to_dict(self):
        """Export dictionary
        """
        dict_ = CellRC.to_dict(self)
#        dict_['rated_capacity'] = self.rated_capacity
#        dict_['limits_voltage'] = self.limits_voltage
#        dict_['limits_current'] = self.limits_current
#        dict_['limits_soc'] = self.limits_soc
#        dict_['mass'] = self.mass
#        dict_['size'] = list(self.size)
#        dict_['ocv_specs'] = self.ocv_specs.Dict()
#        dict_['rint_specs'] = self.rint_specs.Dict()
#        dict_['charge_specs'] = self.charge_specs.Dict()
#        dict_['rint1_specs'] = self.rint1_specs.Dict()
#        dict_['c1_specs'] = self.c1_specs.Dict()
        dict_.update({'rint2_specs' : self.rint2_specs.Dict(),
                      'c2_specs' : self.c2_specs.Dict(),
                      'class_name' : self.class_name})
#        dict_['thermal_transfert_specs'] = []
#        for thermal_transfert_spec in self.thermal_transfert_specs:
#            dict_['thermal_transfert_specs'].append(thermal_transfert_spec.Dict())
        return dict_

    @classmethod
    def dict_to_object(cls, dict_):
        thermal_transfert_specs = [CombinationEvolution.dict_to_object(spec)\
                                   for spec in dict_['thermal_transfert_specs']]
        cell = cls(rated_capacity=dict_['rated_capacity'],
                   ocv_specs=CombinationSpecsEvolution.DictToObject(dict_['ocv_specs']),
                   rint_specs=CombinationSpecsEvolution.DictToObject(dict_['rint_specs']),
                   rint1_specs=CombinationSpecsEvolution.DictToObject(dict_['rint1_specs']),
                   c1_specs=CombinationSpecsEvolution.DictToObject(dict_['c1_specs']),
                   rint2_specs=CombinationSpecsEvolution.DictToObject(dict_['rint2_specs']),
                   c2_specs=CombinationSpecsEvolution.DictToObject(dict_['c2_specs']),
                   limits_voltage=dict_['limits_voltage'],
                   limits_current=dict_['limits_current'],
                   limits_soc=dict_['limits_soc'],
                   charge_specs=CombinationSpecsEvolution.DictToObject(dict_['charge_specs']),
                   size=dict_['size'],
                   mass=dict_['mass'],
                   thermal_transfert_specs=thermal_transfert_specs,
                   name=dict_['name'])
        return cell

class CellManagementSystem(DessiaObject):
    """
    Defines an electric cell management system

    :param cell: cell
    :type cell: Cell

    :Example:

    >>> import powerpack.electrical as elec
    >>> cms1 = elec.CellManagementSystem(cell = cell1)
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.CellManagementSystem Base Schema",
        "required": ['cell'],
        "properties": {
            'cell': {
                "type" : "object",
                "title" : "Cell",
                "classes" : ["powerpack.electrical.Cell",
                             "powerpack.electrical.CellRC",
                             "powerpack.electrical.Cell2RC"],
                "description" : "Cell",
                "editable" : True,
                "order" : 1
                }
            }
        }

    def __init__(self, cell, name=''):
        self.cell = cell
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        return self.cell == other.cell

    def __hash__(self):
        return hash(self.cell) + 15478

    def _display_angular(self):
        displays = self.cell._display_angular()
        displays.remove({'angular_component': 'app-cad-viewer'}) # !!! Change this when json cofig is available
        return displays

    def Ineq(self, soc_m, temperature, usecase, charger, delta_t, internal_parameter_cell):
        """
        Define the minimum and maximum current and voltage available at the time (t + delta_t) regards
        with cell limitation

        :param soc_m: cell state of charge at time t
        :type soc_m: As
        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param usecase: String define the battery trend (charge or discharge)
        :param charger: use charge_specs of electrical cell
        :type charger: boolean
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **(i_min, i_max), (u_min, u_max)** minimum and maximum current and voltage available at the time (t + delta_t)
        """
        cell = self.cell

        internal_parameter_cell.soc_m = soc_m
        i_min, i_max = cell.Ineq(usecase, delta_t, temperature, internal_parameter_cell)

        if charger:
            i_charger = cell.CurrentChargerEval(soc_m, temperature)
            i_min = i_charger
            i_max = i_charger

        u_min = cell.Voltage(i_min, usecase, delta_t, temperature,
                               internal_parameter_cell)
        u_max = cell.Voltage(i_max, usecase, delta_t, temperature,
                               internal_parameter_cell)

        return (i_min, i_max), (u_min, u_max)

    def update(self, current, soc_m, temperature, usecase, charger, delta_t, results, internal_parameter_cell):
        """
        Update the voltage, soc and thermal losses at the next time (t + delta_t) and add new value in the CellResult object

        :param current: Current at time t + delta_t
        :type current: A
        :param soc_m: cell state of charge at time t
        :type soc_m: As
        :param temperature: Cell temperature
        :type temperature: Kelvin
        :param usecase: String define the battery trend (charge or discharge)
        :param charger: use charge_specs of electrical cell
        :type charger: boolean
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param results: dictionnary define the electrical results
        :type results: {'cms': powerpack.electrical.CellResult, 'mms': powerpack.electrical.ElecModuleResult, 'bms': powerpack.electrical.ElecBatteryResult}
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **current, voltage, soc, thermal_loss** at the time (t + delta_t)
        """
        cell = self.cell

        voltage = cell.Voltage(current, usecase, delta_t, temperature,
                               internal_parameter_cell)

        results['cms'].Add(voltage, current, temperature, delta_t,
                           internal_parameter_cell)
        soc = internal_parameter_cell.soc
        thermal_loss = internal_parameter_cell.thermal_loss

        return current, voltage, soc, thermal_loss

    def CurrentObjective(self, power, i_limits, u_limits, internal_parameter_cell):
        """
        Search of the current at time t + delta_t to deliver a define power and check current and voltage limitation

        :param power: Power at time t + delta_t
        :type power: W
        :param i_limits: i_min, i_max
        :type i_limits: (A, A)
        :param u_limits: u_min, u_max
        :type u_limits: (V, V)
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **current**
        """
        (i_min, i_max) = i_limits
        (u_min, u_max) = u_limits
        current = self.cell.CurrentObjective(power, (i_min, i_max),
                                             (u_min, u_max), internal_parameter_cell)
        return current

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_['cell'] = self.cell.to_dict()
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an CellManagementSystem object

        :param dict_: CellManagementSystem dictionnary generate with the Dict method
        """
        cell = Cell.dict_to_object(dict_['cell'])
        return cls(cell=cell, name=dict_['name'])

class ElecModule(DessiaObject):
    """
    Defines an electric module object based on a cell management system

    :param cms: cms
    :type cms: CellManagementSystem
    :param number_cell_serie: cell number in serie per module
    :type number_cell_serie: integer
    :param number_cell_parallel: cell number in parallel per module
    :type number_cell_parallel: integer

    :Example:

    >>> import powerpack.electrical as elec
    >>> m1 = elec.ElecModule(cms = cms1,
                                   number_cell_serie = 5,
                                   number_cell_parallel = 3)
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.ElecModule Base Schema",
        "required": ['cms', 'number_cell_serie', 'number_cell_parallel'],
        "properties": {
            'cms': {
                "type" : "object",
                "title" : "Cell Management System",
                "classes" : ["powerpack.electrical.CellManagementSystem"],
                "description" : "Cell management system",
                "editable" : True,
                "order" : 3
                },
            'number_cell_serie': {
                "type": "number",
                "title" : "Number of cells in series",
                "step" : 1,
                "examples": [10],
                "editable": True,
                "description": "Number cell serie",
                'order': 1
                },
            'number_cell_parallel': {
                "type": "number",
                "title" : "Number of cells in parallels",
                "step" : 1,
                "examples": [10],
                "editable": True,
                "description": "Number cell parallel",
                'order': 2
                }
            }
        }

    def __init__(self, cms, number_cell_serie, number_cell_parallel, name=''):
        self.cms = cms

        self.number_cell_serie = number_cell_serie
        self.number_cell_parallel = number_cell_parallel
        self.number_cells = self.number_cell_serie*self.number_cell_parallel

        self.rated_capacity = cms.cell.rated_capacity*self.number_cells

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_module):
        cell = self.cms.cell
        other_cell= other_module.cms.cell
        equal = (self.number_cell_serie == other_module.number_cell_serie
                 and self.number_cell_parallel == other_module.number_cell_parallel
                 and cell == other_cell)
        return equal

    def __hash__(self):
        module_hash = int(hash(self.number_cell_serie) + hash(self.number_cell_parallel)\
                     + hash(self.cms.cell) % 45e5)
        return module_hash

    def _display_angular(self):
        displays = [{'angular_component': 'app-d3-plot-data',
                     'component': 'concept_plot_data',
                     'data': self.concept_plot_data()}]
        displays.extend(self.cms._display_angular())
        return displays

    def Copy(self):
        """
        Returns a copy of a module object
        """
        module = ElecModule(self.cms,
                            self.number_cell_serie,
                            self.number_cell_parallel)

        return module

    def concept_plot_data(self, detail=True, p_init_global=vm.Point2D((0, 0)), p_end_global=vm.Point2D((1, 0)), color_box='red'):
        delta_box = 0.05
        length_global = vm.LineSegment2D(p_init_global, p_end_global).Length()
        p_init = p_init_global.Translation(vm.Vector2D((delta_box*length_global, 0)), True)
        p_end = p_end_global.Translation(vm.Vector2D((-delta_box*length_global, 0)), True)
        length = vm.LineSegment2D(p_init, p_end).Length()
        block_line = [{'type': 'Cell', 'name': ''} for i in range(self.number_cell_serie)]
        blocks = [{i: block_line for i in range(self.number_cell_parallel)}]
        nb_block = len(blocks)
        p_block_init = p_init.copy()
        plot_datas = []
        diam_point = length*0.005
        font_size = length*10
        sup_y = -npy.inf
        inf_y = npy.inf
        for block in blocks:
            nb_line = len(block.keys())
            if nb_line > 1:
                post_nd_init = 0.1
            else:
                post_nd_init = 0
            length_block = length/nb_block
            length_block_real = length_block - 2*post_nd_init*length_block
            p_block_init_real = p_block_init.Translation(vm.Vector2D((post_nd_init*length_block, 0)), True)
            p_block_end_real = p_block_init.Translation(vm.Vector2D(((1 - post_nd_init)*length_block, 0)), True)
            p_block_end = p_block_init.Translation(vm.Vector2D((length_block, 0)), True)
            plot_datas.append(vm.LineSegment2D(p_block_init, p_block_init_real).plot_data())
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_init.vector[0], p_block_init.vector[1])), diam_point).plot_data(color = 'black',
                              fill = 'black'))
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_init_real.vector[0], p_block_init_real.vector[1])), diam_point).plot_data(color = 'black',
                              fill = 'black'))
            high_line = 0
            for num_line, items_line in block.items():
                nb_elem = len(items_line)
                length_elem = length_block_real/(nb_elem)
                plot_data_elem, sup_y_elem, inf_y_elem = self.cms.cell.concept_plot_data(False, vm.Point2D((0, 0)), vm.Point2D((length_elem, 0)))
                high_line = max(high_line, sup_y_elem - inf_y_elem)
            high_block = nb_line*high_line
            for num_line, items_line in block.items():
                nb_elem = len(items_line)
                length_elem = length_block_real/(nb_elem)
                if nb_line > 1:
                    y_init = high_block/2.
                    pas_y = high_block/(nb_line - 1)
                else:
                    y_init, pas_y = 0, 0
                p_elem_past = p_block_init_real.Translation(vm.Vector2D((0, y_init - pas_y*num_line)), True)
                plot_datas.append(vm.LineSegment2D(p_block_init_real, p_elem_past).plot_data())
                for num_elem, elem in enumerate(items_line):
                    p_elem_current = p_elem_past.Translation(vm.Vector2D((length_elem, 0)), True)
                    plot_data_elem, sup_y_elem, inf_y_elem = self.cms.cell.concept_plot_data(False, p_elem_past, p_elem_current)
                    plot_datas.extend(plot_data_elem)
                    sup_y = max(sup_y, sup_y_elem)
                    inf_y = min(inf_y, inf_y_elem)
                    p_elem_past = p_elem_current.copy()
                plot_datas.append(vm.LineSegment2D(p_elem_past, p_block_end_real).plot_data())
            plot_datas.append(vm.LineSegment2D(p_block_end_real, p_block_end).plot_data())
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_end_real.vector[0], p_block_end_real.vector[1])), diam_point).plot_data(color = 'black',
                         fill = 'black'))
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_end.vector[0], p_block_end.vector[1])), diam_point).plot_data(color = 'black',
                         fill = 'black'))
            p_block_init = p_block_end.copy()

        if not detail:
            plot_datas = []
            pt_data = {}
            pt_data['type'] = 'text'
            pt_data['label'] = 'ElecModule'
            pt_data['x_label'] = vm.Point2D.MiddlePoint(p_init, p_end).vector[0]
            pt_data['y_label'] = vm.Point2D.MiddlePoint(p_init, p_end).vector[1]
            pt_data['rot_label'] = 0
            pt_data['baseline_shift'] = -0.5
            pt_data['font_size'] = font_size*10
            plot_datas.append(pt_data)

        p0_box = vm.Point2D.MiddlePoint(p_init_global, p_init)
        p1_box = vm.Point2D((p0_box.vector[0], sup_y + delta_box*length_global))
        p4_box = vm.Point2D((p0_box.vector[0], inf_y - delta_box*length_global))
        p21_box = vm.Point2D.MiddlePoint(p_end, p_end_global)
        p2_box = vm.Point2D((p21_box.vector[0], sup_y + delta_box*length_global))
        p3_box = vm.Point2D((p21_box.vector[0], inf_y - delta_box*length_global))
        plot_datas.append(vm.LineSegment2D(p4_box, p1_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p1_box, p2_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p2_box, p3_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p3_box, p4_box).plot_data(color=color_box))

        if detail:
            plot_datas.append(vm.LineSegment2D(p_init_global, p_init).plot_data())
            plot_datas.append(vm.LineSegment2D(p_end, p_end_global).plot_data())
        else:
            plot_datas.append(vm.LineSegment2D(p_init_global, p0_box).plot_data())
            plot_datas.append(vm.LineSegment2D(p21_box, p_end_global).plot_data())

        return plot_datas, sup_y + delta_box*length_global, inf_y - delta_box*length_global

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'cms' : self.cms.Dict(),
                      'number_cell_serie' : int(self.number_cell_serie),
                      'number_cell_parallel' : int(self.number_cell_parallel)})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an ElecModule object

        :param dict_: ElecModule dictionnary generate with the Dict method
        """
        cms = CellManagementSystem.DictToObject(dict_['cms'])
        elec_module = cls(cms=cms,
                          number_cell_serie=dict_['number_cell_serie'],
                          number_cell_parallel=dict_['number_cell_parallel'],
                          name=dict_['name'])
        return elec_module


class ModuleManagementSystem(DessiaObject):
    """
    Defines an electric module management system based on an electrical module

    :param module: module
    :type module: ElecModule
    :param limits_voltage: Dictionnary define the module voltage limit
    :type limits_voltage: {'charge': {'minimum': value, 'maximum': value},
                           'discharge': {'minimum': value, 'maximum': value}}
    :param limits_current: Dictionnary define the module current limit
    :type limits_current: {'charge': {'minimum': value, 'maximum': value},
                           'discharge': {'minimum': value, 'maximum': value}}

    :Example:

    >>> import powerpack.electrical as elec
    >>> mms = elec.ModuleManagementSystem(module = m1,
                                          limits_voltage = {'charge': {'minimum': 1, 'maximum': 100},
                                                            'discharge': {'minimum': 1, 'maximum': 100}},
                                          limits_current = {'charge': {'minimum': 0, 'maximum': 300},
                                                            'discharge': {'minimum': -300, 'maximum': 0}})
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.ModuleManagementSystem Base Schema",
        "required": ['module', 'limits_voltage', 'limits_current'],
        "properties": {
            'module': {
                "type" : "object",
                "title" : "Electrical Module",
                "classes" : ["powerpack.electrical.ElecModule"],
                "description" : "Module",
                "editable" : True,
                "order" : 3
                },
            "limits_voltage": {
                "type": "object",
                "title" : "Voltage Limitations",
                "order" : 1,
                "editable" : True,
                "description" : "Limits voltage",
                "required": ["charge", "discharge"],
                "properties": {
                    "charge": {
                        "type": "object",
                        "editable" : True,
                        "required": ['minimum', 'maximum'],
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "V"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "V"
                                }
                            },

                        },
                    "discharge": {
                       "type": "object",
                       "editable" : True,
                       "required": ['minimum', 'maximum'],
                       "properties": {
                           "minimum": {
                               "type":"number",
                               "editable" : True,
                               "minimum":0,
                               "step" : 0.001,
                               "unit": "V"
                               },
                           "maximum": {
                               "type":"number",
                               "editable" : True,
                               "minimum":0,
                                "step" : 0.001,
                               "unit": "V"
                               }
                           }
                       }
                    }
                },
            "limits_current": {
                "type": "object",
                "title" : "Current Limitations",
                "order" : 2,
                "editable" : True,
                "required": [ "charge", "discharge" ],
                "description" : "Limits current",
                "properties": {
                    "charge": {
                        "type": "object",
                        "editable" : True,
                        "required": ['minimum', 'maximum'],
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "A"
                                }
                            }
                        },
                    "discharge": {
                        "type": "object",
                        "editable" : True,
                        "required": ['minimum', 'maximum'],
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "step" : 0.001,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "step" : 0.001,
                                "unit": "A"
                                }
                            }
                        }
                    }
                }
            }
        }

    def __init__(self, module, limits_voltage, limits_current, name=''):
        self.module = module
        self.limits_voltage = limits_voltage
        self.limits_current = limits_current

        self.number_cell_serie = self.module.number_cell_serie
        self.number_cell_parallel = self.module.number_cell_parallel
        self.number_cells = self.number_cell_serie*self.number_cell_parallel

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        valid = (self.module == other.module
                 and self.limits_voltage == other.limits_voltage
                 and self.limits_current == other.limits_current
                 and self.number_cell_serie == other.number_cell_serie
                 and self.number_cell_parallel == other.number_cell_parallel)
        return valid

    def __hash__(self):

        mms_hash = (hash(self.module)\
                    + 7*self.number_cell_serie + 13*self.number_cell_parallel)
        return mms_hash

    def _display_angular(self):
        displays = []
        displays.extend(self.module._display_angular())
        return displays

    def Ineq(self, soc_m, temperature, usecase, charger, delta_t, internal_parameter_cell):
        """
        Define the minimum and maximum module current and module voltage available at the time (t + delta_t) regards
        with cell and module limitation

        :param soc_m: module state of charge at time t
        :type soc_m: As
        :param temperature: module temperature
        :type temperature: Kelvin
        :param usecase: String define the battery trend (charge or discharge)
        :param charger: use charge_specs of electrical cell
        :type charger: boolean
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **(i_min, i_max), (u_min, u_max)** minimum and maximum module current and module voltage available at the time (t + delta_t)
        """
        module = self.module
        (i_min_cell, i_max_cell), (u_min_cell, u_max_cell) = module.cms.Ineq(soc_m/self.number_cells,
                                            temperature, usecase, charger, delta_t, internal_parameter_cell)

        u_min = u_min_cell*self.number_cell_serie
        u_max = u_max_cell*self.number_cell_serie
        i_min = i_min_cell*self.number_cell_parallel
        i_max = i_max_cell*self.number_cell_parallel

        u_min = max([self.limits_voltage[usecase]['minimum'], u_min])
        u_max = min([self.limits_voltage[usecase]['maximum'], u_max])
        i_min = max([self.limits_current[usecase]['minimum'], i_min])
        i_max = min([self.limits_current[usecase]['maximum'], i_max])

        return (i_min, i_max), (u_min, u_max)

    def update(self, current, soc_m, temperature, usecase, charger, delta_t, results, internal_parameter_cell):
        """
        Update the voltage, soc and thermal losses at the next time (t + delta_t) and add new value in the ElecModuleResult object.
        Update of the cell management system.

        :param current: module current at time t + delta_t
        :type current: A
        :param soc_m: module state of charge at time t
        :type soc_m: As
        :param temperature: module temperature
        :type temperature: Kelvin
        :param usecase: String define the battery trend (charge or discharge)
        :param charger: use charge_specs of electrical cell
        :type charger: boolean
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param results: dictionnary define the electrical results
        :type results: {'cms': powerpack.electrical.CellResult, 'mms': powerpack.electrical.ElecModuleResult, 'bms': powerpack.electrical.ElecBatteryResult}
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **current, voltage, soc, thermal_loss** at the time (t + delta_t)
        """
        module = self.module

        current_cell = current/self.number_cell_parallel

        current_cell, voltage_cell, soc_cell, thermal_loss_cell = \
            module.cms.update(current_cell, soc_m/self.number_cells,
                              temperature, usecase, charger, delta_t, results, internal_parameter_cell)

        voltage = voltage_cell*self.number_cell_serie
        soc_p = soc_cell*self.number_cells
        thermal_loss_p = thermal_loss_cell*self.number_cells

        results['mms'].Add(soc_p, voltage, current, temperature, thermal_loss_p, delta_t)

        return current, voltage, soc_p, thermal_loss_p

    def CurrentObjective(self, power, i_limits, u_limits, internal_parameter_cell):
        """
        Search of the module current at time t + delta_t to deliver a define power and check module current and module voltage limitation.
        This search is based on the cell current define by the CurrentObjective method of the CellManagementSystem object

        :param power: Power at time t + delta_t
        :type power: W
        :param i_limits: i_min and i_max module limitation
        :type i_limits: (A, A)
        :param u_limits: u_min and u_max module limitation
        :type u_limits: (V, V)
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **current**
        """
        (i_min, i_max) = i_limits
        (u_min, u_max) = u_limits

        power_cell = power/self.number_cells
        (i_min_cell, i_max_cell) = (i_min/self.number_cell_parallel, i_max/self.number_cell_parallel)
        (u_min_cell, u_max_cell) = (u_min/self.number_cell_serie, u_max/self.number_cell_serie)
        current_cell = self.module.cms.CurrentObjective(power_cell, (i_min_cell, i_max_cell),
                                                           (u_min_cell, u_max_cell), internal_parameter_cell)
        return current_cell*self.number_cell_parallel

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'module' : self.module.Dict(),
                      'limits_voltage' : self.limits_voltage,
                      'limits_current' : self.limits_current})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an ModuleManagementSystem object

        :param dict_: ModuleManagementSystem dictionnary generate with the Dict method
        """
        module = ElecModule.DictToObject(dict_['module'])
        mms = cls(module=module,
                  limits_voltage=dict_['limits_voltage'],
                  limits_current=dict_['limits_current'],
                  name=dict_['name'])
        return mms


class ElecBattery(DessiaObject):
    """
    Defines an electric battery object which is a combination of electric modules

    :param mms: module management system
    :type modules: ModuleManagementSystem
    :param number_module_serie: module number in serie per battery
    :type number_module_serie: integer
    :param number_module_parallel: module number in parallel per battery
    :type number_module_parallel: integer

    :Example:

    >>> import powerpack.electrical as elec
    >>> bat1 = elec.ElecBattery(mms = mms1,
                                number_module_serie = 5,
                                number_module_parallel = 5)
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.ElecBattery Base Schema",
        "required": ['mms', 'number_module_serie', 'number_module_parallel'],
        "properties": {
            'mms': {
                "type" : "object",
                "title" : "Module Management System",
                "classes" : ["powerpack.electrical.ModuleManagementSystem"],
                "description" : "Module management system",
                "editable" : True,
                "order" : 3
                },
            'number_module_serie': {
                "type": "number",
                "title" : "Number of modules in series",
                "step" : 1,
                "examples": [10],
                "editable": True,
                "description": "Number module serie",
                "order" : 2
                },
            'number_module_parallel': {
                "type": "number",
                "title" : "Number of modules in parallels",
                "step" : 1,
                "examples": [10],
                "editable": True,
                "description": "Number module parallel",
                "order" : 1
                 }
             }
         }

    def __init__(self, mms, number_module_serie, number_module_parallel, name=''):
        self.mms = mms

        self.number_module_serie = number_module_serie
        self.number_module_parallel = number_module_parallel
        self.number_modules = self.number_module_serie*self.number_module_parallel
        self.number_cells = self.number_modules*self.mms.number_cells

        self.rated_capacity = self.mms.module.rated_capacity*self.number_modules

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_eb):
        module = self.mms.module
        other_module = other_eb.mms.module
        equal = (self.number_module_serie == other_eb.number_module_serie
                 and self.number_module_parallel == other_eb.number_module_parallel
                 and self.rated_capacity == other_eb.rated_capacity
                 and module == other_module)
        return equal

    def __hash__(self):
        eb_hash = hash(self.number_module_serie) + hash(self.number_module_parallel)\
                 + hash(self.rated_capacity) + hash(self.mms.module)
        return eb_hash

    def _display_angular(self):
        displays = [{'angular_component': 'app-d3-plot-data',
                     'component': 'concept_plot_data',
                     'data': self.concept_plot_data()}]
        displays.extend(self.mms._display_angular())
        return displays

    def Copy(self):
        """
        Returns a copy of a module object
        """
        battery = ElecBattery(self.mms,
                              self.number_module_serie,
                              self.number_module_parallel)
        return battery

    def concept_plot_data(self, p_init_global=vm.Point2D((0, 0)), p_end_global=vm.Point2D((1, 0)), color_box='green'):
        delta_box = 0.05
        length_global = vm.LineSegment2D(p_init_global, p_end_global).Length()
        p_init = p_init_global.Translation(vm.Vector2D((delta_box*length_global, 0)), True)
        p_end = p_end_global.Translation(vm.Vector2D((-delta_box*length_global, 0)), True)
        length = vm.LineSegment2D(p_init, p_end).Length()
        block_line = [{'type': 'Module', 'name': ''} for i in range(self.number_module_serie)]
        blocks = [{i: block_line for i in range(self.number_module_parallel)}]
        nb_block = len(blocks)
        p_block_init = p_init.copy()
        plot_datas = []
        diam_point = length*0.005
        sup_y = -npy.inf
        inf_y = npy.inf
        for block in blocks:
            nb_line = len(block.keys())
            if nb_line > 1:
                post_nd_init = 0.1
            else:
                post_nd_init = 0
            length_block = length/nb_block
            length_block_real = length_block - 2*post_nd_init*length_block
            p_block_init_real = p_block_init.Translation(vm.Vector2D((post_nd_init*length_block, 0)), True)
            p_block_end_real = p_block_init.Translation(vm.Vector2D(((1 - post_nd_init)*length_block, 0)), True)
            p_block_end = p_block_init.Translation(vm.Vector2D((length_block, 0)), True)
            plot_datas.append(vm.LineSegment2D(p_block_init, p_block_init_real).plot_data())
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_init.vector[0], p_block_init.vector[1])), diam_point).plot_data(color = 'black',
                              fill = 'black'))
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_init_real.vector[0], p_block_init_real.vector[1])), diam_point).plot_data(color = 'black',
                              fill = 'black'))
            high_line = 0
            for num_line, items_line in block.items():
                nb_elem = len(items_line)
                length_elem = length_block_real/(nb_elem)
                plot_data_elem, sup_y_elem, inf_y_elem = self.mms.module.concept_plot_data(False, vm.Point2D((0, 0)), vm.Point2D((length_elem, 0)))
                high_line = max(high_line, sup_y_elem - inf_y_elem)
            high_block = nb_line*high_line
            for num_line, items_line in block.items():
                nb_elem = len(items_line)
                length_elem = length_block_real/(nb_elem)
                if nb_line > 1:
                    y_init = high_block/2.
                    pas_y = high_block/(nb_line - 1)
                else:
                    y_init, pas_y = 0, 0
                p_elem_past = p_block_init_real.Translation(vm.Vector2D((0, y_init - pas_y*num_line)), True)
                plot_datas.append(vm.LineSegment2D(p_block_init_real, p_elem_past).plot_data())
                for num_elem, elem in enumerate(items_line):
                    p_elem_current = p_elem_past.Translation(vm.Vector2D((length_elem, 0)), True)
                    plot_data_elem, sup_y_elem, inf_y_elem = self.mms.module.concept_plot_data(False, p_elem_past, p_elem_current)
                    plot_datas.extend(plot_data_elem)
                    sup_y = max(sup_y, sup_y_elem)
                    inf_y = min(inf_y, inf_y_elem)
                    p_elem_past = p_elem_current.copy()
                plot_datas.append(vm.LineSegment2D(p_elem_past, p_block_end_real).plot_data())
            plot_datas.append(vm.LineSegment2D(p_block_end_real, p_block_end).plot_data())
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_end_real.vector[0], p_block_end_real.vector[1])), diam_point).plot_data(color = 'black',
                         fill = 'black'))
            plot_datas.append(vm.Circle2D(vm.Point2D((p_block_end.vector[0], p_block_end.vector[1])), diam_point).plot_data(color = 'black',
                         fill = 'black'))
            p_block_init = p_block_end.copy()

        plot_datas.append(vm.LineSegment2D(p_init_global, p_init).plot_data())
        plot_datas.append(vm.LineSegment2D(p_end, p_end_global).plot_data())
        p0_box = vm.Point2D.MiddlePoint(p_init_global, p_init)
        p1_box = vm.Point2D((p0_box.vector[0], sup_y + delta_box*length_global))
        p4_box = vm.Point2D((p0_box.vector[0], inf_y - delta_box*length_global))
        p21_box = vm.Point2D.MiddlePoint(p_end, p_end_global)
        p2_box = vm.Point2D((p21_box.vector[0], sup_y + delta_box*length_global))
        p3_box = vm.Point2D((p21_box.vector[0], inf_y - delta_box*length_global))
        plot_datas.append(vm.LineSegment2D(p4_box, p1_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p1_box, p2_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p2_box, p3_box).plot_data(color=color_box))
        plot_datas.append(vm.LineSegment2D(p3_box, p4_box).plot_data(color=color_box))

        return plot_datas, sup_y + delta_box*length_global, inf_y - delta_box*length_global

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'mms' : self.mms.Dict(),
                      'number_module_serie' : self.number_module_serie,
                      'number_module_parallel' : self.number_module_parallel})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an ElecBattery object

        :param dict_: ElecBattery dictionnary generate with the Dict method
        """
        mms = ModuleManagementSystem.DictToObject(dict_['mms'])
        elec_battery = cls(mms=mms,
                           number_module_serie=dict_['number_module_serie'],
                           number_module_parallel=dict_['number_module_parallel'],
                           name=dict_['name'])
        return elec_battery

class BatteryManagementSystem(DessiaObject):
    """
    Defines an electric battery management system based on an electrical battery

    :param battery: electrical battery
    :type battery: ElecBattery
    :param limits_voltage: Dictionnary define the battery voltage limit
    :type limits_voltage: {'charge': {'minimum': value, 'maximum': value},
                           'discharge': {'minimum': value, 'maximum': value}}
    :param limits_current: Dictionnary define the battery current limit
    :type limits_current: {'charge': {'minimum': value, 'maximum': value},
                           'discharge': {'minimum': value, 'maximum': value}}

    :Example:

    >>> import powerpack.electrical as elec
    >>> bms1 = elec.ElecBattery(battery = battery1,
                                limits_voltage =  {'charge': {'minimum': 1, 'maximum': 100},
                                                   'discharge': {'minimum': 1, 'maximum': 20}},
                                limits_current = {'charge': {'minimum': 0, 'maximum': 100},
                                                  'discharge': {'minimum': -100, 'maximum': 0}})
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.BatteryManagementSystem Base Schema",
        "required": ['battery', 'limits_voltage', 'limits_current'],
        "properties": {
            'battery': {
                "type" : "object",
                "title" : "Electrical Battery",
                "classes" : ["powerpack.electrical.ElecBattery"],
                "description" : "Battery",
                "editable" : True,
                "order" : 3
                },
            "limits_voltage": {
                "type": "object",
                "title" : "Voltage Limitations",
                "editable" : True,
                "required": [ "charge", "discharge" ],
                "order" : 1,
                "description" : "Limits voltage",
                "properties": {
                    "charge": {
                        "required": ['minimum', 'maximum'],
                        "type": "object",
                        "editable" : True,
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "V"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "V"
                                }
                            }
                        },
                    "discharge": {
                        "type": "object",
                        "editable" : True,
                        "required": ['minimum', 'maximum'],
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "V"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "V"
                                }
                            }
                        }
                    }
                },
            "limits_current": {
                "type": "object",
                "title" : "Current Limitations",
                "required": [ "charge", "discharge" ],
                "editable" : True,
                "order" : 2,
                "description" : "Limits current",
                "properties": {
                    "charge": {
                        "type": "object",
                        "editable" : True,
                        "required": ['minimum', 'maximum'],
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "minimum":0,
                                "step" : 0.001,
                                "unit": "A"
                                }
                            }
                        },
                    "discharge": {
                        "type": "object",
                        "editable" : True,
                        "required": ['minimum', 'maximum'],
                        "properties": {
                            "minimum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "step" : 0.001,
                                "unit": "A"
                                },
                            "maximum": {
                                "type":"number",
                                "editable" : True,
                                "maximum":0,
                                "step" : 0.001,
                                "unit": "A"
                                }
                            }
                        }
                    }
                }
            }
        }

    def __init__(self, battery, limits_voltage, limits_current, name=''):
        self.battery = battery
        self.limits_voltage = limits_voltage
        self.limits_current = limits_current

        self.number_module_serie = self.battery.number_module_serie
        self.number_module_parallel = self.battery.number_module_parallel
        self.number_modules = self.number_module_serie*self.number_module_parallel
        self.number_cells = self.battery.number_cells

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_eb):
        equal = self.battery == other_eb.battery
        return equal

    def __hash__(self):
        eb_hash = hash(self.battery)
        return eb_hash

    def _display_angular(self):
        displays = []
        displays.extend(self.battery._display_angular())
        return displays

    def Ineq(self, soc_m, temperature, usecase, charger, delta_t, internal_parameter_cell):
        """
        Define the minimum and maximum battery current and battery voltage available at the time (t + delta_t) regards
        with cell, module and battery limitation

        :param soc_m: battery state of charge at time t
        :type soc_m: As
        :param temperature: battery temperature
        :type temperature: Kelvin
        :param usecase: String define the battery trend (charge or discharge)
        :param charger: use charge_specs of electrical cell
        :type charger: boolean
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **(i_min, i_max), (u_min, u_max)** minimum and maximum battery current and battery voltage available at the time (t + delta_t)
        """
        battery = self.battery
        (i_min_module, i_max_module), (u_min_module, u_max_module) \
                        = battery.mms.Ineq(soc_m/self.number_modules,
                                           temperature, usecase, charger, delta_t, internal_parameter_cell)

        u_min = u_min_module*self.number_module_serie
        u_max = u_max_module*self.number_module_serie
        i_min = i_min_module*self.number_module_parallel
        i_max = i_max_module*self.number_module_parallel

        u_min = max([self.limits_voltage[usecase]['minimum'], u_min])
        u_max = min([self.limits_voltage[usecase]['maximum'], u_max])
        i_min = max([self.limits_current[usecase]['minimum'], i_min])
        i_max = min([self.limits_current[usecase]['maximum'], i_max])

        return (i_min, i_max), (u_min, u_max)

    def update(self, current, soc_m, temperature, usecase, charger, delta_t,
               results, internal_parameter_cell):
        """
        Update the voltage, soc and thermal losses at the next time (t + delta_t) and add new value in the ElecBatteryResult object.
        Update of the module management system

        :param current: battery current at time t + delta_t
        :type current: A
        :param soc_m: battery state of charge at time t
        :type soc_m: As
        :param temperature: battery temperature
        :type temperature: Kelvin
        :param usecase: String define the battery trend (charge or discharge)
        :param charger: use charge_specs of electrical cell
        :type charger: boolean
        :param delta_t: Difference of time between the current time and the past time
        :type delta_t: s
        :param results: dictionnary define the electrical results
        :type results: {'cms': powerpack.electrical.CellResult, 'mms': powerpack.electrical.ElecModuleResult, 'bms': powerpack.electrical.ElecBatteryResult}
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **current, voltage, soc, thermal_loss** at the time (t + delta_t)
        """
        battery = self.battery

        current_module = current/self.number_module_parallel

        current_module, voltage_module, soc_module, thermal_loss_module = \
            battery.mms.update(current_module, soc_m/self.number_modules, temperature,
                    usecase, charger, delta_t, results, internal_parameter_cell)

        soc_p = soc_module*self.number_modules
        thermal_loss_p = thermal_loss_module*self.number_modules
        voltage = voltage_module*self.number_module_serie
        results['bms'].Add(soc_p, voltage, current, temperature, thermal_loss_p,
                                     delta_t)
        return current, voltage, soc_p, thermal_loss_p

    def CurrentObjective(self, power, i_limits, u_limits, internal_parameter_cell):
        """
        Search of the battery current at time t + delta_t to deliver a define power and check battery current and battery voltage limitation.
        This search is based on the module current define by the CurrentObjective method of the ModuleManagementSystem object

        :param power: Power at time t + delta_t
        :type power: W
        :param i_limits: i_min and i_max battery limitation
        :type i_limits: (A, A)
        :param u_limits: u_min and u_max battery limitation
        :type u_limits: (V, V)
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell

        :returns: * **current**
        """
        (i_min, i_max) = i_limits
        (u_min, u_max) = u_limits

        power_module = power/self.number_modules
        (i_min_module, i_max_module) = (i_min/self.number_module_parallel, i_max/self.number_module_parallel)
        (u_min_module, u_max_module) = (u_min/self.number_module_serie, u_max/self.number_module_serie)
        current_module = self.battery.mms.CurrentObjective(power_module, (i_min_module, i_max_module),
                                                           (u_min_module, u_max_module), internal_parameter_cell)
        return current_module*self.number_module_parallel

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'battery' : self.battery.Dict(),
                      'limits_voltage' : self.limits_voltage,
                      'limits_current' : self.limits_current})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an BatteryManagementSystem object

        :param dict_: BatteryManagementSystem dictionnary generate with the Dict method
        """
        battery = ElecBattery.DictToObject(dict_['battery'])
        bms = cls(battery=battery,
                  limits_voltage=dict_['limits_voltage'],
                  limits_current=dict_['limits_current'],
                  name=dict_['name'])
        return bms


class ElecBatteryResult(DessiaObject):
    """
    battery result object to store simulation results

    :param soc: evolution object define the soc result
    :type soc: powerpack.electrical.Evolution
    :param voltage: evolution object define the voltage result
    :type voltage: powerpack.electrical.Evolution
    :param current: evolution object define the current result
    :type current: powerpack.electrical.Evolution
    :param temperature: evolution object define the temperature result
    :type temperature: powerpack.electrical.Evolution
    :param thermal_loss: evolution object define the thermal_loss result
    :type thermal_loss: powerpack.electrical.Evolution
    :param time: evolution object define the time result
    :type time: powerpack.electrical.Evolution
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        "title": "powerpack.electrical.ElecBatteryResult Base Schema",
        'type': 'object',
        "properties": {
            'soc': {
                "type" : "object",
                "title" : "SoC Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "SOC evolution",
                "editable" : False,
                "unit": 'Ah',
                "order" : 1
                },
            'voltage': {
                "type" : "object",
                "title" : "Voltage Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Voltage evolution",
                "editable" : False,
                "unit": 'V',
                "order" : 2
                },
            'current': {
                "type" : "object",
                "title" : "Current Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Current evolution",
                "editable" : False,
                "unit": 'A',
                "order" : 3
                },
            'temperature': {
                "type" : "object",
                "title" : "Temperature Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Temperature evolution",
                "editable" : False,
                "unit": 'K',
                "order" : 4
                },
            'thermal_loss': {
                "type" : "object",
                "title" : "Thermal loss Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Thermal losses evolution",
                "editable" : False,
                "unit": 'W',
                "order" : 5},
            'time': {
                "type" : "object",
                "title" : "Time Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Time evolution",
                "editable" : False,
                "unit": 's',
                "order" : 6
                }
            }
        }

    def __init__(self, soc=None, voltage=None, current=None, temperature=None,
                 thermal_loss=None, time=None, name=''):
        if soc is None:
            self.soc = Evolution()
        else:
            self.soc = soc
        if voltage is None:
            self.voltage = Evolution()
        else:
            self.voltage = voltage
        if current is None:
            self.current = Evolution()
        else:
            self.current = current
        if temperature is None:
            self.temperature = Evolution()
        else:
            self.temperature = temperature
        if thermal_loss is None:
            self.thermal_loss = Evolution()
        else:
            self.thermal_loss = thermal_loss
        if time is None:
            self.time = Evolution()
        else:
            self.time = time
            self.analysis()

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = (self.soc == other.soc
                 and self.voltage == other.voltage
                 and self.current == other.current
                 and self.temperature == other.temperature
                 and self.thermal_loss == other.thermal_loss
                 and self.time == other.time)
        return equal

    def __hash__(self):
        li_hash = hash(self.soc) + hash(self.voltage) + hash(self.current)\
             + hash(self.temperature) + hash(self.thermal_loss) + hash(self.time)
        return li_hash

    def _display_angular(self):
        displays = [{'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.soc.evolution],
                     'label_y': ['soc']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.voltage.evolution],
                     'label_y': ['voltage']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.current.evolution],
                     'label_y': ['current']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.temperature.evolution],
                     'label_y': ['temperature']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.thermal_loss.evolution],
                     'label_y': ['thermal_loss']}]
        return displays

    def Add(self, soc, voltage, current, temperature, thermal_loss, delta_t):
        """
        Add result on the battery result object

        :param soc: new soc data
        :type soc: float
        :param voltage: new voltage data
        :type voltage: float
        :param current: new current data
        :type current: float
        :param temperature: new temperature data
        :type temperature: float
        :param thermal_loss: new thermal_loss data
        :type thermal_loss: float
        :param time: new time data
        :type time: float
        """
        self.soc.evolution.append(soc)
        self.voltage.evolution.append(voltage)
        self.current.evolution.append(current)
        self.temperature.evolution.append(temperature)
        self.thermal_loss.evolution.append(thermal_loss)
        if self.time.evolution == []:
            self.time.evolution.append(0)
        else:
            time_m = self.time.evolution[-1]
            self.time.evolution.append(time_m + delta_t)

    def analysis(self):
        self.number_iter = len(self.time.evolution)
        self.voltage_max = float(max(self.voltage.evolution))
        self.voltage_min = float(min(self.voltage.evolution))
        self.voltage_mean = float(sum(self.voltage.evolution)/len(self.voltage.evolution))
        self.current_max = float(max(self.current.evolution))
        self.current_min = float(min(self.current.evolution))
        self.current_mean = float(sum(self.current.evolution)/len(self.current.evolution))

    def BatteryCharacteristic(self):
        """
        Estimate of several battery characteristic: time_charge, time_discharge,
        power_charge, power_discharge, power_loss_charge, power_loss_discharge
        """
        power = [u*i for u, i in zip(self.voltage.evolution, self.current.evolution)]
        time_charge = 0
        time_discharge = 0
        power_charge = 0
        power_loss_charge = 0
        power_discharge = 0
        power_loss_discharge = 0
        for position, (p, t) in enumerate(zip(power[0: -2], self.time.evolution[0: -2])):
            if p > 0.01:
                time_charge += self.time.evolution[position + 1] - self.time.evolution[position]
                power_charge += p*(self.time.evolution[position + 1] - self.time.evolution[position])
                power_loss_charge += self.thermal_loss.evolution[position]*(self.time.evolution[position + 1] - self.time.evolution[position])
            elif p < -0.01:
                time_discharge += self.time.evolution[position + 1] - self.time.evolution[position]
                power_discharge += p*(self.time.evolution[position + 1] - self.time.evolution[position])
                power_loss_discharge += self.thermal_loss.evolution[position]*(self.time.evolution[position + 1] - self.time.evolution[position])
        self.time_charge = time_charge
        self.time_discharge = time_discharge
        self.power_charge = power_charge
        self.power_discharge = power_discharge
        self.power_loss_charge = power_loss_charge
        self.power_loss_discharge = power_loss_discharge

    def PlotResults(self):
        """
        Plot result in a matplotlib graph all battery results
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(421)
        ax1.set_ylabel('Current (A)')
        ax1.plot(self.time.evolution, self.current.evolution)

        ax2 = fig.add_subplot(423, sharex=ax1)
        ax2.set_ylabel('Voltage (V)')
        ax2.plot(self.time.evolution, self.voltage.evolution)

        ax3 = fig.add_subplot(425, sharex=ax1)
        ax3.set_ylabel('SOC')
        ax3.plot(self.time.evolution, self.soc.evolution)

        power = [u*i for u, i in zip(self.voltage.evolution, self.current.evolution)]
        ax4 = fig.add_subplot(427, sharex=ax1)
        ax4.set_ylabel('Power')
        ax4.plot(self.time.evolution, power)

        ax4.set_xlabel('Time (s)')

        ax5 = fig.add_subplot(422, sharex=ax1)
        ax5.set_ylabel('Power loss')
        ax5.plot(self.time.evolution, self.thermal_loss.evolution)

        ax6 = fig.add_subplot(424)
        ax6.set_ylabel('Current')
        ax6.set_xlabel('Soc')
        ax6.plot(self.soc.evolution, self.current.evolution)

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        if self.soc.evolution != []:
            dict_['soc'] = self.soc.Dict()

        if self.voltage.evolution != []:
            dict_['voltage'] = self.voltage.Dict()

        if self.current.evolution != []:
            dict_['current'] = self.current.Dict()

        if self.temperature.evolution != []:
            dict_['temperature'] = self.temperature.Dict()

        if self.thermal_loss.evolution != []:
            dict_['thermal_loss'] = self.thermal_loss.Dict()

        if self.time.evolution != []:
            dict_['time'] = self.time.Dict()
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an ElecBatteryResult object

        :param dict_: ElecBatteryResult dictionnary generate with the Dict method
        """
        soc = None
        if 'soc' in dict_:
            if dict_['soc'] is not None:
                soc = Evolution.DictToObject(dict_['soc'])
        voltage = None
        if 'voltage' in dict_:
            if dict_['voltage'] is not None:
                voltage = Evolution.DictToObject(dict_['voltage'])
        current = None
        if 'current' in dict_:
            if dict_['current'] is not None:
                current = Evolution.DictToObject(dict_['current'])
        temperature = None
        if 'temperature' in dict_:
            if dict_['temperature'] is not None:
                temperature = Evolution.DictToObject(dict_['temperature'])
        thermal_loss = None
        if 'thermal_loss' in dict_:
            if dict_['thermal_loss'] is not None:
                thermal_loss = Evolution.DictToObject(dict_['thermal_loss'])
        time = None
        if 'time' in dict_:
            if dict_['time'] is not None:
                time = Evolution.DictToObject(dict_['time'])

        battery_result = cls(soc=soc, voltage=voltage, current=current,
                             temperature=temperature, thermal_loss=thermal_loss,
                             time=time, name=dict_['name'])
        return battery_result

class ElecModuleResult(DessiaObject):
    """
    module result object to store simulation results

    :param soc: evolution object define the soc result
    :type soc: powerpack.electrical.Evolution
    :param voltage: evolution object define the voltage result
    :type voltage: powerpack.electrical.Evolution
    :param current: evolution object define the current result
    :type current: powerpack.electrical.Evolution
    :param temperature: evolution object define the temperature result
    :type temperature: powerpack.electrical.Evolution
    :param thermal_loss: evolution object define the thermal_loss result
    :type thermal_loss: powerpack.electrical.Evolution
    :param time: evolution object define the time result
    :type time: powerpack.electrical.Evolution
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        "title": "powerpack.electrical.ElecModuleResult Base Schema",
        'type': 'object',
        "properties": {
            'soc': {
                "type" : "object",
                "title" : "SoC Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "SOC evolution",
                "editable" : False,
                "unit": 'Ah',
                "order" : 1
                },
            'voltage': {
                "type" : "object",
                "title" : "Voltage Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Voltage evolution",
                "editable" : False,
                "unit": 'V',
                "order" : 2
                },
            'current': {
                "type" : "object",
                "title" : "Current Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Current evolution",
                "editable" : False,
                "unit": 'A',
                "order" : 3
                },
            'temperature': {
                "type" : "object",
                "title" : "Temperature Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Temperature evolution",
                "editable" : False,
                "unit": 'K',
                "order" : 4
                },
            'thermal_loss': {
                "type" : "object",
                "title" : "Thermal loss Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Thermal losses evolution",
                "editable" : False,
                "unit": 'W',
                "order" : 5
                },
            'time': {
                "type" : "object",
                "title" : "Time Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Time evolution",
                "editable" : False,
                "unit": 's',
                "order" : 6
                }
            }
        }

    def __init__(self, soc=None, voltage=None, current=None, temperature=None,
                 thermal_loss=None, time=None, name=''):
        # TODO: simplify this by deleting Add method?
        if soc is None:
            self.soc = Evolution()
        else:
            self.soc = soc
        if voltage is None:
            self.voltage = Evolution()
        else:
            self.voltage = voltage
        if current is None:
            self.current = Evolution()
        else:
            self.current = current
        if temperature is None:
            self.temperature = Evolution()
        else:
            self.temperature = temperature
        if thermal_loss is None:
            self.thermal_loss = Evolution()
        else:
            self.thermal_loss = thermal_loss
        if time is None:
            self.time = Evolution()
        else:
            self.time = time
            self.analysis()

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = (self.soc == other.soc
                 and self.voltage == other.voltage
                 and self.current == other.current
                 and self.temperature == other.temperature
                 and self.thermal_loss == other.thermal_loss
                 and self.time == other.time)
        return equal

    def __hash__(self):
        li_hash = hash(self.soc) + hash(self.voltage) + hash(self.current)\
             + hash(self.temperature) + hash(self.thermal_loss) + hash(self.time)
        return li_hash

    def _display_angular(self):
        displays = [{'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.soc.evolution],
                     'label_y': ['soc']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.voltage.evolution],
                     'label_y': ['voltage']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.current.evolution],
                     'label_y': ['current']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.temperature.evolution],
                     'label_y': ['temperature']},
                    {'angular_component': 'app-evolution2d',
                     'table_show': False,
                     'evolution_x': self.time.evolution,
                     'label_x': 'time',
                     'evolution_y': [self.thermal_loss.evolution],
                     'label_y': ['thermal_loss']}]
        return displays

    def Add(self, soc, voltage, current, temperature, thermal_loss, delta_t):
        """
        Add result on the module result object

        :param soc: new soc data
        :type soc: float
        :param voltage: new voltage data
        :type voltage: float
        :param current: new current data
        :type current: float
        :param temperature: new temperature data
        :type temperature: float
        :param thermal_loss: new thermal_loss data
        :type thermal_loss: float
        :param time: new time data
        :type time: float
        """
        self.soc.evolution.append(soc)
        self.voltage.evolution.append(voltage)
        self.current.evolution.append(current)
        self.temperature.evolution.append(temperature)
        self.thermal_loss.evolution.append(thermal_loss)
        if self.time.evolution == []:
            self.time.evolution.append(0)
        else:
            time_m = self.time.evolution[-1]
            self.time.evolution.append(time_m + delta_t)

    def analysis(self):
        self.number_iter = len(self.time.evolution)
        self.voltage_max = float(max(self.voltage.evolution))
        self.voltage_min = float(min(self.voltage.evolution))
        self.voltage_mean = float(sum(self.voltage.evolution)/len(self.voltage.evolution))
        self.current_max = float(max(self.current.evolution))
        self.current_min = float(min(self.current.evolution))
        self.current_mean = float(sum(self.current.evolution)/len(self.current.evolution))

    def PlotResults(self):
        """
        Plot result in a matplotlib graph all battery results
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(421)
        ax1.set_ylabel('Current (A)')
        ax1.plot(self.time.evolution, self.current.evolution)

        ax2 = fig.add_subplot(423, sharex=ax1)
        ax2.set_ylabel('Voltage (V)')
        ax2.plot(self.time.evolution, self.voltage.evolution)

        ax3 = fig.add_subplot(425, sharex=ax1)
        ax3.set_ylabel('SOC')
        ax3.plot(self.time.evolution, self.soc.evolution)

        power = [u*i for u, i in zip(self.voltage.evolution, self.current.evolution)]
        ax4 = fig.add_subplot(427, sharex=ax1)
        ax4.set_ylabel('Power')
        ax4.plot(self.time.evolution, power)

        ax4.set_xlabel('Time (s)')

        ax5 = fig.add_subplot(422, sharex=ax1)
        ax5.set_ylabel('Power loss')
        ax5.plot(self.time.evolution, self.thermal_loss.evolution)

        ax5.set_xlabel('Time (s)')

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        if self.soc.evolution != []:
            dict_['soc'] = self.soc.Dict()

        if self.voltage.evolution != []:
            dict_['voltage'] = self.voltage.Dict()

        if self.current.evolution != []:
            dict_['current'] = self.current.Dict()

        if self.temperature.evolution != []:
            dict_['temperature'] = self.temperature.Dict()

        if self.thermal_loss.evolution != []:
            dict_['thermal_loss'] = self.thermal_loss.Dict()

        if self.time.evolution != []:
            dict_['time'] = self.time.Dict()
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an ElecModuleResult object

        :param dict_: ElecModuleResult dictionnary generate with the Dict method
        """
        soc = None
        if 'soc' in dict_:
            if dict_['soc'] is not None:
                soc = Evolution.DictToObject(dict_['soc'])
        voltage = None
        if 'voltage' in dict_:
            if dict_['voltage'] is not None:
                voltage = Evolution.DictToObject(dict_['voltage'])
        current = None
        if 'current' in dict_:
            if dict_['current'] is not None:
                current = Evolution.DictToObject(dict_['current'])
        temperature = None
        if 'temperature' in dict_:
            if dict_['temperature'] is not None:
                temperature = Evolution.DictToObject(dict_['temperature'])
        thermal_loss = None
        if 'thermal_loss' in dict_:
            if dict_['thermal_loss'] is not None:
                thermal_loss = Evolution.DictToObject(dict_['thermal_loss'])
        time = None
        if 'time' in dict_:
            if dict_['time'] is not None:
                time = Evolution.DictToObject(dict_['time'])

        module_result = cls(soc=soc, voltage=voltage, current=current,
                            temperature=temperature, thermal_loss=thermal_loss,
                            time=time, name=dict_['name'])
        return module_result


class CellResult(DessiaObject):
    """
    module result object to store simulation results

    :param soc: evolution object define the soc result
    :type soc: powerpack.electrical.Evolution
    :param voltage: evolution object define the voltage result
    :type voltage: powerpack.electrical.Evolution
    :param current: evolution object define the current result
    :type current: powerpack.electrical.Evolution
    :param ocv: evolution object define the ocv result
    :type ocv: powerpack.electrical.Evolution
    :param rint: evolution object define the rint result
    :type rint: powerpack.electrical.Evolution
    :param temperature: evolution object define the temperature result
    :type temperature: powerpack.electrical.Evolution
    :param thermal_loss: evolution object define the thermal_loss result
    :type thermal_loss: powerpack.electrical.Evolution
    :param time: evolution object define the time result
    :type time: powerpack.electrical.Evolution
    :param rint1: evolution object define the rint1 result
    :type rint1: powerpack.electrical.Evolution
    :param c1: evolution object define the c1 result
    :type c1: powerpack.electrical.Evolution
    :param current_rint1: evolution object define the current_rint1 result
    :type current_rint1: powerpack.electrical.Evolution
    :param rint2: evolution object define the rint2 result
    :type rint2: powerpack.electrical.Evolution
    :param c2: evolution object define the c2 result
    :type c2: powerpack.electrical.Evolution
    :param current_rint2: evolution object define the current_rint2 result
    :type current_rint2: powerpack.electrical.Evolution
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        "title": "powerpack.electrical.CellResult Base Schema",
        'type': 'object',
        "properties": {
            'soc': {
                "type" : "object",
                "title" : "SoC Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "SOC evolution",
                "editable" : False,
                "unit": 'Ah',
                "order" : 1
                },
            'voltage': {
                "type" : "object",
                "title" : "Voltage Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Voltage evolution",
                "editable" : False,
                "unit": 'V',
                "order" : 2
                },
            'current': {
                "type" : "object",
                "title" : "Current Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Current evolution",
                "editable" : False,
                "unit": 'A',
                "order" : 3
                },
            'temperature': {
                "type" : "object",
                "title" : "Temperature Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Temperature evolution",
                "editable" : False,
                "unit": 'K',
                "order" : 4
                },
            'thermal_loss': {
                "type" : "object",
                "title" : "Thermal loss Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Thermal losses evolution",
                "editable" : False,
                "unit": 'W',
                "order" : 5
                },
            'time': {
                "type" : "object",
                "title" : "Time Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Time evolution",
                "editable" : False,
                "unit": 's',
                "order" : 6
                },
            'ocv': {
                "type" : "object",
                "title" : "OCV Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Ocv evolution",
                "editable" : False,
                "unit": 'V',
                "order" : 7
                },
            'rint': {
                "type" : "object",
                "title" : "Internal Resistance Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Rint evolution",
                "editable" : False,
                "unit": 'ohm',
                "order" : 8
                },
            'rint1': {
                "type" : "object",
                "title" : "Rint1 Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Rint1 evolution",
                "editable" : False,
                "unit": 'ohm',
                "order" : 9
                },
            'c1': {
                "type" : "object",
                "title" : "C1 Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "C1 evolution",
                "editable" : False,
                "unit": 'F',
                "order" : 10
                },
            'current_rint1': {
                "type" : "object",
                "title" : "Rint1 Current Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Current rint1 evolution",
                "editable" : False,
                "unit": 'A',
                "order" : 11
                },
            'rint2': {
                "type" : "object",
                "title" : "Rint2 Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Rint2 evolution",
                "editable" : False,
                "unit": 'ohm',
                "order" : 12
                },
            'c2': {
                "type" : "object",
                "title" : "C2 Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "C2 evolution",
                "editable" : False,
                "unit": 'F',
                "order" : 13
                },
            'current_rint2': {
                "type" : "object",
                "title" : "Rint2 Current Evolution",
                "classes" : ["powerpack.electrical.Evolution"],
                "description" : "Current rint2 evolution",
                "editable" : False,
                "unit": 'A',
                "order" : 14
                },
            'name': {
                "type": "string",
                "title" : "Name",
                "examples": ['Name'],
                "editable": True,
                "description": "Name",
                'order': 0
                },
            }
        }

    def __init__(self, soc=None, voltage=None, current=None, ocv=None,
                 rint=None, temperature=None, thermal_loss=None, time=None,
                 rint1=None, c1=None, current_rint1=None,
                 rint2=None, c2=None, current_rint2=None, name=''):
        if soc is None:
            self.soc = Evolution()
        else:
            self.soc = soc
        if voltage is None:
            self.voltage = Evolution()
        else:
            self.voltage = voltage
        if current is None:
            self.current = Evolution()
        else:
            self.current = current
        if ocv is None:
            self.ocv = Evolution()
        else:
            self.ocv = ocv
        if rint is None:
            self.rint = Evolution()
        else:
            self.rint = rint
        if temperature is None:
            self.temperature = Evolution()
        else:
            self.temperature = temperature
        if thermal_loss is None:
            self.thermal_loss = Evolution()
        else:
            self.thermal_loss = thermal_loss
        if time is None:
            self.time = Evolution()
        else:
            self.time = time
            self.analysis()
        if rint1 is None:
            self.rint1 = Evolution()
        else:
            self.rint1 = rint1
        if rint2 is None:
            self.rint2 = Evolution()
        else:
            self.rint2 = rint2
        if c1 is None:
            self.c1 = Evolution()
        else:
            self.c1 = c1
        if c2 is None:
            self.c2 = Evolution()
        else:
            self.c2 = c2
        if current_rint1 is None:
            self.current_rint1 = Evolution()
        else:
            self.current_rint1 = current_rint1
        if current_rint2 is None:
            self.current_rint2 = Evolution()
        else:
            self.current_rint2 = current_rint2

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = (self.soc == other.soc
                 and self.voltage == other.voltage
                 and self.current == other.current
                 and self.temperature == other.temperature
                 and self.thermal_loss == other.thermal_loss
                 and self.time == other.time
                 and self.ocv == other.ocv
                 and self.rint == other.rint)
        if hasattr(self, 'rint1'):
            equal = equal and self.rint1 == other.rint1
            equal = equal and self.c1 == other.c1
        if hasattr(self, 'rint2'):
            equal = equal and self.rint2 == other.rint2
            equal = equal and self.c2 == other.c2
        return equal

    def __hash__(self):
        li_hash = hash(self.soc) + hash(self.voltage) + hash(self.current)\
             + hash(self.temperature) + hash(self.thermal_loss) + hash(self.time)\
             + hash(self.ocv) + hash(self.rint)
        if hasattr(self, 'rint1'):
            li_hash += hash(self.rint1) + hash(self.c1)
        if hasattr(self, 'rint2'):
            li_hash += hash(self.rint2) + hash(self.c2)
        return li_hash

    def _display_angular(self):
        displays= [{'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.soc.evolution],
                    'label_y': ['soc']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.voltage.evolution],
                    'label_y': ['voltage']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.current.evolution],
                    'label_y': ['current']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.current.evolution],
                    'label_y': ['temperature']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.thermal_loss.evolution],
                    'label_y': ['thermal_loss']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.ocv.evolution],
                    'label_y': ['ocv']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.rint.evolution],
                    'label_y': ['rint']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.rint1.evolution],
                    'label_y': ['rint1']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.c1.evolution],
                    'label_y': ['c1']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.current_rint1.evolution],
                    'label_y': ['current_rint1']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.rint2.evolution],
                    'label_y': ['rint2']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.c2.evolution],
                    'label_y': ['c2']},
                   {'angular_component': 'app-evolution2d',
                    'table_show': False,
                    'evolution_x': self.time.evolution,
                    'label_x': 'time',
                    'evolution_y': [self.current_rint2.evolution],
                    'label_y': ['current_rint2']}]
        return displays

    def Add(self, voltage, current, temperature, delta_t,
            internal_parameter_cell):
        """
        Add result on the cell result object

        :param soc: new soc data
        :type soc: float
        :param voltage: new voltage data
        :type voltage: float
        :param current: new current data
        :type current: float
        :param temperature: new temperature data
        :type temperature: float
        :param delta_t: new delta_t data
        :type delta_t: float
        :param internal_parameter_cell: InternalParameterCell object define all internal cell parameters
        :type internal_parameter_cell: powerpack.electrical.InternalParameterCell
        """
        self.soc.evolution.append(internal_parameter_cell.soc)
        self.voltage.evolution.append(voltage)
        self.current.evolution.append(current)
        self.ocv.evolution.append(internal_parameter_cell.ocv)
        self.rint.evolution.append(internal_parameter_cell.rint)
        self.temperature.evolution.append(temperature)
        self.thermal_loss.evolution.append(internal_parameter_cell.thermal_loss)
        if self.time.evolution == []:
            self.time.evolution.append(0)
        else:
            time_m = self.time.evolution[-1]
            self.time.evolution.append(time_m + delta_t)
        if internal_parameter_cell.rint1 is not None:
            self.rint1.evolution.append(internal_parameter_cell.rint1)
        if internal_parameter_cell.rint2 is not None:
            self.rint2.evolution.append(internal_parameter_cell.rint2)
        if internal_parameter_cell.c1 is not None:
            self.c1.evolution.append(internal_parameter_cell.c1)
        if internal_parameter_cell.c2 is not None:
            self.c2.evolution.append(internal_parameter_cell.c2)
        if internal_parameter_cell.current_rint1 is not None:
            self.current_rint1.evolution.append(internal_parameter_cell.current_rint1)
        if internal_parameter_cell.current_rint2 is not None:
            self.current_rint2.evolution.append(internal_parameter_cell.current_rint2)

    def analysis(self):
        self.number_iter = len(self.time.evolution)
        self.voltage_max = float(max(self.voltage.evolution))
        self.voltage_min = float(min(self.voltage.evolution))
        self.voltage_mean = float(sum(self.voltage.evolution)/len(self.voltage.evolution))
        self.current_max = float(max(self.current.evolution))
        self.current_min = float(min(self.current.evolution))
        self.current_mean = float(sum(self.current.evolution)/len(self.current.evolution))

    def pop(self):
        self.soc.evolution.pop()
        self.voltage.evolution.pop()
        self.current.evolution.pop()
        self.ocv.evolution.pop()
        self.rint.evolution.pop()
        self.temperature.evolution.pop()
        self.thermal_loss.evolution.pop()
        self.time.evolution.pop()
        if self.rint1.evolution != []:
            self.rint1.evolution.pop()
        if self.rint2.evolution != []:
            self.rint2.evolution.pop()
        if self.c1.evolution != []:
            self.c1.evolution.pop()
        if self.c2.evolution != []:
            self.c2.evolution.pop()
        if self.current_rint1.evolution != []:
            self.current_rint1.evolution.pop()
        if self.current_rint2.evolution != []:
            self.current_rint2.evolution.pop()

    def PlotResults(self):
        """
        Plot result in a matplotlib graph all battery results
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(421)
        ax1.set_ylabel('OCV (V)')
        ax1.plot(self.time.evolution, self.ocv.evolution)

        ax2 = fig.add_subplot(423, sharex=ax1)
        ax2.set_ylabel('Internal Resistance (Ohms)')
        ax2.plot(self.time.evolution, self.rint.evolution)

        ax3 = fig.add_subplot(425, sharex=ax1)
        ax3.set_ylabel('Current (A)')
        ax3.plot(self.time.evolution, self.current.evolution)

        ax4 = fig.add_subplot(427, sharex=ax1)
        ax4.set_ylabel('Voltage (V)')
        ax4.plot(self.time.evolution, self.voltage.evolution)

        ax4.set_xlabel('Time (s)')

        power = [abs(u*i) for u, i in zip(self.voltage.evolution, self.current.evolution)]
        ax5 = fig.add_subplot(422, sharex=ax1)
        ax5.set_ylabel('Power Out (W)')
        ax5.plot(self.time.evolution, power)

        ax6 = fig.add_subplot(424, sharex=ax1)
        ax6.set_ylabel('Thermal loss (W)')
        ax6.plot(self.time.evolution, self.thermal_loss.evolution)

        total_power = [p - l for p, l in zip(power, self.thermal_loss.evolution)]
        ax7 = fig.add_subplot(426, sharex=ax1)
        ax7.set_ylabel('Effective Power (W)')
        ax7.plot(self.time.evolution, total_power)

        ax8 = fig.add_subplot(428, sharex=ax1)
        ax8.set_ylabel('SOC')
        ax8.plot(self.time.evolution, self.soc.evolution)

        ax8.set_xlabel('Time (s)')

    def ExportToCSV(self, file):
        """
        Export result object in a csv file

        :param file: open python file
        """
        power = [abs(u*i) for u, i in zip(self.voltage.evolution, self.current.evolution)]
        total_power = [p - l for p, l in zip(power, self.thermal_loss.evolution)]
        file.write('time; ' + '; '.join([str(i) for i in self.time.evolution]) + '\n')
        file.write('ocv; ' + '; '.join([str(i) for i in self.ocv.evolution]) + '\n')
        file.write('rint; ' + '; '.join([str(i) for i in self.rint.evolution]) + '\n')
        file.write('current; ' + '; '.join([str(i) for i in self.current.evolution]) + '\n')
        file.write('voltage; ' + '; '.join([str(i) for i in self.voltage.evolution]) + '\n')
        file.write('thermal_loss; ' + '; '.join([str(i) for i in self.thermal_loss.evolution]) + '\n')
        file.write('power; ' + '; '.join([str(i) for i in power]) + '\n')
        file.write('total_power; ' + '; '.join([str(i) for i in total_power]) + '\n')
        file.write('soc; ' + '; '.join([str(i) for i in self.soc.evolution]) + '\n')
        if self.rint1 is not None:
            file.write('rint1; ' + '; '.join([str(i) for i in self.rint1.evolution]) + '\n')
        if self.rint2 is not None:
            file.write('rint2; ' + '; '.join([str(i) for i in self.rint2.evolution]) + '\n')
        if self.c1 is not None:
            file.write('c1; ' + '; '.join([str(i) for i in self.c1.evolution]) + '\n')
        if self.c2 is not None:
            file.write('c2; ' + '; '.join([str(i) for i in self.c2.evolution]) + '\n')
        if self.current_rint1 is not None:
            file.write('current_rint1; ' + '; '.join([str(i) for i in self.current_rint1.evolution]) + '\n')
        if self.current_rint2 is not None:
            file.write('current_rint2; ' + '; '.join([str(i) for i in self.current_rint2.evolution]) + '\n')
        return file

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        if self.soc.evolution != []:
            dict_['soc'] = self.soc.Dict()

        if self.voltage.evolution != []:
            dict_['voltage'] = self.voltage.Dict()

        if self.current.evolution != []:
            dict_['current'] = self.current.Dict()

        if self.ocv.evolution != []:
            dict_['ocv'] = self.ocv.Dict()

        if self.rint.evolution != []:
            dict_['rint'] = self.rint.Dict()

        if self.temperature.evolution != []:
            dict_['temperature'] = self.temperature.Dict()

        if self.thermal_loss.evolution != []:
            dict_['thermal_loss'] = self.thermal_loss.Dict()

        if self.time.evolution != []:
            dict_['time'] = self.time.Dict()

        if self.rint1.evolution != []:
            dict_['rint1'] = self.rint1.Dict()

        if self.c1.evolution != []:
            dict_['c1'] = self.c1.Dict()

        if self.current_rint1.evolution != []:
            dict_['current_rint1'] = self.current_rint1.Dict()

        if self.rint2.evolution != []:
            dict_['rint2'] = self.rint2.Dict()

        if self.c2.evolution != []:
            dict_['c2'] = self.c2.Dict()

        if self.current_rint2.evolution != []:
            dict_['current_rint2'] = self.current_rint2.Dict()
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an CellResult object

        :param dict_: CellResult dictionnary generate with the Dict method
        """
        soc = None
        if 'soc' in dict_:
            if dict_['soc'] is not None:
                soc = Evolution.DictToObject(dict_['soc'])
        voltage = None
        if 'voltage' in dict_:
            if dict_['voltage'] is not None:
                voltage = Evolution.DictToObject(dict_['voltage'])
        current = None
        if 'current' in dict_:
            if dict_['current'] is not None:
                current = Evolution.DictToObject(dict_['current'])
        temperature = None
        if 'temperature' in dict_:
            if dict_['temperature'] is not None:
                temperature = Evolution.DictToObject(dict_['temperature'])
        thermal_loss = None
        if 'thermal_loss' in dict_:
            if dict_['thermal_loss'] is not None:
                thermal_loss = Evolution.DictToObject(dict_['thermal_loss'])
        time = None
        if 'time' in dict_:
            if dict_['time'] is not None:
                time = Evolution.DictToObject(dict_['time'])
        ocv = None
        if 'ocv' in dict_:
            if dict_['ocv'] is not None:
                ocv = Evolution.DictToObject(dict_['ocv'])
        rint = None
        if 'rint' in dict_:
            if dict_['rint'] is not None:
                rint = Evolution.DictToObject(dict_['rint'])
        rint1 = None
        if 'rint1' in dict_:
            if dict_['rint1'] is not None:
                rint1 = Evolution.DictToObject(dict_['rint1'])
        rint2 = None
        if 'rint2' in dict_:
            if dict_['rint2'] is not None:
                rint2 = Evolution.DictToObject(dict_['rint2'])
        c1 = None
        if 'c1' in dict_:
            if dict_['c1'] is not None:
                c1 = Evolution.DictToObject(dict_['c1'])
        c2 = None
        if 'c2' in dict_:
            if dict_['c2'] is not None:
                c2 = Evolution.DictToObject(dict_['c2'])
        current_rint1 = None
        if 'current_rint1' in dict_:
            if dict_['current_rint1'] is not None:
                current_rint1 = Evolution.DictToObject(dict_['current_rint1'])
        current_rint2 = None
        if 'current_rint2' in dict_:
            if dict_['current_rint2'] is not None:
                current_rint2 = Evolution.DictToObject(dict_['current_rint2'])

        cell_result = cls(soc=soc, voltage=voltage, current=current,
                          ocv=ocv, rint=rint, temperature=temperature,
                          thermal_loss=thermal_loss, time=time,
                          rint1=rint1, c1=c1, current_rint1=current_rint1,
                          rint2=rint2, c2=c2, current_rint2=current_rint2,
                          name=dict_['name'])
        return cell_result

class CellElectricSimulator(DessiaObject):
    def __init__(self, cms, combination_profils, cell_results=None, name=''):
        self.cms = cms
        self.cell_results = cell_results
        self.combination_profils = combination_profils

        DessiaObject.__init__(self, name=name)

    def simulate(self, progress_callback=lambda x:0):
        del self.cell_results
        if not hasattr(self, 'cell_results'):
            cell_results = []
            for comb_profil in self.combination_profils:
                cell_results.append(CellResult())
            self.cell_results = cell_results

        valid_profil = []
        for num_result, combination_profil in enumerate(self.combination_profils):
            progress_callback(num_result/len(self.combination_profils))
            for profile in combination_profil.power_profiles:
                valid = True
                internal_parameter_cell = InternalParameterCell()
                soc_m = profile.soc_init
                results = {'cms': self.cell_results[num_result]}
                for indice, (current, time) in enumerate(zip(profile.evolutions[1:], profile.times[1:])):
                    delta_t = profile.times[indice + 1] - profile.times[indice]

                    if current > 0:
                        usecase = 'charge'
                    else:
                        usecase = 'discharge'

                    (i_min, i_max), (u_min, u_max) = self.cms.Ineq(soc_m, 298.15, usecase, False,
                                                                   delta_t, internal_parameter_cell)
                    if i_max < i_min:
                        valid = False
                        break
                    if u_max < u_min:
                        valid = False
                        break
                    current_new = min(i_max, current)
                    current_new = max(i_min, current_new)

                    p_tuple = self.cms.update(current_new, soc_m, 298.15,
                                          usecase, charger=False,
                                          delta_t=delta_t, results=results,
                                          internal_parameter_cell=internal_parameter_cell)
                    soc_p = p_tuple[2]
                    soc_m = deepcopy(soc_p)

                    if profile.soc_end is not None:
                        if usecase == 'discharge':
                            if soc_m < profile.soc_end:
                                results['cms'].pop()
                                break
                        else:
                            if soc_m > profile.soc_end:
                                results['cms'].pop()
                                break
                valid_profil.append(valid)
        return valid_profil


class PowerPackElectricSimulator(DessiaObject):
    """
    Defines a powerpack electric simulator to simulate battery parameters with
    a power profile in input

    :param bms: electrical battery management system
    :type bms: BatteryManagementSystem
    :param combination_profils: list of power profile object to define input power
    :type combination_profils: [powerpack.electrical.CombinationPowerProfile]
    :param battery_results: list of battery result object to store simulation result
    :type battery_results: [powerpack.electrical.ElecBatteryResult]
    :param module_results: list of module result object to store simulation result
    :type module_results: [powerpack.electrical.ElecModuleResult]
    :param cell_results: list of cell result object to store simulation result
    :type cell_results: [powerpack.electrical.CellResult]

    :Example:

    >>> import powerpack.electrical as elec
    >>> pf1 = elec.PowerPackElectricSimulator(bms = bms1,
                                              combination_profils = [comb_profile_load, comb_profile_wltp, comb_profile_end],
                                              battery_results = [electrical.ElecBatteryResult()]*3,
                                              module_results = [electrical.ElecModuleResult()]*3,
                                              cell_results = [electrical.CellResult()]*3)
    """
    _standalone_in_db = True
    _allowed_methods = ['Simulate']
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.PowerPackElectricSimulator Base Schema",
        "required": ['bms', 'combination_profils'],
        "properties": {
            'bms': {
                "type" : "object",
                "title" : "Battery Management System",
                "classes" : ["powerpack.electrical.BatteryManagementSystem"],
                "description" : "Battery management system",
                "editable" : True,
                "order" : 1
                },
            'analysis': {
                "type" : "object",
                "title" : "PowerPack Analysis",
                "classes" : ["powerpack.electrical.ElecAnalysis"],
                "description" : "PowerPack Analysis",
                "editable" : False
                },
            'battery_results': {
                'type': 'array',
                "title" : "Battery Results",
                "description" : "Battery results",
                "editable" : False,
                "order" : 2,
                'items': {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.ElecBatteryResult"]
                    },
                },
            'module_results': {
                'type': 'array',
                "title" : "Modules Results",
                "description" : "Module results",
                "editable" : False,
                "order" : 3,
                'items': {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.ElecModuleResult"]
                    },
                },
            'cell_results': {
                'type': 'array',
                "title" : "Cells Results",
                "description" : "Cell results",
                "editable" : False,
                "order" : 4,
                'items': {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.CellResult"]
                    },
                },
            'combination_profils': {
                'type': 'array',
                "title" : "Combination Power Profiles",
                "description" : "Combination power profile",
                "editable" : True,
                "order" : 5,
                'items': {
                    "type" : "object",
                    "classes" : ["powerpack.electrical.CombinationPowerProfile"]
                    },
                }
            }
        }

    def __init__(self, bms, combination_profils, battery_results=None,
                 module_results=None, cell_results=None, analysis=None, name=''):
        self.bms = bms
        self.battery_results = battery_results
        self.module_results = module_results
        self.cell_results = cell_results

        self.combination_profils = combination_profils

        self.analysis = analysis

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = self.bms == other.bms
        if self.battery_results is not None:
            for pp, other_pp in zip(self.battery_results, other.battery_results):
                equal = equal and pp == other_pp
        if self.module_results is not None:
            for pp, other_pp in zip(self.module_results, other.module_results):
                equal = equal and pp == other_pp
        if self.cell_results is not None:
            for pp, other_pp in zip(self.cell_results, other.cell_results):
                equal = equal and pp == other_pp
        for pp, other_pp in zip(self.combination_profils, other.combination_profils):
            equal = equal and pp == other_pp
        return equal

    def __hash__(self):
        li_hash = 0
        if self.battery_results is not None:
            for pp in self.battery_results:
                li_hash += hash(pp)
        if self.module_results is not None:
            for pp in self.module_results:
                li_hash += hash(pp)
        if self.cell_results is not None:
            for pp in self.cell_results:
                li_hash += hash(pp)
        for pp in self.combination_profils:
            li_hash += hash(pp)
        li_hash += hash(self.bms)
        return int(li_hash % 1e8)

    def _display_angular(self):
        displays = []
        displays.extend([cp._display_angular() for cp in self.combination_profils])
        if self.battery_results is not None:
            displays.extend([br._display_angular() for br in self.battery_results])
        displays.extend(self.bms._display_angular())
        return displays

    def Simulate(self, progress_callback=lambda x:0):
        """
        Simulation the battery based on combination_profils specifications and
        store results in battery_results, module_results and cell_results

        :returns: * **valid_profil** list of boolean define the PowerProfile exit condition (of each CombinationPowerProfile present in the combination_profils)
        """

        battery_results = []
        for comb_profil in self.combination_profils:
            battery_results.append(ElecBatteryResult())
        self.battery_results = battery_results
        module_results = []
        for comb_profil in self.combination_profils:
            module_results.append(ElecModuleResult())
        self.module_results = module_results
        cell_results = []
        for comb_profil in self.combination_profils:
            cell_results.append(CellResult())
        self.cell_results = cell_results

        valid_profil = []
        for num_result, combination_profil in enumerate(self.combination_profils):
            progress_callback(num_result/len(self.combination_profils))
            valid = True
            for profil_i in combination_profil.power_profiles:
                valid_profil_i = self.SimulateElem(profil = profil_i,
                                                   battery_results = self.battery_results[num_result],
                                                   module_results = self.module_results[num_result],
                                                   cell_results = self.cell_results[num_result])
                if not valid_profil_i:
                    valid = False
            valid_profil.append(valid)

        return valid_profil

    def _analysis(self):
        for battery_result in self.battery_results:
            battery_result.analysis()
        for module_result in self.module_results:
            module_result.analysis()
        for cell_result in self.cell_results:
            cell_result.analysis()

        number_iter = self.battery_results[0].number_iter
        electric_range = number_iter/1478.*14.6
        load_time = len(self.battery_results[1].time.evolution)/10.
        number_cells = self.bms.number_cells
        number_modules = self.bms.number_modules

        voltage_max = self.battery_results[0].voltage_max
        voltage_min = self.battery_results[0].voltage_min
        voltage_mean = self.battery_results[0].voltage_mean
        current_max = self.battery_results[0].current_max
        current_min = self.battery_results[0].current_min
        current_mean = self.battery_results[0].current_mean

        self.analysis = ElecAnalysis(electric_range, load_time, number_cells,
                                     number_modules, voltage_max, voltage_min, voltage_mean,
                                     current_max, current_min, current_mean)
        self.remove()

    def remove(self):
        self.battery_results = None
        self.module_results = None
        self.cell_results = None

#        for battery_result in self.battery_results:
#            battery_result.time.evolution = [0]
#            battery_result.soc.evolution = [0]
#            battery_result.voltage.evolution = [0]
#            battery_result.current.evolution = [0]
#            battery_result.temperature.evolution = [0]
#            battery_result.thermal_loss.evolution = [0]
#
#        for module_result in self.module_results:
#            module_result.time.evolution = [0]
#            module_result.soc.evolution = [0]
#            module_result.voltage.evolution = [0]
#            module_result.current.evolution = [0]
#            module_result.temperature.evolution = [0]
#            module_result.thermal_loss.evolution = [0]
#
#        for cell_result in self.cell_results:
#            cell_result.time.evolution = [0]
#            cell_result.soc.evolution = [0]
#            cell_result.voltage.evolution = [0]
#            cell_result.current.evolution = [0]
#            cell_result.temperature.evolution = [0]
#            cell_result.thermal_loss.evolution = [0]
#            if cell_result.rint1 is not None:
#                cell_result.rint1.evolution = [0]
#            if cell_result.c1 is not None:
#                cell_result.c1.evolution = [0]
#            if cell_result.current_rint1 is not None:
#                cell_result.current_rint1.evolution = [0]
#            if cell_result.rint2 is not None:
#                cell_result.rint2.evolution = [0]
#            if cell_result.c2 is not None:
#                cell_result.c2.evolution = [0]
#            if cell_result.current_rint2 is not None:
#                cell_result.current_rint2.evolution = [0]

    def SimulateElem(self, profil, battery_results, module_results, cell_results):

        result = {'bms': battery_results, 'mms': module_results, 'cms': cell_results}
        valid = True
        valid_profil = True
        soc_m = profil.soc_init*self.bms.number_cells

        number_loop = 0
        number_loop_without_charge = 0
        max_number_loop_without_charge = 20
        internal_parameter_cell = InternalParameterCell()

        while valid:
            for indice, (power, time) in enumerate(zip(profil.evolutions[1:], profil.times[1:])):

                delta_t = profil.times[indice + 1] - profil.times[indice]
                if power > 0:
                    usecase = 'charge'
                else:
                    usecase = 'discharge'

                temperature = 298.15
                (i_min, i_max), (u_min, u_max) = self.bms.Ineq(soc_m, temperature, usecase,
                            profil.charger, delta_t, internal_parameter_cell)

                if u_min > u_max:
                    valid_profil = False
                    valid = False
                    break

                p_min = u_min*i_min
                p_max = u_max*i_max

                p = power
                if p_min > p:
                    p = max(p_min, p)
                if p_max < p:
                    p = min(p_max, p)

                try:
                    current = self.bms.CurrentObjective(p, (i_min, i_max), (u_min, u_max),
                                                        internal_parameter_cell)
                except CurrentObjectiveError:
                    valid = False
                    valid_profil = False
                    break

                current, voltage, soc_p, thermal_loss_p = self.bms.update(current, soc_m, temperature,
                                usecase, profil.charger, delta_t, result, internal_parameter_cell)
                if profil.soc_end is None:
                    if soc_m == soc_p:
                        valid = False
                if usecase == 'charge' and soc_m == soc_p:
                    number_loop_without_charge += 1
                elif usecase == 'charge' and soc_m != soc_p:
                    number_loop_without_charge = 0

                soc_m = soc_p
                delta_power = abs(power - current*voltage)
                if profil.power_accuracy is not None:
                    if delta_power > profil.power_accuracy*(abs(power) + 1e2):
                        valid = False
                        valid_profil = False
                        break

                if profil.soc_end is not None:
                    if abs(soc_p - profil.soc_end*self.bms.number_cells) < 0.05*profil.soc_end*self.bms.number_cells:
                        valid = False
                        valid_profil = True
                        break

                if usecase == 'charge' and number_loop_without_charge == max_number_loop_without_charge:
                    valid = False
                    valid_profil = False
                    break

            number_loop += 1
            if profil.loop:
                if profil.max_loop is not None:
                    if profil.max_loop < number_loop:
                        valid = False
                        valid_profil = False
            else:
                valid = False
        return valid_profil

    def DiscretPower(self, dtime_power=100):
        if self.module_results is None:
            self.Simulate()
        dtimes = []
        li_power_analysis = []
        for elec_module_result in self.module_results:
            dtime = dtime_power
            power_analysis = []
            p, t = 0, 0
            for i, di in enumerate(elec_module_result.time.evolution[0:-1]):
                t += (elec_module_result.time.evolution[i + 1] - di)
                p += elec_module_result.thermal_loss.evolution[i]*(elec_module_result.time.evolution[i + 1] - di)
                if t >= dtime:
                    power_analysis.append(p/dtime)
                    p, t = 0, 0
            if len(power_analysis) < 5:
                power_analysis = elec_module_result.thermal_loss.evolution
                dtime = elec_module_result.time.evolution[1] - elec_module_result.time.evolution[0]
            dtimes.append(dtime)
            li_power_analysis.append(power_analysis)
        self.remove()
        return dtimes, li_power_analysis

    def Dict(self):
        """
        Export cell in a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'bms' : self.bms.Dict(),
                      'combination_profils' : [p.to_dict()\
                                               for p in self.combination_profils]})

        if self.battery_results is not None:
            dict_['battery_results'] = [r.to_dict() for r in self.battery_results]
        if self.module_results is not None:
            dict_['module_results'] = [r.to_dict() for r in self.module_results]
        if self.cell_results is not None:
            dict_['cell_results'] = [r.to_dict() for r in self.cell_results]

        if self.analysis is not None:
            dict_['analysis'] = self.analysis.to_dict()
        else:
            dict_['analysis'] = None
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an PowerPackElectricSimulator object

        :param dict_: PowerPackElectricSimulator dictionnary generate with the Dict method
        """
        bms = BatteryManagementSystem.DictToObject(dict_['bms'])
        battery_results = None
        if 'battery_results' in dict_:
            if dict_['battery_results'] is not None:
                battery_results = [ElecBatteryResult.DictToObject(case_result)\
                                   for case_result in dict_['battery_results']]
        module_results = None
        if 'module_results' in dict_:
            if dict_['module_results'] is not None:
                module_results = [ElecModuleResult.DictToObject(case_result)\
                                  for case_result in dict_['module_results']]
        cell_results = None
        if 'cell_results' in dict_:
            if dict_['cell_results'] is not None:
                cell_results = [CellResult.DictToObject(case_result)\
                                for case_result in dict_['cell_results']]
        profils = [CombinationPowerProfile.DictToObject(combination_profil)\
                   for combination_profil in dict_['combination_profils']]

        analysis = None
        if 'analysis' in dict_:
            analysis = ElecAnalysis.dict_to_object(dict_['analysis'])

        powerpack_simu = cls(bms=bms,
                             combination_profils=profils,
                             battery_results=battery_results,
                             module_results=module_results,
                             cell_results=cell_results,
                             analysis=analysis,
                             name=dict_['name'])
        return powerpack_simu

class InternalParameterCell(DessiaObject):
    """
    Internal object to store internal parameter a the current time

    :param soc_m: current state of charge at the current time
    :type soc_m: float
    :param soc: state of charge a the next step
    :type soc: float
    :param thermal_loss: thermal_loss a the next step
    :type thermal_loss: float
    :param ocv: ocv a the next step
    :type ocv: float
    :param rint: rint a the next step
    :type rint: float
    :param rint1: rint1 a the next step
    :type rint1: float
    :param c1: c1 a the next step
    :type c1: float
    :param current_rint1: current_rint1 a the next step
    :type current_rint1: float
    :param rint2: rint2 a the next step
    :type rint2: float
    :param c2: c2 a the next step
    :type c2: float
    :param current_rint2: current_rint2 a the next step
    :type current_rint2: float
    :param current_rint1_m: current_rint1 a the current time
    :type current_rint1_m: float
    :param current_rint2_m: current_rint2 a the current time
    :type current_rint2_m: float
    """
    def __init__(self, soc_m=None, soc=None, thermal_loss=None, ocv=None,
                 rint=None, rint1=None, c1=None, current_rint1=None,
                 rint2=None, c2=None, current_rint2=None,
                 current_rint1_m=0, current_rint2_m=0):
        self.soc_m = soc_m
        self.soc = soc
        self.thermal_loss = thermal_loss
        self.ocv = ocv
        self.rint = rint
        self.rint1 = rint1
        self.rint2 = rint2
        self.c1 = c1
        self.c2 = c2
        self.current_rint1 = current_rint1
        self.current_rint2 = current_rint2
        self.current_rint1_m = current_rint1_m
        self.current_rint2_m = current_rint2_m

class CurrentObjectiveError(Exception):
    def __init__(self):
        super().__init__('Fail in search a current to reach the power objective')


def GenerateElecBatteries(batteries_combinations, cell,
                          electrical_limits, detail=False):
    """
    Generate ElecBatteries from specs

    :param specs_dict: List of dictionnaries that represent an electrical structure of a battery

    :Example:

    >>> specs = [{'battery': (2, 19), 'module': (4, 10)},
                 {'battery': (2, 20), 'module': (4, 10)},
                 {'battery': (2, 21), 'module': (4, 9)},
                 {'battery': (2, 21), 'module': (4, 10)}]

    :returns: **batteries** List of ElecBattery objects
    """
    # !!! Is this still used ? ElecModule and ElecBattery instantiations look outdated
    elec_batteries = []
    for batteries_combination in batteries_combinations:
        if detail:
            # TODO Modify this if statement for BMS
            elec_cells = []
            count_cells = 0
            position_cells = []
            for _ in range(batteries_combination['module'][0]):
                line = []
                for _ in range(batteries_combination['module'][1]):
                    line.append(count_cells)
                    elec_cells.append(deepcopy(cell))
                    count_cells += 1
                position_cells.append(line)

            elec_modules = []
            count_modules = 0
            position_modules = []
            for _ in range(batteries_combination['battery'][0]):
                line = []
                for _ in range(batteries_combination['battery'][1]):
                    line.append(count_modules)
                    elec_modules.append(ElecModule(elec_cells,
                                                   position_cells,
                                                   electrical_limits['voltage_module'],
                                                   electrical_limits['current_module'],
                                                   detail))
                    count_cells += 1
                position_modules.append(line)

        else:
            position_cms = [[0]*batteries_combination['module'][1]]*batteries_combination['module'][0]
            position_mms = [[0]*batteries_combination['battery'][1]]*batteries_combination['battery'][0]

            cms = CellManagementSystem([cell])
            elec_modules = [ElecModule([cms],
                                       position_cms,
                                       electrical_limits['voltage_module'],
                                       electrical_limits['current_module'],
                                       detail)]
            mms = ModuleManagementSystem(elec_modules)

        elec_battery = ElecBattery([mms],
                                   position_mms,
                                   electrical_limits['voltage_battery'],
                                   electrical_limits['current_battery'],
                                   detail)

        elec_batteries.append(elec_battery)
    return elec_batteries
