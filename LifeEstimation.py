# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 11:10:36 2021

@author: Lkappel
"""

import matplotlib.pyplot as plt
import numpy as np
import math

#L1(km)=50(C/P)^3
    
def Plot_BvR(CurrentLoad=1, RatedLoad = [1,1]):
    # RatedLoad variable should be formatted as [RatedLoadBall, RatedLoadRoller]

    plt.xlabel("Factor of Safety (Rated Load / Applied Load)")
    plt.ylabel("Expected Life (km)")
    plt.title("Roller Bearing Life Expectancy\nImprove performance by increasing the rated load or decreasing applied load.")
    
    fs = [5, RatedLoad[0]/CurrentLoad, RatedLoad[1]/CurrentLoad] # [minimum, Ball, Roller]
    
    L1_Ball = lambda FactorOfSafety: 50*pow(FactorOfSafety, 3)
    L1_Roller = lambda FactorOfSafety: 50*pow(FactorOfSafety,10/3)
    
    FactorOfSafety_AxisX = np.arange(0.1, math.ceil(max(fs)*4/3), 0.1)
    AxisY_Ball = [L1_Ball(xval) for xval in FactorOfSafety_AxisX]
    AxisY_Roller = [L1_Roller(xval) for xval in FactorOfSafety_AxisX]
    
    AppliedPerformance = [fs[1:], [L1_Ball(fs[1]), L1_Roller(fs[2])]]
    MinimumPerformance = [[fs[0], fs[0]],  [L1_Ball(fs[0]), L1_Roller(fs[0])]]
    
    plt.ylim([0,max(max(AxisY_Ball, AxisY_Roller))*1.2])
    plt.plot(FactorOfSafety_AxisX, AxisY_Ball, 'm', label = "Ball Bearing Life",)
    plt.plot(FactorOfSafety_AxisX, AxisY_Roller, 'b', label = "Roller Bearing Life")
    plt.plot(AppliedPerformance[0], AppliedPerformance[1], 'ro', label="Current Performance")
    plt.plot(MinimumPerformance[0], MinimumPerformance[1], 'go', label="Minimum Factor of Safety Performance (5)")
    for xy in zip(AppliedPerformance[0], AppliedPerformance[1]):
        plt.annotate('(%.2f, %.1f)' % xy, xy=xy, textcoords='data')
    for xy in zip(MinimumPerformance[0], MinimumPerformance[1]):
        plt.annotate('(%.2f, %.1f)' % xy, xy=xy, textcoords='data')
    plt.legend()
    plt.show()

#### Main ####
P = 4247.66
C = [11600, 14900]

plt.figure()
Plot_BvR(P, C)

