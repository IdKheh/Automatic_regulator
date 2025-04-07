import math
import plotly.express as px
import pandas as pd

A = 1.5 # przekroj [m^2]
beta = 0.035 # stala [m^(5/2)/s]
Tp = 0.1 # okres probkowania [s]
h_0 = 0 # wysokosc poczatkowa [m]
t_sym = 1800 # czas symulacji [s]
Q_d = [0.0] # doplyw wody [m^3/s]
Q_d_min = 0 #doplyw wody min [m^3/s]
Q_d_max = 0.05 #doplyw wody max [m^3/s]
u_min=0 #wartość prądu z regulatora min [V]
u_max = 10 #wartość prądu z regulatora max [V]
u = [0] #wartość prądu z regulatora zaworu [V]
h_zadane = 1 # h zadane [m]
h_min = 0
h_max = 5
kp = 0.5 # nastawa regulatora
Ti = 2.5 # czas zdwojenia [s], [2.5 - 5.0]
h = []
e=[0] #uchyb [m]
upi= []
t = [0] #czas symulacji
n=int(round(t_sym/Tp,0))
h.append(h_0)
for i in range(n):
    t.append(Tp*i)
    e.append(h_zadane-h[-1])
    upi.append(kp*(e[-1]+(Tp/Ti)*sum(e)))
    u.append(max(min(upi[-1], u_max), u_min))
    Q_d.append((Q_d_max - Q_d_min) / (u_max - u_min) * (upi[-1] - u_min) + Q_d_min)

    #costam = (Q_d_max-Q_d_min)/(u_max-u_min) *u[-1]+Q_d[-1]
    #Q_d.append(max(min(Q_d[0]*u[-1], Q_d_max), Q_d_min))

    h_new = Tp/A*(Q_d[-1]-beta*math.sqrt(h[-1]))+h[-1]
    h.append(max(min(h_new, h_max), h_min))

#print(h)
#print(u)
#print(Q_d)
print((Q_d[0]/beta)**2) # sprawdzenie stanu końcowego
#dosztukuj wykres z Q_odpływu
df = pd.DataFrame(dict(
    Time=t,
    Height=h
))

fig = px.line(df, x="Time", y="Height",
              title="Przebieg zmian poziomów wody w zbiorniku",
              labels={"Time": "Okres próbkowania (s)", "Height": "Wysokość (m)"})

fig.write_image("water_height_plot.png")

df = pd.DataFrame(dict(
    Time=t,
    Height=u
))
fig = px.line(df, x="Time", y="Height",
              title="regulator",
              labels={"Time": "Okres próbkowania (s)", "Height": "regulator (V)"})

fig.write_image("plot2.png")

df = pd.DataFrame(dict(
    Time=t,
    Height=Q_d
))
fig = px.line(df, x="Time", y="Height",
              title="Regulacja poziomu wody w zbiorniku",
              labels={"Time": "Okres próbkowania (s)", "Height": "Wysokość (m)"})

fig.write_image("plot3.png")

df = pd.DataFrame(dict(
    Time=t,
    Height=e
))
fig = px.line(df, x="Time", y="Height",
              title="uchyb",
              labels={"Time": "Okres próbkowania (s)", "Height": "Uchyb (m)"})

fig.write_image("plot4.png")