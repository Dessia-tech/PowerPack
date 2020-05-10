#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 15:08:32 2018

@author: jezequel
"""
import time
from scipy import integrate
from powerpack import electrical, power_profile
import numpy as npy
import matplotlib.pyplot as plt
from dessia_api_client import Client

c=Client()
c.api_url='https://api.platform.dessia.tech'

# =============================================================================
# Electrical specs
# =============================================================================

runfile('elec_battery_complex.py')

# =============================================================================
# Export API DessIA
# =============================================================================

r=c.create_object_from_python_object(pf1)

# =============================================================================
# Import API DessIA
# =============================================================================

pf2=c.GetObject('powerpack.electrical.PowerPackElectricSimulator', 
              '5ced5cf15b6e13291c2566fb')
pf2.battery_results[0].PlotResults()
