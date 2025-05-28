import math
import plotly.express as px
import pandas as pd

class ClassicPI:
    def __init__(self, conn, kp: float, Ti: float, Tp: float, t_sym: int, c_zadane: float):
        self.__beta = 0.035  # stala [m^(5/2)/s]
        self.__Tp = Tp  # okres probkowania [s]
        self.__V_0 = 0  # objętość poczatkowa [m^3]
        self.__t_sym = t_sym  # czas symulacji [s]
        self.__Q_d1 = [0]  # doplyw wody [m^3/s]
        self.__Q_d2 = 0.01  # doplyw wody [m^3/s]

        self.__Q_d1_min, self.__Q_d1_max = 0, 0.04  # doplyw wody min, max [m^3/s]

        self.__Q_o = [0.00]  # odplyw wody [m^3/s]
        #self.__Q_o_min = 0  # odplyw wody min [m^3/s]
        #self.__Q_o_max = 0.025  # odplyw wody max [m^3/s]

        self.__c_d1 = 0.98  # stężenie [%] [0.0 - 1.0]
        self.__c_d2 = [0]  # stężenie [%] [0.0 - 1.0]
        self.__c_d2_min, self.__c_d2_max = 0.01, 0.4
        self.__c_min, self.__c_max = min(self.__c_d1, self.__c_d2_min), max(self.__c_d1, self.__c_d2_max)

        self.__u_min = 0  # wartość prądu z regulatora min [V]
        self.__u_max = 10  # wartość prądu z regulatora max [V]
        self.__u = []  # wartość prądu z regulatora zaworu [V]
        self.__upi = []

        self.__V = [self.__V_0]
        self.__e = []  # uchyb [%]
        self.__c = [0]  # stezenie
        self.__c_zadane = c_zadane  # [%]
        self.__V_min = 0
        self.__V_max = 25

        self.__kp = kp  # nastawa regulatora
        self.__Ti = Ti  # czas zdwojenia [s], [2.5 - 5.0]
        self.__t = [0]  # czas symulacji
        self.__n = int(round(self.__t_sym / self.__Tp, 0))

    def calculate(self):
        for i in range(self.__n):
            self.__t.append(self.__Tp*i)
            self.__e.append(self.__c_zadane - self.__c[-1])
            self.__upi.append(self.__kp*(self.__e[-1] + (self.__Tp/self.__Ti)*sum(self.__e)))
            self.__u.append(max(min(self.__upi[-1], self.__u_max), self.__u_min))
            
            self.__Q_d1.append((self.__Q_d1_max - self.__Q_d1_min) / (self.__u_max - self.__u_min) * (self.__u[-1] - self.__u_min) + self.__Q_d1_min)
            self.__Q_o.append(self.__beta*math.sqrt(self.__V[-1]))
            self.__c_d2.append((self.__c_d2_max - self.__c_d2_min) / (self.__u_max - self.__u_min) * (self.__u[-1] - self.__u_min) + self.__c_d2_min)
            
            V_new = self.__Tp * (self.__Q_d2+self.__Q_d1[-1]-self.__Q_o[-1])+self.__V[-1]
            if self.__V[-1]!=0 :
                c_new = (1 / self.__V[-1]) * (self.__Q_d1[-1] * (self.__c_d1 - self.__c[-1]) + self.__Q_d2 * (self.__c_d2[-1] - self.__c[-1])) * self.__Tp + self.__c[-1]
            else : c_new = 0
            
            self.__V.append(max(min(V_new, self.__V_max), self.__V_min))
            self.__c.append(max(min(c_new, self.__c_max), self.__c_min))
    
    
    def savePlot(self):
        # wykres poziomu wody w zbiorniku
        df = pd.DataFrame(dict(
            Time=self.__t,
            Height=self.__V
        ))
        fig = px.line(df, x="Time", y="Height",
                    title="Przebieg zmian poziomów alkoholu w zbiorniku dla regulatora klasycznego",
                    labels={"Time": "Okres próbkowania [s]", "Height": "Objętość [m³]","variable": ""})
        fig.write_image("static/classic_pi_objetosc.png")


        # wykres odpływu od czasu
        df = pd.DataFrame(dict(
            Time=self.__t,
            Odplyw=self.__Q_o,
            Doplyw1=self.__Q_d1,
            Doplyw2=[self.__Q_d2] * (self.__n+1)
        ))

        fig = px.line(df, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw"],
                    title="Przebieg zmian dopływu i odpływu alkoholu w czasie dla regulatora klasycznego",
                    labels={"Time": "Czas [s]", "value": "Przepływ [m³/s]", "variable": "Rodzaj przepływu"})


        fig.write_image("static/classic_pi_doplyw.png")

        # wykres stężenia od czasu
        df = pd.DataFrame(dict(
            Time=self.__t,
            Odplyw=[val * 100 for val in self.__c],
            Doplyw1=[self.__c_d1 * 100] * (self.__n+1),
            Doplyw2=[val * 100 for val in self.__c_d2],
            Zadane=[self.__c_zadane * 100] * (self.__n+1)
        ))

        fig = px.line(df, x="Time", y=["Doplyw1", "Doplyw2", "Odplyw","Zadane"],
                    title="Przebieg zmian stężenia w czasie dla regulatora klasycznego",
                    labels={"Time": "Czas [s]", "value": "Stężenie substancji [%]", "variable": "Rodzaj przepływu"})


        fig.write_image("static/classic_pi_stezenie.png")
