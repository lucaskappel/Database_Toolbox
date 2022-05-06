# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 10:28:07 2022

@author: lkappel
"""

import sqlite3, csv

class SQLDB:
    def __init__(self, absolutePathToDB):
        self.SQLConnection = sqlite3.connect(absolutePathToDB)
        
    def __del__():
        self.SQLConnection.close()
    
    def getTables
        
def GetTableList():
    return QueryCatalog(r"SELECT * FROM sqlite_master WHERE type='table';")