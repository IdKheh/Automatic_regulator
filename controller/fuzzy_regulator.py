import math
import plotly.express as px
import pandas as pd
from simpful import *

A = 1.5 # przekroj [m^2]
beta = 0.035 # stala [m^(5/2)/s]
Tp = 0.1 # okres probkowania [s]
V_0 = 0 # objętość poczatkowa [m^3]
t_sym = 1800 # czas symulacji [s]

Q_d1 = 0.01 # doplyw wody [m^3/s]
Q_d2 = [0] # doplyw wody [m^3/s]
Q_d2_min, Q_d2_max = 0, 0.06 #doplyw wody min, max [m^3/s]
Q_o = [0.00] #odplyw wody [m^3/s]
Q_o_min, Q_o_max = 0, 0.1  #odplyw wody min, max [m^3/s]

c_d1 = 0.0 # stężenie [%] [0.0 - 1.0]
c_d2 = [0] # stężenie [%] [0.0 - 1.0]
c_d2_min, c_d2_max = 0.0, 0.98
c_min, c_max = min(c_d1,c_d2_min), max(c_d1,c_d2_max)

u_min, u_max = 0, 10  #wartość prądu z regulatora min, max [V]
u = [] #wartość prądu z regulatora zaworu [V]
u_half = int((u_max-u_min)/2) # punkt pośrodku U_min i U_max [V]
upi= []
V = [V_0]
e = [] #uchyb [%]
c = [0] #stezenie
c_zadane = 0.4 # [%]
V_min, V_max = 0, 5
t = [0] #czas symulacji

kp = 0.5 # nastawa regulatora
Ti = 5 # czas zdwojenia [s], [2.5 - 5.0]
n=int(round(t_sym/Tp,0))

# Create fuzzy system
FS = FuzzySystem()

# Definicja funkcji uchybu [%/100]
FS.add_linguistic_variable("E",
    LinguisticVariable([
        FuzzySet(function=Triangular_MF(-100, -50, -2), term="NEG"),
        FuzzySet(function=Triangular_MF(-2, 0, 2), term="ZERO"),
        FuzzySet(function=Triangular_MF( 2, 50, 100), term="POS")
    ], universe_of_discourse=[-100, 100])
)


# Definicja funkcji natezenia [V]
FS.add_linguistic_variable("U",
    LinguisticVariable([
        FuzzySet(function=Triangular_MF(u_min, u_min, int(u_half/2)), term="LOW"),
        FuzzySet(function=Triangular_MF(int(u_half/2), u_half, 3*int(u_half/2)), term="MEDIUM"),
        FuzzySet(function=Triangular_MF(3*int(u_half/2), u_max,  u_max), term="HIGH")
    ], universe_of_discourse=[u_min, u_max])
)

# reguły
rules = [
    "IF (E IS NEG) THEN (U IS HIGH)",
    "IF (E IS ZERO) THEN (U IS MEDIUM)",
    "IF (E IS POS) THEN (U IS LOW)",
]
FS.add_rules(rules)


def fuzzy():
    for i in range(n):
        t.append(Tp * i)
        e.append(c_zadane - c[-1])
        
        FS.set_variable("E", e[-1]*100)
        u.append(max(min(FS.inference()["U"], u_max), u_min))

        Q_d2.append((Q_d2_max - Q_d2_min) / (u_max - u_min) * (u[-1] - u_min) + Q_d2_min)
        Q_o.append(max(min(beta * math.sqrt(V[-1]), Q_o_max), Q_o_min))
        c_d2.append((c_d2_max - c_d2_min) / (u_max - u_min) * (u[-1] - u_min) + c_d2_min)

        V_new = Tp * (Q_d1 + Q_d2[-1] - Q_o[-1]) + V[-1]
        if V[-1] != 0:
            c_new = (1 / V[-1]) * (Q_d1 * (c_d1 - c[-1]) + Q_d2[-1] * (c_d2[-1] - c[-1])) * Tp + c[-1]
        else:
            c_new = 0
        
        V.append(max(min(V_new, V_max), V_min))
        c.append(max(min(c_new, c_max), c_min))

    df1 = pd.DataFrame(dict(Time=t, Height=V))
    fig1 = px.line(df1, x="Time", y="Height", title="Poziom wody w zbiorniku", labels={"Time": "Czas [s]", "Height": "Wysokość [m]"})
    fig1.write_image("fuzzy_pi_stezenie.png")

    df2 = pd.DataFrame(dict(Time=t, Odplyw=Q_o, Doplyw1=[Q_d1] * len(t), Doplyw2=Q_d2))
    fig2 = px.line(df2, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw"], title="Dopływ i odpływ wody", labels={"Time": "Czas [s]", "value": "Przepływ [m³/s]", "variable": "Rodzaj"})
    fig2.write_image("fuzzy_pi_doplyw.png")

    df3 = pd.DataFrame(dict(
        Time=t,
        Odplyw=[val * 100 for val in c],
        Doplyw1=[c_d1 * 100] * len(t),
        Doplyw2=[val * 100 for val in c_d2],
        Zadane=[c_zadane * 100] * len(t)
    ))
    fig3 = px.line(df3, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw", "Zadane"], title="Stężenie w czasie", labels={"Time": "Czas [s]", "value": "Stężenie [%]", "variable": "Typ"})
    fig3.write_image("fuzzy_pi_objetosc.png")
