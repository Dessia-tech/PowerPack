#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 14:29:25 2018

@author: jezequel
"""

import math
from copy import copy
import numpy as npy
import networkx as nx
import volmdlr as vm
from volmdlr import primitives2D
from volmdlr import primitives3D

from powerpack import electrical, thermal
from dessia_common import DessiaObject, number3factor

import hydraulic as hy
import hydraulic.thermal as hy_thermal

class PackStructure(DessiaObject):
    """
    Defines a conceptual view of the battery casing

    :param size: Tuple that represent pack structure size in global frame
    :type size: (x, y, z) m
    :param trans_rails: List of pack structure transversal rails
    :type trans_rails: [TranversalRail, TransversalRail, ...]
    :param long_rails: List of pack structure longitudinal rails
    :type trans_rails: [LongitudinalRail, LongitudinalRail, ...]
    :param th_casing: pack structure thickness
    :type th_casing: m
    :param triangle: TODO triangle ?
    :type triangle: TODO triangle ?
    :param radius: Radius of pack structure corners fillets
    :type radius: m
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.PackStructure Base Schema",
        "required": ["size", "cases", "long_rails", "trans_rails", "rail_specs",
                     "th_casing", "triangle", "radius"],
        "properties": {
            "size" : {
                "type" : "array",
                "title" : "Size",
                "order" : 1,
                "items" : {
                    "type" : "number",
                    "editable" : True,
                    "step" : 0.0001,
                    "minimum" : 0
                    },
                "examples": [[1.8, 2.5, 0.30]],
                "minItems": 3,
                "maxItems": 3,
                "editable" : True,
                "description" : "Size of the pack structure"
                },
            "cases" : {
                "type" : "array",
                "title" : "Cases",
                "order" : 2,
                "items" : {
                    "type" : "object",
                    "classes" : ["powerpack.mechanical.Case"]
                    },
                "editable" : True,
                "description" : "List of cases"
                },
            "long_rails" : {
                "type" : "array",
                "title" : "Longitudinal Rails",
                "order" : 3,
                "items" : {
                    "type" : "object",
                    "editable" : True,
                    "classes" : ["powerpack.mechanical.LongitudinalRail"]
                    },
                "editable" : True,
                "description" : "List of longitudinal rails"
                },
            "trans_rails" : {
                "type" : "array",
                "title" : "Transversal Rails",
                "order" : 4,
                "items" : {
                    "type" : "object",
                    "editable" : True,
                    "classes" : ["powerpack.mechanical.TransversalRail"]
                    },
                "editable" : True,
                "description" : "List of transversal rails"
                },
            "rail_specs" : {
                "type" : "object",
                "title" : "Rails Specifications",
                "editable" : True,
                "description" : "Specifications for rails",
                "order" : 5,
                "properties" : {
                    "longitudinal" : {
                        "type" : "number",
                        "editable" : True,
                        "step" : 0.001,
                        "minimum" : 0,
                        "example" : [0.010],
                        "desription" : "Width of longitudinal rails"
                        },
                    "transversal" : {
                        "type" : "number",
                        "editable" : True,
                        "step" : 0.001,
                        "minimum" : 0,
                        "example" : [0.005],
                        "desription" : "Width of transversal rails"
                        }
                    }
                },
            "th_casing" : {
                "type" : "number",
                "title" : "Casing Thickness",
                "order" : 6,
                "step" : 0.001,
                "minimum" : 0,
                "editable" : True,
                "examples" : [0.005],
                "description" : "Casing thickness"
                },
            "triangle" : {
                "type" : "array",
                "title" : "Triangle",
                "order" : 7,
                "items" : {
                    "type" : "number",
                    "editable" : True,
                    "step" : 0.001,
                    "minimum" : 0
                    },
                "examples": [[0, 0]],
                "minItems" : 2,
                "maxItems" : 2,
                "editable" : True,
                "description" : "TODO"
                },
            "radius" : {
                "type" : "number",
                "title" : "Radius",
                "order" : 8,
                "step" : 0.001,
                "minimum" : 0,
                "editable" : True,
                "examples" : [0.01],
                "description" : "Radius of pack strcture corners fillets"
                }
            }
        }

    def __init__(self, size, cases, long_rails, trans_rails, rail_specs,
                 th_casing=0.005, triangle=(0, 0), radius=0.01, name=''):
        # TODO : Why are rails_specs ang rails defined in init together. Hint : probably for vector building purpose
        self.size = size
        self.cases = cases
        self.long_rails = long_rails
        self.trans_rails = trans_rails
        self.rail_specs = rail_specs
        self.th_casing = th_casing
        self.triangle = triangle
        self.radius = radius

        DessiaObject.__init__(self, name=name)

        self.RailsFromCases(cases, long_rails, trans_rails, rail_specs)

    def __getitem__(self, key):
        return self.cases[key]

    def __contains__(self, element):
        # !!! Will find element in pack_structure but will not be in the loop if not a case
        contained = element in self.cases + self.long_rails + self.trans_rails
        return contained

    def __eq__(self, other_ps):
        if len(self.cases) == len(other_ps.cases)\
        and len(self.long_rails) == len(other_ps.long_rails)\
        and len(self.trans_rails) == len(other_ps.trans_rails):
            equal = (npy.allclose(self.size, other_ps.size)
                     and all([elt == other_elt
                              for elt, other_elt
                              in zip(self.cases + self.long_rails + self.trans_rails,
                                     other_ps.cases + other_ps.long_rails + other_ps.trans_rails)]))
            return equal
        return False

    def __hash__(self):
        elements_hash = sum([hash(elt) for elt
                             in self.cases + self.long_rails + self.trans_rails])
        return int(sum(1500*self.size) + elements_hash)

    def CasesFromRails(self):
        """
        Creates casing rails
        """
        n = len(self.long_rails)
        m = len(self.trans_rails)

        trans_rails_positions = [tr.position for tr in self.trans_rails]
        long_rails_positions = [lr.position for lr in self.long_rails]
        trans_rails_widths = [tr.width for tr in self.trans_rails]
        long_rails_widths = [lr.width for lr in self.long_rails]

        cases = []
        case_indices = {}

        for j in range(m+1):
            for i in range(n+1):
                if i == 0:
                    y = -0.5*self.size[1]
                else:
                    y = long_rails_positions[i-1] + 0.5*long_rails_widths[i-1]

                if j == 0:
                    x = 0
                else:
                    x = trans_rails_positions[j-1] + 0.5*trans_rails_widths[j-1]

                if i == n:
                    h = 0.5*self.size[1] - y
                else:
                    h = long_rails_positions[i] - 0.5*long_rails_widths[i] - y

                if j == m:
                    l = self.size[0] - x
                else:
                    l = trans_rails_positions[j] - 0.5*trans_rails_widths[j] - x

                case = Case(vm.Point3D((x, y, 0)),
                            (round(l, 4),
                             round(h, 4),
                             round(self.size[2], 4)))
                cases.append(case)
                case_indices[case] = (j, i)

        return cases, case_indices

    def RailsFromCases(self, cases, long_rails, trans_rails, rail_specs):
        self.cases = cases
        self.rail_specs = rail_specs
        case_indices = {}
        n_lr = len(long_rails)
        n_tr = len(trans_rails)
        max_x = 0
        max_y = 0
        max_z = 0
        first_case = cases[0]
        if first_case is not None:
            current_x = first_case.position[0]
            init_y = first_case.position[1]
            current_z = first_case.position[2]
        else:
            current_x = 0
            init_y = -self.size[1]/2.
            current_z = 0
        current_y = init_y

        tr_width = rail_specs['transversal']
        lr_width = rail_specs['longitudinal']
        fixed_tr_indices = []
        fixed_lr_indices = []
        for case_index, case in enumerate(cases):
            i, j = CaseCoords(case_index, n_lr)
            case_indices[case] = (j, i)
            if case is not None:
                if i and case.position[1] < long_rails[i-1].position + lr_width/2.:
                    case.position[1] = long_rails[i-1].position + lr_width/2.

                    # Find its symmetric case in case its sym_i is 0
                    sym_case_index = GetSymmetricCase(case_index, n_lr)
                    if sym_case_index is not None:
                        sym_i, sym_j = CaseCoords(sym_case_index, n_lr)
                        if sym_i == 0:
                            sym_case = cases[sym_case_index]
                            sym_case.position[1] = -(long_rails[i-1].position\
                                                     + lr_width/2.\
                                                     + sym_case.size[1])
#                if i and case.position[1] + case.size[1] > long_rails[i].position - lr_width/2.:
                if j and case.position[0] < trans_rails[j-1].position + tr_width/2.:
                    case.position[0] = trans_rails[j-1].position + tr_width/2.
                current_x = case.position[0] + case.size[0]
                current_y = case.position[1] + case.size[1]
                current_z = case.position[2] + case.size[2]
            max_x = max(current_x, max_x)
            max_y = max(current_y, max_y)
            max_z = max(current_z, max_z)
            self.size = (max_x, 2*max_y, max_z)

            # Add rail at given x/y if no rail is already placed and one should be
            if i < n_lr and i not in fixed_lr_indices:
                rail = LongitudinalRail(current_y + lr_width/2.,
                                        self.size[0],
                                        lr_width,
                                        self.size[2])
                long_rails[i] = rail
                fixed_lr_indices.append(i)
                current_y += rail.width

            if i == n_lr and j < n_tr and j not in fixed_tr_indices:
                rail = TransversalRail(max_x + tr_width/2.,
                                       self.size[1],
                                       tr_width,
                                       self.size[2])
                trans_rails[j] = rail
                fixed_tr_indices.append(j)

                # Update x position
                current_x += rail.width

                # Reset y position
                current_y = init_y

        self.Update()
        self.long_rails = long_rails
        self.trans_rails = trans_rails
        self.case_indices = case_indices

    def Update(self):
        for rail in self.long_rails:
            if rail is not None:
                rail.length = self.size[0]
                rail.height = self.size[2]
        for rail in self.trans_rails:
            if rail is not None:
                rail.length = self.size[1]
                rail.height = self.size[2]

    def CheckViability(self, longitudinal_tolerances, transversal_tolerances, max_pack_size):
        """
        Checks if a solution follows construction rules
        returns a boolean
        """
        n_lr = len(self.long_rails)
        n_tr = len(self.trans_rails)

        i_last, j_last = CaseCoords((n_lr+1)*(n_tr+1)-1, n_lr)
        i_ref = [i for i, ratios in enumerate(transversal_tolerances) if ratios == {'minus' : 1, 'plus' : 1}][0]
        j_ref = [j for j, ratios in enumerate(longitudinal_tolerances) if ratios == {'minus' : 1, 'plus' : 1}][0]

        if j_ref and j_ref != j_last:
            prior_rail = self.trans_rails[j_ref-1]
            later_rail = self.trans_rails[j_ref]
            x_ref = later_rail.position - later_rail.width/2.\
                   - (prior_rail.position + prior_rail.width/2.)
        elif j_ref == j_last:
            prior_rail = self.trans_rails[j_ref-1]
            x_ref = max_pack_size[0] - (prior_rail.position + prior_rail.width/2.)
        else:
            later_rail = self.trans_rails[j_ref]
            x_ref = later_rail.position - later_rail.width/2.

        if i_ref and i_ref != i_last:
            prior_rail = self.long_rails[i_ref-1]
            later_rail = self.long_rails[i_ref]
            y_ref = later_rail.position - later_rail.width/2.\
                   - (prior_rail.position + prior_rail.width/2.)
        elif i_ref == i_last:
            prior_rail = self.long_rails[i_ref-1]
            y_ref = max_pack_size[1] - (prior_rail.position + prior_rail.width/2.)
        else:
            later_rail = self.long_rails[i_ref]
            y_ref = later_rail.position - later_rail.width/2.

        cases_ref = []
        complete_column_ref = False
        for case_index, case in enumerate(self.cases):
            i, j = CaseCoords(case_index, n_lr)
            if j == j_ref:
                cases_ref.append(case)

            if case is not None:
                if case.position[0] + case.size[0] > max_pack_size[0]\
                or case.position[1] + case.size[1] > max_pack_size[1]/2.\
                or case.position[2] + case.size[2] > max_pack_size[2]:
                    return False
                if complete_column_ref:
                    longitudinal_tolerance = longitudinal_tolerances[j]
                    transversal_tolerance = transversal_tolerances[i]
                    if not (case.size[0] >= x_ref*longitudinal_tolerance['minus']\
                            and case.size[0] <= x_ref*longitudinal_tolerance['plus']\
                            and case.size[1] <= y_ref*transversal_tolerance['plus']): # !!!
                        return False
            complete_column_ref = len(cases_ref) == len(transversal_tolerances)
        return True

    def LowerCasingVolume(self, fem=False):
        """
        Computes volume of the casing lower lower part
        """
        screw_holes_diameter = 0.008
        screw_holes_clearance = 0.005
        n_screws = 30

        triangle_x = self.triangle[0]
        triangle_y = self.triangle[1]

        if fem:
            p1 = vm.Point2D((0, triangle_y - self.size[1]/2.))
            p2 = vm.Point2D((0, self.size[1]/2. - triangle_y))
            p3 = vm.Point2D((triangle_x, self.size[1]/2.))
            p4 = vm.Point2D((self.size[0] - triangle_x, self.size[1]/2.))
            p5 = vm.Point2D((self.size[0], self.size[1]/2. - triangle_y))
            p6 = vm.Point2D((self.size[0], triangle_y - self.size[1]/2.))
            p7 = vm.Point2D((self.size[0] - triangle_x, -self.size[1]/2.))
            p8 = vm.Point2D((triangle_x, -self.size[1]/2.))
            points = [p1, p2, p3, p4, p5, p6, p7, p8]

        else:
            p1 = vm.Point2D((0, -0.5*self.size[1]))
            p2 = vm.Point2D((self.size[0], -0.5*self.size[1]))
            p3 = vm.Point2D((self.size[0], 0.5*self.size[1]))
            p4 = vm.Point2D((0, 0.5*self.size[1]))
            points = [p1, p2, p3, p4]

        radii = {i : self.radius for i in range(len(points))}
        inner_primitive = primitives2D.ClosedRoundedLineSegments2D(points, radii, True)
        outer_primitive = inner_primitive.Offset(-self.th_casing)
        # inner_contour = vm.Contour2D([inner_primitive])
        # outer_contour = vm.Contour2D([outer_primitive])

        sides = primitives3D.ExtrudedProfile(vm.O3D,
                                             vm.X3D, vm.Y3D,
                                             outer_primitive, [inner_primitive],
                                             self.size[2]*vm.Z3D,
                                             'sides')

        bottom = primitives3D.ExtrudedProfile(vm.O3D,
                                             vm.X3D, vm.Y3D,
                                              outer_primitive, [],
                                              -self.th_casing*vm.Z3D,
                                              'bottom')

        screw_holes_contour = inner_primitive.Offset(-(self.th_casing\
                                                                     + screw_holes_clearance\
                                                                     + 0.5*screw_holes_diameter))

        belt_outer_contour = inner_primitive.Offset(-(2*screw_holes_clearance\
                                                                    + screw_holes_diameter\
                                                                    + self.th_casing))

        if fem:
            belt = primitives3D.ExtrudedProfile(vm.Z3D*self.size[2],
                                                vm.X3D,
                                                vm.Y3D,
                                                belt_outer_contour,
                                                [inner_contour],
                                                self.th_casing*vm.Z3D,
                                                'belt')
        else:
            screw_holes = []
            l = screw_holes_contour.Length()
            for i in range(n_screws):
                s = i * l/n_screws
                p = screw_holes_contour.PointAtCurvilinearAbscissa(s)
                screw_holes.append(vm.Circle2D(p, screw_holes_diameter*0.5))

            print(belt_outer_contour, [inner_primitive]+screw_holes)
            belt = primitives3D.ExtrudedProfile(vm.Z3D*self.size[2],
                                                vm.X3D,
                                                vm.Y3D,
                                                belt_outer_contour,
                                                [inner_primitive] + screw_holes,
                                                self.th_casing*vm.Z3D,
                                                'belt')

        casing = vm.primitives3D.Fuse([bottom, sides, belt], 'Lower Casing')
        return casing

    def CADVolumes(self, fem=False):
        """
        Computes casing volumes (Rails and cells volumes) for CAD Export
        """
        volumes = []
        volumes.extend([self.LowerCasingVolume(fem)])
        for rail in self.long_rails + self.trans_rails:
            if fem:
                radius = 0
            else:
                radius = 0.10*rail.width
            volumes.extend([rail.CADVolume(radius)])
        return volumes

    def volume_model(self, fem=False):
        """
        Computes VolumeModel of MechBattery components
        """
        ps_volumes = self.CADVolumes(fem)
        model = vm.VolumeModel(ps_volumes, 'pack_structure')
        return model

    def volmdlr_volume_model(self):
        model = self.volume_model()
        return model

    # def CADExport(self, fem=False,
    #               name='An_unnamed_pack_structure',
    #               python_path='python',
    #               freecad_path='/usr/lib/freecad/lib/',
    #               export_types=('fcstd')):
    #     """
    #     Exports casing CAD file
    #     """
    #     model = self.VolumeModel(fem)
    #     resp = model.FreeCADExport(name, python_path, freecad_path, export_types)
    #     return resp

    def Dict(self):
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'cases' : [case.Dict() for case in self.cases],
                      'long_rails' : [rail.Dict() for rail in self.long_rails],
                      'trans_rails' : [rail.Dict() for rail in self.trans_rails],
                      'rail_specs' : self.rail_specs,
                      'th_casing' : self.th_casing,
                      'triangle' : self.triangle,
                      'size': self.size,
                      'radius': self.radius})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        size = dict_['size']
        cases = [Case.DictToObject(case_dict) for case_dict in dict_['cases']]
        long_rails = [LongitudinalRail.DictToObject(rail_dict)\
                      for rail_dict in dict_['long_rails']]
        trans_rails = [TransversalRail.DictToObject(rail_dict)\
                       for rail_dict in dict_['trans_rails']]
        rail_specs = dict_['rail_specs']
        th_casing = dict_['th_casing']
        triangle = dict_['triangle']
        radius = dict_['radius']
        name = dict_['name']
        pack_structure = cls(size=size, cases=cases,
                             long_rails=long_rails, trans_rails=trans_rails,
                             rail_specs=rail_specs, th_casing=th_casing,
                             triangle=triangle, radius=radius, name=name)
        return pack_structure


class JunctionBox(DessiaObject):
    """
    :param position: a volmdlr Point3D
    """
    def __init__(self, position, length, width, height, name=''):
        self.position = position
        self.length = length
        self.width = width
        self.height = height
        self.power_terminal_position = self.position + vm.Point3D((0, 0, 0))

        DessiaObject.__init__(self, name=name)

    def CADContour(self):
        """
        Computes rail section for CAD Export
        """
        p0 = vm.Point2D((-0.5*self.length, 0))
        p1 = vm.Point2D((0.5*self.length, 0))
        p2 = vm.Point2D((0.5*self.length, self.height))
        p3 = vm.Point2D((-0.5*self.length, self.height))

        l0 = vm.LineSegment2D(p0, p1)
        l1 = vm.LineSegment2D(p1, p2)
        l2 = vm.LineSegment2D(p2, p3)
        l3 = vm.LineSegment2D(p3, p0)

        contour = vm.Contour2D([l0, l1, l2, l3])

        return contour

    def CADVolumes(self):
        """
        Computes rail volume for CAD Export
        """
        contour = self.CADContour()

        xp = vm.Vector3D((1, 0, 0))
        yp = vm.Vector3D((0, self.width, 0))
        zp = vm.Vector3D((0, 0, 1))

        origin = self.position - 0.5*self.width*vm.Y3D

        volume = primitives3D.ExtrudedProfile(origin,
                                              xp, zp,
                                              contour, [],
                                              yp)
        return [volume]

    def Dict(self):
        dict_ = copy(self.__dict__)
        dict_['power_terminal_position'] = self.power_terminal_position.Dict()
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        return cls(position=dict_['position'], length=dict_['length'],
                   width=dict_['width'], height=dict_['height'], name=dict_['name'])


class HydraulicNode:
    def __init__(self):
        pass

    def Dict(self):
        return {}

    @classmethod
    def DictToObject(cls):
        return cls()

class ChainHydraulicNetwork:
    """
    An hydraulic circuit where cooling plates in a chain are only defined by types and number
    """
    def __init__(self, nodes, connections, number_type_cp_chain, cp_classes):
        self.nodes = nodes
        self.connections = connections
        self.number_type_cp_chain = number_type_cp_chain
        self.cp_classes = cp_classes


class HydraulicNetwork:
    """
    A conceptual view of an hydraulic routing

    :param nodes: a list of hydraulic nodes or CoolantSockets
    :param cooling_plates: a list of cooling plates object
    :param connections: a list of tuples of shape: (hydraulic_node, cooling_plate)
    :cooling_plates_inlets: a dict with keys cooling plates and
                            values the hydraulic node connected to the first
                            inlet socket of the cooling plate
    """
    def __init__(self, nodes, cooling_plates, connections, cooling_plates_inlets):
        self.nodes = nodes
        self.cooling_plates = cooling_plates
        self.connections = connections
        self.cooling_plates_inlets = cooling_plates_inlets

    def Graph(self):
        G = nx.Graph()
        G.add_nodes_from(self.nodes)
        G.add_nodes_from(self.cooling_plates)
        G.add_edges_from(self.connections)
        return G

    def Plot(self):
        G = self.Graph()
        # TODO: replace kamada kawai by socket positions?
        pos = nx.kamada_kawai_layout(G)
        sockets = []
        other_nodes = []
        for node in self.nodes:
            if node.__class__.__name__ == 'CoolantSocket':
                sockets.append(node)
            else:
                other_nodes.append(node)
        nx.draw_networkx_nodes(G, pos, sockets, node_color='red', node_shape='o')
        nx.draw_networkx_nodes(G, pos, other_nodes, node_color='blue', node_shape='o')
        nx.draw_networkx_nodes(G, pos, self.cooling_plates, node_shape='s', node_color='grey')
        nx.draw_networkx_edges(G, pos)

    def Length(self, cooling_plates_sockets_frames):
        piping_length = 0.
        G = self.Graph()
        for nG in G.nodes():
            if nG.__class__ == HydraulicNode:
                junction_pos = vm.O3D # Estimate position of junction (barycenter)
                n_neigbors = 0
                cp_sockets_positions = []
                for neighbor in G[nG]:
                    if neighbor.__class__.__name__ == 'CoolingPlate':
                        if G[nG][neighbor]:
                            p = cooling_plates_sockets_frames[neighbor][0]
                        else:
                            p = cooling_plates_sockets_frames[neighbor][1]
                        cp_sockets_positions.append(p)
                        junction_pos += p
                        n_neigbors += 1

                junction_pos /= float(n_neigbors)
                for socket_pos in cp_sockets_positions:
                    piping_length += junction_pos.PointDistance(socket_pos)

        return piping_length


class CoolantSocket(HydraulicNode):
    def __init__(self, position):
        HydraulicNode.__init__(self)
        self.position = position

    def Dict(self):
        dict_ = {'position' : self.position.to_dict()}
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        position = vm.Point3D.dict_to_object(dict_['position'])
        coolant_socket = cls(position)
        return coolant_socket


class Pump:
    def __init__(self, pmin, pmax, qmin, qmax, power_max):
        self.pmin = pmin
        self.pmax = pmax
        self.qmin = qmin
        self.qmax = qmax
        self.power_max = power_max


class Cooler:
    def __init__(self, pressure_drop_map, htc_map):
        self.pressure_drop_map = pressure_drop_map
        self.htc_map = htc_map


class MechBattery(DessiaObject):
    """
    Defines a battery casing

    :param mech_module: MechModule object used in battery
    :type mech_module: MechModule()
    :param elec_battery: ElecBattery object representing electrical circuit
    :type elec_battery: ElecBattery()
    :param pack_structure: PackStructure object that represents battery box
    :type pack_structure: PackStructure()
    :param module_gap: Gap between modules defined by process needs
    :type module_gap: m
    :param hydraulic_connections: TODO
    :type hydraulic_connections: TODO
    :param wiring: TODO
    :type wiring: TODO
    :param piping: TODO
    :type piping: TODO
    """
    # TODO: Problem: BMS is lost?
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.MechBattery Base Schema",
        "required": ["mech_module", "elec_battery", "pack_structure", "module_gap"],
        "properties": {
            "mech_module" : {
                "type" : "object",
                "title" : "Mechanical Module",
                "order" : 1,
                "classes" : ["powerpack.mechanical.MechModule"],
                "editable" : True,
                "description" : "Module"
                },
            "elec_battery" : {
                "type" : "object",
                "title" : "Electrical Battery",
                "order" : 2,
                "classes" : ["powerpack.electrical.ElecBattery"],
                "editable" : True,
                "description" : "Electric vision of battery"
                },
            "pack_structure" : {
                "type" : "object",
                "title" : "Pack Structure",
                "order" : 3,
                "classes" : ["powerpack.mechanical.PackStructure"],
                "editable" : True,
                "description" : "Pack structure"
                },
            "module_gap" : {
                "type" : "number",
                "title" : "Module Gap",
                "order" : 4,
                "step" : 0.001,
                "minimum" : 0,
                "editable" : True,
                "examples" : [0.005],
                "description" : "Gap between modules"
                }
            }
        }

    def __init__(self, mech_module, elec_battery, pack_structure, module_gap,
                 hydraulic_nodes=[], hydraulic_connections=[], wiring=None,
                 hydraulic_circuit=None, thermal_circuit=None, name=''):

        self.mech_module = mech_module
        self.elec_battery = elec_battery
        self.pack_structure = pack_structure
        self.module_gap = module_gap

        self.hydraulic_nodes = hydraulic_nodes
        self.hydraulic_connections = hydraulic_connections

        self.wiring = wiring
        self.hydraulic_circuit = hydraulic_circuit
        self.thermal_circuit = thermal_circuit
        self._utd_wiring_optimizer = False

        # BJB
        l_jb = 0.250
        w_jb = 0.300
        h_jb = 0.080
        # z-> height

        jb_position = vm.Point3D((self.pack_structure.size[0] - 0.5*l_jb,
                                  0,
                                  self.pack_structure.size[2]))
        self.junction_box = JunctionBox(jb_position, l_jb, w_jb, h_jb)

        self.coolant_inlet = CoolantSocket(vm.Point3D((self.pack_structure.size[0],
                                                       -0.02,
                                                       0.95*self.pack_structure.size[2])))
        self.coolant_outlet = CoolantSocket(vm.Point3D((self.pack_structure.size[0],
                                                        0.02,
                                                        0.95*self.pack_structure.size[2])))

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_mb):
        equal = (self.mech_module == other_mb.mech_module
                 and self.pack_structure == other_mb.pack_structure
                 and self.module_gap == other_mb.module_gap
                 and self.elec_battery == other_mb.elec_battery)
        # TODO wiring, etc ?
        return equal

    def __hash__(self):
        mb_hash = hash(self.mech_module)\
                 + hash(self.pack_structure)\
                 + int(1500*self.module_gap)\
                 + hash(self.elec_battery)
        return mb_hash

    def Packing(self):
        """
        Computes the total packing of the battery
        """
        battery_volume = sum([case.Volume() for case in self.pack_structure.cases])
        n_modules = sum([case.n_modules for case in self.pack_structure.cases])
        module_volume = n_modules*self.mech_module.volume
        packing = module_volume/battery_volume
        return packing

    def ModulesFrames(self):
        """
        Computes a dict of module frames
        """
        frames = {}
        nmodules = 0
        for case in self.pack_structure.cases:
            case_frames = case.Frames()
            modules_frames_case = case_frames[0]
            for imodule, frame in modules_frames_case.items():
                frames[nmodules + imodule] = frame
            nmodules += len(modules_frames_case)
        return frames

    def CoolingPlatesFrames(self):
        """
        Computes a dict of module frames
        """
        frames = {}
        for case in self.pack_structure.cases:
            modules_frames_case, cp_frames_case = case.Frames()
            for cp, frame in cp_frames_case.items():
                frames[cp] = frame
        return frames

    def CoolingPlatesSocketsPositions(self):
        cooling_plates_frames = self.CoolingPlatesFrames()
        cooling_plates_sockets_positions = {c: c.SocketsPositions(f)
                                            for c, f in cooling_plates_frames.items()}
        return cooling_plates_sockets_positions

    def DirectRouting(self, waypoint1, waypoint2, routing_height):
        """
        Finds best wiring strategy towards wire length for the current battery
        Routing from waypoint1 to waypoint2 by going to plane z=routing_height

        :returns: a list of mechanical_components.wires.Wiring
        :param number_wirings: The number of best wirings to return
        """

        waypoints = [waypoint1, waypoint2]

        x1, y1, z1 = waypoint1.vector
        x2, y2, z2 = waypoint2.vector

        if z1 != routing_height:
            new_wpt = vm.Point3D((x1, y1, routing_height))
            waypoints.insert(1, new_wpt)

        if z2 != routing_height:
            new_wpt = vm.Point3D((x1, y1, routing_height))
            waypoints.insert(-1, new_wpt)

        return waypoints

    def WiringOptimizer(self, wire_diameter=0.008):
        waypoints_cr = []
        routes_cr = []
        sorted_tr = sorted(self.pack_structure.trans_rails, key=lambda r: r.position)
        sorted_lr = sorted(self.pack_structure.long_rails, key=lambda r: r.position)
        x = 0
        y = 0
        w1, w2, w3, w4 = {}, {}, {}, {}

        nlr = len(self.pack_structure.long_rails) # Number of longitudinal rails
        ntr = len(self.pack_structure.trans_rails) # Number of transversal rails

        # Corner points
        w4[-1, -1] = vm.Point3D((wire_diameter,
                                 wire_diameter - 0.5*self.pack_structure.size[1],
                                 self.pack_structure.size[2]))
        w3[ntr, -1] = vm.Point3D((self.pack_structure.size[0] - wire_diameter,
                                  wire_diameter - 0.5*self.pack_structure.size[1],
                                  self.pack_structure.size[2]))
        w2[-1, nlr] = vm.Point3D((wire_diameter,
                                  0.5*self.pack_structure.size[1] - wire_diameter,
                                  self.pack_structure.size[2]))
        w1[ntr, nlr] = vm.Point3D((self.pack_structure.size[0] - wire_diameter,
                                   0.5*self.pack_structure.size[1] - wire_diameter,
                                   self.pack_structure.size[2]))

        # longitudinal sides of pack
        for i, t_rail in enumerate(sorted_tr):
            # Bottom
            w3[i, -1] = vm.Point3D((t_rail.position - 0.5*t_rail.width - wire_diameter,
                                    wire_diameter - 0.5*self.pack_structure.size[1],
                                    self.pack_structure.size[2]))
            w4[i, -1] = vm.Point3D((t_rail.position + 0.5*t_rail.width + wire_diameter,
                                    wire_diameter - 0.5*self.pack_structure.size[1],
                                    self.pack_structure.size[2]))
            # Top
            w1[i, nlr] = vm.Point3D((t_rail.position - 0.5*t_rail.width - wire_diameter,
                                     0.5 * self.pack_structure.size[1] - wire_diameter,
                                     self.pack_structure.size[2]))
            w2[i, nlr] = vm.Point3D((t_rail.position + 0.5*t_rail.width + wire_diameter,
                                     0.5 * self.pack_structure.size[1] - wire_diameter,
                                     self.pack_structure.size[2]))

            # Crossing t_rail
            routes_cr.extend([(w3[i, -1], w4[i, -1]),
                              (w1[i, nlr], w2[i, nlr])])
            # Between t_rails
            routes_cr.extend([(w4[i-1, -1], w3[i, -1]),
                              (w2[i-1, nlr], w1[i, nlr])])

        # Transversal sides of pack
        for j, l_rail in enumerate(sorted_lr):
            # Left
            w2[-1, j] = vm.Point3D((wire_diameter,
                                    l_rail.position - 0.5*l_rail.width - wire_diameter,
                                    self.pack_structure.size[2]))
            w4[-1, j] = vm.Point3D((wire_diameter,
                                    l_rail.position + 0.5*l_rail.width + wire_diameter,
                                    self.pack_structure.size[2]))
            # Right
            w1[ntr, j] = vm.Point3D((self.pack_structure.size[0] - wire_diameter,
                                     l_rail.position - 0.5*l_rail.width - wire_diameter,
                                     self.pack_structure.size[2]))
            w3[ntr, j] = vm.Point3D((self.pack_structure.size[0] - wire_diameter,
                                     l_rail.position + 0.5*l_rail.width + wire_diameter,
                                     self.pack_structure.size[2]))

            # Crossing l_rail
            routes_cr.extend([(w4[-1, j], w2[-1, j]),
                              (w1[ntr, j], w3[ntr, j])])
            # Between l_rails
            routes_cr.extend([(w4[-1, j-1], w2[-1, j]),
                              (w3[ntr, j-1], w1[ntr, j])])

        # Inner part of case
        for i, t_rail in enumerate(sorted_tr):
            for j, l_rail in enumerate(sorted_lr):
                w1[i, j] = vm.Point3D((t_rail.position - 0.5*t_rail.width - wire_diameter,
                                       l_rail.position - 0.5*l_rail.width - wire_diameter,
                                       self.pack_structure.size[2]))
                w2[i, j] = vm.Point3D((t_rail.position + 0.5*t_rail.width + wire_diameter,
                                       l_rail.position - 0.5*l_rail.width - wire_diameter,
                                       self.pack_structure.size[2]))
                w3[i, j] = vm.Point3D((t_rail.position - 0.5*t_rail.width - wire_diameter,
                                       l_rail.position + 0.5*l_rail.width + wire_diameter,
                                       self.pack_structure.size[2]))
                w4[i, j] = vm.Point3D((t_rail.position + 0.5*t_rail.width + wire_diameter,
                                       l_rail.position + 0.5*l_rail.width + wire_diameter,
                                       self.pack_structure.size[2]))
                routes_cr.extend([(w1[i, j], w2[i, j]),
                                  (w1[i, j], w3[i, j]),
                                  (w2[i, j], w4[i, j]),
                                  (w3[i, j], w4[i, j]),
                                  (w3[i, j], w2[i, j]),
                                  (w1[i, j], w4[i, j])])

                routes_cr.append((w2[i-1, j], w1[i, j]))
                routes_cr.append((w4[i-1, j], w3[i, j]))
                routes_cr.append((w3[i, j-1], w1[i, j]))
                routes_cr.append((w4[i, j-1], w2[i, j]))

        for i in range(ntr):
            # Descending to n-1 nodes
            routes_cr.extend([(w1[i, nlr], w3[i, nlr-1]),
                              (w2[i, nlr], w4[i, nlr-1])])
        for j in range(nlr):
            routes_cr.extend([(w3[ntr, j], w4[ntr-1, j]),
                              (w1[ntr, j], w2[ntr-1, j])])

        routes_cr.extend([(w2[-1, nlr], w4[-1, nlr-1]),
                          (w2[ntr-1, nlr], w1[ntr, nlr]),
                          (w3[ntr, nlr-1], w1[ntr, nlr]),
                          (w4[ntr-1, -1], w3[ntr, -1])])

        waypoints_cr.extend(w1.values())
        waypoints_cr.extend(w2.values())
        waypoints_cr.extend(w3.values())
        waypoints_cr.extend(w4.values())

        # Connecting end of longitudinal rails to JB
        waypoints_cr.append(self.junction_box.power_terminal_position)

        if nlr%2 == 1:
            # There's a central long rail
            j = nlr // 2
            routes_cr.extend([(w2[ntr-1, j], self.junction_box.power_terminal_position),
                              (w4[ntr-1, j], self.junction_box.power_terminal_position),
                              (w1[ntr, j], self.junction_box.power_terminal_position),
                              (w3[ntr, j], self.junction_box.power_terminal_position)])
        else:
            # There's a central case
            j = nlr // 2
            routes_cr.extend([(w2[ntr-1, j], self.junction_box.power_terminal_position),
                              (w4[ntr-1, j-1], self.junction_box.power_terminal_position),
                              (w1[ntr, j], self.junction_box.power_terminal_position),
                              (w3[ntr, j-1], self.junction_box.power_terminal_position)])

        # Connecting modules sokets to routing graph
        for case in self.pack_structure.cases:
            i, j = self.pack_structure.case_indices[case]
            for grid in case.case_content.grids:
                modules_frames, cp_frames = grid.Frames(case.position)
                for imodule_case, frame in modules_frames.items():
                    for n_tl in range(3):
                        grid.mech_module.SetTerminalsLayout(n_tl)
                        for module_side in [False, True]:
                            pm, pp = grid.mech_module.TerminalsPositions(frame, module_side)
                            for point_socket in (pp, pm):
                                if point_socket[2] != (self.pack_structure.size[2]
                                                       + 0.5*wire_diameter):
                                    x, y, _ = point_socket.vector
                                    z = self.pack_structure.size[2]
                                    point_socket2 = vm.Point3D((x, y, z))
                                    waypoints_cr.append(point_socket2)
                                    routes_cr.extend([(w4[i-1, j-1], point_socket2),
                                                      (w2[i-1, j], point_socket2),
                                                      (w3[i, j-1], point_socket2),
                                                      (w1[i, j], point_socket2),
                                                      (point_socket, point_socket2)])
                                else:
                                    routes_cr.extend([(w4[i-1, j-1], point_socket),
                                                      (w2[i-1, j], point_socket),
                                                      (w3[i, j-1], point_socket),
                                                      (w1[i, j], point_socket)])

        wo = wires_opt.WiringOptimizer(waypoints_cr, routes_cr)
        return wo

    def _get_wiring_optimizer(self):
        if not self._utd_wiring_optimizer:
            self._wiring_optimizer = self.WiringOptimizer()
            self._utd_wiring_optimizer = True
        return self._wiring_optimizer

    wiring_optimizer = property(_get_wiring_optimizer)



    def ThermoHydraulicCircuits(self, hydraulic_network, diameter=0.008, dP=1):
        """
        Create the corresponding hydraulic circuit out of the conceptual hydraulic
        network given as parameter

        :param hydraulic_network: a hydraulic netwok object:
        :param diameter: the estimate diameter of pipes
        :param dP: the estimate difference of pressure between input and output
        """

        cooling_plates_sockets_positions = self.CoolingPlatesSocketsPositions()

        sockets = []
        G = hydraulic_network.Graph()
        pipes = []
        points = []
        up2cp = {}

        for hy_node in hydraulic_network.nodes:
            if hy_node.__class__.__name__ == 'CoolantSocket':
                sockets.append(hy_node.position)
                piping_endpoints = [hy_node.position]# List of endpoints
            else:
                piping_endpoints = []

            for cooling_plate in G[hy_node]:
                if hydraulic_network.cooling_plates_inlets[cooling_plate] == hy_node:
                    piping_endpoints.append(cooling_plates_sockets_positions[cooling_plate][0])
                else:
                    piping_endpoints.append(cooling_plates_sockets_positions[cooling_plate][1])

            nconnec = len(piping_endpoints)

            if nconnec == 2:
                # Creating a pipe between 2 points
                x1, y1, _ = piping_endpoints[0]
                x2, y2, _ = piping_endpoints[1]
                z = self.pack_structure.size[2] + 0.5*diameter
                piping_endpoints.insert(1, vm.Point3D((x1, y1, z)))
                piping_endpoints.insert(2, vm.Point3D((x2, y2, z)))
                rl = primitives3D.RoundedLineSegments3D(piping_endpoints,
                                                        {i+1:3* diameter for i in range(2)},
                                                        adapt_radius=True)
                pipes.extend([hy.pipes.PipesFromVolmdlrPrimitives(p, diameter)
                              for p in rl.basis_primitives])
                points.extend([p.points[0]
                               for p in rl.basis_primitives]+[rl.basis_primitives[-1].points[-1]])

            elif nconnec == 1:
                raise NotImplementedError
#                x_socket, y_socket, _ = hy_node.position
#                x2, y2, _ = hy_node_connections[0]
#                z = self.pack_structure.size[2] + 0.5*diameter
#                hy_node_connections.append(vm.Point3D((x2, y2, z)))
#                hy_node_connections.append(vm.Point3D((x_socket-1.25*diameter, y_socket, z)))
#                hy_node_connections.append(hy_node.position - 1.25*diameter*vm.X3D)
#                hy_node_connections.append(hy_node.position)
#                rl = primitives3D.RoundedLineSegments3D(hy_node_connections,
#                                                        {i+1:3* diameter for i in range(3)},
#                                                        adapt_radius=True)
#                pipes.extend([hy.pipes.PipesFromVolmdlrPrimitives(p, diameter)
#                              for p in rl.basis_primitives])
#                points.extend([p.points[0]
#                               for p in rl.basis_primitives]+[rl.basis_primitives[-1].points[-1]])

            elif nconnec >= 3:
                p_mean = vm.O3D
                for p in piping_endpoints:
                    p_mean += p
                p_mean /= len(piping_endpoints)
                points.extend(piping_endpoints)
                points.append(p_mean)
                pipes.append(hy.pipes.JunctionPipe(p_mean, piping_endpoints, diameter))

            else:
                print(nconnec)
                raise NotImplementedError

        for cooling_plate in hydraulic_network.cooling_plates:
            user_pipe = hy.pipes.UserDefined(*cooling_plates_sockets_positions[cooling_plate], 1)
            pipes.append(user_pipe) # !!! fQ = 1
            up2cp[cooling_plate] = user_pipe

        # TODO: remove next lines?
        if not sockets[0] in points:
            points.append(sockets[0])
        if not sockets[1] in points:
            points.append(sockets[1])

        boundary_conditions = [hy.PressureCondition(sockets[0], dP),
                               hy.PressureCondition(sockets[-1], 0)]
        circuit = hy.Circuit3D(points, pipes, boundary_conditions, hy.fluids.water)

        result = circuit.SolveFluidics()

        # Thermal nodes and blocks from hydraulic part of the circuit
        input_points = []
        output_points = []
        system_data = circuit.ResolutionSettings()
        flows_dict = system_data[1]
        for boundary_condition in circuit.boundary_conditions:
            point = boundary_condition.points[0]
            j = flows_dict[(boundary_condition, point)]
            flow = result.solution[j]
            if flow > 0:
                output_points.append(point)
            elif flow < 0:
                input_points.append(point)
            else:
                raise ValueError("Flow = 0 at point"+point)
        thc = result.ToThermal(input_points, output_points)

        for input_node in thc.interface_nodes['input']:
            block = hy_thermal.TemperatureBound([input_node], 293) # !!! Value
            thc.thermal_circuit.AddBlocks([block])

        connected_modules = []
        for i_case, case in enumerate(self.pack_structure.cases):
            grid = case.case_content.grids[0] # !!! grids[0]
            module_frames, cp_frames = case.Frames()
            for i_module, (x_module, y_module) in enumerate(grid.module_coords):
                if (i_case, i_module) not in connected_modules:
                    connected_modules.append((i_case, i_module))
                    modules_cp, cp_modules = grid.CooledModules()
                    cooling_plates = modules_cp[i_module]

                    module_node = hy_thermal.Node()
                    module_frame = module_frames[i_module]
                    module_point = module_frame.origin
                    thc.node2point[module_node] = module_point

                    cp_nodes = []
                    res_nodes = []
                    if len(cooling_plates) == 1:
                        cp = cooling_plates[0]
                        user_pipe = up2cp[cp]
                        block = thc.pipe2block[user_pipe]
                        for cp_node in block.nodes:
                            if cp_node in thc.interface_nodes['wall_nodes']:
                                cp_nodes.append(cp_node)
                                cp_frame = cp_frames[cp]
                                cp_point = cp_frame.origin
                                thc.node2point[cp_node] = cp_point

                                res_node = hy_thermal.Node()
                                res_point = (module_point + cp_point)/2
                                thc.node2point[res_node] = res_point
                                res_nodes.append(res_node)
                                resistor = hy_thermal.Resistor([cp_node, res_node], 1)
                                thc.thermal_circuit.AddBlocks([resistor])

                    elif len(cooling_plates) == 2:
                        user_pipes = [up2cp[cp] for cp in cooling_plates]
                        blocks = [thc.pipe2block[up] for up in user_pipes]
                        for i_block, block in enumerate(blocks):
                            for cp_node in block.nodes:
                                if cp_node in thc.interface_nodes['wall_nodes']:
                                    cp_nodes.append(cp_node)
                                    cp = cooling_plates[i_block]
                                    cp_frame = cp_frames[cp]
                                    cp_point = cp_frame.origin
                                    thc.node2point[cp_node] = cp_point

                                    res_node = hy_thermal.Node()
                                    res_point = (module_point + cp_point)/2
                                    thc.node2point[res_node] = res_point
                                    res_nodes.append(res_node)
                                    resistor = hy_thermal.Resistor([cp_node, res_node], 1)
                                    thc.thermal_circuit.AddBlocks([resistor])

                    nodes = [*res_nodes, module_node]
                    medium = hy_thermal.UnidimensionalMedium(nodes, 1, 1, 1, 'medium')
                    heat_flux = hy_thermal.HeatFlowInBound([module_node], -1)
                    thc.thermal_circuit.AddBlocks([medium, heat_flux])

        return circuit, thc

    def plot_data(self, max_size=None):
        """
        Draws the casing and its components
        """
        plot_datas = []
        elements = self.pack_structure.trans_rails\
                    + self.pack_structure.long_rails\
                    + self.pack_structure.cases
        for element in elements:
            if element is not None:
                plot_datas.extend(element.plot_data())
#        _ = [element.plot_data() for element in elements if element is not None]

#        if self.wiring is not None:
#            self.wiring.Draw(x3D=vm.X3D, y3D=vm.Y3D, ax=ax)

        if max_size is not None:
            p1 = vm.Point2D((0, -max_size[1]/2.))
            p2 = p1.Translation(vm.Vector2D((max_size[0], 0)))
            p3 = p2.Translation(vm.Vector2D((0, max_size[1])))
            p4 = p3.Translation(vm.Vector2D((-max_size[0], 0)))
            poly = vm.Polygon2D([p1, p2, p3, p4, p1])
            polY2D = vm.Contour2D([poly])
            plot_datas.append(polY2D.plot_data(fill='black'))

        return plot_datas

#            ax.add_patch(patches.Rectangle((0, -max_size[1]/2.),
#                                           max_size[0], max_size[1],
#                                           fill=False, color='k', linewidth=2))

#        ax.axis('equal')
#        ax.autoscale()


    def CADContour(self):
        """
        Computes cell section for CAD Export
        """
        p0 = vm.Point2D((0, 0))
        p1 = vm.Point2D((self.pack_structure.size[0], 0))
        p2 = vm.Point2D((self.pack_structure.size[0], self.pack_structure.size[1]))
        p3 = vm.Point2D((0, self.pack_structure.size[1]))

        l0 = vm.LineSegment2D(p0, p1)
        l1 = vm.LineSegment2D(p1, p2)
        l2 = vm.LineSegment2D(p2, p3)
        l3 = vm.LineSegment2D(p3, p0)

        inner_contour = vm.Contour2D([l0, l1, l2, l3])

        p0 = vm.Point2D((-0.010, -0.010))
        p1 = vm.Point2D((self.pack_structure.size[0] + 0.020, -0.010))
        p2 = vm.Point2D((self.pack_structure.size[0] + 0.020, self.pack_structure.size[1] + 0.020))
        p3 = vm.Point2D((-0.010, self.pack_structure.size[1] + 0.020))

        l0 = vm.LineSegment2D(p0, p1)
        l1 = vm.LineSegment2D(p1, p2)
        l2 = vm.LineSegment2D(p2, p3)
        l3 = vm.LineSegment2D(p3, p0)

        outer_contour = vm.Contour2D([l0, l1, l2, l3])

        return inner_contour, outer_contour

    def CADVolumes(self):
        """
        Computes casing volumes (Rails and cells volumes) for CAD Export
        """
        volumes = []
        for case in self.pack_structure.cases:
            volumes.extend(case.case_content.CADVolume(case.position))

        return volumes

    def volume_model(self):
        """
        Computes VolumeModel of MechBattery components
        """
        volumes = self.CADVolumes()
        volumes.extend(self.pack_structure.CADVolumes())

        # Adding wires volumes
        wire_volumes = []
        if self.wiring is not None:
            for wire in self.wiring.wires:
                wire_volumes.append(wire.CADVolume())

        # Adding hydraulic circuit primitives
        pipes_volumes = []
        if self.hydraulic_circuit is not None:
            pipes_volumes = self.hydraulic_circuit.CADModel().groups[0][1]

        jb_volumes = self.junction_box.CADVolumes()
        model = vm.VolumeModel(primitives=volumes + jb_volumes + wire_volumes + pipes_volumes)
        return model

    def volmdlr_volume_model(self):
        model = self.volume_model()
        return model

    def _display_angular(self):
        model = self.volmdlr_volume_model()
        displays = [{'angular_component': 'cad_viewer', 'data': model.babylon_data()},
                    {'angular_component': 'plot_data', 'data': self.plot_data()}]
        return displays

    # def CADExport(self, name='An_unnamed_battery',
    #               python_path='python',
    #               freecad_path='/usr/lib/freecad/lib/',
    #               export_types=('fcstd')):
    #     """
    #     Exports casing CAD file
    #     """
    #     model = self.VolumeModel()
    #     print(model)
    #     resp = model.FreeCADExport(name, python_path, freecad_path, export_types)
    #     return resp

    def Dict(self):
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'mech_module' : self.mech_module.Dict(),
                      'elec_battery' : self.elec_battery.Dict(),
                      'pack_structure' : self.pack_structure.Dict(),
                      'coolant_inlet' : self.coolant_inlet.Dict(),
                      'coolant_outlet' : self.coolant_outlet.Dict(),
                      'module_gap' : self.module_gap,
                      'hydraulic_nodes' : [hn.Dict() for hn in self.hydraulic_nodes],
                      'hydraulic_connections' : [hc.Dict() for hc in self.hydraulic_connections]})
        if self.wiring is not None:
            dict_['wiring'] = self.wiring.Dict()
        else:
            dict_['wiring'] = None
        if self.hydraulic_circuit is not None:
            dict_['hydraulic_circuit'] = self.hydraulic_circuit.Dict()
        else:
            dict_['hydraulic_circuit'] = None

        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        mech_module = MechModule.DictToObject(dict_['mech_module'])
        elec_battery = electrical.ElecBattery.DictToObject(dict_['elec_battery'])
        pack_structure = PackStructure.DictToObject(dict_['pack_structure'])
        if 'hydraulic_nodes' in dict_:
            hydraulic_nodes = [HydraulicNode.DictToObject() for d in dict_['hydraulic_nodes']]
        else:
            hydraulic_nodes=[]
        if 'hydraulic_connections' in dict_:
            hydraulic_connections = dict_['hydraulic_connections']
        else:
            hydraulic_connections=[]
        if 'wiring' in dict_:
            wiring = dict_['wiring']
        else:
            wiring=None
        if 'hydraulic_circuit' in dict_:
            hydraulic_circuit = dict_['hydraulic_circuit']
        else:
            hydraulic_circuit=None
        mech_battery = cls(mech_module=mech_module,
                           elec_battery=elec_battery,
                           pack_structure=pack_structure,
                           module_gap=dict_['module_gap'],
                           hydraulic_nodes=hydraulic_nodes,
                           hydraulic_connections=hydraulic_connections,
                           wiring=wiring,
                           hydraulic_circuit=hydraulic_circuit,
                           name=dict_['name'])
        return mech_battery


class Case(DessiaObject):
    """
    Defines a case

    :param position: Origin of the case in global frame
    :type position: vm.Point3D()
    :param size: Tuple that represent case size in global frame
    :type size: (x, y, z) mm
    :param case_content: Positions of modules inside case
    :type case_content: CaseContent()
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.Case Base Schema",
        "required": ["position", "size"],
        "properties": {
            "position" : {
                "type" : "object",
                "title" : "Position",
                "order" : 1,
                "classes" : ["volmdlr.core.Point3D"],
                "editable" : True,
                "description" : "Position of case"
                },
            "size" : {
                "type" : "array",
                "title" : "Size",
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
                "description" : "Size of the case"
                },
            "case_content" : {
                "type" : "object",
                "title" : "Case Content",
                "order" : 3,
                "classes" : ["powerpack.mechanical.CaseContent"],
                "editable" : True,
                "description" : "Content of the case"
                }
            }
        }

    def __init__(self, position, size, case_content=None, name=''):
        self.position = position
        self.size = size
        self.case_content = case_content

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_case):
        equal = (self.position == other_case.position
                 and npy.allclose(self.size, other_case.size)
                 and self.case_content == other_case.case_content)
        return equal

    def __hash__(self):
        return int(sum(756*self.position) + sum(156*self.size) + hash(self.case_content))

    def _display_angular(self):
        displays = [{'angular_component': 'app-d3-plot-data',
                     'component': 'plot_data',
                     'data': self.plot_data()},
                    {'angular_component': 'app-cad-viewer'}]
        return displays

    def Frames(self):
        if self.case_content is not None:
            return self.case_content.Frames(self.position)
        return None

    def Volume(self):
        """
        Calculs case volume
        """
        volume = self.size[0]*self.size[1]*self.size[2]
        return volume

    def plot_data(self, border=False):

        plot_datas = []
        if self.case_content is not None:
            plot_datas.extend(self.case_content.plot_data(self.position))

        if border:
            p1 = vm.Point2D((self.position[:2]))
            p2 = p1.Translation(vm.Vector2D((self.size[0], 0)))
            p3 = p2.Translation(vm.Vector2D((0, self.size[1])))
            p4 = p3.Translation(vm.Vector2D((-self.size[0], 0)))
            poly = vm.Polygon2D([p1, p2, p3, p4, p1])
            polY2D = vm.Contour2D([poly])
            plot_datas.append(polY2D.plot_data(fill='black'))

        return plot_datas
#            ax.add_patch(patches.Rectangle(self.position[:2],
#                                           self.size[0],
#                                           self.size[1],
#                                           fill=False,
#                                           color='b'))
#            plt.axis('equal')

    def Dict(self):
        float_size = [float(v) for v in self.size]
        if self.case_content is not None:
            case_content_dict = self.case_content.Dict()
        else:
            case_content_dict = None
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'position' : self.position.to_dict(),
                      'case_content' : case_content_dict,
                      'size' : float_size})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        position = vm.Point3D.dict_to_object(dict_['position'])
        if 'case_content' in dict_:
            case_content = CaseContent.DictToObject(dict_['case_content'])
        else:
            case_content = None
        case = cls(position=position, size=dict_['size'],
                   case_content=case_content, name=dict_['name'])
        return case


class CaseContent(DessiaObject):
    """
    Gathers several modules grids

    :param grids: List of Grid objects that represent modules position
    :type grids: [Grid, Grid, ...]
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.CaseContent Base Schema",
        "required": ["grids"],
        "properties": {
            "grids" : {
                "type" : "array",
                "title" : "Grids",
                "order" : 1,
                "items" : {
                    "type" : "object",
                    "classes" : ["powerpack.mechanical.Grid"]},
                    "editable" : True,
                    "description" : "Grid objects contained in case"
                    }
                }
            }

    def __init__(self, grids, name=''):
        self.grids = grids

        DessiaObject.__init__(self, name=name)

    def __getitem__(self, key):
        return self.grids[key]

    def __eq__(self, other_content):
        if len(self.grids) == len(other_content.grids):
            equal = all([grid == other_grid
                         for grid, other_grid
                         in zip(self.grids, other_content.grids)])
            return equal
        return False

    def __hash__(self):
        return sum([hash(grid) for grid in self.grids])

    def _display_angular(self):
        displays = [{'angular_component': 'app-d3-plot-data',
                     'component': 'plot_data',
                     'data': self.plot_data()},
                    {'angular_component': 'app-cad-viewer'}]
        return displays

    def Dimensions(self):
        size = [0, 0, 0]
        for grid in self.grids:
            grid_size = grid.Dimensions()
            size[0] += grid_size[0]
            size[1] += grid_size[1]
            size[2] += grid_size[2]
        return size

    def Frames(self, position):
        modules_frames, cooling_plates_frames = {}, {}
        for grid in self.grids:
            mf_grid, cpf_grid = grid.Frames(position)
            modules_frames.update(mf_grid)
            cooling_plates_frames.update(cpf_grid)
        return modules_frames, cooling_plates_frames

    def NumberOfModules(self):
        n_modules = sum([grid.n_modules for grid in self.grids])
        return n_modules

    def plot_data(self, position=vm.O3D):

        plot_datas = []
        for grid in self.grids:
            plot_datas.extend(grid.plot_data(position))
#        _ = [grid.plot_data(position) for grid in self.grids]
        return plot_datas

    def CADVolume(self, origin=vm.O3D):
        volumes = []

        for grid in self.grids:
            volumes.extend(grid.CADVolume(origin))
        return volumes

    def volume_model(self):
        model = vm.VolumeModel(self.CADVolume(), self.name)
        return model

    def volmdlr_volume_model(self):
        model = self.volume_model()
        return model

    def Dict(self):
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'grids' : [grid.Dict() for grid in self.grids]})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        grids = [Grid.DictToObject(grid_dict) for grid_dict in dict_['grids']]
        case_content = cls(grids=grids, name=dict_['name'])
        return case_content


class Grid(DessiaObject):
    """
    Defines a grid that represent positions of modules, cooling plates...

    :param grid: Tuple representing number of modules in 2D
    :type grid: (nx, ny)
    :param mech_module: MechModule object used in grid
    :type mech_module: MechModule()
    :param basis: Basis object that represent modules orientation in grid
    :type basis: vm.Basis3D
    :param cooling_plates_normal_vector: Vector that indicates cooling plates normal direction
    :type cooling_plates_normal_vector: vm.Vector3D
    :param piles: TODO
    :type piles: List TODO
    :param cp_thickness: Thickness of cooling plates
    :type cp_thickness: m
    :param module_gap: Gap between modules defined by process needs
    :type module_gap: m
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.Grid Base Schema",
        "required": ["grid", "mech_module", "basis", "cp_normal_vector"],
        "properties": {
            "grid" : {
                "type" : "array",
                "title" : "Grid",
                "order" : 1,
                "items" : {
                    "type" : "number",
                    "editable" : True,
                    "step" : 1,
                    "minimum" : 1,
                    },
                "examples": [[3, 2]],
                "minItems": 2,
                "maxItems": 2,
                "editable" : True,
                "description" : "Grid"
                },
            "mech_module" : {
                "type" : "object",
                "title" : "Mech Module",
                "order" : 2,
                "classes" : ["powerpack.mechanical.MechModule"],
                "editable" : True,
                "description" : "Mechanical module"
                },
            "basis" : {
                "type" : "object",
                "title" : "Basis",
                "order" : 3,
                "classes" : ["volmdlr.core.Basis3D"],
                "editable" : True,
                "description" : "Orientation basis of modules"
                },
            "cp_normal_vector" : {
                "type" : "object",
                "title" : "Cooling Plates Normal Vector",
                "order" : 4,
                "classes" : ["volmdlr.core.Vector3D"],
                "editable" : True,
                "description" : "Cooling plates normal vector"
                }
            }
        }

    def __init__(self, grid, mech_module, basis, cooling_plates_normal_vector,
                 piles=None, modules_side=None, cp_thickness=0.010,
                 module_gap=0.005, name=''):
        self.grid = grid
        self.mech_module = mech_module
        self.basis = basis
        self.modules_side = modules_side
        self.module_gap = module_gap
        self.cp_thickness = cp_thickness
        self.n_modules = grid[0]*grid[1]

        self.cp_normal_vector = cooling_plates_normal_vector
        self.cp_direction_vector = cooling_plates_normal_vector.Rotation(vm.O3D,
                                                                         vm.Z3D,
                                                                         math.pi/2)

        n_modules_norm = abs(npy.dot(self.cp_normal_vector.vector, grid))
        if n_modules_norm + 1 == len(piles):
            self.piles = piles
        else:
            msg = 'Number of modules in piles normal direction ({}) '.format(n_modules_norm)\
                + 'and cooling plates piles ({}) is not consistent. '.format(len(piles))\
                + 'Add or remove piles to match number_of_modules == len(piles) - 1.'
            raise ValueError(msg)

        self.isempty = not all(grid)

        self.cp_piles = self.GenerateCoolingPlates(cp_thickness)

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_grid):
        equal = (self.grid == other_grid.grid
                 and self.mech_module == other_grid.mech_module
                 and self.basis == other_grid.basis)

        # TODO more criteria ?
        return equal

    def __hash__(self):
        grid_hash = sum(self.grid) + hash(self.mech_module)
        # TODO: hash of basis in volmdlr?
        return grid_hash

    def _display_angular(self):
        displays = [{'angular_component': 'app-d3-plot-data',
                     'component': 'plot_data',
                     'data': self.plot_data()},
                    {'angular_component': 'app-cad-viewer'}]
        return displays

    def _get_volume(self):
        """
        Computes volume of the grid
        """
        if self.isempty:
            # If empty grid, module is None and module volume is therefore 0
            volume = 0
        else:
            # Else, computes module volume
            volume = self.n_modules*self.mech_module.volume
        return volume

    volume = property(_get_volume)

    def GenerateCoolingPlates(self, thickness):
        """
        Generate cooling plates with specified thickness
        """
        # TODO abs is a good idea?
        if self.isempty:
            # If empty grid, module is None and module dimensions is therefore (0, 0, 0)
            module_vect_size_ijk = vm.Point3D((0, 0, 0))
        else:
            # Else, computes module dimensions
            module_dimension = self.mech_module.ModuleDimensions(self.basis)
            module_vect_size_ijk = vm.Point3D([abs(i) for i in module_dimension.vector])

        module_size_b = abs(module_vect_size_ijk.Dot(self.cp_direction_vector))
        cp_piles = []
        for pile in self.piles:
            cp_pile = []
            for bounds in pile:
                count = bounds[1] - bounds[0] + 1
                cp_size = (thickness,
                           count*module_size_b + (count - 1)*self.module_gap,
                           module_vect_size_ijk[2])
                cooling_plate = CoolingPlate(copy(cp_size))
                cp_pile.append(cooling_plate)
            cp_piles.append(cp_pile)
        return cp_piles

    def _get_module_coords(self):
        """
        Computes module coordinates from grid and cooling plates normal vector

        :returns: List of module coordinates
        """
        na = int(round(abs(npy.dot(self.cp_normal_vector.vector, self.grid))))
        nb = int(round(abs(npy.dot(self.cp_direction_vector.vector, self.grid))))
        return [(i, j)  for j in range(nb) for i in range(na)]

    module_coords = property(_get_module_coords)

    def CooledModules(self):
        module_coords = self.module_coords
        modules_cp = {i : [] for i in range(len(module_coords))}
        cp_modules = {}
        for cp_pile in self.cp_piles:
            for cp in cp_pile:
                cp_modules[cp] = []
        for i_module, (x_module, y_module) in enumerate(module_coords):
            for x in [x_module, x_module+1]:
                pile = self.piles[x]
                cp_pile = self.cp_piles[x]
                for j_cp, bounds in enumerate(pile):
                    if y_module >= bounds[0] and y_module <= bounds[1]:
                        cp = cp_pile[j_cp]
                        modules_cp[i_module].append(cp)
                        cp_modules[cp].append(i_module)
        return modules_cp, cp_modules

    def Frames(self, position):
        """
        Computes a dict of in-grid-module frames
        :returns : two dictionnaries: one for module frames and one for cooling
        plate frames
        """
        module_frames = {}
        cp_frames = {}
        imodule = 0

        cp_basis = vm.Basis3D(self.cp_normal_vector,
                              self.cp_direction_vector,
                              vm.Z3D)

        if self.isempty:
            # If empty grid, module is None and module dimensions is therefore (0, 0, 0)
            module_vect_size_ijk = vm.Point3D((0, 0, 0))
        else:
            # Else, computes module dimensions
            module_vect_size_ijk = self.mech_module.ModuleDimensions(self.basis)
        modules_b_positions = {}
        module_pos_b = 0
        module_pos_c = 0.5*module_vect_size_ijk[2]
        for m in range(int(round(abs(npy.dot(self.grid, cp_basis.v.vector))))):
            module_pos_b += self.module_gap
            modules_b_positions[m] = module_pos_b
            module_pos_b += abs(npy.dot(module_vect_size_ijk.vector,
                                        cp_basis.v.vector))

        module_pos_a = self.module_gap
        cp_pos_a = self.module_gap
        for i, cp_pile in enumerate(self.cp_piles):
            module_pos_b = 0
            cp_pos_b = 0

            # Cooling plate positionning
            if cp_pile:
                cooling_plate = cp_pile[0]
                cp_pos_a += 0.5*cooling_plate.size[0]
                for j, cp in enumerate(cp_pile):
                    start_module = self.piles[i][j][0]
                    cp_pos_b = modules_b_positions[start_module] + 0.5*cp.size[1]
                    cp_pos = (cp_pos_a, cp_pos_b, 0)
                    cp_pos_ijk = (abs(npy.dot(cp_pos, cp_basis.u.vector)),
                                  abs(npy.dot(cp_pos, cp_basis.v.vector)),
                                  0)
                    cp_frame = vm.Frame3D(vm.Point3D(cp_pos_ijk),
                                          cp_basis.u,
                                          cp_basis.v,
                                          cp_basis.w)
                    cp_frames[cp] = cp_frame
                cp_pos_a += 0.5*cooling_plate.size[0]

            # Module positionning
            if i < int(abs(npy.dot(self.grid, cp_basis.u.vector))):
                if cp_pile:
                    cooling_plate = cp_pile[0]
                    module_pos_a += cooling_plate.size[0]
                else:
                    module_pos_a += self.module_gap
                module_pos_a += 0.5*abs(npy.dot(module_vect_size_ijk.vector,
                                                cp_basis.u.vector))
                for m in range(int(round(abs(npy.dot(self.grid, cp_basis.v.vector))))):
                    module_pos_b = modules_b_positions[m]\
                                  + 0.5*abs(npy.dot(module_vect_size_ijk.vector,
                                                    cp_basis.v.vector))
                    module_origin = (module_pos_a, module_pos_b, module_pos_c)
                    module_origin_ijk = (abs(npy.dot(module_origin, cp_basis.u.vector)),
                                         abs(npy.dot(module_origin, cp_basis.v.vector)),
                                         abs(npy.dot(module_origin, cp_basis.w.vector)))
                    module_frame = vm.Frame3D(vm.Point3D(module_origin_ijk),
                                              self.basis.u,
                                              self.basis.v,
                                              self.basis.w)
                    module_frames[imodule] = module_frame
                    imodule += 1
                module_pos_a += 0.5*abs(npy.dot(module_vect_size_ijk.vector,
                                                cp_basis.u.vector))
                cp_pos_a = module_pos_a
        for frame in module_frames.values():
            frame.origin += position

        for frame in cp_frames.values():
            frame.origin += position
        return module_frames, cp_frames

    def Dimensions(self):
        """
        Computes grid dimensions
        """
        if self.isempty:
            # If empty grid, module is None and module dimensions is therefore (0, 0, 0)
            module_vect_size_ijk = vm.Point3D((0, 0, 0))
        else:
            # Else, computes module dimensions
            module_vect_size_ijk = self.mech_module.ModuleDimensions(self.basis)
        grid_vector = vm.Vector3D(self.grid)

        n_modules_a = abs(self.cp_normal_vector.Dot(grid_vector))
        module_dim_a = n_modules_a*abs(self.cp_normal_vector.Dot(module_vect_size_ijk))
        cp_dim_a = sum([cp[0].size[0] if cp else self.module_gap for cp in self.cp_piles])

        n_modules_b = abs(self.cp_direction_vector.Dot(grid_vector))
        module_dim_b = n_modules_b*abs(self.cp_direction_vector.Dot(module_vect_size_ijk))
        cp_dim_b = self.module_gap*(n_modules_b+1)

        vect_size = (module_dim_a + cp_dim_a + 2*self.module_gap)*self.cp_normal_vector\
                    + (module_dim_b + cp_dim_b)*self.cp_direction_vector\
                    + module_vect_size_ijk[2]*vm.Z3D

        return npy.abs(vect_size.vector)

    def plot_data(self, origin=vm.O3D):
        """
        Draws 2D representation of modules in grid
        """
        plot_datas = []
        module_frames, cp_frames = self.Frames(origin)
        for im, module_frame in module_frames.items():
            if self.modules_side is not None:
                side = self.modules_side[im]
            else:
                side = None
            plot_datas.extend(self.mech_module.plot_data(module_frame, side))

        for cp, cp_frame in cp_frames.items():
            plot_datas.append(cp.plot_data(cp_frame))
        return plot_datas

    def CADVolume(self, origin=vm.O3D):
        """
        Computes volumes of modules in grid
        """
        volumes = []

        module_frames, cp_frames = self.Frames(origin)
        for module_frame in module_frames.values():
            volumes.extend(self.mech_module.CADVolume(module_frame))

        for cp, cp_frame in cp_frames.items():
            volumes.extend(cp.CADVolume(cp_frame))
        return volumes

    def volume_model(self):
        model = vm.VolumeModel(self.CADVolume(), self.name)
        return model

    def volmdlr_volume_model(self):
        model = self.volume_model()
        return model

    def CADExport(self,
                  name='An_unnamed_grid',
                  python_path='python',
                  freecad_path='/usr/lib/freecad/lib/',
                  export_types=('stl', 'fcstd')):
        """
        Export Module CAD files (cell volumes)
        """
        volumes = self.CADVolume()

        model = vm.VolumeModel([('grid', volumes)])

        resp = model.FreeCADExport(name, python_path, freecad_path, export_types)

        return resp

    def Copy(self, deep=False):
        """
        Returns a copy of a grid oject

        :param deep: True to spread Copy to children objects
        :type deep: Boolean
        """
        if deep:
            module = self.mech_module.Copy(deep)
        else:
            module = self.mech_module

        grid = Grid(self.grid, module, self.basis,
                    self.cp_normal_vector, self.piles, self.modules_side,
                    self.cp_thickness, self.module_gap)

        return grid

    def Dict(self):
        dict_ = DessiaObject.base_dict(self)
        dict_.update(copy(self.__dict__))

        if self.mech_module is not None:
            dict_['mech_module'] = self.mech_module.Dict()
        else:
            dict_['mech_module'] = None

        if self.basis is not None:
            dict_['basis'] = self.basis.to_dict()
        else:
            dict_['basis'] = None

        dict_['cp_normal_vector'] = self.cp_normal_vector.to_dict()
        dict_['cp_direction_vector'] = self.cp_direction_vector.to_dict()
        dict_cp_piles = []
        for cp_pile in self.cp_piles:
            dict_cp_pile = []
            for cp in cp_pile:
                dict_cp_pile.append(cp.Dict())
            dict_cp_piles.append(dict_cp_pile)
        dict_['cp_piles'] = dict_cp_piles
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        mech_module = None
        if dict_['mech_module'] is not None:
            mech_module = MechModule.DictToObject(dict_['mech_module'])
        basis = None
        if dict_['basis'] is not None:
            basis = vm.Basis3D.dict_to_object(dict_['basis'])
        cooling_plate_normal_vector = vm.Vector3D.dict_to_object(dict_['cp_normal_vector'])
        grid = cls(grid=dict_['grid'], mech_module=mech_module, basis=basis,
                   cooling_plates_normal_vector=cooling_plate_normal_vector,
                   piles=dict_['piles'], modules_side=dict_['modules_side'],
                   cp_thickness=dict_['cp_thickness'], module_gap=dict_['module_gap'],
                   name=dict_['name'])
        return grid


class MechModule(DessiaObject):
    """
    Defines a mechanical view of a module

    :param cell: Cell object used in module
    :type cell: electrical.Cell
    :param cell_basis: Basis object that represents cells orientation in module
    :type cell_basis: vm.Basis3D
    :param grid: Tuple representing number of cells in 3D (in module coordinates)
    :type grid: (nx_module, ny_module, nz_module)
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.MechModule Base Schema",
        "required": ["cell", "cell_basis", "grid", "side_plates_thickness",
                     "end_plates_thickness", "bottom_plate_thickness"],
        "properties": {
            "cell" : {
                "type" : "object",
                "title" : "Cell",
                "order" : 1,
                "classes" : ["powerpack.electrical.Cell",
                             "powerpack.electrical.CellRC",
                             "powerpack.electrical.Cell2RC"],
                "editable" : True,
                "description" : "Cell"
                },
            "cell_basis" : {
                "type" : "object",
                "title" : "Cell Basis",
                "order" : 2,
                "classes" : ["volmdlr.core.Basis3D"],
                "editable" : True,
                "description" : "Orientation basis of cells"
                },
            "grid" : {
                "type" : "array",
                "title" : "Grid",
                "order" : 3,
                "items" : {
                    "type" : "number",
                    "editable" : True,
                    "step" : 1,
                    "minimum" : 1,
                    },
                "minItems": 3,
                "maxItems": 3,
                'examples' : [[1, 3, 2]],
                "editable" : True,
                "description" : "Grid"
                },
            "side_plates_thickness" : {
                "type" : "number",
                "title" : "Side Plates Thickness",
                "order" : 4,
                "editable" : True,
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "examples" : [0.002],
                "description" : "Thickness of side plates"
                },
            "end_plates_thickness" : {
                "type" : "number",
                "title" : "End Plates Thickness",
                "order" : 5,
                "editable" : True,
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "examples" : [0.006],
                "description" : "Thickness of end plates"
                },
            "bottom_plate_thickness" : {
                "type" : "number",
                "title" : "Bottom Plate Thickness",
                "order" : 6,
                "editable" : True,
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "examples" : [0.002],
                "description" : "Thickness of bottom plate"
                }
            }
        }

    def __init__(self, cell, cell_basis, grid, name=''):
        self.cell = cell
        self.cell_basis = cell_basis
        self.grid = grid
        self.cell_number = self.grid[0]*self.grid[1]*self.grid[2]
        self.side_plates_thickness = 0.002 # !!! Constant value
        self.end_plates_thickness = 0.006 # !!! Constant value
        self.bottom_plate_thickness = 0.002 # !!! Constant value

        self.terminals_layout = 0

        self._utd_size = False

        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_module):
        equal = (self.cell == other_module.cell
                 and self.cell_basis == other_module.cell_basis
                 and self.grid == other_module.grid
                 and self.side_plates_thickness == other_module.side_plates_thickness
                 and self.end_plates_thickness == other_module.end_plates_thickness
                 and self.bottom_plate_thickness == other_module.bottom_plate_thickness)
        # TODO terminals_layout ?
        return equal

    def __hash__(self):
        module_hash = hash(self.cell)  + sum(self.grid)\
                     + int(1000*self.side_plates_thickness) + int(4500*self.end_plates_thickness)\
                     + int(2000*self.bottom_plate_thickness)
        return module_hash

    def _display_angular(self):
        model = self.volmdlr_volume_model()
        displays = [{'angular_component': 'cad_viewer', 'data': model.babylon_data()},
                    # {'angular_component': 'plot_data', 'data': self.plot_data()},
                    {'angular_component': 'plot_data', 'data': self.iso_plot_data()}]
        return displays

    def _get_size(self):
        """
        Computes module size for a gient cell arragement
        """
        if not self._utd_size:
            cell_size = self.CellDimensions()
            plate_size = self.PlateDimensions()

            self._size = [self.grid[0]*abs(cell_size[0]) + abs(plate_size[0]),
                          self.grid[1]*abs(cell_size[1]) + abs(plate_size[1]),
                          self.grid[2]*abs(cell_size[2]) + abs(plate_size[2])]

            self._utd_size = True

        return self._size

    size = property(_get_size)

    def _get_volume(self):
        """
        Computes volume of the module
        """
        volume = self.size[0]*self.size[1]*self.size[2]
        return volume

    volume = property(_get_volume)

    def _get_mass(self):
        """
        Computes total mass of the module
        """
        mass = self.cell.mass*self.cell_number
        return mass

    mass = property(_get_mass)

    def SetTerminalsLayout(self, number):
        """
        0:     __________
            + |          |
            - |__________|

        1:     __________
            - |          |
            + |__________|

        2:     __________
            - |          | +
              |__________|

        """
        self.terminals_layout = number

    def TerminalsPositions(self, frame, side):
        """
        Computes positions of module + and - terminals
        """
        if not side:
            frame = vm.Frame3D(frame.origin, -frame.u, -frame.v, frame.w)
        h = 0.5*self.size[2]
        l1 = -0.45 * self.size[0]
        l2 = 0.45 * self.size[0]
        w1 = -0.4 * self.size[1]
        w2 = 0
        w3 = 0.4 * self.size[1]
        if self.terminals_layout == 0:
            minus_position = vm.Point3D((l1, w1, h))
            plus_position = vm.Point3D((l1, w3, h))
        elif self.terminals_layout == 1:
            minus_position = vm.Point3D((l1, w3, h))
            plus_position = vm.Point3D((l1, w1, h))
        elif self.terminals_layout == 2:
            minus_position = vm.Point3D((l1, w2, h))
            plus_position = vm.Point3D((l2, w2, h))
#        elif self.terminals_layout == 3:
#            minus_position = vm.Point3D((l2, w2, h))
#            plus_position = vm.Point3D((l1, w2, h))
#        elif self.terminals_layout == 4:
#            minus_position = vm.Point3D((l2, w1, h))
#            plus_position = vm.Point3D((l2, w3, h))
#        elif self.terminals_layout == 5:
#            minus_position = vm.Point3D((l2, w3, h))
#            plus_position = vm.Point3D((l2, w1, h))
        else:
            print('{} is not a valid terminals layout number'.format(self.terminals_layout))
            raise ValueError

        return (frame.OldCoordinates(minus_position),
                frame.OldCoordinates(plus_position))

    def ModuleDimensions(self, basis):
        """
        Computes module dimension in battery global basis
        """
        # Getting dimension of modules in (i, j, k)
        vect_size_xyz = vm.Point3D(self.size)
        size_ijk = basis.OldCoordinates(vect_size_xyz)

        return size_ijk

    def CellDimensions(self):
        """
        Computes cell dimensions in module basis
        """
        # Getting dimension of cells in (xm, ym, zm)
        cell_vect_size_uvw = vm.Point3D(self.cell.size)
        cell_size_xyz = self.cell_basis.OldCoordinates(cell_vect_size_uvw)

        return cell_size_xyz

    def PlateDimensions(self):
        """
        Computes plates dimensions in module basis
        """
        plates_vect_size_uvw = vm.Point3D((2*(self.end_plates_thickness\
                                              + self.side_plates_thickness),
                                           2*self.side_plates_thickness,
                                           0))
        plates_size_xyz = self.cell_basis.OldCoordinates(plates_vect_size_uvw)
        return plates_size_xyz

    def plot_data(self, frame=vm.OXYZ, detail=True):
        """
        Draws a 2D representation of the module (matplotlib)
        """
        # Module 2D projection
        plot_datas = []
        vect_size_ijk = self.ModuleDimensions(frame.Basis())
        block = primitives3D.Block(vm.Frame3D(frame.origin,
                                              vect_size_ijk[0]*vm.X3D,
                                              vect_size_ijk[1]*vm.Y3D,
                                              vect_size_ijk[2]*vm.Z3D))
        plot_datas.extend(block.plot_data(vm.X3D, vm.Y3D, color='blue', stroke_width=1))

        # Terminals display
        if detail:
            terminal_positions = self.TerminalsPositions(frame, detail)
            plot_datas.append(vm.Circle2D(vm.Point2D((terminal_positions[0][0], terminal_positions[0][1])), 0.005).plot_data(color = 'black',
                              fill = 'black'))
            plot_datas.append(vm.Circle2D(vm.Point2D((terminal_positions[1][0], terminal_positions[1][1])), 0.005).plot_data(color = 'red',
                              fill = 'red'))

        # Cell position and display
        cell_size = self.CellDimensions()
        plate_size = self.PlateDimensions()

        m_module = - 0.5*vm.Vector3D(self.size)

        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                for k in range(self.grid[2]):
                    xc_xyz = m_module[0]\
                            + 0.5*abs((2*i + 1)*cell_size[0])\
                            + 0.5*abs(plate_size[0])
                    yc_xyz = m_module[1]\
                            + 0.5*abs((2*j + 1)*cell_size[1])\
                            + 0.5*abs(plate_size[1])
                    zc_xyz = m_module[2]\
                            + 0.5*abs((2*k + 1)*cell_size[2])\
                            + 0.5*abs(plate_size[2])

                    m_cell_xyz = vm.Point3D((xc_xyz, yc_xyz, zc_xyz))
                    m_cell_ijk = frame.OldCoordinates(m_cell_xyz)

                    cell_frame = vm.Frame3D(vm.Point3D(m_cell_ijk),
                                            frame.Basis().OldCoordinates(self.cell_basis.u),
                                            frame.Basis().OldCoordinates(self.cell_basis.v),
                                            frame.Basis().OldCoordinates(self.cell_basis.w))
                    plot_datas.extend(self.cell.plot_data(cell_frame, stroke_width=0.5))

#        ax.axis('equal')
        return plot_datas

    def iso_plot_data(self, frame=None, detail=True):
        if frame == None:
            frame = vm.Frame3D(vm.Point3D((0, 0, 0)), vm.Vector3D((1, 0, 0)), vm.Vector3D((0, 1, 0)), vm.Vector3D((0, 0, 1)))
        wide = min(self.size)/2
        plot_datas = []
        plot_datas.extend(self.plot_data(frame, detail=detail))
        plot_datas.extend(self.plot_data(vm.Frame3D(frame.origin + vm.Point3D((0, self.size[1]/2 + self.size[2]/2 + wide, 0)), frame.u, frame.w, frame.v), detail = detail))
        plot_datas.extend(self.plot_data(vm.Frame3D(frame.origin + vm.Point3D((self.size[0]/2 + self.size[2]/2 + wide, 0, 0)), frame.w, frame.v, frame.u), detail = detail))
        return plot_datas

    def StructureCADVolumes(self, frame):
        """
        Computes volume of module structures for CAD Export
        """
        l = abs(npy.dot(self.cell_basis.u.vector, self.size))
        w = abs(npy.dot(self.cell_basis.v.vector, self.size))
        h = abs(npy.dot(self.cell_basis.w.vector, self.size))

        origin = frame.origin - frame.w*h/2

        # Side Plates
        # Sketch in X,Y of module
        p1 = -0.5*l*vm.X2D - 0.5*w*vm.Y2D
        p2 = p1 + l *vm.X2D
        p3 = p2 + 0.2*w*vm.Y2D
        p4 = p3 - self.side_plates_thickness * vm.X2D
        p8 = p1 + 0.2*w*vm.Y2D
        p7 = p8 + self.side_plates_thickness * vm.X2D
        p6 = p1 + self.side_plates_thickness * (vm.X2D+vm.Y2D)
        p5 = p2 + self.side_plates_thickness * (vm.Y2D-vm.X2D)

        ls1 = vm.LineSegment2D(p1, p2)
        ls2 = vm.LineSegment2D(p2, p3)
        ls3 = vm.LineSegment2D(p3, p4)
        ls4 = vm.LineSegment2D(p4, p5)
        ls5 = vm.LineSegment2D(p5, p6)
        ls6 = vm.LineSegment2D(p6, p7)
        ls7 = vm.LineSegment2D(p7, p8)
        ls8 = vm.LineSegment2D(p8, p1)

        c1 = vm.Contour2D([ls1, ls2, ls3, ls4, ls5, ls6, ls7, ls8])
        left_plate = primitives3D.ExtrudedProfile(origin,
                                                  frame.u, frame.v,
                                                  c1, [], h*frame.w,
                                                  color=[0.8, 0.8, 0.8], alpha=0.7,
                                                  name='left plate')

        p1 = -0.5*l*vm.X2D + 0.5*w*vm.Y2D
        p2 = p1 + l *vm.X2D
        p3 = p2 - 0.2*w*vm.Y2D
        p4 = p3 - self.side_plates_thickness * vm.X2D
        p8 = p1 - 0.2*w*vm.Y2D
        p7 = p8 + self.side_plates_thickness * vm.X2D
        p6 = p1 + self.side_plates_thickness * (vm.X2D-vm.Y2D)
        p5 = p2 - self.side_plates_thickness * (vm.Y2D+vm.X2D)

        ls1 = vm.LineSegment2D(p1, p2)
        ls2 = vm.LineSegment2D(p2, p3)
        ls3 = vm.LineSegment2D(p3, p4)
        ls4 = vm.LineSegment2D(p4, p5)
        ls5 = vm.LineSegment2D(p5, p6)
        ls6 = vm.LineSegment2D(p6, p7)
        ls7 = vm.LineSegment2D(p7, p8)
        ls8 = vm.LineSegment2D(p8, p1)

        c2 = vm.Contour2D([ls1, ls2, ls3, ls4, ls5, ls6, ls7, ls8])
        right_plate = primitives3D.ExtrudedProfile(origin,
                                                   frame.u, frame.v,
                                                   c2, [], h*frame.w,
                                                   color=[0.8, 0.8, 0.8], alpha=0.7,
                                                   name='right plate')

        # End plates
        # Sketch in X,Y of module
        p1 = -0.5*l*vm.X2D - 0.5*w*vm.Y2D + self.side_plates_thickness*(vm.X2D+vm.Y2D)
        p2 = p1 + self.end_plates_thickness*vm.X2D
        p3 = p2 + (w - 2 * self.side_plates_thickness)*vm.Y2D
        p4 = p3 - self.end_plates_thickness*vm.X2D
        ls1 = vm.LineSegment2D(p1, p2)
        ls2 = vm.LineSegment2D(p2, p3)
        ls3 = vm.LineSegment2D(p3, p4)
        ls4 = vm.LineSegment2D(p4, p1)

        c1 = vm.Contour2D([ls1, ls2, ls3, ls4])
        end_plate1 = primitives3D.ExtrudedProfile(origin,
                                                  frame.u, frame.v,
                                                  c1, [], h*frame.w,
                                                  color=[0.8, 0.8, 0.8], alpha=0.7,
                                                  name='end plate 1')

        p1 = (-0.5*w + self.side_plates_thickness)*vm.Y2D\
            + (0.5*l - self.end_plates_thickness - self.side_plates_thickness)*vm.X2D
        p2 = p1 + self.end_plates_thickness*vm.X2D
        p3 = p2 + (w - 2 * self.side_plates_thickness)*vm.Y2D
        p4 = p3 - self.end_plates_thickness*vm.X2D
        ls1 = vm.LineSegment2D(p1, p2)
        ls2 = vm.LineSegment2D(p2, p3)
        ls3 = vm.LineSegment2D(p3, p4)
        ls4 = vm.LineSegment2D(p4, p1)
        c2 = vm.Contour2D([ls1, ls2, ls3, ls4])
        end_plate2 = primitives3D.ExtrudedProfile(origin,
                                                  frame.u, frame.v,
                                                  c2, [], h*frame.w,
                                                  color=[0.8, 0.8, 0.8], alpha=0.7,
                                                  name='end plate 2')

        return [left_plate, right_plate, end_plate1, end_plate2]

    def CADVolume(self, frame):
        """
        Computes module volume (cells volumes) for CAD Export
        """
        volumes = []

        cell_size = self.CellDimensions()
        plate_size = self.PlateDimensions()

        cell_u = frame.Basis().OldCoordinates(self.cell_basis.u)
        cell_v = frame.Basis().OldCoordinates(self.cell_basis.v)
        cell_w = frame.Basis().OldCoordinates(self.cell_basis.w)

        m_module = -0.5*vm.Point3D(self.size)

        for i in range(self.grid[0]):
            for j in range(self.grid[1]):
                for k in range(self.grid[2]):
                    xc_xyz = m_module[0]\
                            + 0.5*abs((2*i + 1)*cell_size[0])\
                            + 0.5*abs(plate_size[0])
                    yc_xyz = m_module[1]\
                            + 0.5*abs((2*j + 1)*cell_size[1])\
                            + 0.5*abs(plate_size[1])
                    zc_xyz = m_module[2]\
                            + 0.5*abs((2*k + 1)*cell_size[2])\
                            + 0.5*abs(plate_size[2])

                    m_cell_xyz = vm.Point3D((xc_xyz, yc_xyz, zc_xyz))
                    m_cell_ijk = frame.OldCoordinates(m_cell_xyz)

                    cell_frame = vm.Frame3D(vm.Point3D(m_cell_ijk),
                                            cell_u,
                                            cell_v,
                                            cell_w)

                    volumes.extend(self.cell.CADVolume(cell_frame))

        module_frame = vm.Frame3D(frame.origin, cell_u, cell_v, cell_w)
        volumes.extend(self.StructureCADVolumes(module_frame))

        return volumes

    def volume_model(self):
        frame = vm.Frame3D(vm.Point3D((0, 0, 0)), vm.Vector3D((1, 0, 0)), vm.Vector3D((0, 1, 0)),
                           vm.Vector3D((0, 0, 1)))
        model = vm.VolumeModel(self.CADVolume(frame), self.name)
        return model

    def volmdlr_volume_model(self):
        model = self.volume_model()
        return model

    # def CADExport(self,
    #               name='An_unnamed_module',
    #               python_path='python',
    #               freecad_path='/usr/lib/freecad/lib/',
    #               export_types=('stl', 'fcstd')):
    #     """
    #     Export Module CAD files (cell volumes)
    #     """
    #     frame = vm.Frame3D(vm.Point3D((0, 0, 0)), vm.Vector3D((1, 0, 0)), vm.Vector3D((0, 1, 0)), vm.Vector3D((0, 0, 1)))
    #     volumes = self.CADVolume(frame)
    #
    #     model = vm.VolumeModel(primitives=volumes)
    #
    #     resp = model.FreeCADExport(name, python_path, freecad_path, export_types)
    #
    #     return resp

    def Copy(self, deep=False):
        """
        Returns a copy of a mech_module object

        :param deep: True to spread Copy to children objects
        :type deep: Boolean
        """
        if deep:
            cell = self.cell.Copy(deep)
        else:
            cell = self.cell

        module = MechModule(cell, self.cell_basis, self.grid)

        return module

    def Dict(self):
        dict_ = DessiaObject.base_dict(self)
        dict_.update(copy(self.__dict__))
        dict_.pop('_size', None)
        dict_.pop('_utd_size', None)

        dict_['cell'] = self.cell.to_dict()
        dict_['cell_basis'] = self.cell_basis.to_dict()
        dict_['size'] = [float(v) for v in self.size]
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        cell = electrical.Cell.dict_to_object(dict_['cell'])
        cell_basis = vm.Basis3D.dict_to_object(dict_['cell_basis'])
        return cls(cell=cell, cell_basis=cell_basis, grid=dict_['grid'], name=dict_['name'])


class CoolingPlate(DessiaObject):
    """
    Represents a cooling plate

    :param size:Tuple that represent cooling plate size in global frame, 0 -> thickness, 1 -> length, 2 -> height
    :type size: (x, y, z) m
    """
    def __init__(self, size, name=''):
        self.size = size
        self.exchange_area = self.size[1]*self.size[2]
        DessiaObject.__init__(self, name=name)

    def BasisDimensions(self, basis):
        """
        Computes cooling plate dimensions in given basis

        :param basis: Orientation of the cooling plate
        :type basis: vm.Basis3D

        :returns: vm.Vector3D representing size
        """
        vect_size_xyz = vm.Point3D(self.size)
        return basis.OldCoordinates(vect_size_xyz)

    def SocketsPositions(self, frame):
        """
        Computes positions of inlet and outlet sockets
        """
        socket1_position = vm.Point3D((0, -0.4*self.size[1], self.size[2]))
        socket2_position = vm.Point3D((0, 0.4*self.size[1], self.size[2]))
        return (frame.OldCoordinates(socket1_position),
                frame.OldCoordinates(socket2_position))

    def plot_data(self, frame=vm.O3D):
        """
        Displays a 2D representation of the cell (matplotlib)
        """

        vect_size_ijk = self.BasisDimensions(frame.Basis())
#        ax.add_patch(patches.Rectangle((frame.origin[0] - 0.5*vect_size_ijk[0],
#                                        frame.origin[1] - 0.5*vect_size_ijk[1]),
#                                       vect_size_ijk[0],
#                                       vect_size_ijk[1],
#                                       facecolor='red',
#                                       edgecolor='black',
#                                       linewidth=0.25))
        p1 = vm.Point2D((frame.origin[0] - 0.5*vect_size_ijk[0], frame.origin[1] - 0.5*vect_size_ijk[1]))
        p2 = p1.Translation(vm.Vector2D((vect_size_ijk[0], 0)))
        p3 = p2.Translation(vm.Vector2D((0, vect_size_ijk[1])))
        p4 = p3.Translation(vm.Vector2D((-vect_size_ijk[0], 0)))
        poly = vm.Polygon2D([p1, p2, p3, p4, p1])
        polY2D = vm.Contour2D([poly])
        return polY2D.plot_data(fill = 'url(#diagonal-stripe-1)')

    def CADVolume(self, frame=vm.O3D):
        """
        Computes plate CAD Volume
        """
        origin = frame.origin - frame.u*self.size[0]/2. + frame.w*self.size[2]/2.
        volume = primitives3D.ExtrudedProfile(origin,
                                              frame.v,
                                              frame.w,
                                              self.CADContour(),
                                              [],
                                              frame.u*self.size[0],
                                              name='Cooling_plate')
        return [volume]

    def CADContour(self):
        """
        Computes plate section for CAD Export
        """
        p0 = vm.Point2D((-self.size[1]/2., -self.size[2]/2.))
        p1 = vm.Point2D((self.size[1]/2., -self.size[2]/2.))
        p2 = vm.Point2D((self.size[1]/2., self.size[2]/2.))
        p3 = vm.Point2D((-self.size[1]/2., self.size[2]/2.))

        l0 = vm.LineSegment2D(p0, p1)
        l1 = vm.LineSegment2D(p1, p2)
        l2 = vm.LineSegment2D(p2, p3)
        l3 = vm.LineSegment2D(p3, p0)

        contour = vm.Contour2D([l0, l1, l2, l3])

        return contour

    def Dict(self):
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'size' : self.size})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        return cls(size=dict_['size'], name=dict_['name'])


class Rail(DessiaObject):
    """
    Defines a structure rail

    :param position: Center of extruded profile
    :type position: m
    :param length: Length of extrusion
    :type length: m
    :param width: Rail width (extruded profile side)
    :type width: m
    :param height: Rail height (extruded profile side)
    :type height: m
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.PackStructure Base Schema",
        "required": ["size", "rail_specs"],
        "properties": {
            "position" : {
                "type" : "number",
                "title" : "Position",
                "order" : 1,
                "editable" : True,
                "step" : 0.001,
                "examples" : [0.050],
                "unit" : "m",
                "description" : "Position of the rail"
                },
            "length" : {
                "type" : "number",
                "title" : "Length",
                "order" : 2,
                "editable" : True,
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "examples" : [0.200],
                "description" : "Length of the rail"
                },
            "width" : {
                "type" : "number",
                "title" : "Width",
                "order" : 3,
                "editable" : True,
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "examples" : [0.005],
                "description" : "Width of the rail"
                },
            "height" : {
                "type" : "number",
                "title" : "Height",
                "order" : 4,
                "editable" : True,
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "examples" : [0.010],
                "description" : "Height of the rail"
                },
            "thickness" : {
                "type" : "number",
                "title" : "Thickness",
                "order" : 5,
                "editable" : True,
                "examples" : [0],
                "step" : 0.001,
                "minimum" : 0,
                "unit" : "m",
                "description" : "Rail thickness"
                }
            }
        }
    def __init__(self, position, length, width, height, thickness=0, name=''):
        self.position = position
        self.length = length
        self.width = width
        self.height = height
        if thickness:
            self.thickness = thickness
        else:
            self.thickness = 0.5*width
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other_rail):
        if self.__class__ == other_rail.__class__:
            equal = (self.position == other_rail.position
                     and self.length == other_rail.length
                     and self.width == other_rail.width
                     and self.height == other_rail.height
                     and self.thickness == other_rail.thickness)
            return equal
        return False

    def __hash__(self):
        rail_hash = 1000*self.position + 750*self.length\
                    + (self.width) + (4563*self.height) + (75112*self.thickness)
        return int(rail_hash)

    def CADContour(self, radius=0):
        """
        Computes rail section for CAD Export
        """
        p0 = vm.Point2D((-self.width/2., -self.height/2.))
        p1 = vm.Point2D((self.width/2., -self.height/2.))
        p2 = vm.Point2D((self.width/2., -self.height/2. + self.thickness))
        p3 = vm.Point2D((self.thickness/2., -self.height/2. + self.thickness))
        p4 = vm.Point2D((self.thickness/2., self.height/2. -self.thickness))
        p5 = vm.Point2D((self.width/2., self.height/2. - self.thickness))
        p6 = vm.Point2D((self.width/2., self.height/2.))
        p7 = vm.Point2D((-self.width/2., self.height/2.))
        p8 = vm.Point2D((-self.width/2., self.height/2. - self.thickness))
        p9 = vm.Point2D((-self.thickness/2., self.height/2. - self.thickness))
        p10 = vm.Point2D((-self.thickness/2., -self.height/2. + self.thickness))
        p11 = vm.Point2D((-self.width/2., -self.height/2. + self.thickness))
        points = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11]

        if radius:
            radii = {i: radius for i in range(len(points))}
        else:
            radii = {}

        return primitives2D.ClosedRoundedLineSegments2D(points, radii, True)

    def Dict(self):
        dict_= DessiaObject.base_dict(self)
        dict_.update({'position' : float(self.position),
                      'length' : float(self.length),
                      'width' : float(self.width),
                      'height' : float(self.height),
                      'thickness' : float(self.thickness)})
        return dict_


class TransversalRail(Rail):
    """
    Defines a case rail
    """
    def __init__(self, position, length, width, height, thickness=0, name=''):
        Rail.__init__(self, position=position, length=length, width=width,
                      height=height, thickness=thickness, name=name)

    def plot_data(self):
        """
        Displays a 2D representation of the cell (matplotlib)
        """
        p1 = vm.Point2D((self.position - 0.5*self.width, -0.5*self.length))
        p2 = p1.Translation(vm.Vector2D((self.width, 0)))
        p3 = p2.Translation(vm.Vector2D((0, self.length)))
        p4 = p3.Translation(vm.Vector2D((-self.width, 0)))
        poly = vm.Polygon2D([p1, p2, p3, p4, p1])
        polY2D = vm.Contour2D([poly])
        return [polY2D.plot_data(fill='black')]

#    def Draw(self, ax):
#        """
#        Draws rail
#        """
#        ax.add_patch(patches.Rectangle((self.position - 0.5*self.width, -0.5*self.length),
#                                       self.width,
#                                       self.length,
#                                       fill=True,
#                                       color='grey'))

    def CADVolume(self, radius=0):
        """
        Computes rail volume for CAD Export
        """
        contour = self.CADContour(radius)
        origin = vm.Point3D((self.position, -0.5*self.length, 0))

        volume = primitives3D.ExtrudedProfile(origin + 0.5*self.height*vm.Z3D,
                                              vm.X3D, vm.Z3D,
                                              contour, [],
                                              self.length*vm.Y3D,
                                              name='Transversal rail')

        return volume

    def CADExport(self, name='An_unnamed_rail',
                  python_path='python',
                  freecad_path='/usr/lib/freecad/lib/',
                  export_types=('stl', 'fcstd')):
        """
        Export rail CAD file
        """
        volumes = self.CADVolume()

        model = vm.VolumeModel([('rail', volumes)])

        resp = model.FreeCADExport(python_path, name, freecad_path, export_types)

        return resp

    def Copy(self):
        """
        Returns a copy of the rail object
        """
        return TransversalRail(position=self.position, length=self.length,
                               width=self.width, height=self.height,
                               thickness=self.thickness, name=self.name)

    @classmethod
    def DictToObject(cls, dict_):
        return cls(position=dict_['position'], length=dict_['length'],
                   width=dict_['width'], height=dict_['height'],
                   thickness=dict_['thickness'], name=dict_['name'])


class LongitudinalRail(Rail):
    """
    Defines a case rail
    """
    def __init__(self, position, length, width, height, thickness=0, name=''):
        Rail.__init__(self, position=position, length=length, width=width,
                      height=height, thickness=thickness, name=name)

    def plot_data(self):
        """
        Displays a 2D representation of the cell (matplotlib)
        """
        p1 = vm.Point2D((0, self.position - 0.5*self.width))
        p2 = p1.Translation(vm.Vector2D((self.width, 0)))
        p3 = p2.Translation(vm.Vector2D((0, self.length)))
        p4 = p3.Translation(vm.Vector2D((-self.width, 0)))
        poly = vm.Polygon2D([p1, p2, p3, p4, p1])
        polY2D = vm.Contour2D([poly])
        return [polY2D.plot_data(fill='black')]

#    def Draw(self, ax):
#        """
#        Draws rail
#        """
#        ax.add_patch(patches.Rectangle((0, self.position - 0.5*self.width),
#                                       self.length,
#                                       self.width,
#                                       fill=True,
#                                       color='grey'))

    def CADVolume(self, radius=0):
        """
        Computes rail volume for CAD Export
        """

        contour = self.CADContour(radius)
        origin = vm.Point3D((0, self.position, 0))

        volume = primitives3D.ExtrudedProfile(origin + 0.5*self.height*vm.Z3D,
                                              vm.Y3D, vm.Z3D,
                                              contour, [],
                                              vm.X3D*self.length,
                                              name='Longitudinal rail')

        return volume

    def CADExport(self, name='An_unnamed_rail',
                  python_path='python',
                  freecad_path='/usr/lib/freecad/lib/',
                  export_types=('stl', 'fcstd')):
        """
        Export rail CAD file
        """
        volumes = self.CADVolume()

        model = vm.VolumeModel([('rail', volumes)])

        resp = model.FreeCADExport(python_path, name, freecad_path, export_types)

        return resp

    def Copy(self):
        """
        Returns a copy of the rail object
        """
        return LongitudinalRail(position=self.position, length=self.length,
                                width=self.width, height=self.height,
                                thickness=self.thickness, name=self.name)
    @classmethod
    def DictToObject(cls, dict_):
        return cls(position=dict_['position'], length=dict_['length'],
                   width=dict_['width'], height=dict_['height'],
                   thickness=dict_['thickness'], name=dict_['name'])

class PowerPackMechanicalSimulator(DessiaObject):
    """
    Defines a powerpack mechanical simulator to store mechanical design

    :param powerpack_thermal_simulator: Thermal powerpack simulation
    :type powerpack_thermal_simulator: powerpack.thermal.PowerPackThermalSimulator
    :param mech_battery: mechanical battery
    :type mech_battery: powerpack.mechanical.MechBattery
    """
    _standalone_in_db = True
    _jsonschema = {
        "definitions": {},
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "title": "powerpack.mechanical.PowerPackMechanicalSimulator Base Schema",
        "required": ['powerpack_thermal_simulator', 'mech_battery'],
        "properties": {
            'powerpack_thermal_simulator': {
                "type" : "object",
                "title" : "Powerpack Thermal Simulators",
                "classes" : ["powerpack.thermal.PowerPackThermalSimulator"],
                "description" : "Powerpack thermal simulation",
                "editable" : True,
                "order" : 1
                },
            'mech_battery': {
                "type" : "object",
                "title" : "Mech Battery",
                "classes" : ["powerpack.mechanical.MechBattery"],
                "description" : "Mechanical battery",
                "editable" : True,
                "order" : 2
                },
            }
        }

    def __init__(self, powerpack_thermal_simulator, mech_battery, name=''):
        self.powerpack_thermal_simulator = powerpack_thermal_simulator
        self.mech_battery = mech_battery
        DessiaObject.__init__(self, name=name)

    def __eq__(self, other):
        equal = self.powerpack_thermal_simulator == other.powerpack_thermal_simulator
        equal = equal and (self.mech_battery == other.mech_battery)
        return equal

    def __hash__(self):
        li_hash = hash(self.powerpack_thermal_simulator)
        li_hash += hash(self.mech_battery)
        return li_hash

    def _display_angular(self):
        displays = self.mech_battery._display_angular()
        return displays

    def volmdlr_volume_model(self):
        model = self.mech_battery.volume_model()
        return model

    def Dict(self):
        """
        Export a dictionary
        """
        dict_ = DessiaObject.base_dict(self)
        dict_.update({'powerpack_thermal_simulator' : self.powerpack_thermal_simulator.Dict(),
                      'mech_battery' : self.mech_battery.Dict()})
        return dict_

    @classmethod
    def DictToObject(cls, dict_):
        """
        Generate an PowerPackMechanicalSimulator object

        :param dict_: PowerPackMechanicalSimulator dictionnary generate with the Dict method
        """
        therm_simulator = thermal.PowerPackThermalSimulator.DictToObject(dict_['powerpack_thermal_simulator'])
        mech_battery = MechBattery.DictToObject(dict_['mech_battery'])

        mech_simulator = cls(powerpack_thermal_simulator=therm_simulator,
                             mech_battery=mech_battery,
                             name=dict_['name'])
        return mech_simulator

BASES = [vm.Basis3D(vm.X3D, vm.Y3D, vm.Z3D),
         vm.Basis3D(vm.Y3D, -vm.X3D, vm.Z3D),
         vm.Basis3D(-vm.Z3D, -vm.X3D, vm.Y3D),
         vm.Basis3D(-vm.Z3D, vm.Y3D, vm.X3D),
         vm.Basis3D(vm.Y3D, vm.Z3D, vm.X3D),
         vm.Basis3D(-vm.X3D, vm.Z3D, vm.Y3D)]

EMPTY_GRID = Grid((0, 0, 0), None, None, vm.X3D, [[]])

def GenerateMechModules(elec_battery, two_cell_cooling=True):
    """
    Generate a mechanical module for each orientation of its cells

    :param elec_battery: ElecBattery object
    :type elec_battery: ElecBattery()
    :param two_cell_cooling: True : Check if there is at least one direction in which
                             there is a maximum of 2 cells so that cooling is possible
                             False : Let "internal cell" possible
    :type two_cell_cooling: Boolean

    :returns: **mech_modules** List of MechModule objects
    """
    # TODO : See for module and cell selections in lists
    cells = [elec_battery.mms.module.cms.cell]

    n_cells_per_module = elec_battery.mms.module.number_cells

    mech_modules = []
    for cell in cells:
        grids = number3factor(n_cells_per_module, False)

        # Check for possibility to connect cooling plates
        if two_cell_cooling:
            ok_grids = [grid for grid in grids if any([i <= 2 for i in grid])]
        else:
            ok_grids = grids
        for grid in ok_grids:
            for cell_basis in BASES:
                mech_module = MechModule(cell=cell, cell_basis=cell_basis, grid=grid,
                                         name='Automatically generated module')
                mech_modules.append(mech_module)
    return mech_modules

def CaseCoords(case_index, n_long_rails):
    """
    Computes case coordinates from its index

    :param case_index: Index of case
    :type case_index: int

    :returns: **(i, j)** Tuple that represents case coordinates (line, column)
    """
    i = case_index % (n_long_rails+1)
    j = case_index // (n_long_rails+1)
    return i, j

def GetSymmetricCase(case_index, n_long_rails):
    """
    Computes symmetric case index from specified case index

    :param case_index: Origin case_index
    :type case_index: int

    :returns: **sym_case_index** int that represent symmetric case index
    """
    i, j = CaseCoords(case_index, n_long_rails)
    sym_case_index = (n_long_rails + 1)*(j+1) - (i+1)
    if sym_case_index == case_index:
        return None
    return sym_case_index
