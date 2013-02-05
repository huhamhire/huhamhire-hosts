#!/usr/bin/python
# -*- coding: utf-8 -*-
U"""
生成hosts原始文件及Zip文件
"""
import sys, os
import zipfile

from combine import combineHosts
from convert import convertfile

class buildRAW:
    def __init__(self, dir, rawdir, zipdir):
        #运行路径
        self.dir = dir
        #输出路径
        self.rawdir = rawdir
        if os.path.exists(self.rawdir) == False:
            os.mkdir(self.rawdir)
        self.zipdir = zipdir
        if os.path.exists(self.zipdir) == False:
            os.mkdir(self.zipdir)
        #创建中间文件
        self.combine = combineHosts(dir)
        self.combine.run()
        
        #参数设置
        self.IPvX = ['ipv4', 'ipv6']
        self.platforms = ['win', 'unix', 'mobile']
        self.encodings = ['ansi', 'utf8']
        self.filename = 'hosts'
        self.mainfile_pre = 'main_'
        self.adfile = 'adblock'
        self.fileext = '.hosts'     #扩展名
        self.tmpdir = 'tmp/'
        
        #资源文件编码
        self.coding = 'utf-8'
        
    def build(self):
        #编码控制
        subdir = ''
        
        #初始化信息
        print('Start building hosts')
        print('-' * 50)
        
        for ip in self.IPvX:
            for platform in self.platforms:
                if platform == 'win':
                    subdir = ip + '_' + platform + '_' + self.encodings[0] + '/'
                    self.export(subdir, ip, 'gb2312')
                elif platform == 'mobile':
                    subdir = ip + '_' + platform + '_' + self.encodings[1] + '/'
                    self.export(subdir, ip, 'utf-8', False)
                else:
                    subdir = ip + '_' + platform + '_' + self.encodings[1] + '/'
                    self.export(subdir, ip, 'utf-8')
                
                #输出信息
                print("Building '%s' ..." % ('raw/' + subdir + 'hosts'))
                print("Compressing to '%s' ..." % ('zip/' + subdir[0:-1] + '.zip'))
                
                #压缩为ZIP
                self.toZip(subdir)
        #删除临时文件
        self.combine.delTmpDir()
        
        print('-' * 50)
        print('Done!')
    
    def export(self, subdir, ip, coding, ADflag = True):
        #生成文件
        if os.path.exists(self.rawdir + subdir) == False:
            os.mkdir(self.rawdir + subdir)
        outstream = open(self.rawdir + subdir + 'hosts', 'w')
        #写主文件
        instream = open(self.dir + self.tmpdir + self.mainfile_pre + ip + self.fileext, 'rU')
        lines = instream.readlines()
        for line in lines:
            outstream.write(line.decode(self.coding).encode(coding, 'ignore'))
        instream.close()
        #写ADBlock文件
        if ADflag:
            instream = open(self.dir + self.tmpdir + self.adfile + self.fileext, 'rU')
            lines = instream.readlines()
            for line in lines:
                outstream.write(line.decode(self.coding).encode(coding, 'ignore'))
        outstream.close()
        if coding == 'utf-8':
            convertfile(self.rawdir + subdir + 'hosts')
        
    
    def toZip(self, subdir):
        #生成压缩包
        f = zipfile.ZipFile(self.zipdir + subdir[0:-1] + '.zip', 'w', zipfile.ZIP_DEFLATED)
        f.write(self.rawdir + subdir + self.filename, self.filename)
        f.close() 
        
def clear():
    # 清理运行生成的二进制文件
    os.remove('convert.pyc')
    os.remove('combine.pyc')

if __name__ == '__main__':
    build = buildRAW('./', '../downloads/raw/', '../downloads/zip/')
    build.build()
    clear()
    