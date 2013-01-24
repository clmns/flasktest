from sqlalchemy import *
MAX_LENGTH=20
engine = create_engine('sqlite:///tmp/sqlstudio.db')
i = 0
result = []
row = []
conn = engine.connect()
sql = "select * from Server"

sql = sql.replace(u"\xa0", " ")
res = conn.execute(sql)
res_row = res.fetchone()
while res_row is not None:
	new_val= ()
	row =  []
	if (i==0):
		header=res_row.keys()
		i=1
	for val in res_row.values():
		print val
		if len(str(val)) > MAX_LENGTH:
			new_val = (val, val[:MAX_LENGTH])
			row.append(new_val)
		else:
			new_val = (val,0)
			row.append(new_val)
	res_row = res.fetchone()
	result.append(row)

print header
print result