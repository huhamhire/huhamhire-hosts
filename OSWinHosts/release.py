# coding: gbk
"""
生成hosts原始文件
"""
import os, shutil
import zipfile

class releaseHostsPanel:
    def __init__(self, dir, downdir, relname):
        #初始化
        self.bindir = dir + 'WinHosts/bin/'
        self.reldir = 'Release/'
        self.binfile = 'HostsPanel.exe'
        self.downdir = downdir
        if os.path.exists(self.downdir) == False:
            os.mkdir(self.downdir)
        self.relname = relname
        
    def toZip(self, destination):
        #生成压缩包
        f = zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED)
        f.write(self.bindir + self.reldir + self.binfile, self.binfile)
        f.close() 

    def delBinDir(self):
        #删除临时目录
        shutil.rmtree(self.bindir)
        
    def run(self):
        self.toZip(self.downdir + self.relname + '.zip')
        self.delBinDir()
        
if __name__ == '__main__':
    rel = releaseHostsPanel('./', '../downloads/win/', 'HostsPanel_win_1.0beta')
    try:
        rel.run()
        print('Done!')
    except WindowsError:
        print('Bin file not exists!')