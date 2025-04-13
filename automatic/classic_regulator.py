import math
import plotly.express as px
import pandas as pd

A = 1.5 # przekroj [m^2]
beta = 0.035 # stala [m^(5/2)/s]
Tp = 0.1 # okres probkowania [s]
V_0 = 0 # objętość poczatkowa [m^3]
t_sym = 1800 # czas symulacji [s]
Q_d1 = [0.0] # doplyw wody [m^3/s]
Q_d2 = [0.0] # doplyw wody [m^3/s]
Q_d_min = 0 #doplyw wody min [m^3/s]
Q_d_max = 0.05 #doplyw wody max [m^3/s]
Q_o = [0.0] #odplyw wody [m^3/s]
Q_o_min = 0 #odplyw wody min [m^3/s]
Q_o_max = 0.1 #odplyw wody max [m^3/s]

u_min=0 #wartość prądu z regulatora min [V]
u_max = 10 #wartość prądu z regulatora max [V]
u = [0] #wartość prądu z regulatora zaworu [V]
upi= []
V = [V_0]
e=[0] #uchyb [m]
V_zadane = 3 # V zadane [m]
V_min = 0
V_max = 5

kp = 0.5 # nastawa regulatora
Ti = 2.5 # czas zdwojenia [s], [2.5 - 5.0]
t = [0] #czas symulacji
n=int(round(t_sym/Tp,0))

for i in range(n):
    t.append(Tp*i)
    e.append(V_zadane-V[-1])
    upi.append(kp*(e[-1]+(Tp/Ti)*sum(e)))
    u.append(max(min(upi[-1], u_max), u_min))
    Q_d1.append((Q_d_max - Q_d_min) / (u_max - u_min) * (upi[-1] - u_min) + Q_d_min)
    Q_d1.append((Q_d_max - Q_d_min) / (u_max - u_min) * (upi[-1] - u_min) + Q_d_min)
    Q_o.append(max(min(beta*math.sqrt(V[-1]), Q_o_max), Q_o_min))

    #costam = (Q_d_max-Q_d_min)/(u_max-u_min) *u[-1]+Q_d[-1]
    #Q_d.append(max(min(Q_d[0]*u[-1], Q_d_max), Q_d_min))

    V_new = Tp/A*(Q_d[-1]-Q_o[-1])+V[-1]
    V.append(max(min(V_new, V_max), V_min))

#print((Q_d[0]/beta)**2) # sprawdzenie stanu końcowego

# wykres poziomu wody w zbiorniku
df = pd.DataFrame(dict(
    Time=t,
    Height=V
))
fig = px.line(df, x="Time", y="Height",
              title="Przebieg zmian poziomów wody w zbiorniku",
              labels={"Time": "Okres próbkowania (s)", "Height": "Wysokość (m)"})
fig.write_image("pi_water_height_plot.png")


# wykres odpływu od czasu
df = pd.DataFrame(dict(
    Time=t,
    Odplyw=Q_o,
    Doplyw1=Q_d1,
    Doplyw2=Q_d2
))

fig = px.line(df, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw"],
              title="Przebieg zmian dopływu i odpływu wody w czasie",
              labels={"Time": "Czas [s]", "value": "Przepływ [m³/s]", "variable": "Rodzaj przepływu"})

fig.write_image("pi_doplyw_odplyw.png")
