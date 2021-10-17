import datetime
import pysolar.solar as solar
import time
import sys

try:
    PERIOD = 10 # seconds
    LAT    = float(sys.argv[1])
    LON    = float(sys.argv[2])
    while True:
        now = datetime.datetime.now(datetime.timezone.utc)
        zenith = solar.get_altitude(LAT, LON, now)
        azimuth = solar.get_azimuth(LAT, LON, now)
        print(zenith, azimuth)
        sys.stdout.flush()
        time.sleep(PERIOD)
except:
    print("usage: %s <lattiude> <longitude>" % sys.argv[0])
