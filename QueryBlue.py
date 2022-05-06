# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 13:19:45 2021

@author: Lkappel
"""
import sqlite3, csv, tkinter
from tkinter import simpledialog

SQLDB = r"C:\Users\Lkappel\Desktop\SQLite\iko_catalogue_databases\IKOCatalog_Blue.db"
OutputPathDefault = r"C:\Users\Lkappel\Desktop\QueryResults.txt"
PrimaryValues = ('page', 'h', 'w', 'w3', 'l1', 'l2', 'thread_M_1', 'id')
TablesBlue = ['\'C-Lube Linear Roller Way Super MX\'',
              '\'C-Lube Linear Way ME\'',
              '\'C-Lube Linear Way MH\'',
              '\'C-Lube Linear Way ML\'',
              '\'C-Lube Linear Way MLV\'',
              '\'C-Lube Linear Way MUL\'',
              '\'C-Lube Linear Way MV\'',
              '\'Linear Roller Way X\'',
              '\'Linear Way F\'',
              '\'Linear Way Module\'']
DatabaseCache = []

def CacheDatabase():
    SQLConnection = sqlite3.connect(SQLDB)
    SQLCursor = SQLConnection.cursor()
    for table in GetTableList():
        TableData = SQLCursor.execute(r"SELECT * FROM '" + str(table[1]) + "'")
        ColumnList = GetColumnNames(SQLCursor)
        DatabaseCache.append((str(table[1]), ColumnList, TableData.fetchall()))

def GetTableList():
    return QueryCatalog(r"SELECT * FROM sqlite_master WHERE type='table';")

def GetColumnNames(SQLCursor):
    return list(map(lambda x: x[0], SQLCursor.description))

def QueryCatalog(SQLQuery):
    SQLConnection = sqlite3.connect(SQLDB)
    SQLCursor = SQLConnection.cursor()
    QueryResults = SQLCursor.execute(SQLQuery).fetchall()
    SQLConnection.close()
    return QueryResults

def WriteQueryResults(IterableToWrite, OutputPath = OutputPathDefault):
    with open(OutputPath, 'w', encoding = 'utf-8') as writeFile:
        csvWriter = csv.writer(writeFile, delimiter='\t')
        csvWriter.writerows(IterableToWrite)



def DefaultQueryCatalogueBlue():
    ROOT = tkinter.Tk()
    ROOT.withdraw()
    QueryParameters = simpledialog.askstring(
        title = "Query: IKO Catalogue Blue",
        prompt = "Enter part paramters to match (e. L2 = 32 and W3 = 15)")
    #ROOT.destroy()
    
    QueryResults = []
    for table in TablesBlue:
        QueryString = f"SELECT {','.join(PrimaryValues)}  FROM {table} WHERE {QueryParameters}"
        SQLConnection = sqlite3.connect(SQLDB)
        SQLCursor = SQLConnection.cursor()
        for result in SQLCursor.execute(QueryString).fetchall():
            QueryResults.append(result)
        SQLConnection.close()
    QueryResults.insert(0, PrimaryValues)
    WriteQueryResults(QueryResults)

DefaultQueryCatalogueBlue()