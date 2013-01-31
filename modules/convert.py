# coding: gbk
"""
文件转换工具：Dos文件转Unix
"""
import re, os

def convert_line_endings(temp, mode): 
    #替换换行符
    if mode in ['u', 'p']: #unix, posix  
        temp = temp.replace('\r\n', '\n')  
        temp = temp.replace('\r', '\n')  
    elif mode == 'm':      #mac (before Mac OS 9)  
        temp = temp.replace('\r\n', '\r')  
        temp = temp.replace('\n', '\r')  
    elif mode == 'w':      #windows  
        temp = re.sub("\r(?!\n)|(?<!\r)\n", "\r\n", temp)  
    return temp  
    
def convertfile(filename):
    #转换文件
    statinfo = None 
    with file(filename, 'rb+') as f:  
        data = f.read() 
        newdata = convert_line_endings(data, 'u')
        if (data != newdata):
            statinfo = os.stat(filename)
            f.seek(0)  
            f.write(newdata)  
            f.truncate()
    if statinfo:  
        os.utime(filename, (statinfo.st_atime, statinfo.st_mtime))