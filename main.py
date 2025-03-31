import math
import plotly.express as px
import pandas as pd

A = 1.5 # przekroj [m^2]
beta = 0.035 # stala [m^(5/2)/s]
Tp = 0.1 # okres probkowania [s]
h_0 = 0 # wysokosc poczatkowa [m]
Q_d = 0.05 # doplyw wody [m^3/s]
t_sym = 1800 # czas symulacji [s]

Q_d_min = 0 #doplyw wody min [m^3/s]
Q_d_max = 0.05 #doplyw wody max [m^3/s]
u_min=0 #uchyb min [V]
u_max = 10 #uchyb max [V]
u = 10 #uchyb zaworu [V]
h_zadane = 2 # h zadane [m]
h_min = 0

h = []
n=int(round(t_sym/Tp,0))
h.append(h_0)
for i in range(n):
    h_delta = h_zadane-h[-1]
    u_new = max(min(u, u_max), u_min)
    Q_d_new = max(min(Q_d, Q_d_max), Q_d_min)

    h_new = Tp/A*(Q_d_new-beta*math.sqrt(h[-1]))+h[-1]
    h.append(max(min(h_new, h_zadane), h_min))
    u=u_new
    Q_d=Q_d_new
    print("u:"+str(u))
    print("Q_d:"+str(Q_d))


print(h)
print((Q_d/beta)**2) # sprawdzenie stanu końcowego

df = pd.DataFrame(dict(
    Time=[i * Tp for i in range(n + 1)],
    Height=h
))

fig = px.line(df, x="Time", y="Height",
              title="Regulacja poziomu wody w zbiorniku",
              labels={"Time": "Okres próbkowania (s)", "Height": "Wysokość (m)"})

fig.write_image("water_height_plot.png")