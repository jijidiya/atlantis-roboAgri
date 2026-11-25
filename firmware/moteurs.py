from machine import Pin, PWM
from time import ticks_ms, ticks_diff

IN1= Pin(26, Pin.OUT)
IN2= Pin(27, Pin.OUT)
IN3= Pin(16, Pin.OUT)
IN4= Pin(17, Pin.OUT)

ENA= PWM(Pin(25), freq=1000, duty=0)
ENB= PWM(Pin(14), freq=1000, duty=0)

vitesse = 256
vitesse_max = 768
augmentation = 102
intervalle = 1000

deplacement_actif = False

dernier_temps = ticks_ms()


def avancer():
    IN1.value(1)
    IN2.value(0)

    IN3.value(1)
    IN4.value(0)

    demarrer_acceleration()

def reculer():
    IN1.value(0)
    IN2.value(1)

    IN3.value(0)
    IN4.value(1)

    demarrer_acceleration()

def tourner_gauche():
    IN1.value(0)
    IN2.value(1)

    IN3.value(1)
    IN4.value(0)

    demarrer_acceleration()

def tourner_droite():
    IN1.value(1)
    IN2.value(0)

    IN3.value(0)
    IN4.value(1)

    demarrer_acceleration()

def arreter():
    global vitesse, deplacement_actif
    ENA.duty(0)
    ENB.duty(0)

    vitesse = 256
    deplacement_actif = False 

def accelerer():
    global vitesse, dernier_temps

    if not deplacement_actif :
        return 

    temps_actuel = ticks_ms()

    if vitesse < vitesse_max and ticks_diff(temps_actuel, dernier_temps) >= intervalle :
        vitesse = min(vitesse + augmentation, vitesse_max)

        ENA.duty(vitesse)
        ENB.duty(vitesse)

        dernier_temps = temps_actuel

def demarrer_acceleration():
    global vitesse, dernier_temps, deplacement_actif
    
    vitesse = 256
    dernier_temps = ticks_ms()
    deplacement_actif = True 
    
    ENA.duty(vitesse)
    ENB.duty(vitesse)

def obstacle_detecte():
    arreter()
    

    


