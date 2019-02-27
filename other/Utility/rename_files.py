import os

path = "/media/vips/TOSHIBA EXT/SyntheticRTI/003 - sphere cycles/EXR"
files = os.listdir(path)
for file in files:
    temp = file.split('_')

    newname = "003-{}-{}".format(temp[0], temp[1])

    old_file = os.path.join(path, file)
    new_file = os.path.join(path, newname)
    
    print(old_file)
    print(new_file)
    
    #os.rename(old_file, new_file)
    