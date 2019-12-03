#! /usr/bin/python3

import re, os, rrdtool, time

### rrdb location
db = "/home/pi/var/sk2gj-temp.rrd"


### Read 1-wire sensor
### https://www.mkompf.com/weather/pionewiremini.html
def read_sensor(path):
    value = "U"
    try:
      with open(path, "r") as f:
          line = f.readline()
          if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
              line = f.readline()
              m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
              if m:
                  value = str(float(m.group(2)) / 1000.0)
    except IOError as e:
        print("%s: Error reading %s: %s" % (time.strftime("%x %X"), path, e) )
    return value

def read_all(paths1w):
    data = 'N'
    for pathw in paths1w:
        data += ':'
        data += read_sensor(pathw)
        time.sleep(1)
    return(data)

def plot_hour():
    graph="/home/pi/var/sk2gj-temp-h.png"
    rrdtool.graph(graph,
                  '--start', 'end-1h', 
                  '--title', 'Temperatur vid SK2GJ', '--vertical-label', u'\xb0C',
                  '--lower-limit','-40',
                  '--upper-limit','30',
                  'DEF:ute=%s:ute:AVERAGE' % db,
                  'DEF:inne=%s:inne:AVERAGE' % db,
                  'VDEF:innenu=inne,LAST', 
                  'VDEF:utenu=ute,LAST', 
                  'LINE2:ute#0000FF:Ute', 'GPRINT:utenu:%.1lf', 
                  'LINE2:inne#00FF00:Inne', 'GPRINT:innenu:%.1lf')

def plot_day():
    graph="/home/pi/var/sk2gj-temp-d.png"
    rrdtool.graph(graph, 
                  '--start', '00:00', 
                  '--title', 'Temperatur vid SK2GJ', '--vertical-label', u'\xb0C',
                  '--lower-limit', '-40',
                  '--upper-limit', '30', 
                  'DEF:ute=%s:ute:AVERAGE' % db, 
                  'DEF:inne=%s:inne:AVERAGE' % db, 
                  'DEF:utemax=%s:ute:MAX' % db, 
                  'DEF:utemin=%s:ute:MIN' % db, 
                  'DEF:innemax=%s:inne:MAX' % db, 
                  'DEF:innemin=%s:inne:MIN' % db, 
                  'LINE2:ute#0000FF:Ute', 
                  'VDEF:uteminnu=utemin,MINIMUM',
                  'GPRINT:uteminnu:Min %4.1lf',
                  'VDEF:utemaxnu=utemax,MAXIMUM',
                  'GPRINT:utemaxnu:Max %4.1lf',  
                  'LINE2:inne#00FF00:Inne',
                  'VDEF:inneminnu=innemin,MINIMUM',
                  'GPRINT:inneminnu:Min %4.1lf',
                  'VDEF:innemaxnu=innemax,MAXIMUM',
                  'GPRINT:innemaxnu:Max %4.1lf')
                 
def plot_month():
    graph="/home/pi/var/sk2gj-temp-m.png"
    rrdtool.graph(graph, 
                  '--start', 'end - 1 month', 
                  '--title', 'Temperatur vid SK2GJ', '--vertical-label', u'\xb0C',
                  '--lower-limit', '-40',
                  '--upper-limit', '30', 
                  'DEF:utemax=%s:ute:MAX' % db,
                  'DEF:uteavg=%s:ute:AVERAGE' % db, 
                  'DEF:utemin=%s:ute:MIN' % db, 
                  'DEF:innemax=%s:inne:MAX' % db, 
                  'DEF:inneavg=%s:inne:AVERAGE' % db,
                  'DEF:innemin=%s:inne:MIN' % db, 
                  'CDEF:ute=utemin,utemax,-',
                  'CDEF:inne=innemin,innemax,-',
                  'VDEF:uteminnu=utemin,MINIMUM',
                  'VDEF:utemaxnu=utemax,MAXIMUM',
                  'VDEF:inneminnu=innemin,MINIMUM',
                  'VDEF:innemaxnu=innemax,MAXIMUM',
                  'LINE1:utemin#0000FF',
                  'AREA:ute#CCCCF0::STACK',
                  'LINE2:uteavg#0000FF:Ute',
                  'GPRINT:uteminnu:Min %4.1lf',
                  'GPRINT:utemaxnu:Max %4.1lf',
                  'LINE1:utemax#0000FF',
                  'LINE1:innemin#00FF00',
                  'AREA:inne#CCF0CC::STACK',
                  'LINE2:inneavg#00FF00:Inne',
                  'GPRINT:inneminnu:Min %4.1lf',
                  'GPRINT:innemaxnu:Max %4.1lf',
                  'LINE1:innemax#00FF00',
                  )

### Main
if __name__ == '__main__':
    #Read all sensors
    path1w=(
        "/sys/bus/w1/devices/28-0316a09e49ff/w1_slave",  
        "/sys/bus/w1/devices/28-0516a09274ff/w1_slave"	
    )
    data=read_all(path1w)
    # Add to db
    rrdtool.update(db,data)

    # Do plotting
    if (time.time() % 900) < 60:
	# new plots every 15 min
        plot_hour()
        plot_day()
    if (time.time() % 86400) < 60:
        # new month plot once per day
        plot_month()

