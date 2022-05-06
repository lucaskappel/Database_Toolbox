# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:44:52 2022

@author: lkapp
"""

import sqlite3, re, functools#, copy

# ============================================================================
class dbConnection:
    
    SQLConnection = None
    
    def __init__(self, SQLAddress):
        self.SQLConnection = sqlite3.connect(SQLAddress)
        
    def __del__(self):
        try:
            self.SQLConnection.close()
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            
    def __commit__(self):
        self.SQLConnection.commit()
    
    # ========================================================================
    
    def dbGetTableList(self):
        '''Returns list of tuples, each tuple is a table contained in the SQLConnection's .db file.
        Tuple is formatted as:
            (
             "table",
             
             "tableName", 
             
             "tableName (again)", 
             
             an integer that i dont know what it is for, 
             
             "CREATE TABLE *space* 
                 ""table name"" *space* 
                 (
                     column heading *space* 
                     
                     column TYPE *space* 
                     
                     other attributes for that heading separated by spaces
                )"
            )'''
        SQLCursor = self.SQLConnection.cursor()
        QueryResults = SQLCursor.execute(r"SELECT * FROM sqlite_master WHERE type='table';").fetchall()
        SQLCursor.close()
        return QueryResults
    
    def dbTableExists(self, SQLTableName):
        '''Returns TRUE if a table with the exact same name as SQLTableName exists in 
        the .db file given by SQLConnection.'''
        for table in self.dbGetTableList():
            if table[1] == SQLTableName: return True
        return False
    
    def dbGetTableDefinition(self, SQLTableName):
        '''Retrieve the entire table definition given by SQLTableName'''
    
        # If SQLTableName is not in the list of tables, raise an exception saying so.
        if not self.dbTableExists(SQLTableName):    
            tableListAsString = "\n" + "\n".join(map(
                lambda x: x[1], 
                self.dbGetTableList()))
            raise Exception(f'{SQLTableName} was not found in the table list: {tableListAsString}')
        
        # Otherwise return the table
        tableList = self.dbGetTableList()
        for table in tableList:
            if table[1] == SQLTableName: return table
        raise Exception(f'{SQLTableName} exists in the SQLConnection, but was not able to be found.')
    
    def dbSubmitQuery(self, QueryString):
        SQLCursor = self.SQLConnection.cursor()
        QueryResults = SQLCursor.execute(QueryString).fetchall()
        SQLCursor.close()
        return QueryResults
    
    def dbGetTableData(self, SQLTableName):
        '''Retrieve the table with the same name as SQLTableName as a list of records (as tuples).'''
        SQLQuery = f"""SELECT * FROM '{SQLTableName}'"""
        SQLCursor = self.SQLConnection.cursor()
        QueryResults = SQLCursor.execute(SQLQuery).fetchall()
        SQLCursor.close()
        return QueryResults
    
    def dbGetTableHeaders(self, SQLTableName):
        '''Returns list of str, the column titles of the table with the given name.
        Pretty much obsolete with dbGetTableColumnDefinition.'''
        SQLCursor = self.SQLConnection.cursor()
        TableHeaders = list(map(lambda x: x[0], SQLCursor.execute(f"SELECT * FROM '{SQLTableName}'").description))
        SQLCursor.close()
        return TableHeaders
    
    def dbGetTableColumnDefinition(self, SQLTableName):
        '''Returns a list of tuples, 
        each tuple is the column name, followed by its TYPE and additional definitions.
        
        : tuple, tuple[0] is the column name, tuple[1] is the column data type.'''
        
        tableDefinition = self.dbGetTableDefinition(SQLTableName)[-1]
        RegexToFind = re.compile(r'\((.*)\)') # look for "( )" and take that as the table defs
        RegexResults = RegexToFind.search(tableDefinition).group(1)
        ColumnDefinitions = list(map(lambda x: tuple(x.split(' ')), RegexResults.split(', ')))
        return ColumnDefinitions
    
    def dbCreateTable(self, SQLTableName, ColumnDefinitions):
        '''Create a DB tabe with the columns defined by the parameters.
        ColumnDefinitions is a list of tuples. 
        
        tuple[0] is the column name, 
        tuple[1] is the column data type, 
        tuple[2:] includes things like "PRIMARY", "KEY", "AUTOINCREMENT".'''
        
        # Create the beginning of the SQL statement, using the part prefix as the table title.
        SQL_CreateTable = f"CREATE TABLE IF NOT EXISTS {SQLTableName} (" # Initialize the string
        for columndef in ColumnDefinitions: # add all the columns and their attributes
            SQL_CreateTable += "\n" + functools.reduce(
                lambda prevElem, currElem: f"{prevElem} {currElem}", 
                columndef) + ","
        SQL_CreateTable = SQL_CreateTable[0:-2] # Trim the last comma
        SQL_CreateTable += ");" # close the string
        
        # Push the change
        SQLCursor = self.SQLConnection.cursor()
        SQLCursor.execute(SQL_CreateTable)
        SQLCursor.close()
        return
    
    def dbDropTable(self, SQLTableName):
        '''Delete the given table from the DB if it exists. Dont need to return anything
        because the end result is the same: the given table doesn't exist.'''
        if not self.dbTableExists(SQLTableName): return
        SQLCursor = self.SQLConnection.cursor()
        SQLCursor.execute(f"DROP TABLE {SQLTableName};")
        SQLCursor.close()
        return
    
    def dbTableAddColumn(self, SQLTableName, ColumnDefinition):
        '''Add the column with the given definition to the given table.
        ColumnDefinition is a tuple of the form:
            
                ColumnName ColumnDataType AdditionalDefinitions(such as PRIMARY KEY, AUTOINCREMENT)...
        '''
        ColumnDefinitionString = " ".join(ColumnDefinition)
        SQLCursor = self.SQLConnection.cursor()
        SQLCursor.execute(f"ALTER TABLE {SQLTableName} ADD COLUMN {ColumnDefinitionString};")
        SQLCursor.close()
    
    def dbTableInsertRecord(self, SQLTableName, RecordDefinition,  CreateTableIfNotExists = False):
        '''RecordDefinition should be of the form:
            
            ([Headers], [Values])'''
        
        if not (SQLTableName in [TableDefinition[1] for TableDefinition in self.dbGetTableList()]) or (CreateTableIfNotExists == False):
            raise Exception("Invalid table name for record insertion.")
        if not compareListContents([HeaderDefinition[0] for HeaderDefinition in self.dbGetTableColumnDefinitions(SQLTableName)], RecordDefinition[0]):
            raise Exception("Target table headers and record headers do not match.")
        
        SQLCommand = """INSERT OR REPLACE INTO 
            {SQLTableName}({','.join(RecordDefinition[0])}) 
            VALUES({','.join(['?' for _ in Headers])});"""
        SQLCursor = self.SQLConnection.cursor()
        SQLCursor.execute(SQLCommand, RecordDefinition[1])
        SQLCursor.close()
    
    def dbGetTable(self, SQLTableName):
        '''Get all the records from the given table.
        Return both the records and the headers.'''
        return (self.dbGetTableHeaders(SQLTableName), self.dbGetTableData(SQLTableName))
        
    def defineColumnMap(self, ColumnDefinitionSource, OrderedColumnDefinitionDestination):
        '''Just creates a dictionary as-ordered from the two inputs. If inputs
        are not the same length, does not include values without a pair.'''
        ColumnDefinitionDictionary = {"SourceColumn" : "DestinationColumn"}
        for HeaderDefinition in zip(ColumnDefinitionSource, OrderedColumnDefinitionDestination):
            ColumnDefinitionDictionary[HeaderDefinition[1]] = HeaderDefinition[0]
        return ColumnDefinitionDictionary
    
    def scorchDB(self):
        TableList = self.dbGetTableList()
        SQLCursor = self.SQLConnection.cursor()
        for DBTable in TableList:
            #SQLCursor.execute(f"DROP TABLE {DBTable[1]};")
            print(DBTable)
        SQLCursor.close()
        return
    
# ============================================================================

def getAlphabeticPrefix(matchString):
    '''Return the substring starting at 0, ending when a non-alphabetic character is found.'''
    RegexToFind = re.compile(r'(^[a-zA-Z]*)')
    RegexResults = RegexToFind.match(matchString)
    returnString = RegexResults.group()
    return re.sub("^AS$", "\"AS\"", returnString)

def typeToSQLType(typeInput):
    '''Converts the type (str, float, or int) input of something to its string 
    representation ("str", "float", or "int").'''
    if typeInput is str: 
        return "text"
    elif typeInput is float or int: 
        return "float"
    else:
        raise Exception(f"Data type was not text, float, or int: {typeInput}")

def compareListContents(list1,list2):
    '''Compare to see if two lists have all the same contents, regardless of elements' order.'''
    
    #create list to remember the removed elements.
    compareList = []
    
    for elem in list1:
        # if elem is in list2, remove it and put it in comparelist
        if elem in list2:
            compareList.append(list2.pop(list2.index(elem)))
            
    # if the two lists had the same contents, then compareList should be exactly
    # the same as list1, and there should be no elements left in list2.
    return (list1 == compareList) and len(list2) == 0

def divideTableByIdPrefix():
    SQLDB_Source = dbConnection(r"C:\Users\lkapp\Desktop\IKOCatalog_copy.db")
    SQLDB_Destination = dbConnection(r"C:/Users/lkapp/Desktop/IKOCatalogue_Release.db")
    SQLDB_Destination.scorchDB()
    
    SQLDB_Source_Cache = SQLDB_Source.dbGetTableData()
    
    # Load Table
    # : element, find the prefix
    # look for a table to put it in
    # if no table exists, create it with the proper columns
    # if the table exists, then push the record into that table.
    # before pushing, verify the columns all match. If they don't, then find a map for it (TODO)
    # commit the changes.
    return

# ============================================================================

def runSQLSequence():
    # Create the connection
    SQLDB = dbConnection(r"C:\Users\lkapp\Desktop\IKOCatalog_copy.db")
    SQLTableName = "C-Lube Linear Way ME"
    
    #t1 = ("one","two","three","four","five","six","seven","eight")
    #t2 = (1,2,3,4,5,6,7,8,9)
    #t = "f"
    
    #print(functools.reduce(lambda previousValue, currentValue: f"{previousValue} {currentValue}", t1))
    
    #print(SQLDB.dbGetTableColumnDefinition(SQLTableName))
    #print(SQLDB.dbGetTableHeaders("C-Lube Linear Way ME"))
    #print(SQLDB.dbTableExists("C-Lube Linear Way ME"))
    #print(SQLDB.dbGetTableDefinition("C-Lube Linear Way ME"))
    #print(SQLDB.dbGetTableList())
    #print(compareListContents([1,2,3,4,5,6,7], [7,4,5,1,2,3,6]))
    #SQLDB.dbCreateTable("kekw", SQLDB.dbGetTableColumnDefinition(SQLTableName))
    
    #print(SQLDB.defineColumnMap(t1, t2))
    
    divideTableByIdPrefix()
    
    return

runSQLSequence()