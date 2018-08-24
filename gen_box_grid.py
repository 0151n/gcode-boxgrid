# generate grid of boxes
# Oisin O'Halloran 2018
# ---------- 
# input:
# bit size
# safe height
# depth per cut
# box width, height, depth
# x,y space
# x,y number of boxes
# name of output file

import datetime

#get input
bsize = float(raw_input("BIT SIZE:"))
safez = float(raw_input("SAFE Z HEIGHT:"))
cutdpth = float(raw_input("DEPTH PER CUT:"))
feed = int(raw_input("FEED RATE:"))
boxw = float(raw_input("BOX WIDTH:"))
boxh = float(raw_input("BOX HEIGHT:"))
boxd = float(raw_input("BOX DEPTH:"))
spcx = float(raw_input("HORIZONTAL SPACE:"))
spcy = float(raw_input("VERTICAL SPACE:"))
gx = int(raw_input("NUMBER OF COLUMNS OF BOXES:"))
gy = int(raw_input("NUMBER OF ROWS OF BOXES:"))
filename = raw_input("FILENAME:")

#open file
out = open(filename,"w")

#write base commands
out.write("(generated on: " + datetime.datetime.today().strftime("%d-%b-%Y %I:%M") + ")\n") 
out.write("(bit size = " + str(bsize) + ")\n")
out.write("(safez = " + str(safez) + ")\n")
out.write("(cut depth = " + str(cutdpth) + ")\n")
out.write("(feed = " + str(feed) + ")\n")

out.write("(boxw = " + str(boxw) + ")\n")
out.write("(boxh = " + str(boxh) + ")\n")
out.write("(boxd = " + str(boxd) + ")\n")

out.write("(spcx = " + str(spcx) + ")\n")
out.write("(spcy = " + str(spcy) + ")\n")

out.write("(columns = " + str(gx) + ")\n")
out.write("(rows = " + str(gy) + ")\n")

out.write("G21\n") #set to millimeters
out.write("M3\n") #turn on spindle

x = 0 #cutter x
y = 0 #cutter y
z = 0 #cutter z

#move cutter head to relative position using linear interpolation (G1)
def cut(cx, cy, cz):
    global x,y,z
    x += cx
    y += cy
    z += cz
    out.write("G1 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F" + str(feed) + "\n")

#move cutter head to relative position in fast mode (G0)
def go(cx, cy, cz):
    global x,y,z
    x += cx
    y += cy
    z += cz
    out.write("G0 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F" + str(feed) + "\n")

#move cutter by absolute position in fast mode (G0)
def go_abs(cx, cy, cz):
    global x,y,z
    x = cx
    y = cy
    z = cz
    out.write("G0 X" + str(x) + " Y" + str(y) + " Z" + str(z) + " F" + str(feed) + "\n")


#function to cut boxes
#starts and ends at safez
def cut_box():
    global x,y,z
    #initial offset
    go((bsize / 2),(bsize / 2),-safez)
    #loop through box
    vcuts = int(boxw / bsize)
    rem = boxw % bsize
    for j in range(1,int(boxd / cutdpth) + 1):
        #drop down cut depth
        cut(0,0,-(j * cutdpth))
        print(-j * cutdpth) 
        #check if even
        extra = False
        if vcuts % 2 == 0:
            vcuts_m = vcuts / 2
        else:
            vcuts_m = vcuts - 1
            vcuts_m /= 2
            extra = True
      
        #cut all normal cuts
        for i in range(0,vcuts_m):
            #cut down boxh
            cut(0,boxh - bsize,0)
            #move across to next slot
            cut(bsize,0,0)
            #cut up to top
            cut(0,0 - (boxh - bsize),0)
            #move to next slot as long as its not the last cut
            if(i != vcuts_m - 1):
                cut(bsize,0,0)

        #run extra cut for odd numbered total vertical cuts
        if(extra):
            #cut into new slot
            cut(bsize,0,0)
            #cut down
            cut(0,boxh - bsize,0) 
            #move to top
            cut(0,0 - (boxh - bsize),0)

        #cut remainder extra outside bitsize
        if(rem > 0):
            #cut into new slot, moving in by remainder space
            cut(rem,0,0)
            #cut down
            cut(0,boxh - bsize,0) 
            #move to top
            cut(0,0 - (boxh - bsize),0)
        
        #move up to safez
        go_abs(x,y,safez)
        #move to start
        go(0 - boxw + bsize,0,0)
        go(0,0,0 -safez)
    go(0,0,safez)
    go(-(bsize / 2),-(bsize / 2),0)

go(0,0,safez)
for i in range(0,gy):
    for j in range(0,gx):
        #cut a box
        cut_box()
        #move across on xaxis to start of next box
        go(boxw + spcx,0,0)
    #move dow to new row and back to start of row
    go(0 - (gx * boxw) - (gx * spcx),boxh + spcy,0)
#move to starting position
go_abs(0,0,safez)
