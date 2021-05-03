from datetime import datetime
import time

while 1:
    with open("/usr/src/app/time.txt",'w') as f:
        now = datetime.now()
        f.write( now.strftime("%m/%d/%Y, %H:%M:%S") )
    time.sleep(1)
