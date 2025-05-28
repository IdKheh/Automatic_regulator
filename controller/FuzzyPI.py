import math
import plotly.express as px
import pandas as pd
import simpful as sf

class FuzzyPI:
    def __init__(self, conn, Tp: float, t_sym: int, c_zadane: float):
        self.__beta = 0.035  # stala [m^(5/2)/s]
        self.__Tp = Tp  # okres probkowania [s]
        self.__V_0 = 0  # objętość poczatkowa [m^3]
        self.__t_sym = t_sym  # czas symulacji [s]
        self.__Q_d1 = [0.0]  # doplyw wody [m^3/s]
        self.__Q_d2 = 0.01  # doplyw wody [m^3/s]

        self.__Q_d1_min, self.__Q_d1_max = 0, 0.04  # doplyw wody min, max [m^3/s]

        self.__Q_o = [0.00]  # odplyw wody [m^3/s]
        self.__Q_o_min = 0  # odplyw wody min [m^3/s]
        self.__Q_o_max = 0.025  # odplyw wody max [m^3/s]

        self.__c_d1 = 0.98  # stężenie [%] [0.0 - 1.0]
        self.__c_d2 = [0]  # stężenie [%] [0.0 - 1.0]
        self.__c_d2_min, self.__c_d2_max = 0.0, 0.4
        self.__c_min, self.__c_max = min(self.__c_d1, self.__c_d2_min), max(self.__c_d1, self.__c_d2_max)

        self.__u_min = 0  # wartość prądu z regulatora min [V]
        self.__u_max = 10  # wartość prądu z regulatora max [V]
        self.__u = []  # wartość prądu z regulatora zaworu [V]
        self.__u_half = int((self.__u_max-self.__u_min)/2)

        self.__V = [self.__V_0]
        self.__e = []  # uchyb [%]
        self.__c = [0]  # stezenie
        self.__c_zadane = c_zadane  # [%]
        self.__V_min = 0
        self.__V_max = 25

        self.__t = [0]  # czas symulacji
        self.__n = int(round(self.__t_sym / self.__Tp, 0))
        
        self.__FS = sf.FuzzySystem()
        

    def __config(self):
        self.__FS.add_linguistic_variable("E",  # Definicja funkcji uchybu [%/100]
            sf.LinguisticVariable([
                sf.FuzzySet(function=sf.Triangular_MF(-100, -50, -2), term="NEG"),
                sf.FuzzySet(function=sf.Triangular_MF(-2, 0, 2), term="ZERO"),
                sf.FuzzySet(function=sf.Triangular_MF( 2, 50, 100), term="POS")
            ], universe_of_discourse=[-100, 100])
        )

        self.__FS.add_linguistic_variable("U",  # Definicja funkcji natezenia [V]
            sf.LinguisticVariable([
                sf.FuzzySet(function=sf.Triangular_MF(self.__u_min,int(self.__u_half/4), int(self.__u_half/2)), term="LOW"),
                sf.FuzzySet(function=sf.Triangular_MF(int(self.__u_half/2), self.__u_half, 3*int(self.__u_half/2)), term="MEDIUM"),
                sf.FuzzySet(function=sf.Triangular_MF(3*int(self.__u_half/2), self.__u_max,  self.__u_max), term="HIGH")
            ], universe_of_discourse=[self.__u_min, self.__u_max])
        )

        rules = [
        "IF (E IS NEG) THEN (U IS LOW)",
        "IF (E IS ZERO) THEN (U IS MEDIUM)",
        "IF (E IS POS) THEN (U IS HIGH)",
        "IF (E IS NEG) AND (E IS ZERO) THEN (U IS LOW)",
        "IF (E IS POS) AND (E IS ZERO) THEN (U IS HIGH)",
    ]
        self.__FS.add_rules(rules)


    def calculate(self):
        self.__config()
        
        for i in range(self.__n):
            self.__t.append(self.__Tp * i)
            self.__e.append(self.__c_zadane - self.__c[-1])
            
            self.__FS.set_variable("E", self.__e[-1]*100)
            self.__u.append(max(min(self.__FS.inference()["U"], self.__u_max), self.__u_min))

            self.__Q_d1.append((self.__Q_d1_max - self.__Q_d1_min) / (self.__u_max - self.__u_min) * (self.__u[-1] - self.__u_min) + self.__Q_d1_min)
            self.__Q_o.append(self.__beta * math.sqrt(self.__V[-1]))
            self.__c_d2.append((self.__c_d2_max - self.__c_d2_min) / (self.__u_max - self.__u_min) * (self.__u[-1] - self.__u_min) + self.__c_d2_min)

            V_new = self.__Tp * (self.__Q_d1[-1] + self.__Q_d2 - self.__Q_o[-1]) + self.__V[-1]
            if self.__V[-1] != 0:
                c_new = (1 / self.__V[-1]) * (self.__Q_d1[-1] * (self.__c_d1 - self.__c[-1]) + self.__Q_d2 * (self.__c_d2[-1] - self.__c[-1])) * self.__Tp + self.__c[-1]
            else:
                c_new = 0
            
            self.__V.append(max(min(V_new, self.__V_max), self.__V_min))
            self.__c.append(max(min(c_new, self.__c_max), self.__c_min))
            
    def savePlot(self):
        df1 = pd.DataFrame(dict(Time=self.__t, Height=self.__V))
        fig1 = px.line(df1, x="Time", y="Height", 
                        title="Przebieg zmian poziomów alkoholu w zbiorniku dla regulatora rozmytego",
                        labels={"Time": "Okres próbkowania [s]", "Height": "Objętość [m³]","variable": ""})
        fig1.write_image("static/fuzzy_pi_objetosc.png")

        df2 = pd.DataFrame(dict(Time=self.__t, Odplyw=self.__Q_o, Doplyw1=  self.__Q_d1 , Doplyw2 = [self.__Q_d2] * len(self.__t)))
        fig2 = px.line(df2, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw"], 
                       title="Przebieg zmian dopływu i odpływu alkoholu w czasie dla regulatora rozmytego", 
                       labels={"Time": "Czas [s]", "value": "Przepływ [m³/s]", "variable": "Rodzaj przepływu"})
        fig2.write_image("static/fuzzy_pi_doplyw.png")

        df3 = pd.DataFrame(dict(
            Time=self.__t,
            Odplyw=[val * 100 for val in self.__c],
            Doplyw1=[self.__c_d1 * 100] * len(self.__t),
            Doplyw2=[val * 100 for val in self.__c_d2],
            Zadane=[self.__c_zadane * 100] * len(self.__t)
        ))
        fig3 = px.line(df3, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw", "Zadane"], 
                       title="Przebieg zmian stężenia w czasie dla regulatora rozmytego", 
                       labels={"Time": "Czas [s]", "value": "Stężenie substancji [%]", "variable": "Typ"})
        fig3.write_image("static/fuzzy_pi_stezenie.png")
