import math
import plotly.express as px
import pandas as pd
import simpful as sf

A = 1.5 # przekroj [m^2]
beta = 0.035 # stala [m^(5/2)/s]
Tp = 0.1 # okres probkowania [s]
V_0 = 0 # objętość poczatkowa [m^3]
t_sym = 1800 # czas symulacji [s]
Q_d1 = 0.01 # doplyw wody [m^3/s]
Q_d2 = [0] # doplyw wody [m^3/s]

Q_d2_min, Q_d2_max = 0, 0.06 #doplyw wody min, max [m^3/s]

Q_o = [0.00] #odplyw wody [m^3/s]
Q_o_min = 0 #odplyw wody min [m^3/s]
Q_o_max = 0.1 #odplyw wody max [m^3/s]

c_d1 = 0.0 # stężenie [%] [0.0 - 1.0]
c_d2 = [0] # stężenie [%] [0.0 - 1.0]
c_d2_min, c_d2_max = 0.0, 0.98
c_min, c_max = min(c_d1,c_d2_min), max(c_d1,c_d2_max)

u_min=0 #wartość prądu z regulatora min [V]
u_max = 10 #wartość prądu z regulatora max [V]
u = [] #wartość prądu z regulatora zaworu [V]
upi= []


V = [V_0]
e = [] #uchyb [%]
c = [0] #stezenie
c_zadane = 0.4 # [%]
V_min = 0
V_max = 5

kp = 0.5 # nastawa regulatora
Ti = 5 # czas zdwojenia [s], [2.5 - 5.0]
t = [0] #czas symulacji
n=int(round(t_sym/Tp,0))

def fuzzy():
    print(":)")