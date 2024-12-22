import datetime
from DiskManager import DiskManager  
from DBConfig import DBConfig
from BufferManager import BufferManager
import struct
import time

class MyClass:
    def __init__(self, name):
        self.name = name


db_config = DBConfig.load_db_config("./config1.json")
disk_manager = DiskManager(db_config)
text = ""
text2 = ""
siiize = db_config.pageSize 
BufferPool = BufferManager(db_config,disk_manager)
new_epoch = datetime.datetime(2024, 10, 1)
epoch_difference = (new_epoch - datetime.datetime(1970, 1, 1)).total_seconds()
time1 =float((time.time() - epoch_difference)*1000000)
time.sleep(2)

for i in range(db_config.pageSize):
    text += "X"
    text2 += "y"


for i in range(10):
    newpage = disk_manager.AllocPage()
#    print(newpage)
    disk_manager.WritePage(newpage, text.encode("utf-8") )

#bytearray1 = bytearray()
#bytearray1 = disk_manager.ReadPage(newpage)
#print(bytearray1)
    
    bytearray1 = BufferPool.GetPage(newpage)
#    print(time1 - struct.unpack("i", BufferPool.buffer_pool[bytearray1][16:20])[0])
    time.sleep(1.5)


time.sleep(5)

for i in range(3):
    newpage = disk_manager.AllocPage()
#    print(newpage)
    disk_manager.WritePage(newpage, text.encode("utf-8") )

#bytearray1 = bytearray()
#bytearray1 = disk_manager.ReadPage(newpage)
#print(bytearray1)
    
    bytearray1 = BufferPool.GetPage(newpage)
#    print(time1 - struct.unpack("i", BufferPool.buffer_pool[bytearray1][16:20])[0])
    time.sleep(1.5)


#for i in range(10):
#    print(struct.unpack('i', BufferPool.buffer_pool[i][:4])[0])
#    print(struct.unpack('i', BufferPool.buffer_pool[i][4:8])[0])
#    print("**********" + i + "************\n" + BufferPool.buffer_pool[i])
#    print(struct.unpack('i', BufferPool.buffer_pool[i][8:12])[0])
#    print(struct.unpack('i', BufferPool.buffer_pool[i][12:16])[0])
#    print(struct.unpack('f', BufferPool.buffer_pool[i][16:20])[0])
#
#for i in range(10):
#    bytearray1 = BufferPool.buffer_pool[2]
#    print( "********" + str(i) + "********")
#    print(struct.unpack('i', bytearray1[:4])[0])
#    print(struct.unpack('i', bytearray1[4:8]))
#    print(struct.unpack('i', bytearray1[8:12]))
#    print(struct.unpack('i', bytearray1[12:16]))
#    print(struct.unpack('f', bytearray1[16:20])[0])

