"""
Contador de Radiacion Nuclear - RA0
"""

#import RPi.GPIO as GPIO
import customtkinter
from random import gauss
from functools import partial

from constants import *

"""Implements UI"""
"""12/10/2024 actualizacion de Tkinter a CustomTkinter Realizada por Mariano Ceballos y Facundo Ceballos"""

class NuclearUI(customtkinter.CTk):
    def __init__(self, l1, l2, l3, l4, ud):
        super().__init__()

        # Initialize tkinter window
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.title("Contador de Radiacion Nuclear - RA0")
        self.geometry("1024x600")
        self.grid_columnconfigure((1, 2, 3, 4), weight=1)
        # Add some stuff
        self.textbox = customtkinter.CTkTextbox(self, height=200, width=400)
        self.textbox.insert("end",
                            "Bienvenido al simulador Contador de Radiacion Nuclear" + "\n" + 
                            "Elija un laboratorio")
        self.textbox.configure(state="disabled",font=("Lexend", 20, "bold"))
        self.textbox.grid(row=0, column=0)
        self.button_lab1 = customtkinter.CTkButton(self, text="Lab1", font=("Lexend", 40, "bold"),height=150, command=l1)
        self.button_lab1.grid(row=0, column=1)
        self.button_lab2 = customtkinter.CTkButton(self, text="Lab2", font=("Lexend", 40, "bold"), height=150, command=l2)
        self.button_lab2.grid(row=0, column=2)
        self.button_lab3 = customtkinter.CTkButton(self, text="Lab3", font=("Lexend", 40, "bold"), height=150, command=l3)
        self.button_lab3.grid(row=0, column=3)
        self.button_lab4 = customtkinter.CTkButton(self, text="Lab4", font=("Lexend", 40, "bold"), height=150, command=l4)
        self.button_lab4.grid(row=0, column=4)
        self.buttons = []
        # Poll data from the tower
        self.after(100, ud)
    
    def execution(self):
        self.mainloop()
    
    def update_text(self, new_text=""):
        self.textbox.configure(state="normal",font=("Lexend", 20, "bold"))
        self.textbox.delete("1.0", "end") # Clear the window
        self.textbox.insert("end", new_text)
        self.textbox.configure(state="disabled",font=("Lexend", 20, "bold"))
    
    def add_button(self, name="", action=None, color="indianRed4",
                   cor_radius=40 , border_color="gray8",
                   border_width=1, border_spacing=10, hover_color="firebrick1", category=0):
        button = customtkinter.CTkButton(self, text=name, font=("Lexend", 14), fg_color=color, corner_radius=cor_radius,
                                         border_color=border_color, border_width=border_width,
                                         border_spacing=border_spacing, hover_color=hover_color, command=action)
        button.grid(row=1+len(self.buttons), column=1+category)
        self.buttons.append(button)
    
    def flush_buttons(self):
        for button in self.buttons:
            button.destroy()


class NuclearRadiationCounter(customtkinter.CTk):
    """Implements the Nuclear Radiation Counter"""
    nslots = 4 # Amount of slots in the tower
    slot_pins = [0, 0, 0, 0] # GPIO pins

    def __init__(self):
        """Initializes the Nuclear Radiation Counter"""
        #GPIO.setmode(GPIO.BOARD) # Use the board's pin numbering
        # Initialize GPIO
        self.slot_status = [0 for _ in range(self.nslots)]
        #for i in range(self.nslots):
            #self.slot_status[i] = GPIO.setup(self.slot_pins[i],
             #                                GPIO.IN,
              #                               pull_up_down=GPIO.PUD_DOWN)
        # Initialize lab-specific information
        self.current_lab = -1
        self.lab_selector = [self.lab1, self.lab2, self.lab3, self.lab4]
        self.lab_init = [self.lab1_init, self.lab2_init, self.lab3_init, self.lab4_init]
        self.status = {}
        # Initialize UI
        self.gui = NuclearUI(lambda : self.change_lab(0),
                             lambda : self.change_lab(1),
                             lambda : self.change_lab(2),
                             lambda : self.change_lab(3),
                             self.update_data)

    def read_tower_data(self):
        for i in range(self.nslots):
            self.slot_status[i] = self.slot_pins[i]
    
    def update_data(self):
        old_data = [i for i in self.slot_status]
        self.read_tower_data()
        if old_data != self.slot_status:
            print(self.slot_status)
            # Call the corresponding lab function
            new_text = self.lab_selector[self.current_lab]()
            self.gui.update_text(new_text)
        self.gui.after(100, self.update_data)
    
    def change_lab(self, lab):
        if self.current_lab != lab:
            self.gui.flush_buttons()
            self.lab_init[lab]()
            new_text = self.lab_selector[lab]()
            self.gui.update_text(new_text)

    def execution(self):
        self.gui.execution()

    def create_data(self, val):
        return gauss(val, 0.005*val)

    def lab1_init(self):
        self.status = {"Voltage" : 550}
        for voltage in lab1_data.keys():
            action = partial(self.lab1_update, voltage)
            self.gui.add_button(str(voltage),
                                action=action)
        self.current_lab = 0

    def lab1(self):
        voltage = self.status["Voltage"]
        new_text = ("Laboratorio 1:\n" +
                    "Plateau\n" +
                    "\n\n")
        new_text += "Voltaje = " + str(voltage) + " V\n"
        new_text += "Actividad = " + "{:.3f}".format(self.create_data(lab1_data[voltage])) + "\n"
        self.gui.update_text(new_text=new_text)
        return new_text
    
    def lab1_update(self, voltage):
        self.status = {"Voltage" : voltage}
        self.lab1()



    def lab2_init(self):
        self.status = {"Source" : "Co60",
                       "Absorb" : "Papel"}
        self.current_lab = 1
        for source in lab2_data.keys():
            action = partial(self.lab2_update, source=source)
            self.gui.add_button(str(source),
                                action=action, hover_color="DarkOrange1",
                                color="orange")
        for material in lab2_data[source].keys():
            if material:
                action = partial(self.lab2_update, absorb=material)
                self.gui.add_button(str(material),
                                    action=action,
                                    color="indianRed4", hover_color="firebrick1",
                                    category=1)
        self.current_lab = 1

    def lab2(self):
        source = self.status["Source"]
        absorb = self.status["Absorb"]
        if not self.slot_status[2]:
            # Slot 3 vacío => sin absorbente
            absorb = False
        new_text = ("Laboratorio 2:\n" +
                    "Absorción\n" +
                    "\n\n")
        new_text += "Fuente radiactiva: " + source + "\n"
        if absorb:
            new_text += "Absorbente: " + absorb + "\n"
        else:
            new_text += "Sin absorbente\n"
        new_text += "Actividad = " + "{:.3f}".format(self.create_data(lab2_data[source][absorb])) + "\n"
        self.gui.update_text(new_text=new_text)
        return new_text
    
    def lab2_update(self, source=None, absorb=None):
        if source is not None:
            self.status["Source"] = source
        if absorb is not None:
            self.status["Absorb"] = absorb
        self.lab2()



    def lab3_init(self):
        self.status = {"Source" : "Co60",
                       "Retrodispersor" : "Aluminio"}
        self.current_lab = 1
        for source in lab3_data.keys():
            action = partial(self.lab3_update, source=source)
            self.gui.add_button(str(source),
                                action=action, hover_color="DarkOrange1",
                                color="orange")
        for material in lab3_data[source].keys():
            if material:
                action = partial(self.lab3_update, retrodisp=material)
                self.gui.add_button(str(material),
                                    action=action,
                                    color="indianRed4", hover_color="firebrick1",
                                    category=1)
        self.current_lab = 2

    def lab3(self):
        source = self.status["Source"]
        retrodisp = self.status["Retrodispersor"]
        if not self.slot_status[3]:
            # Slot 4 vacío => sin retrodispersor
            retrodisp = False
        new_text = ("Laboratorio 3:\n" +
                    "Retrodispersión\n" +
                    "\n\n")
        new_text += "Fuente radiactiva: " + source + "\n"
        if retrodisp:
            new_text += "Retrodispersor: " + retrodisp + "\n"
        else:
            new_text += "Sin retrodispersor\n"
        new_text += "Actividad = " + "{:.3f}".format(self.create_data(lab3_data[source][retrodisp])) + "\n"
        self.gui.update_text(new_text=new_text)
        return new_text
    
    def lab3_update(self, source=None, retrodisp=None):
        if source:
            self.status["Source"] = source
        if retrodisp:
            self.status["Retrodispersor"] = retrodisp
        self.lab3()


    # 6/11/2024 LABORATORIO #4 Implementado por Facundo Ceballos y Mariano Ceballos

    def lab4_init(self):
        """Initialize Lab 4 with background radiation data."""
        self.status = {"Source": "Nada", "TimeStep":0}
        self.current_lab = 3


    def lab4(self):
         self.update_lab4()

    def update_lab4(self):
        timestep = self.status["TimeStep"]
        radiation_value = interpolated_lab4_data.get(timestep, "No data")

        # Generar el texto para mostrar en la GUI
        new_text = (
            "Laboratorio 4:\n"
            "Radiación de fondo\n"
            f"Tiempo: ({(round(timestep/10 ,1))} segundos)\n"
            f"Valor de Radiación: {radiation_value} µSv/h\n"
            "\n\n"
        )

        # Actualizar el texto en la GUI si hay datos
        if timestep in interpolated_lab4_data:
            self.gui.update_text(new_text=new_text)
            self.status["TimeStep"] += 1  # Avanzar el timestep
            self.gui.after(100, self.update_lab4)  # Programar la próxima actualización
        else:
            self.gui.update_text("Fin de los datos de radiación de fondo\npara Lab 4.")

    def __del__(self):
        """Cleans up initialized data"""
        
       # GPIO.cleanup()
