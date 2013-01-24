import pyodbc
from sqlalchemy import * 

def connect():
	return pyodbc.connect("DRIVER={SQL Server};Server=CLEMENS-PC\SQLEXPRESS;Database=test;Trusted_Connection=Yes")
	
engine = create_engine("mssql+pyodbc://", creator=connect)
#cur = engine.cursor()

res = engine.execute("select top 1 * from sys.all_columns")
row = res.fetchall()
print row


