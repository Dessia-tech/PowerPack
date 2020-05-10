import matplotlib.pyplot as plt
import numpy as npy
from scipy import interpolate
import volmdlr as vm
from volmdlr import primitives2D
from powerpack import electrical, mechanical
from dessia_common import DessiaObject
from scipy.optimize import minimize, minimize_scalar

from powerpack.electrical import Evolution

class ThermalAnalysis(DessiaObject):
    _standalone_in_db = True
    _jsonschema = {
        "definitions": { },
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.electrical.ThermalAnalysis Base Schema",
        "required": [],
        "properties": {
            'cooling_price': {
                "type": "number",
                "title" : "Cooling Price",
                "examples": [1],
                "editable": False,
                "description": "Cooling Price",
                },
            'cooling_surface': {
                "type": "number",
                "title" : "Cooling Surface",
                "examples": [1],
                "editable": False,
                "description": "Cooling Surface",
                },
            'grid_0': {
                "type": "number",
                "title" : "Grid Direction 0",
                "examples": [1],
                "editable": False,
                "description": "Grid Direction 0",
                },
            'grid_1': {
                "type": "number",
                "title" : "Grid Direction 1",
                "examples": [1],
                "editable": False,
                "description": "Grid Direction 1",
                },
            'grid_2': {
                "type": "number",
                "title" : "Grid Direction 2",
                "examples": [1],
                "editable": False,
                "description": "Grid Direction 2",
                },
            'normal_face_cooling': {
                "type": "number",
                "title" : "Normal Face Cooling",
                "examples": [1],
                "editable": False,
                "description": "Normal Face Cooling",
                },
            'internal_cooling': {
                "type": "number",
                "title" : "Internal Cooling",
                "examples": [1],
                "editable": False,
                "description": "Internal Cooling",
                },
            'use_two_faces': {
                "type": "number",
                "title" : "Use Two Faces",
                "examples": [1],
                "editable": False,
                "description": "Use Two Faces",
                },
            'alpha': {
                "type": "number",
                "title" : "Alpha",
                "examples": [1],
                "editable": False,
                "description": "Alpha",
                },
            'htc_mean': {
                "type": "number",
                "title" : "HTC Mean",
                "examples": [1],
                "editable": False,
                "description": "HTC Mean",
                },
            'htc_min': {
                "type": "number",
                "title" : "HTC Min",
                "examples": [1],
                "editable": False,
                "description": "HTC Min",
                },
            'htc_max': {
                "type": "number",
                "title" : "HTC Max",
                "examples": [1],
                "editable": False,
                "description": "HTC Max",
                },
            'dispersed_power_mean': {
                "type": "number",
                "title" : "Dispersed Power Mean",
                "examples": [1],
                "editable": False,
                "description": "Dispersed Power Mean",
                },
            'dispersed_power_min': {
                "type": "number",
                "title" : "Dispersed Power Min",
                "examples": [1],
                "editable": False,
                "description": "Dispersed Power Min",
                },
            'dispersed_power_max': {
                "type": "number",
                "title" : "Dispersed Power Max",
                "examples": [1],
                "editable": False,
                "description": "Dispersed Power Max",
                },
            }
        }

    def __init__(self, cooling_price=None, cooling_surface=None, grid_0=None, grid_1=None, grid_2=None,
                 normal_face_cooling=None, internal_cooling=None, use_two_faces=None, alpha=None,
                 htc_mean=None, htc_min=None, htc_max=None, dispersed_power_mean=None,
                 dispersed_power_min=None, dispersed_power_max=None, name=''):
        self.cooling_price = cooling_price
        self.cooling_surface = cooling_surface
        self.grid_0 = grid_0
        self.grid_1 = grid_1
        self.grid_2 = grid_2
        self.normal_face_cooling = normal_face_cooling
        self.internal_cooling = internal_cooling
        self.use_two_faces = use_two_faces
        self.alpha = alpha
        self.htc_mean = htc_mean
        self.htc_min = htc_min
        self.htc_max = htc_max
        self.dispersed_power_mean = dispersed_power_mean
        self.dispersed_power_min = dispersed_power_min
        self.dispersed_power_max = dispersed_power_max

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = all([v == getattr(other, k) for k, v in self.__dict__.items()])
        return equal

    def __hash__(self):
        hash_ = int(hash(self.cooling_price) + hash(self.cooling_surface) + hash(self.htc_mean) % 10e5)
        return hash_

    def to_dict(self):
        """
        Export object in a dictionary
        """
        d={}
        d['cooling_price'] = self.cooling_price
        d['cooling_surface'] = self.cooling_surface
        d['grid_0'] = self.grid_0
        d['grid_1'] = self.grid_1
        d['grid_2'] = self.grid_2
        d['normal_face_cooling'] = self.normal_face_cooling
        d['internal_cooling'] = self.internal_cooling
        d['use_two_faces'] = self.use_two_faces
        d['alpha'] = self.alpha
        if self.htc_mean is not None:
            d['htc_mean'] = self.htc_mean
        if self.htc_min is not None:
            d['htc_min'] = self.htc_min
        if self.htc_max is not None:
            d['htc_max'] = self.htc_max
        if self.dispersed_power_mean is not None:
            d['dispersed_power_mean'] = self.dispersed_power_mean
        if self.dispersed_power_min is not None:
            d['dispersed_power_min'] = self.dispersed_power_min
        if self.dispersed_power_max is not None:
            d['dispersed_power_max'] = self.dispersed_power_max
        d['name'] = self.name
        return d

    @classmethod
    def dict_to_object(cls, d):
        """
        Generate an Evolution object

        :param d: Evolution dictionnary generate with the Dict method
        """
        if d != None:
            out = {}
            for key, val in d.items():
                out[key] = val
            return cls(**out)
        return ThermalAnalysis()

class SpecsCooling(DessiaObject):
    """
    Define specification cooling for a fixed internal parameter

    :param internal_parameter: internal parameter value
    :param thermal_transfer_coefficient_min: minimum thermal resistance combination evolution (htc versus dissipated power)
    :type thermal_transfer_coefficient_min: powerpack.electrical.CombinationEvolution
    :param thermal_transfer_coefficient_max: maximum thermal resistance combination evolution (htc versus dissipated power)
    :type thermal_transfer_coefficient_max: powerpack.electrical.CombinationEvolution
    :param title: title of this cooling
    :type title: string

    :Example:

    >>> import dessia_common as dc
    >>> import powerpack.optimization.thermal as thermal
    >>> import powerpack.optimization.electrical as elec
    >>> altitude = 0.1
    >>> evol_power1 = elec.Evolution(evolution = [0, 2, 4, 6, 8, 10])
    >>> evol_power2 = electrical.Evolution(evolution = [0, 3, 5, 7, 9, 12])
    >>> evol_h_min1 = electrical.Evolution(evolution = [0 + 0.3*1e1*p/(p + 0.1)/2.
                                                        for p in [0, 2, 4, 6, 8, 10]])
    >>> evol_h_max2 = electrical.Evolution(evolution = [altitude + 0.3*1e1*p/(p + 0.1)/2.
                                                        for p in [0, 3, 5, 7, 9, 12]])
    >>> ce_cooling1_min = electrical.CombinationEvolution(evolution1 = [evol_power1],
                                                          evolution2 = [evol_h_min1]),
                                                          title1='power', title2='h')
    >>> ce_cooling1_max = electrical.CombinationEvolution(evolution1 = [evol_power2],
                                                          evolution2 = [evol_h_max2],
                                                          title1='power', title2='h')
    >>> sc1 = thermal.SpecsCooling(temperature = 273, thermal_transfer_coefficient_min = ce_cooling1_min,
                                   thermal_transfer_coefficient_max = ce_cooling1_max, title = 'Cooling')
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.SpecsCooling Base Schema",
        "required": ['internal_parameter', 'thermal_transfer_coefficient_min', 'thermal_transfer_coefficient_max'],
        "properties": {
            "thermal_transfer_coefficient_min" : {
                "type" : "object",
                "title" : "Thermal Trasnfer Coefficient Minimum",
                "classes" : ["powerpack.electrical.CombinationEvolution"],
                "order" : 1,
                "editable" : True,
                "description" : "Thermal resistance min"
                },
            "thermal_transfer_coefficient_max" : {
                "type" : "object",
                "title" : "Thermal Transfer Coefficient Maximum",
                "classes" : ["powerpack.electrical.CombinationEvolution"],
                "order" : 2,
                "editable" : True,
                "description" : "Thermal resistance max"
                },
            'title': {
                "type": "string",
                "title" : "Title",
                "examples": ['Title'],
                "editable": True,
                "description": "Title",
                "order": 3
                },
            "internal_parameter" : {
                "type" : "number",
                "title" : "Internal Parameter",
                "order" : 4,
                "step" : 1,
                "minimum" : 0,
                "editable": True,
                "examples" : [273]
                }
            }
        }

    def __init__(self, internal_parameter, thermal_transfer_coefficient_min,
                 thermal_transfer_coefficient_max, title='', name=''):
        self.thermal_transfer_coefficient_min = thermal_transfer_coefficient_min
        self.thermal_transfer_coefficient_max = thermal_transfer_coefficient_max
        self.internal_parameter = internal_parameter
        self.title = title
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_cell):
        equal = (self.internal_parameter == other_cell.internal_parameter
                 and self.thermal_transfer_coefficient_min == other_cell.thermal_transfer_coefficient_min
                 and self.thermal_transfer_coefficient_max == other_cell.thermal_transfer_coefficient_max)
        return equal

    def __hash__(self):
        hash_spec = hash(self.thermal_transfer_coefficient_min) + hash(self.thermal_transfer_coefficient_max)
        return hash_spec

    def update(self, alpha, thermal_transfer_coefficient):
        """
        Update thermal_transfer_coefficient CombinationEvolution at the alpha level
        """
        x, y = [], []
        for evol_min_x, evol_min_y, evol_max_x, evol_max_y in zip(self.thermal_transfer_coefficient_min.x,
                                                                  self.thermal_transfer_coefficient_min.y,
                                                                  self.thermal_transfer_coefficient_max.x,
                                                                  self.thermal_transfer_coefficient_max.y):
            x.append(evol_min_x + alpha*(evol_max_x - evol_min_x))
            y.append(evol_min_y + alpha*(evol_max_y - evol_min_y))
        thermal_transfer_coefficient.update([x], [y])

    def Plot(self, thermal_transfer_coefficient=None, a=None):
        """
        Plot the SpecsCooling curve and the thermal_transfer_coefficient curve
        """
        points = []
        curves = []
        li_thermal_transfer_coefficient = [self.thermal_transfer_coefficient_min, self.thermal_transfer_coefficient_max]
        if thermal_transfer_coefficient is not None:
            li_thermal_transfer_coefficient.append(thermal_transfer_coefficient)
        for tr in li_thermal_transfer_coefficient:
            evol_x = tr.x
            evol_y = tr.y
            points_temp = []
            for x, y in zip(evol_x, evol_y):
                points_temp.append(vm.Point2D((x, y)))
            curves.append(primitives2D.RoundedLineSegments2D(points_temp, {}, False))
            points.extend(points_temp)
        curves2D = vm.Contour2D(curves)
        if a == None:
            f, a = curves2D.MPLPlot()
        else:
            curves2D.MPLPlot(a)
        for point in points:
            point.MPLPlot(a)
        return a

    def Dict(self):
        """
        Export object in a dictionary
        """
        d={}
        d['internal_parameter'] = self.internal_parameter
        d['thermal_transfer_coefficient_min'] = self.thermal_transfer_coefficient_min.Dict()
        d['thermal_transfer_coefficient_max'] = self.thermal_transfer_coefficient_max.Dict()
        d['title'] = self.title
        d['name'] = self.name
        return d

    @classmethod
    def DictToObject(cls, d):
        """
        Generate an SpecsCooling object

        :param d: SpecsCooling dictionnary generate with the Dict method
        """
        specs = cls(internal_parameter=d['internal_parameter'],
                   thermal_transfer_coefficient_min=electrical.CombinationEvolution.DictToObject(d['thermal_transfer_coefficient_min']),
                   thermal_transfer_coefficient_max=electrical.CombinationEvolution.DictToObject(d['thermal_transfer_coefficient_max']),
                   title=d['title'],
                   name=d['name'])
        return specs

class CombinationSpecsCooling(DessiaObject):
    """
    Define specification cooling combination

    :param specs_coolings: list of cooling specification for several internal parameter
    :type specs_coolings: [powerpack.thermal.SpecsCooling]
    :param title: title of this cooling
    :type title: string

    :Example:

    >>> import powerpack.optimization.thermal as thermal
    >>> csc1 = thermal.CombinationSpecsCooling(specs_coolings = [sc1])
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.CombinationSpecsCooling Base Schema",
        "required": ['specs_coolings'],
        "properties": {
            'specs_coolings': {
               "type": "array",
               "title" : "Cooling Specifications",
               "order": 2,
               "editable": True,
               "description": "Spec coolings",
               "items" : {
                   "type" : "object",
                   "classes" : ["powerpack.thermal.SpecsCooling"]
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

    def __init__(self, specs_coolings, title='', name=''):
        self.specs_coolings = specs_coolings
        self.title = title
        self._update_data = None

        f_specs_coolings = {}
        for specs_cooling in specs_coolings:
            internal_parameter = specs_cooling.internal_parameter
            f_specs_coolings[internal_parameter] = {}
            curve_min = specs_cooling.thermal_transfer_coefficient_min
            curve_max = specs_cooling.thermal_transfer_coefficient_max
            f_specs_coolings[internal_parameter]['thermal_transfer_coefficient_min'] = interpolate.splrep(curve_min.x, curve_min.y)
            f_specs_coolings[internal_parameter]['thermal_transfer_coefficient_max'] = interpolate.splrep(curve_max.x, curve_max.y)
        self.specs_coolings = specs_coolings
        self.f_specs_coolings = f_specs_coolings
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_cell):
        equal = True
        for specs_cooling, other_specs_cooling in zip(self.specs_coolings, other_cell.specs_coolings):
            equal = (equal and specs_cooling == other_specs_cooling)
        return equal

    def __hash__(self):
        hash_spec = 0
        for specs_cooling in self.specs_coolings:
            hash_spec += hash(specs_cooling)
        return hash_spec

    def Plot(self, thermal_transfer_coefficients=None, a=None):
        """
        Plot all the SpecsCooling curve include in the specs_coolings attribute
        and the thermal_transfer_coefficients list curve
        """
        a = None
        for specs_cooling in self.specs_coolings:
            if thermal_transfer_coefficients is not None:
                for thermal_transfer_coefficient in thermal_transfer_coefficients:
                    a = specs_cooling.Plot(thermal_transfer_coefficient = thermal_transfer_coefficient, a = a)
            else:
                a = specs_cooling.Plot(a = a)
        return a

    def Plotevaluate(self, alpha, power , thermal_transfer_coefficient,
                     internal_parameter, thermal_transfer_coefficients_other=None,
                     discret=10, a=None):
        """
        Plot all the SpecsCooling curve include in the specs_coolings attribute
        and a thermal_transfer_coefficient curve interpolate with alpha and internal_parameter input
        """
        h_estim = self.evaluate(alpha, power, thermal_transfer_coefficient,
                                internal_parameter, discret)
        if thermal_transfer_coefficients_other is not None:
            a = self.Plot(thermal_transfer_coefficients = thermal_transfer_coefficients_other)
        else:
            a = self.Plot()
        evol_x = thermal_transfer_coefficient.x
        evol_y = thermal_transfer_coefficient.y
        points = []
        for x, y in zip(evol_x, evol_y):
            points.append(vm.Point2D((x, y)))
        curve = primitives2D.RoundedLineSegments2D(points, {}, False)
        curves2D = vm.Contour2D([curve])
        curves2D.MPLPlot(a, style = '-g')
        for point in points:
            point.MPLPlot(a, style = 'og')
        vm.Point2D((abs(power), h_estim)).MPLPlot(a, style = 'or')

    def Interp(self, alpha, thermal_transfer_coefficient, internal_parameter, discret=10):
        dict_cooling = {}
        for specs_cooling in self.specs_coolings:
            tr = thermal_transfer_coefficient.Copy()
            specs_cooling.update(alpha, tr)
            dict_cooling[specs_cooling.internal_parameter] = tr
        temp_inf = []
        temp_sup = []
        for specs_cooling in self.specs_coolings:
            temp = specs_cooling.internal_parameter
            if temp <= internal_parameter:
                temp_inf.append(temp)
            else:
                temp_sup.append(temp)
        if temp_inf == []:
            temp_interp = [min(temp_sup)]*2
        elif temp_sup == []:
            temp_interp = [max(temp_inf)]*2
        else:
            temp_interp = [max(temp_inf), min(temp_sup)]
        f_coolings = []
        bound_coolings = []
        for ti in temp_interp:
            thermal_re = dict_cooling[ti]
            bound_coolings.append([min(thermal_re.x), max(thermal_re.x)])
            f_coolings.append(interpolate.interp1d(thermal_re.x, thermal_re.y, fill_value="extrapolate"))
        matrix_interp = []
        for bound_cooling, f_cooling in zip(bound_coolings, f_coolings):
            y = []
            li_x = list(npy.linspace(bound_cooling[0], bound_cooling[1], discret))
            for x in li_x:
                y.append(float(f_cooling(x)))
            matrix_interp.append([li_x, y])
        x, y = [], []
        for x_t1, y_t1, x_t2, y_t2 in zip(matrix_interp[0][0], matrix_interp[0][1],
                                          matrix_interp[1][0], matrix_interp[1][1]):
            if temp_interp[0] != temp_interp[1]:
                coeff1 = (internal_parameter - temp_interp[0])/(temp_interp[1] - temp_interp[0])
            else:
                coeff1 = 1/2.
            x.append((x_t1 + coeff1*(x_t2 - x_t1)))
            y.append((y_t1 + coeff1*(y_t2 - y_t1)))
        thermal_transfer_coefficient.update([x], [y])

    def evaluate(self, alpha, power, thermal_transfer_coefficient, internal_parameter=293, discret=10):
        """
        Estimation of the htc define with power, alpha and internal_parameter

        :param alpha: cooling specification parameter
        :type alpha: float
        :param power: dissipated power
        :type power: W
        :param thermal_transfer_coefficient: String define the battery trend (charge or discharge)
        :type thermal_transfer_coefficient: powerpack.electrical.CombinationEvolution
        :param internal_parameter: internal parameter
        :type internal_parameter: float
        :param discret: number of point to generate the interpolation
        :type discret: integer

        :returns: * **htc** htc parameter
        """
        self.Interp(alpha, thermal_transfer_coefficient, internal_parameter, discret)
        x = thermal_transfer_coefficient.x
        y = thermal_transfer_coefficient.y
        f = interpolate.interp1d(x, y, fill_value="extrapolate")
        return float(f(min(max(min(x), abs(power)), max(x))))

    def Dict(self):
        """
        Export object in a dictionary
        """
        d={}
        d['specs_coolings'] = []
        for specs_cooling in self.specs_coolings:
            d['specs_coolings'].append(specs_cooling.Dict())
        d['title'] = self.title
        d['name'] = self.name
        return d

    @classmethod
    def DictToObject(cls, d):
        """
        Generate an CombinationSpecsCooling object

        :param d: CombinationSpecsCooling dictionnary generate with the Dict method
        """
        specs_coolings = []
        for specs_cooling in d['specs_coolings']:
            specs_coolings.append(SpecsCooling.DictToObject(specs_cooling))
        specs = cls(specs_coolings=specs_coolings, title=d['title'], name=d['name'])
        return specs

class CoolingComponent(DessiaObject):
    """
    Define a cooling component

    :param combination_specs_cooling: specification cooling combination
    :type combination_specs_cooling: powerpack.thermal.CombinationSpecsCooling
    :param thermal_capacity: thermal capacity
    :type thermal_capacity: J.kg-1.K-1
    :param delta_internal_variable: maximum variation speed of the internal parameter
    :type delta_internal_variable: s-1
    :param coeff_a_price: slope coefficient to estimate cooling component price per surface
    :type coeff_a_price: €.alpha-1.m-2
    :param coeff_b_price: y intercept to estimate cooling component price per surface
    :type coeff_b_price: €.m-2

    :Example:

    >>> import powerpack.optimization.thermal as thermal
    >>> csc1 = thermal.CombinationSpecsCooling(specs_coolings = [sc1, sc2])
    >>> cc1 = thermal.CoolingComponent(csc1, thermal_capacity = 0.1, coeff_a_price = 0.4,
                                       coeff_b_price = 1)
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.CoolingComponent Base Schema",
        "required": ['combination_specs_cooling', 'thermal_capacity'],
        "properties": {
            "combination_specs_cooling" : {
                "type" : "object",
                "title" : "Combination Specs Cooling",
                "classes" : ["powerpack.thermal.CombinationSpecsCooling"],
                "order" : 1,
                "editable" : True,
                "description" : "Combination specs cooling"
                },
            "thermal_capacity" : {
                "type" : "number",
                "title" : "Thermal Capacity",
                "order" : 2,
                "step" : 0.01,
                "minimum" : 0,
                "unit" : "J.K-1.kg-1",
                "examples" : [0.1],
                "editable": True,
                "description" : "Thermal capacity"
                },
            "delta_internal_variable" : {
                "type" : "number",
                "title" : "Delta Internal Variable",
                "order" : 3,
                "step" : 0.0001,
                "minimum" : 0,
                "unit" : "K.s-1",
                "examples" : [0.001],
                "editable": True,
                "description" : "Delta internal variable"
                },
            "coeff_a_price" : {
                "type" : "number",
                "title" : "Coefficient a Price",
                "order" : 4,
                "step" : 0.01,
                "minimum" : 0,
                "examples" : [1],
                "editable": True,
                "description" : "Coefficient a for the price"
                },
            "coeff_b_price" : {
                "type" : "number",
                "title" : "Coefficient b Price",
                "order" : 5,
                "step" : 0.01,
                "minimum" : 0,
                "examples" : [0],
                "editable": True,
                "description" : "Coefficient b for the price"
                },
            }
        }

    def __init__(self, combination_specs_cooling, thermal_capacity,
                 delta_internal_variable=None,
                 coeff_a_price=None, coeff_b_price=None, name=''):
        self.combination_specs_cooling = combination_specs_cooling
        self.delta_internal_variable = delta_internal_variable
        self.thermal_capacity = thermal_capacity
        if delta_internal_variable is None:
            self.delta_internal_variable = 0.001
        else:
            self.delta_internal_variable = delta_internal_variable
        if coeff_a_price is None:
            self.coeff_a_price = 1
        else:
            self.coeff_a_price = coeff_a_price
        if coeff_b_price is None:
            self.coeff_b_price = 0
        else:
            self.coeff_b_price = coeff_b_price
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_cell):
        equal = (self.combination_specs_cooling == other_cell.combination_specs_cooling
                 and self.thermal_capacity == other_cell.thermal_capacity
                 and self.delta_internal_variable == other_cell.delta_internal_variable
                 and self.coeff_a_price == other_cell.coeff_a_price
                 and self.coeff_b_price == other_cell.coeff_b_price)
        return equal

    def __hash__(self):
        hash_spec = hash(self.combination_specs_cooling) + hash(self.thermal_capacity)
        return hash_spec

    def max_htc(self, internal_parameter=293):
        """
        Estimation of the max htc at a fixed internal parameter

        :param internal_parameter: internal parameter
        :type internal_parameter: float

        :returns: * **max htc** maximum htc
        """
        thermal_transfer_coefficient = electrical.CombinationEvolution(evolution1 = [electrical.Evolution()],
                                                             evolution2 = [electrical.Evolution()])
        self.combination_specs_cooling.evaluate(alpha = 1, power = 0, thermal_transfer_coefficient = thermal_transfer_coefficient)
        def fun(x):
            return 1/(self.evaluate(alpha = 1, power = x, thermal_transfer_coefficient = thermal_transfer_coefficient,
                                    internal_parameter = internal_parameter))**2
        res = minimize_scalar(fun, bounds=(min(thermal_transfer_coefficient.x),
                              max(thermal_transfer_coefficient.x)),
                              method='bounded')
        return self.evaluate(alpha = 1, power = res.x, thermal_transfer_coefficient = thermal_transfer_coefficient,
                             internal_parameter = internal_parameter)
    def evaluate(self, alpha, power, thermal_transfer_coefficient, internal_parameter=293):
        h = self.combination_specs_cooling.evaluate(alpha = alpha, power = power,
                                            thermal_transfer_coefficient = thermal_transfer_coefficient,
                                            internal_parameter = internal_parameter)
        return h
    def price(self, alpha):
        """
        Price estimation of the CoolingComponent (technology level)

        :param alpha: parameter
        :type alpha: float

        :returns: * **price** price in €.m-2 (coeff_b_price + alpha*coeff_a_price)
        """
        return self.coeff_b_price + alpha*self.coeff_a_price

    def Dict(self):
        """
        Export object in a dictionary
        """
        d={}
        d['combination_specs_cooling'] = self.combination_specs_cooling.Dict()
        d['thermal_capacity'] = self.thermal_capacity
        d['delta_internal_variable'] = self.delta_internal_variable
        d['coeff_a_price'] = self.coeff_a_price
        d['coeff_b_price'] = self.coeff_b_price
        d['name'] = self.name
        return d

    @classmethod
    def DictToObject(cls, d):
        """
        Generate an CoolingComponent object

        :param d: CoolingComponent dictionnary generate with the Dict method
        """
        combination_specs_cooling = CombinationSpecsCooling.DictToObject(d['combination_specs_cooling'])
        delta_internal_variable = None
        if 'delta_internal_variable' in d:
            delta_internal_variable = d['delta_internal_variable']
        coeff_a_price = None
        if 'coeff_a_price' in d:
            coeff_a_price = d['coeff_a_price']
        coeff_b_price = None
        if 'coeff_b_price' in d:
            coeff_b_price = d['coeff_b_price']
        specs = cls(combination_specs_cooling=combination_specs_cooling,
                   thermal_capacity=d['thermal_capacity'],
                   delta_internal_variable=delta_internal_variable,
                   coeff_a_price=coeff_a_price,
                   coeff_b_price=coeff_b_price,
                   name=d['name'])
        return specs

class CoolingCatalog(DessiaObject):
    """
    Define a cooling component catalogue

    :param cooling_components: list of cooling component
    :type cooling_components: [powerpack.thermal.CoolingComponent]
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.CoolingCatalog Base Schema",
        "required": ['cooling_components'],
        "properties": {
            'cooling_components': {
               "type": "array",
               "order": 1,
               "editable": True,
               "description": "Cooling components",
               "items" : {
                   "type" : "object",
                   "classes" : ["powerpack.thermal.CoolingComponent"]
                   },
               },
            }
        }

    _display_angular = []

    def __init__(self, cooling_components, name=''):
        self.cooling_components = cooling_components
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_cell):
        equal = True
        for cooling_component, other_cooling_component in zip(self.cooling_components, other_cell.cooling_components):
            equal = (equal and cooling_component == other_cooling_component)
        return equal

    def __hash__(self):
        catalog_hash = 0
        for cooling_component in self.cooling_components:
            catalog_hash += hash(cooling_component)
        return catalog_hash

    def Dict(self):
        """
        Export dictionary
        """
        d={}
        d['cooling_components'] = []
        for cooling_component in self.cooling_components:
            d['cooling_components'].append(cooling_component.Dict())
        d['name'] = self.name
        return d

    @classmethod
    def DictToObject(cls, d):
        cooling_components = []
        for cooling_component in d['cooling_components']:
            cooling_components.append(CoolingComponent.DictToObject(cooling_component))
        specs = cls(cooling_components=cooling_components, name=d['name'])
        return specs

class ThermalModule(DessiaObject):
    """
    Define a thermal module (how a cooling component is apply on a mech_module)

    :param mech_module: mechanical module
    :type mech_module: powerpack.mechanical.MechModule
    :param cell_size: vector define the electric cell size
    :type cell_size: vector
    :param cooling_component: cooling component
    :type cooling_component: powerpack.thermal.CoolingComponent
    :param face: normal direction of the cooling component
    :type face: [0, 1, 2]
    :param use_two_faces: if True two face of the cell are used for the module cooling, else one face is used
    :type use_two_faces: boolean
    :param internal: if True cooling component inside the module is possible, else cooling component are only outside the module
    :type internal: boolean
    :param cooling_surface: cooling surface of all cooling component in the module
    :type cooling_surface: m2
    :param number_cooling_surface: number of discrete surface to cool a module
    :type number_cooling_surface: int
    :param direction_face_cooling: Number of elementary cell cooling interface per electrical module
    :type direction_face_cooling: int
    :param number_cooling_surface_elem: Cell normal direction of the cooling position
    :type number_cooling_surface_elem: int
    :param coeff_number_cooling_price: slope coefficient to estimate the impact of discret cooling surface on the cooling module price

    :Example:

    >>> import powerpack.optimization.thermal as thermal
    >>> mech_modules = GenerateMechModules(pf1.bms.battery, True)
    >>> tm1 = thermal.ThermalModule(mech_modules[0], (0.1, 0.3, 0.4), cooling_component,
                                    face = 1)
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.ThermalModule Base Schema",
        "required": ['mech_module', 'cell_size', 'cooling_component', 'face'],
        "properties": {
            "mech_module" : {
                "type" : "object",
                "classes" : ["powerpack.mechanical.MechModule"],
                "order" : 1,
                "editable" : True,
                "description" : "Mechanical module"
                },
            "cell_size" : {
                "type" : "array",
                "order" : 2,
                "items" : {
                    "type" : "number",
                    "editable" : True,
                    "step" : 0.001,
                    "minimum" : 0
                    },
                "examples": [[0.30, 0.20, 0.30]],
                "minItems": 3,
                "maxItems": 3,
                "editable" : True,
                "description" : "Size of electric cell"
                },
            "cooling_component" : {
                "type" : "object",
                "classes" : ["powerpack.thermal.CoolingComponent"],
                "order" : 3,
                "editable" : True,
                "description" : "Cooling component"
                },
            "face" : {
                "type" : "number",
                "order" : 4,
                "step" : 1,
                "minimum" : 0,
                "examples" : [0],
                "editable": True,
                "description" : "Normal face direction of the cooling component"
                },
            "use_two_faces" : {
                "type" : "boolean",
                "order" : 5,
                "examples" : [False],
                "editable": True,
                "description" : "Two cooling component per electrical cell"
                },
            "internal" : {
                "type" : "boolean",
                "order" : 6,
                "examples" : [False],
                "editable": True,
                "description" : "Cooling component inside electrial module"
                },
            "cooling_surface" : {
                "type" : "number",
                "order" : 7,
                "step" : 0.001,
                "minimum" : 0,
                "examples" : [1],
                "editable": True,
                "description" : "Electrical module cooling surface"
                },
            "number_cooling_surface" : {
                "type" : "number",
                "order" : 8,
                "step" : 1,
                "minimum" : 0,
                "examples" : [1],
                "editable": True,
                "description" : "Number of cooling component per electrical module"
                },
            "number_cooling_surface_elem" : {
                "type" : "number",
                "order" : 9,
                "step" : 1,
                "minimum" : 0,
                "examples" : [1],
                "editable": True,
                "description" : "Number of elementary cell cooling interface per electrical module"
                },
            "direction_face_cooling" : {
                "type" : "number",
                "order" : 10,
                "step" : 1,
                "minimum" : 0,
                "examples" : [0],
                "editable": True,
                "description" : "Cell normal direction of the cooling position"
                },
            "coeff_number_cooling_price" : {
                "type" : "number",
                "order" : 11,
                "step" : 0.001,
                "minimum" : 0,
                "examples" : [1],
                "editable": True,
                "description" : "Price coefficient based on the number of cooling component per electrical module"
                },
            }
        }

    _display_angular = []

    def __init__(self, mech_module, cell_size, cooling_component,
                 face, use_two_faces=None, internal=None,
                 cooling_surface=None, number_cooling_surface=None,
                 number_cooling_surface_elem=None, direction_face_cooling=None,
                 coeff_number_cooling_price=None, name=''):
        self.mech_module = mech_module
        self.cooling_component = cooling_component
        self.face = face
        self.cell_size = cell_size
        if use_two_faces is None:
            self.use_two_faces = False
        else:
            self.use_two_faces = use_two_faces
        if internal is None:
            self.internal = False
        else:
            self.internal = internal
        if coeff_number_cooling_price is None:
            self.coeff_number_cooling_price = 1
        else:
            self.coeff_number_cooling_price = coeff_number_cooling_price

        if cooling_surface is None:
            iter_faces = [0, 1, 2]*2
            cooling_dir1 = mech_module.cell_basis[iter_faces[face + 1]].Dot(vm.Vector3D(cell_size))
            cooling_dir2 = mech_module.cell_basis[iter_faces[face + 2]].Dot(vm.Vector3D(cell_size))
            cooling_surface_cell = abs(cooling_dir1*cooling_dir2)
            iter_grid = list(mech_module.grid)*2
            cooling_surface_elem = cooling_surface_cell*iter_grid[face + 1]*iter_grid[face + 2]
            self.cooling_surface = None
            self.number_cooling_surface = 0
            if internal:
                if use_two_faces:
                    self.cooling_surface = cooling_surface_elem*(iter_grid[face] + 1)
                    self.number_cooling_surface += iter_grid[face] + 1
                else:
                    self.cooling_surface = cooling_surface_elem*(iter_grid[face] // 2 + iter_grid[face] % 2)
                    self.number_cooling_surface += iter_grid[face] // 2 + iter_grid[face] % 2
            else:
                if use_two_faces:
                    if iter_grid[face] == 1:
                        self.cooling_surface = 2*cooling_surface_elem
                        self.number_cooling_surface += 2
                else:
                    if iter_grid[face] <= 2:
                        self.cooling_surface = 2*cooling_surface_elem
                        self.number_cooling_surface += 2
            self.number_cooling_surface_elem = self.number_cooling_surface*iter_grid[face + 1]*iter_grid[face + 2]
            try:
                self.direction_face_cooling = list(mech_module.cell_basis[face].vector).index(1)
            except:
                self.direction_face_cooling = list(mech_module.cell_basis[face].vector).index(-1)
        else:
            self.cooling_surface = cooling_surface

            if number_cooling_surface is None:
                self.number_cooling_surface = 1
            else:
                self.number_cooling_surface = number_cooling_surface

            if number_cooling_surface_elem is None:
                self.number_cooling_surface_elem = 1
            else:
                self.number_cooling_surface_elem = number_cooling_surface_elem

            if direction_face_cooling is None:
                self.direction_face_cooling = 0
            else:
                self.direction_face_cooling = direction_face_cooling
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_cell):
        equal = (self.mech_module == other_cell.mech_module
                 and self.cell_size == other_cell.cell_size
                 and self.cooling_component == other_cell.cooling_component
                 and self.face == other_cell.face
                 and self.use_two_faces == other_cell.use_two_faces
                 and self.number_cooling_surface == other_cell.number_cooling_surface
                 and self.coeff_number_cooling_price == other_cell.coeff_number_cooling_price
                 and self.internal == other_cell.internal
                 and self.number_cooling_surface_elem == other_cell.number_cooling_surface_elem
                 and self.direction_face_cooling == other_cell.direction_face_cooling
                 and self.cooling_surface == other_cell.cooling_surface)
        return equal

    def __hash__(self):
        tm_hash = hash(self.mech_module)\
                  + hash(self.cooling_component)
        return tm_hash

    def check(self):
        valid = True
        iter_grid = list(self.mech_module.grid)*2
        if not self.internal:
            if self.use_two_faces:
                if iter_grid[self.face] != 1:
                    valid = False
            else:
                if iter_grid[self.face] > 2:
                    valid = False
        return valid

    def price(self, alpha):
        price_elem = self.cooling_component.price(alpha)
        price_number_cooling = self.coeff_number_cooling_price*self.number_cooling_surface
        return price_elem*self.cooling_surface*price_number_cooling

    def Dict(self):
        """
        Export dictionary
        """
        d={}
        d['mech_module'] = self.mech_module.to_dict()
        d['cell_size'] = self.cell_size
        d['cooling_component'] = self.cooling_component.Dict()
        d['face'] = self.face
        d['use_two_faces'] = self.use_two_faces
        d['internal'] = self.internal
        d['cooling_surface'] = self.cooling_surface
        d['number_cooling_surface'] = self.number_cooling_surface
        d['number_cooling_surface_elem'] = self.number_cooling_surface_elem
        d['direction_face_cooling'] = self.direction_face_cooling
        d['coeff_number_cooling_price'] = self.coeff_number_cooling_price
        d['name'] = self.name
        return d

    @classmethod
    def DictToObject(cls, d):
        mech_module = mechanical.MechModule.DictToObject(d['mech_module'])
        cooling_component = CoolingComponent.DictToObject(d['cooling_component'])
        use_two_faces = None
        if 'use_two_faces' in d:
            use_two_faces = d['use_two_faces']
        internal = None
        if 'internal' in d:
            internal = d['internal']
        cooling_surface = None
        if 'cooling_surface' in d:
            cooling_surface = d['cooling_surface']
        number_cooling_surface = None
        if 'number_cooling_surface' in d:
            number_cooling_surface = d['number_cooling_surface']
        number_cooling_surface_elem = None
        if 'number_cooling_surface_elem' in d:
            number_cooling_surface_elem = d['number_cooling_surface_elem']
        direction_face_cooling = None
        if 'direction_face_cooling' in d:
            direction_face_cooling = d['direction_face_cooling']
        coeff_number_cooling_price = None
        if 'coeff_number_cooling_price' in d:
            coeff_number_cooling_price = d['coeff_number_cooling_price']
        specs = cls(mech_module=mech_module,
                    cell_size=d['cell_size'],
                    cooling_component=cooling_component,
                    face=d['face'],
                    use_two_faces=use_two_faces,
                    internal=internal,
                    cooling_surface=cooling_surface,
                    number_cooling_surface=number_cooling_surface,
                    number_cooling_surface_elem=number_cooling_surface_elem,
                    direction_face_cooling=direction_face_cooling,
                    coeff_number_cooling_price=coeff_number_cooling_price,
                    name=d['name'])
        return specs

class ThermalModuleResult(DessiaObject):
    """
    Object to store thermal module results

    :param temperature: temperature evolution
    :type temperature: powerpack.electrical.Evolution
    :param internal_variable: internal variable evolution
    :type internal_variable: powerpack.electrical.Evolution
    :param dispersed_power: dispersed power evolution
    :type dispersed_power: powerpack.electrical.Evolution
    :param electric_power: electric power evolution
    :type electric_power: powerpack.electrical.Evolution
    :param internal_power: internal power evolution
    :type internal_power: powerpack.electrical.Evolution
    :param htc: htc evolution
    :type htc: powerpack.electrical.Evolution
    :param time: time evolution
    :type time: powerpack.electrical.Evolution
    :param alpha: alpha value
    :type alpha: float
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.ThermalModuleResult Base Schema",
        "required": [],
        "properties": {
            "temperature" : {
                "type" : "object",
                "classes" : ["powerpack.electrical.Evolution"],
                "order" : 1,
                "editable" : False,
                "description" : "Temperature evolution"
                },
            "internal_variable" : {
                "type" : "object",
                "classes" : ["powerpack.electrical.Evolution"],
                "order" : 2,
                "editable" : False,
                "description" : "Internal variable evolution"
                },
            "dispersed_power" : {
                "type" : "object",
                "classes" : ["powerpack.electrical.Evolution"],
                "order" : 3,
                "editable" : False,
                "description" : "Dispersed power evolution"
                },
            "electric_power" : {
                "type" : "object",
                "classes" : ["powerpack.electrical.Evolution"],
                "order" : 4,
                "editable" : False,
                "description" : "Electric power evolution"
                },
            "internal_power" : {
                "type" : "object",
                "classes" : ["powerpack.electrical.Evolution"],
                "order" : 5,
                "editable" : False,
                "description" : "Internal power evolution"
                },
            "htc" : {
                "type" : "object",
                "classes" : ["powerpack.electrical.Evolution"],
                "order" : 6,
                "editable" : False,
                "description" : "HTC evolution"
                },
            "time" : {
                "type" : "object",
                "classes" : ["powerpack.electrical.Evolution"],
                "order" : 7,
                "editable" : False,
                "description" : "Time evolution"
                },
            "alpha" : {
                "type" : "number",
                "order" : 8,
                "step" : 0.001,
                "minimum" : 0,
                "examples" : [0.5],
                "editable": False,
                "description" : "Coefficient alpha"
                },
            }
        }

    _display_angular = []

    def __init__(self, temperature=None, internal_variable=None, alpha=None,
                 dispersed_power=None, electric_power=None, internal_power=None,
                 htc=None, time=None, name=''):
        if temperature is None:
            self.temperature = Evolution()
        else:
            self.temperature = temperature
        if internal_variable is None:
            self.internal_variable = Evolution()
        else:
            self.internal_variable = internal_variable
        if dispersed_power is None:
            self.dispersed_power = Evolution()
        else:
            self.dispersed_power = dispersed_power
        if electric_power is None:
            self.electric_power = Evolution()
        else:
            self.electric_power = electric_power
        if internal_power is None:
            self.internal_power = Evolution()
        else:
            self.internal_power = internal_power
        if htc is None:
            self.htc = Evolution()
        else:
            self.htc = htc
        if time is None:
            self.time = Evolution()
        else:
            self.time = time
        self.alpha = alpha
        self.htc_mean = None
        self.htc_min = None
        self.htc_max = None
        self.dispersed_power_mean = None
        self.dispersed_power_min = None
        self.dispersed_power_max = None
        if time is not None:
            if time.evolution != []:
                self.analysis()
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = (self.temperature == other.temperature
                 and self.internal_variable == other.internal_variable
                 and self.alpha == other.alpha
                 and self.dispersed_power == other.dispersed_power
                 and self.electric_power == other.electric_power
                 and self.internal_power == other.internal_power
                 and self.htc == other.htc
                 and self.time == other.time)
        return equal

    def __hash__(self):
        li_hash = hash(self.temperature) + hash(self.internal_variable) + hash(self.alpha)\
             + hash(self.dispersed_power) + hash(self.electric_power) + hash(self.internal_power)\
             + hash(self.htc) + hash(self.time)
        return li_hash

    def Add(self, temperature, internal_variable, dispersed_power, electric_power,
            internal_power, htc, delta_t):
        self.temperature.evolution.append(temperature)
        self.internal_variable.evolution.append(internal_variable)
        self.dispersed_power.evolution.append(dispersed_power)
        self.electric_power.evolution.append(electric_power)
        self.internal_power.evolution.append(internal_power)
        self.htc.evolution.append(htc)
        if self.time.evolution == []:
            self.time.evolution.append(0)
        else:
            time_m = self.time.evolution[-1]
            self.time.evolution.append(time_m + delta_t)

    def update(self, alpha):
        self.alpha = alpha

    def analysis(self):
        self.htc_mean = float(sum(self.htc.evolution)/len(self.htc.evolution))
        self.htc_min = float(min(self.htc.evolution))
        self.htc_max = float(max(self.htc.evolution))
        self.dispersed_power_mean = float(sum(self.dispersed_power.evolution)/len(self.dispersed_power.evolution))
        self.dispersed_power_min = float(min(self.dispersed_power.evolution))
        self.dispersed_power_max = float(max(self.dispersed_power.evolution))

    def PlotResults(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(411)
        ax1.set_ylabel('Temperature (K)')
        ax1.plot(self.time.evolution, self.temperature.evolution)

        ax2 = fig.add_subplot(412, sharex=ax1)
        ax2.set_ylabel('Internal variable (K)')
        ax2.plot(self.time.evolution, self.internal_variable.evolution)

        ax3 = fig.add_subplot(413, sharex=ax1)
        ax3.set_ylabel('Power (W)')
        ax3.plot(self.time.evolution, self.dispersed_power.evolution)
        ax3.plot(self.time.evolution, self.electric_power.evolution)
        ax3.plot(self.time.evolution, self.internal_power.evolution)

        ax4 = fig.add_subplot(414, sharex=ax1)
        ax4.set_ylabel('htc (W/m-2/K)')
        ax4.plot(self.time.evolution, self.htc.evolution)

        ax4.set_xlabel('Time (s)')

    def Dict(self):
        """
        Export dictionary
        """
        d={}
        if self.temperature.evolution != []:
            d['temperature'] = self.temperature.Dict()
        if self.internal_variable.evolution != []:
            d['internal_variable'] = self.internal_variable.Dict()
        d['alpha'] = self.alpha
        if self.dispersed_power.evolution != []:
            d['dispersed_power'] = self.dispersed_power.Dict()
        if self.electric_power.evolution != []:
            d['electric_power'] = self.electric_power.Dict()
        if self.internal_power.evolution != []:
            d['internal_power'] = self.internal_power.Dict()
        if self.htc.evolution != []:
            d['htc'] = self.htc.Dict()
        if self.time.evolution != []:
            d['time'] = self.time.Dict()
        d['htc_mean'] = self.htc_mean
        d['htc_min'] = self.htc_min
        d['htc_max'] = self.htc_max
        d['dispersed_power_mean'] = self.dispersed_power_mean
        d['dispersed_power_min'] = self.dispersed_power_min
        d['dispersed_power_max'] = self.dispersed_power_max
        d['name'] = self.name
        return d

    @classmethod
    def DictToObject(cls, d):
        temperature = None
        if 'temperature' in d:
            if d['temperature'] is not None:
                temperature = electrical.Evolution.DictToObject(d['temperature'])
        internal_variable = None
        if 'internal_variable' in d:
            if d['internal_variable'] is not None:
                internal_variable = electrical.Evolution.DictToObject(d['internal_variable'])
        dispersed_power = None
        if 'dispersed_power' in d:
            if d['dispersed_power'] is not None:
                dispersed_power = electrical.Evolution.DictToObject(d['dispersed_power'])
        electric_power = None
        if 'electric_power' in d:
            if d['electric_power'] is not None:
                electric_power = electrical.Evolution.DictToObject(d['electric_power'])
        internal_power = None
        if 'internal_power' in d:
            if d['internal_power'] is not None:
                internal_power = electrical.Evolution.DictToObject(d['internal_power'])
        htc = None
        if 'htc' in d:
            if d['htc'] is not None:
                htc = electrical.Evolution.DictToObject(d['htc'])
        time = None
        if 'time' in d:
            if d['time'] is not None:
                time = electrical.Evolution.DictToObject(d['time'])
        specs = cls(temperature=temperature,
                    internal_variable=internal_variable,
                    alpha=d['alpha'],
                    dispersed_power=dispersed_power,
                    electric_power=electric_power,
                    internal_power=internal_power,
                    htc=htc,
                    time=time)
        return specs

class PowerPackThermalSimulator(DessiaObject):
    """
    Simulate the temperature evolution of a thermal battery applying electric simulation

    :param powerpack_electric_simulator: powerpack electric simulator
    :type powerpack_electric_simulator: powerpack.electrical.PowerPackElectricSimulator
    :param thermal_module: thermal module
    :type thermal_module: powerpack.thermal.ThermalModule
    :param module_temperature_init: initial module temperature
    :type module_temperature_init: K
    :param module_temperature_max: maximum module temperature
    :type module_temperature_max: K
    :param cooling_temperature: cooling temperature
    :type cooling_temperature: K
    :param thermal_module_results: list of thermal module result
    :type thermal_module_results: [powerpack.thermal.ThermalModuleResult]
    :param dtime_power: time step smoothing
    :type dtime_power: s

    :Example:

    >>> import powerpack.optimization.thermal as thermal
    >>> mts = thermal.PowerPackThermalSimulator(powerpack_electric_simulator,
                                                thermal_module,
                                                module_temperature_max=330,
                                                cooling_temperature=290,
                                                module_temperature_init=290)
    """
    _standalone_in_db = True
    _jsonschema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": {},
        'type': 'object',
        "title": "powerpack.thermal.PowerPackThermalSimulator Base Schema",
        "required": ['powerpack_electric_simulator', 'thermal_module', 'module_temperature_init',
                     'module_temperature_max', 'cooling_temperature'],
        "properties": {
            'powerpack_electric_simulator': {
                "type": "object",
                "title" : "Powerpack Electric Simulator",
                "classes" : ["powerpack.electrical.PowerPackElectricSimulator"],
                "order": 1,
                "editable": True,
                "description": "Electric powerpack simulation",
                },
            "thermal_module" : {
                "type" : "object",
                "title" : "Thermal Module",
                "classes" : ["powerpack.thermal.ThermalModule"],
                "order" : 2,
                "editable" : True,
                "description" : "Thermal module"
                },
            "module_temperature_init" : {
                "type" : "number",
                "title" : "Initial Module Temperature",
                "order" : 3,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "module_temperature_max" : {
                "type" : "number",
                "title" : "Maximum Module Temperature",
                "order" : 4,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            "cooling_temperature" : {
                "type" : "number",
                "title" : "Cooling Temperature",
                "order" : 5,
                "step" : 1,
                "minimum" : 0,
                "unit" : "K",
                "editable": True,
                "examples" : [273]
                },
            'thermal_module_results': {
                "type": "array",
                "title" : "Thermal Module Results",
                "order": 6,
                "editable": True,
                "description": "Thermal module results",
                "items" : {
                   "type" : "object",
                   "classes" : ["powerpack.thermal.ThermalModuleResult"]
                   },
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
            'analysis': {
                "type" : "object",
                "title" : "PowerPack Analysis",
                "classes" : ["powerpack.thermal.ThermalAnalysis"],
                "description" : "PowerPack Analysis",
                "editable" : False
                },
            }
        }

    _allowed_methods = ['Simulate']

    def __init__(self, powerpack_electric_simulator, thermal_module,
                 module_temperature_init, module_temperature_max,
                 cooling_temperature, thermal_module_results=None,
                 dtime_power=None, analysis=None, name=''):
        self.powerpack_electric_simulator = powerpack_electric_simulator
        self.thermal_module = thermal_module
        if thermal_module_results is None:
            self.thermal_module_results = []
        else:
            self.thermal_module_results = thermal_module_results
        self.module_temperature_max = module_temperature_max
        self.module_temperature_init = module_temperature_init
        self.cooling_temperature = cooling_temperature
        if dtime_power is not None:
            self.dtime_power = dtime_power
        else:
            self.dtime_power = 100
        self.analysis = analysis
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = (self.thermal_module == other.thermal_module
                 and self.module_temperature_init == other.module_temperature_init
                 and self.module_temperature_max == other.module_temperature_max
                 and self.cooling_temperature == other.cooling_temperature
                 and self.dtime_power == other.dtime_power
                 and self.powerpack_electric_simulator == other.powerpack_electric_simulator)
        if (self.thermal_module_results is not None) and (other.thermal_module_results is not None):
            for thermal_module_result, other_thermal_module_result in zip(self.thermal_module_results, other.thermal_module_results):
                equal = (equal and thermal_module_result == other_thermal_module_result)
        elif not ((self.thermal_module_results is None) and (other.thermal_module_results is None)):
            equal = False
        return equal

    def __hash__(self):
        li_hash = 0
        li_hash += hash(self.powerpack_electric_simulator)
        if self.thermal_module_results is not None:
            for thermal_module_result in self.thermal_module_results:
                li_hash += hash(thermal_module_result)
        li_hash += hash(self.thermal_module)
        return li_hash

    def _quick_analysis(self):

        alpha = 0.5
        cooling_price = self.thermal_module.price(alpha)
        cooling_surface = self.thermal_module.cooling_surface
        grid_0 = self.thermal_module.mech_module.grid[0]
        grid_1 = self.thermal_module.mech_module.grid[1]
        grid_2 = self.thermal_module.mech_module.grid[2]
        normal_face_cooling = self.thermal_module.face
        internal_cooling = self.thermal_module.internal
        use_two_faces = self.thermal_module.use_two_faces
        htc_mean = None
        htc_min = None
        htc_max = None
        dispersed_power_mean = None
        dispersed_power_min = None
        dispersed_power_max = None

        self.analysis = ThermalAnalysis(cooling_price, cooling_surface, grid_0, grid_1, grid_2,
                 normal_face_cooling, internal_cooling, use_two_faces, alpha,
                 htc_mean, htc_min, htc_max, dispersed_power_mean,
                 dispersed_power_min, dispersed_power_max)

    def _analysis(self):
        for thermal_module_result in self.thermal_module_results:
            thermal_module_result.analysis()

        alpha = self.thermal_module_results[0].alpha
        cooling_price = self.thermal_module.price(alpha)
        cooling_surface = self.thermal_module.cooling_surface
        grid_0 = self.thermal_module.mech_module.grid[0]
        grid_1 = self.thermal_module.mech_module.grid[1]
        grid_2 = self.thermal_module.mech_module.grid[2]
        normal_face_cooling = self.thermal_module.face
        internal_cooling = self.thermal_module.internal
        use_two_faces = self.thermal_module.use_two_faces
        htc_mean = self.thermal_module_results[0].htc_mean
        htc_min = self.thermal_module_results[0].htc_min
        htc_max = self.thermal_module_results[0].htc_max
        dispersed_power_mean = self.thermal_module_results[0].dispersed_power_mean
        dispersed_power_min = self.thermal_module_results[0].dispersed_power_min
        dispersed_power_max = self.thermal_module_results[0].dispersed_power_max

        self.analysis = ThermalAnalysis(cooling_price, cooling_surface, grid_0, grid_1, grid_2,
                 normal_face_cooling, internal_cooling, use_two_faces, alpha,
                 htc_mean, htc_min, htc_max, dispersed_power_mean,
                 dispersed_power_min, dispersed_power_max)

    def Simulate(self, alpha, thermal_transfer_coefficient=None, progress_callback=lambda x:0):
        if thermal_transfer_coefficient is None:
            thermal_transfer_coefficient = electrical.CombinationEvolution(evolution1 = [electrical.Evolution()],
                                                                 evolution2 = [electrical.Evolution()])

        self.powerpack_electric_simulator.Simulate()
        elec_module_results = self.powerpack_electric_simulator.module_results
        
        thermal_module_results = []
        for elec_module_result in elec_module_results:
            thermal_module_results.append(ThermalModuleResult())
        self.thermal_module_results = thermal_module_results

        valid_profil = []
        dtimes, li_power_analysis = self.powerpack_electric_simulator.DiscretPower(self.dtime_power)
        for num_result, (dtime, power_analysis) in enumerate(zip(dtimes, li_power_analysis)):
            progress_callback(num_result/len(elec_module_results))
            valid = True
            self.thermal_module_results[num_result].update(alpha)
            valid_profil_i = self.SimulateElementary(alpha, thermal_transfer_coefficient,
                                                     dtime = dtime, power_analysis = power_analysis,
                                                     thermal_module_result = self.thermal_module_results[num_result])
            if not valid_profil_i:
                valid = False
            valid_profil.append(valid)
        self.powerpack_electric_simulator.remove()
        return valid_profil

    def SimulateElementary(self, alpha, thermal_transfer_coefficient, dtime, power_analysis, thermal_module_result):
        U = 0
        module_temperature_m = self.module_temperature_init
        internal_parameters = self.thermal_module.cooling_component.combination_specs_cooling.f_specs_coolings.keys()
        bound_internal_parameter = [min(internal_parameters), max(internal_parameters)]
        internal_variable = bound_internal_parameter[0]
        cell = self.powerpack_electric_simulator.bms.battery.mms.module.cms.cell

        def fun(x, electric_power, module_temperature_m, dt):
            module_temperature = x[0]
            dispersed_power = x[1]
            internal_variable = x[2]

            cooling_surface = self.thermal_module.cooling_surface
            htc = self.thermal_module.cooling_component.evaluate(alpha, abs(dispersed_power),
                                                                 thermal_transfer_coefficient, internal_variable)
            h_cooling_elem = htc*(cooling_surface/self.thermal_module.number_cooling_surface_elem)
            h_cell = cell.eval_thermal_transfer(module_temperature,
                                self.thermal_module.direction_face_cooling)
            h_global = h_cell*h_cooling_elem/(h_cell + h_cooling_elem)
            H_global = self.thermal_module.number_cooling_surface_elem*h_global
            dispersed_power2 = -H_global*(module_temperature - self.cooling_temperature)

            return (dispersed_power - dispersed_power2)**2

        def fineq(x, electric_power, module_temperature_m, dt):
            module_temperature = x[0]
            dispersed_power = x[1]
            internal_variable = x[2]

            ineq = []

            cooling_surface = self.thermal_module.cooling_surface
            htc = self.thermal_module.cooling_component.evaluate(alpha, abs(dispersed_power),
                                                                 thermal_transfer_coefficient, internal_variable)
            h_cooling_elem = htc*(cooling_surface/self.thermal_module.number_cooling_surface_elem)
            h_cell = cell.eval_thermal_transfer(module_temperature,
                                self.thermal_module.direction_face_cooling)
            h_global = h_cell*h_cooling_elem/(h_cell + h_cooling_elem)
            H_global = self.thermal_module.number_cooling_surface_elem*h_global
            dispersed_power_estimate = -H_global*(module_temperature - self.cooling_temperature)

            thermal_capacity = self.thermal_module.cooling_component.thermal_capacity
            cooling_surface = self.thermal_module.cooling_surface
            mass = cell.mass
            U = thermal_capacity*mass*(module_temperature - module_temperature_m)/dt

            borne_inf = min(thermal_transfer_coefficient.x)
            borne_sup = max(thermal_transfer_coefficient.x)

            ineq.append(abs(dispersed_power) - borne_inf)
            ineq.append(borne_sup - abs(dispersed_power))
            ineq.append(module_temperature - self.cooling_temperature)

            ineq.append(1e-6 - (dispersed_power_estimate - dispersed_power))
            ineq.append((dispersed_power_estimate - dispersed_power) + 1e-6)

            ineq.append(1e-6 - (U - electric_power - dispersed_power_estimate))
            ineq.append((U - electric_power - dispersed_power_estimate) - (-1e-6))
            return ineq

        for i, power_elec in enumerate(power_analysis):
            delta_internal_variable = self.thermal_module.cooling_component.delta_internal_variable
            internal_variable_min = max(bound_internal_parameter[0], internal_variable - dtime*delta_internal_variable)
            internal_variable_max = min(bound_internal_parameter[1], internal_variable + dtime*delta_internal_variable)
            bound = [[273, self.module_temperature_max], [-max(power_analysis), 0],
                     [internal_variable_min, internal_variable_max]]
            valid = False

            for itera in range(0, 5):
                x0 = (npy.array(bound)[:,1]-npy.array(bound)[:,0])*npy.random.random(3)+npy.array(bound)[:,0]
                cons = {'type': 'ineq','fun' : fineq, 'args': (power_elec, module_temperature_m, dtime)}

                res = minimize(fun, x0, bounds=bound, args = (power_elec,
                               module_temperature_m, dtime), constraints = cons)

                if (min(fineq(res.x, power_elec, module_temperature_m, dtime)) > -1e-6):
                    sol_x = res.x
                    module_temperature = sol_x[0]
                    dispersed_power = sol_x[1]
                    internal_variable = sol_x[2]

                    cooling_surface = self.thermal_module.cooling_surface
                    htc = self.thermal_module.cooling_component.evaluate(alpha, abs(dispersed_power),
                                                                         thermal_transfer_coefficient, internal_variable)
                    h_cooling_elem = htc*(cooling_surface/self.thermal_module.number_cooling_surface_elem)
                    h_cell = cell.eval_thermal_transfer(module_temperature,
                                        self.thermal_module.direction_face_cooling)
                    h_global = h_cell*h_cooling_elem/(h_cell + h_cooling_elem)
                    H_global = self.thermal_module.number_cooling_surface_elem*h_global

                    thermal_capacity = self.thermal_module.cooling_component.thermal_capacity
                    mass = cell.mass
                    U = thermal_capacity*mass*(module_temperature - module_temperature_m)/dtime
                    thermal_module_result.Add(module_temperature, internal_variable, dispersed_power,
                                              power_elec, U, H_global, dtime)
                    valid = True
                    module_temperature_m = sol_x[0]
                    break
            if not valid:
                mass = cell.mass
                thermal_capacity = self.thermal_module.cooling_component.thermal_capacity
                module_temperature = power_elec/(thermal_capacity*mass)*dtime + module_temperature_m
                U = thermal_capacity*mass*(module_temperature - module_temperature_m)/dtime
                if module_temperature <= self.module_temperature_max:
                    valid = True
                    thermal_module_result.Add(module_temperature, 0, 0,
                                              power_elec, U, 0, dtime)
                module_temperature_m = module_temperature
            if not valid:
                break
        return valid

    def Dict(self):
        """
        Export dictionary
        """
        d={}
        d['powerpack_electric_simulator'] = self.powerpack_electric_simulator.Dict()
        d['thermal_module'] = self.thermal_module.Dict()
        if self.thermal_module_results != []:
            d['thermal_module_results'] = []
            for thermal_module_result in self.thermal_module_results:
                d['thermal_module_results'].append(thermal_module_result.Dict())
        d['module_temperature_init'] = self.module_temperature_init
        d['module_temperature_max'] = self.module_temperature_max
        d['cooling_temperature'] = self.cooling_temperature
        d['dtime_power'] = self.dtime_power
        if self.analysis is not None:
            d['analysis'] = self.analysis.to_dict()
        else:
            d['analysis'] = None
        d['name'] = self.name
        return d

    @classmethod
    def DictToObject(cls, d):
        powerpack_electric_simulator = electrical.PowerPackElectricSimulator.DictToObject(d['powerpack_electric_simulator'])
        thermal_module_results = []
        thermal_module_results = None
        if 'thermal_module_results' in d:
            if len(d['thermal_module_results']) > 0:
                thermal_module_results = []
                for thermal_module_result in d['thermal_module_results']:
                    thermal_module_results.append(ThermalModuleResult.DictToObject(thermal_module_result))
        dtime_power = None
        if 'dtime_power' in d:
            if d['dtime_power'] is not None:
                dtime_power = d['dtime_power']
        if 'analysis' in d and d['analysis'] is not None:
            analysis = ThermalAnalysis.dict_to_object(d['analysis'])
        else:
            analysis = None
        specs = cls(powerpack_electric_simulator=powerpack_electric_simulator,
                    thermal_module=ThermalModule.DictToObject(d['thermal_module']),
                    thermal_module_results=thermal_module_results,
                    module_temperature_init=d['module_temperature_init'],
                    module_temperature_max=d['module_temperature_max'],
                    cooling_temperature=d['cooling_temperature'],
                    dtime_power=dtime_power,
                    analysis=analysis,
                    name=d['name'])
        return specs

