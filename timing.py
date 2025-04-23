import time
from datetime import datetime
import pytz

UTC = pytz.UTC

startTime = time.monotonic()

driftSum = 0
cycles = 0
PROC_INTERVAL = 5.0

while(True):

    cycles+=1
    start = time.time()
    dateTime = datetime.now(UTC)
    formatted = dateTime.strftime("%Y-%m-%d %H:%M:%S")
    print('tick: ', formatted)
    time.sleep(PROC_INTERVAL - ((time.monotonic() - startTime) % PROC_INTERVAL))
    end = time.time()
    elapsed = end - start
    print('elapsed: ', end - start)
    drift = abs(PROC_INTERVAL - elapsed)
    driftSum+=drift
    print('drift: ', drift * 1000, 'ms')
    print('avg drift: ', (driftSum / cycles) * 1000, 'ms')     