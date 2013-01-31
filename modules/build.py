# coding: gbk
"""
生成hosts原始文件
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

    def build(self):
        #编码控制
        subdir = ''
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
                self.toZip(subdir)          #压缩
        self.combine.delTmpDir()
    
    def export(self, subdir, ip, coding, ADflag = True):
        #生成文件
        type = sys.getfilesystemencoding()
        if os.path.exists(self.rawdir + subdir) == False:
            os.mkdir(self.rawdir + subdir)
        outstream = open(self.rawdir + subdir + 'hosts', 'w')
        #写主文件
        instream = open(self.dir + self.tmpdir + self.mainfile_pre + ip + self.fileext, 'rU')
        lines = instream.readlines()
        for line in lines:
            outstream.write(line.decode(type).encode(coding, 'ignore'))
        instream.close()
        #写ADBlock文件
        if ADflag:
            instream = open(self.dir + self.tmpdir + self.adfile + self.fileext, 'rU')
            lines = instream.readlines()
            for line in lines:
                outstream.write(line.decode(type).encode(coding, 'ignore'))
        outstream.close()
        if coding == 'utf-8':
            convertfile(self.rawdir + subdir + 'hosts')
        
    
    def toZip(self, subdir):
        #生成压缩包
        f = zipfile.ZipFile(self.zipdir + subdir[0:-1] + '.zip', 'w', zipfile.ZIP_DEFLATED)
        f.write(self.rawdir + subdir + self.filename, self.filename)
        f.close() 
        
if __name__ == '__main__':
    build = buildRAW('./', '../downloads/raw/', '../downloads/zip/')
    build.build()
    print('Done!')