import urllib.request as rq
import urllib.parse as ps
import sqlite3
import json
import time
import ssl
import sys
buffer = memoryview

serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"
# Deal with SSL certificate anomalies Python > 2.7
# scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
scontext = None

conn = sqlite3.connect('../databases/geodata.sqlite')
cur = conn.cursor()
cur.execute('''
DROP TABLE Locations ''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

fh = open("where.data")
count = 0
for line in fh:
    if count > 200 : break
    address = line.strip()
    print ('')
    cur.execute("SELECT geodata FROM Locations WHERE address= ?", (buffer(address.encode()), ))

    try:
        data = cur.fetchone()[0]
        print ("Found in database ",address)
        continue
    except:
        pass

    print ('Resolving', address)
    url = serviceurl + ps.urlencode({"sensor":"false", "address": address})
    print ('Retrieving', url)
    uh = rq.urlopen(url, context=scontext)
    data = uh.read()
    #print(data)
    #print ('Retrieved',len(data),'characters',data[:20].replace('\n',' '))
    count = count + 1
    try: 
        js = json.loads(str(data.decode()))
        #print(js)
        # print js  # We print in case unicode causes an error
    except:
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') : 
        print ('==== Failure To Retrieve ====')
        print (data)
        break

    cur.execute('''INSERT INTO Locations (address, geodata) 
            VALUES ( ?, ? )''', ( buffer(address.encode()),data ) )
    conn.commit() 
    time.sleep(1)

print ("Run geodump.py to read the data from the database so you can visualize it on a map.")
