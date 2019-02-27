import bpy
import os
obj = bpy.context.active_object
i = 0
list = []
for vert in obj.data.vertices:
    coord = vert.co
    if coord[2] > 0:
        #print(coord[0], coord[1], coord[2])
        i += 1
        string = "{0:08d} {1} {2} {3}".format(i, coord[0], coord[1], coord[2])
        list.append(string)


print(i)
for string in list:
    print (string)
    
file = open("D:\icosphere-8.lp", "w")
file.write(str(i))
file.write('\n')
for line in list:
    file.write(line)
    file.write('\n')

file.close()
