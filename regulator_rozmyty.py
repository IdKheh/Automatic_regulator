import math
import plotly.express as px
import pandas as pd
import simpful as sf

# Parametry systemu fizycznego
A = 1.5
beta = 0.035
Tp = 0.1
h_0 = 0
t_sym = 1800
Q_d_min = 0
Q_d_max = 0.05
Q_o_min = 0
Q_o_max = 0.1
u_min = 0
u_max = 10
h_zadane = 3
h_min = 0
h_max = 5

# Inicjalizacja zmiennych
t = [0]
Q_d = [0.0]
Q_o = [0.0]
u = [0]
e = [0]
h = [h_0]
n = int(round(t_sym/Tp, 0))

# Tworzymy system rozmyty
FS = sf.FuzzySystem()

# Zmienna wejściowa: uchyb (błąd)
FS.add_linguistic_variable("Error", sf.LinguisticVariable([
    sf.FuzzySet(function=sf.Triangular_MF(-5, -3, -1), term="NB"),
    sf.FuzzySet(function=sf.Triangular_MF(-3, -1, 0), term="NM"),
    sf.FuzzySet(function=sf.Triangular_MF(-1, 0, 1), term="ZE"),
    sf.FuzzySet(function=sf.Triangular_MF(0, 1, 3), term="PM"),
    sf.FuzzySet(function=sf.Triangular_MF(1, 3, 5), term="PB")
], universe_of_discourse=[-5, 5]))

# Zmienna wyjściowa: sterowanie (prąd)
FS.add_linguistic_variable("Control", sf.LinguisticVariable([
    sf.FuzzySet(function=sf.Triangular_MF(0, 0, 2), term="Z"),
    sf.FuzzySet(function=sf.Triangular_MF(1, 3, 5), term="L"),
    sf.FuzzySet(function=sf.Triangular_MF(4, 6, 8), term="M"),
    sf.FuzzySet(function=sf.Triangular_MF(7, 9, 10), term="H")
], universe_of_discourse=[0, 10]))

# Reguły sterowania
rule_base = [
    "IF Error IS NB THEN Control IS Z",
    "IF Error IS NM THEN Control IS L",
    "IF Error IS ZE THEN Control IS M",
    "IF Error IS PM THEN Control IS H",
    "IF Error IS PB THEN Control IS H"
]
FS.add_rules(rule_base)

# Symulacja
for i in range(n):
    t.append(Tp*i)
    e.append(h_zadane - h[-1])

    # Ustawiamy wartość wejściową i wnioskujemy
    FS.set_variable("Error", e[-1])
    control_output = FS.inference()["Control"]

    u.append(max(min(control_output, u_max), u_min))
    Q_d.append((Q_d_max - Q_d_min) / (u_max - u_min) * (u[-1] - u_min) + Q_d_min)
    Q_o.append(max(min(beta * math.sqrt(h[-1]), Q_o_max), Q_o_min))
    h_new = Tp / A * (Q_d[-1] - Q_o[-1]) + h[-1]
    h.append(max(min(h_new, h_max), h_min))

# Wykres wysokości wody
df = pd.DataFrame(dict(Time=t, Height=h))
fig = px.line(df, x="Time", y="Height",
              title="Fuzzy: Przebieg zmian poziomu wody w zbiorniku",
              labels={"Time": "Czas [s]", "Height": "Wysokość [m]"})
fig.write_image("fuzzy_water_height_plot.png")

# Wykres odpływu
df2 = pd.DataFrame(dict(Time=t, Odplyw=Q_o))
fig2 = px.line(df2, x="Time", y="Odplyw",
              title="Fuzzy: Przebieg zmiany odpływu wody",
              labels={"Time": "Czas [s]", "Odplyw": "Odpływ [m^3/s]"})
fig2.write_image("fuzzy_plot2.png")
