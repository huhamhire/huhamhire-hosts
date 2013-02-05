#!/usr/bin/python
# -*- coding: utf-8 -*-
U"""
合并hosts模块文件
"""
import os
import shutil

from convert import convertfile

class combineHosts:
    def __init__(self, dir):
        #运行路径
        self.dir = dir
        self.IPvX = ['ipv4', 'ipv6']
        #核心模块
        self.coremods = ['google', 'youtube', 'facebook', 'twitter', 'wikipedia', 'other']
        self.sharemods = ['activation', 'apple']
        self.coredir = '_mods/'
        self.sharedir = 'share_mods/'
        #主模块
        self.modules = ['info', 'timestamp', 'localhost']
        #广告屏蔽模块
        self.admods = ['hostsx','mwsl', 'yoyo', 'mvps']
        self.adfile = 'adblock'
        self.adsubdir = 'adblock_mods/'        
        #扩展名设置
        self.fileext = '.hosts'
        
        #资源文件编码
        self.coding = 'utf-8'
        
        #建立临时路径
        self.tmpdir = 'tmp/'
        try:
            os.makedirs(dir + self.tmpdir)
        except WindowsError:
            pass
        
    def combineCore(self, ip):
        #合并核心列表
        
        #设定模块
        mods = []
        mods.append(self.sharedir + self.sharemods[0])
        for mod in self.coremods:
            mods.append(ip + self.coredir + mod)
        mods.append(self.sharedir + self.sharemods[1])
        
        self.corefile = self.tmpdir + 'core_' + ip
        #操作信息
        corefile = self.dir + self.corefile + self.fileext
        print("Preparing corefile: '%s'" % (corefile))
        
        outstream = open(corefile, 'w')
        
        #合并操作
        for module in mods:
            modfile = self.dir + module + self.fileext
            #反馈状态
            print("%s -> %s" % (modfile, corefile))
            instream = open(modfile, 'r')
            lines = instream.readlines()
            for line in lines:
                outstream.write(line.decode(self.coding).encode(self.coding, 'ignore'))
            instream.close()
            outstream.write('\n')
        outstream.close()
        print('')
        #规范编码及换行符
        convertfile(corefile)
        
    def combineMain(self, ip):
        #合并主列表
        self.outfile = self.tmpdir + 'main_' + ip
        self.corefile = self.tmpdir + 'core_' + ip
        #操作信息
        mainfile = self.dir + self.outfile + self.fileext
        print("Preparing main tempfile: '%s'" % (mainfile))
        
        outstream = open(self.dir + self.outfile + self.fileext, 'w')
        mods = self.modules
        mods.append(self.corefile)
        for module in mods:
            modfile = self.dir + module + self.fileext
            #反馈状态
            print("%s -> %s" % (modfile, mainfile))
            instream = open(modfile, 'r')
            lines = instream.readlines()
            for line in lines:
                outstream.write(line.decode(self.coding).encode(self.coding, 'ignore'))
            instream.close()
            outstream.write('\n')
        outstream.close()
        
        #规范编码及换行符
        convertfile(mainfile)
        
        # Core文件删除信息
        print("remove corefile: '%s'" % (self.corefile))
        
        mods.remove(self.corefile)                                      #删除自有模块
        os.remove(self.dir + self.corefile + self.fileext)              #删除核心文件
        print('')
    
    def combineAdblock(self):
        #合并广告屏蔽列表
        adfile = self.dir + self.tmpdir + self.adfile + self.fileext
        print("Preparing ADblock tempfile: '%s'" % (adfile))
        
        outstream = open(adfile, 'w')
        outstream.write('# region adblock\n\n')
        mods = self.admods
        for module in mods:
            modfile = self.dir + self.adsubdir + module + self.fileext
            #反馈状态
            print("%s -> %s" % (modfile, adfile))
            instream = open(modfile, 'r')
            lines = instream.readlines()
            for line in lines:
                outstream.write(line.decode(self.coding).encode(self.coding, 'ignore'))
            instream.close()
            outstream.write('\n')
            
        outstream.write('# endregion')
        outstream.close()
        print('')
        #规范编码及换行符
        convertfile(adfile)
    
    def run(self):
        #执行入口
        
        #初始化信息
        print("Preparing tempfiles in: '%s' ..." % (self.dir + self.tmpdir))
        print('-' * 50)
        for cate in self.IPvX:
            self.combineCore(cate)          #合并核心文件
            self.combineMain(cate)          #合并主文件
        self.combineAdblock()
    
    def delTmpDir(self):
        #删除临时目录
        tmpdir = self.dir + self.tmpdir
        print("Remove tempdirectory: '%s'" % (tmpdir))
        shutil.rmtree(tmpdir)
        
if __name__ == '__main__':
    ops = combineHosts('./')
    ops.run()
    print('Done!')
