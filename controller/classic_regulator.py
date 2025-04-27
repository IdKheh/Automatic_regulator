import math
import plotly.express as px
import pandas as pd

A = 1.5 # przekroj [m^2]
beta = 0.035 # stala [m^(5/2)/s]
Tp = 0.1 # okres probkowania [s]
V_0 = 0 # objętość poczatkowa [m^3]
t_sym = 1800 # czas symulacji [s]
Q_d1 = 0.01 # doplyw wody [m^3/s]
Q_d2 = [0] # doplyw wody [m^3/s]

Q_d2_min, Q_d2_max = 0, 0.04 #doplyw wody min, max [m^3/s]

Q_o = [0.00] #odplyw wody [m^3/s]
Q_o_min = 0 #odplyw wody min [m^3/s]
Q_o_max = 0.00005 #odplyw wody max [m^3/s]

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
c_zadane = 0.1 # [%]
V_min = 0
V_max = 5

kp = 0.5 # nastawa regulatora
Ti = 5 # czas zdwojenia [s], [2.5 - 5.0]
t = [0] #czas symulacji
n=int(round(t_sym/Tp,0))

def classic():
    for i in range(n):
        t.append(Tp*i)
        e.append(c_zadane - c[-1])
        upi.append(kp*(e[-1] + (Tp/Ti)*sum(e)))
        u.append(max(min(upi[-1], u_max), u_min))
        
        Q_d2.append((Q_d2_max - Q_d2_min) / (u_max - u_min) * (u[-1] - u_min) + Q_d2_min)
        Q_o.append(max(min(beta*math.sqrt(V[-1]), Q_o_max), Q_o_min))
        c_d2.append((c_d2_max - c_d2_min) / (u_max - u_min) * (u[-1] - u_min) + c_d2_min)
        
        V_new = Tp * (Q_d1+Q_d2[-1]-Q_o[-1])+V[-1]
        if V[-1]!=0 :
            c_new = (1 / V[-1]) * (Q_d1 * (c_d1 - c[-1]) + Q_d2[-1] * (c_d2[-1] - c[-1])) * Tp + c[-1]
        else : c_new = 0
        
        V.append(max(min(V_new, V_max), V_min))
        c.append(max(min(c_new, c_max), c_min))

    # wykres poziomu wody w zbiorniku
    df = pd.DataFrame(dict(
        Time=t,
        Height=V
    ))
    fig = px.line(df, x="Time", y="Height",
                title="Przebieg zmian poziomów wody w zbiorniku",
                labels={"Time": "Okres próbkowania (s)", "Height": "Wysokość (m)","variable": ""})
    fig.write_image("pi_water_height_plot1.png")


    # wykres odpływu od czasu
    df = pd.DataFrame(dict(
        Time=t,
        Odplyw=Q_o,
        Doplyw1=[Q_d1] * (n+1),
        Doplyw2=Q_d2
    ))

    fig = px.line(df, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw"],
                title="Przebieg zmian dopływu i odpływu wody w czasie",
                labels={"Time": "Czas [s]", "value": "Przepływ [m³/s]", "variable": "Rodzaj przepływu"})


    fig.write_image("pi_doplyw_odplyw1.png")

    # wykres stężenia od czasu
    df = pd.DataFrame(dict(
        Time=t,
        Odplyw=[val * 100 for val in c],
        Doplyw1=[c_d1 * 100] * (n+1),
        Doplyw2=[val * 100 for val in c_d2],
        Zadane=[c_zadane * 100] * (n+1)
    ))

    fig = px.line(df, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw","Zadane"],
                title="Przebieg zmian stężenia w czasie",
                labels={"Time": "Czas [s]", "value": "Stężenie substancji [%]", "variable": "Rodzaj przepływu"})


    fig.write_image("pi_stezenie.png")
