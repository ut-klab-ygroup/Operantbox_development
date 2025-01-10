#!/bin/sh
raspi-gpio set 20 op pn dl  #cahmber_light
raspi-gpio set 27 op pn dh
raspi-gpio set 26,19,13,6,5 op pn dl #nose poke leds
raspi-gpio set 21 op pn dl  #reward led
raspi-gpio set 7 op pn dl   #reward pump