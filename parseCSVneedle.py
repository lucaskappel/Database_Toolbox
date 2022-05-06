# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 10:23:28 2022

@author: lkappel
"""

import os.path
import pandas

pathExcel = r"C:\Users\Lkappel\Desktop\SQLite\Needle_Python.xls"
pathDB = r"C:\Users\Lkappel\Desktop\SQLite\iko_product\IKO_Product.db"

#%% Excel parsing
ExcelWorkbook = pandas.read_excel(pathExcel)


#%%

print(os.path.exists(pathDB))