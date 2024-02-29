import numpy as np
import sys
import shutil
import os
import math
import pandas as pd
import numpy as np

####################################################################
# File detection function, folder detection function, unit converter
####################################################################

def cf(from_unit, to_unit):
    """Returns the conversion factor from one unit to another."""
    units_conversion_dict = {
        # Units of length. Meter "m" is the base unit.
        "mm": 1e3,
        "cm": 1e2,
        "dm": 1e1,
        "m": 1,
        "dam": 1e-1,
        "hm": 1e-2,
        "km": 1e-3,
        "ft": 1 / 0.3048,
        "in": 1 / 0.0254,
        "mi": 1 / 1609.344,
        "nmi": 1 / 1852,
        "yd": 1 / 0.9144,
        # Units of velocity. Meter per second "m/s" is the base unit.
        "m/s": 1,
        "km/h": 3.6,
        "knot": 1.9438444924406047,
        "mph": 2.2369362920544023,
        "ft/s": 1 / 0.3048,
        # Units of acceleration. Meter per square second "m/s^2" is the base unit.
        "m/s^2": 1,
        "grav": 1 / 9.80665,
        "ft/s^2": 1 / 3.2808399,
        # Units of pressure. Pascal "Pa" is the base unit.
        "Pa": 1,
        "hPa": 1e-2,
        "kPa": 1e-3,
        "MPa": 1e-6,
        "bar": 1e-5,
        "atm": 1.01325e-5,
        "mmHg": 1 / 133.322,
        "inHg": 1 / 3386.389,
        # Units of time. Seconds "s" is the base unit.
        "s": 1,
        "min": 1 / 60,
        "h": 1 / 3600,
        "d": 1 / 86400,
        # Units of mass. Kilogram "kg" is the base unit.
        "mg": 1e-6,
        "g": 1e-3,
        "kg": 1,
        "lb": 2.20462,
        # Units of angle. Radian "rad" is the base unit.
        "rad": 1,
        "deg": 1 / 180 * np.pi,
        "grad": 1 / 200 * np.pi,
    }
    try:
        incoming_factor = units_conversion_dict[to_unit]
    except KeyError:
        raise ValueError(f"Unit {to_unit} is not supported.")
    try:
        outgoing_factor = units_conversion_dict[from_unit]
    except KeyError:
        raise ValueError(f"Unit {from_unit} is not supported.")

    return incoming_factor / outgoing_factor

def folderexist(file1):
    if os.path.exists(file1):
        ans = input("The file you are creating already exists you may overwrite"
                    "data if you proceed.\nDo you wish to proceed? ") 
        ans = ans.lower()
        ans = ans.capitalize()
        if ans == "Yes":
            shutil.rmtree(file1)
            return True
        else:
            return False
    else:
        return True
    

def fileexist(file1):
    if os.path.exists(file1):
        sys.stdout.write("The file you are creating already exists you may overwrite"
                    "data if you proceed.\nDo you wish to proceed? ")
        ans = input("")
        ans = ans.lower()
        ans = ans.capitalize()
        if ans == "Yes":
            os.remove(file1)
            return True
        else:
            return False
    else:
        return True
    
def heading_finder(wind_x, wind_y, type, direction = None):
    def ema(data):
        frame = pd.DataFrame([x[1] for x in data], columns = ["A"])
        ema = frame.ewm(adjust=True, com=23).mean()
        ema.values.tolist()
        return ema
    def ground(data):
        data[0][1]

        return data
    
    if type == "ema":
        wind_x = ema(wind_x)
        wind_y = ema(wind_y)

    elif type == "ground":
        wind_x = ground(wind_x)
        wind_y = ground(wind_y)

    elif type == "default":
        return direction
    
    else:
        raise ValueError("type parameter must be either ema or ground")

    
    theta = math.degrees(math.atan2(np.mean(wind_y),np.mean(wind_x)))
    heading = 90 + theta


    return heading

def damp_coe(flight, motor, rocket):
    # Damping Ratio Model
    v ={
        "mass": (motor.total_mass + rocket.mass), # mass by time
        "mdot": (motor.total_mass + rocket.mass).derivative_function(), # derivative of above
        "nose_to_nozzle": rocket.nozzle_position, # distance from nozzle to tip
        "cg":rocket.evaluate_center_of_mass(), # distance from tip to cg
        "density": flight.density, # density of air
        "velocity": flight.speed, # velocity of rocket 
        "area": rocket.area, # reference area
        "d cp to component": None, 
        "normal coe component": None,
        "normal_coe": flight.aerodynamic_lift/(flight.dynamic_pressure * rocket.area), # normal force coeficient
        "cp":rocket.evaluate_center_of_pressure() - rocket.evaluate_center_of_mass(), # d that cg is in front of cp
        "radius": rocket.radius
    }
    
    #  Propulsive Damping Moment Coefficient
    C2R = v["mdot"] * (v["nose_to_nozzle"] - v["cg"])**2

    #  Aerodynamic Damping Moment Coefficient
    C2A = ((v["density"] * v["velocity"] * v["area"])/2) *  v["normal_coe"]* (v["cg"] - v["cp"])**2  
                                                                # ^this is where the sum would go currently it is stupid version
    # Damping Moment Coe                                   
    C2 = C2R + C2A

    # Longitudinal Moment of Inertia
    L2 = 0.5 * v["mass"] * (v["radius"]**2)

    # Corrective Moment Coefficient
    CL = (v["density"]/2) * (v["velocity"]**2) * v["area"] * (v["normal_coe"] * (v["cg"] - v["cp"]))
 
    # Damping Ratio
    zeta = pow(pow(C2/pow(CL * L2, 0.5), 2), 0.5) # this is negative so I did absolute value btw I relize there is abs function 
                                                    # but it doesnt work with this FUNCTION class

    return zeta

def log_dec(aoa):

    x1 = None
    x2 = None

    gamma = math.log(x1/x2)

    zeta = gamma/(math.sqrt(4*pow((math.pi), 2) + pow(gamma, 2)))

    return zeta

    
    