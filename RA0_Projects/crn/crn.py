"""
Contador de Radiacion Nuclear - RA0
"""

import RPi.GPIO as GPIO
import time
import logging
import tkinter as tk
from random import gauss
from functools import partial

from constants import *


class NuclearUI:
    """Implements UI"""
    def __init__(self, l1, l2, l3, l4, ud):
        # Initialize tkinter window
        self.ui = tk.Tk()
        self.ui.title("Contador de Radiacion Nuclear - RA0")
        self.ui.geometry("1024x600")
        # Add some stuff
        self.textbox = tk.Text(self.ui, height=7, width=30)
        self.textbox.insert(tk.END,
                            "Bienvenido al simulador Contador de Radiacion Nuclear" + "\n" + 
                            "Elija un laboratorio")
        self.textbox.configure(state="disabled",font=("Ubuntu Mono", 20, "bold"))
        self.textbox.grid(row=0, column=0)
        self.button_lab1 = tk.Button(self.ui, text="Lab1", bg="blue", command=l1)
        self.button_lab1.grid(row=0, column=1)
        self.button_lab2 = tk.Button(self.ui, text="Lab2", bg="blue", command=l2)
        self.button_lab2.grid(row=0, column=2)
        self.button_lab3 = tk.Button(self.ui, text="Lab3", bg="blue", command=l3)
        self.button_lab3.grid(row=0, column=3)
        self.button_lab4 = tk.Button(self.ui, text="Lab4", bg="blue", command=l4)
        #self.button_lab4.grid(row=0, column=4)
        self.buttons = []
        # Poll data from the tower
        self.ui.after(100, ud)
    
    def execution(self):
        self.ui.mainloop()
    
    def update_text(self, new_text=""):
        self.textbox.configure(state="normal",font=("Ubuntu Mono", 20, "bold"))
        self.textbox.delete("1.0", "end") # Clear the window
        self.textbox.insert(tk.END, new_text)
        self.textbox.configure(state="disabled",font=("Ubuntu Mono", 20, "bold"))
    
    def add_button(self, name="", action=None, color="red", category=0):
        button = tk.Button(self.ui, text=name, bg=color, command=action)
        button.grid(row=1+len(self.buttons), column=1+category)
        self.buttons.append(button)
    
    def flush_buttons(self):
        for button in self.buttons:
            button.destroy()


class NuclearRadiationCounter:
    """Implements the Nuclear Radiation Counter"""
    nslots = 4 # Amount of slots in the tower
    slot_pins = [11, 13, 15, 16] # GPIO pins

    def __init__(self):
        """Initializes the Nuclear Radiation Counter"""
        GPIO.setmode(GPIO.BOARD) # Use the board's pin numbering
        # Initialize GPIO
        self.slot_status = [0 for _ in range(self.nslots)]
        for i in range(self.nslots):
            self.slot_status[i] = GPIO.setup(self.slot_pins[i],
                                             GPIO.IN,
                                             pull_up_down=GPIO.PUD_DOWN)
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
            self.slot_status[i] = GPIO.input(self.slot_pins[i])
    
    def update_data(self):
        old_data = [i for i in self.slot_status]
        self.read_tower_data()
        if old_data != self.slot_status:
            print(self.slot_status)
            # Call the corresponding lab function
            new_text = self.lab_selector[self.current_lab]()
            #self.gui.update_text(new_text)
        self.gui.ui.after(100, self.update_data)
    
    def change_lab(self, lab):
        if self.current_lab != lab:
            self.gui.flush_buttons()
            self.lab_init[lab]()
            new_text = self.lab_selector[lab]()
            #self.gui.update_text(new_text)

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
                                action=action,
                                color="yellow")
        for material in lab2_data[source].keys():
            if material:
                action = partial(self.lab2_update, absorb=material)
                self.gui.add_button(str(material),
                                    action=action,
                                    color="red",
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
                                action=action,
                                color="yellow")
        for material in lab3_data[source].keys():
            if material:
                action = partial(self.lab3_update, retrodisp=material)
                self.gui.add_button(str(material),
                                    action=action,
                                    color="red",
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
        if source is not None:
            self.status["Source"] = source
        if retrodisp is not None:
            self.status["Retrodispersor"] = retrodisp
        self.lab3()

    def lab4_init(self):
        self.current_lab = 3

    def lab4(self):
        return "Laboratorio aun no implementado"

    def __del__(self):
        """Cleans up initialized data"""
        
        GPIO.cleanup()