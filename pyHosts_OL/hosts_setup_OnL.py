# -*- coding: UTF-8 -*-
# by huhamhire
import urllib
import sys
import time
import os
import socket
import shutil
import getpass

SF_mirror_list = {'superb-dca2': ('Superb Internet', 'United States'), 'aarnet': ('AARNet', 'Melbourne Australia'), 'cdnetworks-kr-1': ('CDNetworks', 'Seoul, Korea, Republic of'),
                  'cdnetworks-kr-2': ('CDNetworks', 'Seoul, Korea, Republic of'), 'cdnetworks-us-2': ('CDNetworks', 'Cumming, GA'), 'dfn': ('German Research Network', 'Germany'),
                  'freefr': ('Free France', 'Paris, France'), 'garr': ('garr.it', 'Ancona, Italy'), 'heanet': ('HEAnet', 'Ireland'), 'hivelocity': ('HiVelocity', 'Tampa, FL'),
                  'internode': ('Internode', 'Adelaide, Australia'), 'iweb': ('iWeb', 'Montreal, QC'), 'jaist': ('JAIST', 'Nomi, Japan'),
                  'nchc': ('NCHC', 'Taipei, Taiwan'), 'netcologne': ('NetCologne', 'Koln, Germany'), 'softlayer': ('Softlayer', 'Dallas, TX'),
                  'switch': ('SWITCH', 'Zurich, Switzerland'), 'tenet': ('TENET', 'Wynberg, South Africa'), 'ufpr': ('C3SL', 'Curitiba, Brazil'),
                  'voxel': ('Voxel Hosting', 'New York, NY'), 'waix': ('Waix', 'Perth, Australia')}
                  #Sourceforge 镜像站点信息：{'Short Name': ('Provider', 'Location')}

startTime = time.time()
url = ''
etc = ''
tmp = ''
fname = ''
hostname = ''
url_tail = ''

def dash():
    for i in range(79):
        sys.stdout.write('-')
    print 

def initial():
    type = sys.getfilesystemencoding()
    print ('         ----------------- 欢迎使用 huhamhire hosts ----------------- ').decode('utf-8').encode(type)
    print ('        |    由于本安装需要连接Internet连接，在安装前请确认您已连接  |').decode('utf-8').encode(type)
    print ('        |  互联网。如在安装过程中遇到网络问题，请检查您的网络并尝试  |').decode('utf-8').encode(type)
    print ('        |  重新安装。修改 hosts要较高用户权限，安装前请确认您已提升  |').decode('utf-8').encode(type)
    print ('        |  相应权限。其余问题可以直接联系我们。                      |').decode('utf-8').encode(type)
    print ('        |  URL: http://code.google.com/p/huhamhire-hosts/            |').decode('utf-8').encode(type)
    print ('        |                                                            |').decode('utf-8').encode(type)

def choice():
    type = sys.getfilesystemencoding()
    print ('        |    请选择您需要的操作：                                    |').decode('utf-8').encode(type)
    print ('        |      1.安装 IPv4 版 hosts 文件（默认）                     |').decode('utf-8').encode(type)
    print ('        |      2.安装 IPv6 版 hosts 文件                             |').decode('utf-8').encode(type)
    print ('        |      3.恢复备份的 hosts 文件                               |').decode('utf-8').encode(type)
    print ('        |      4.设定使用移动简化版 hosts 文件                       |').decode('utf-8').encode(type)
    print ('        |      5.退出                                                |').decode('utf-8').encode(type)
    print ('         ------------------------------------------------------------ ').decode('utf-8').encode(type)
    print

def cbk(a, b, c):
    '''回调函数
    @a: 已经下载的数据块
    @b: 数据块的大小
    @c: 远程文件的大小
    '''
    type = sys.getfilesystemencoding()
    if c == 0:
        raise IOError
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    etime = (time.time() - startTime)
    rate = a * b / float(etime) / 1024
    size = float(c) / 1024
    if size >= 1024:
        size = "%.1fMB" % (size / 1024)
    elif int(size) > 0:
        size = '%dKB' % (size)
    else:
        size = "未知"
        raise IOError
    if rate < 1:
        rate = '%3dB/s' % (rate * 1024)
    else:
        rate = '%.1fKB/s' % (rate)
    print ('\r    文件大小：%s.........................已下载：%05.2f%%(速度：%s)' % (size, per, rate)).decode('utf-8').encode(type),
    if per == 100:
        print

def set_os():       
    #获取操作系统信息，返回本机机器名, etc, tmp, fname
    system = os.name
    if system == 'nt':
        tmp = 'C:\\temp\\hosts'
        if not os.path.exists(r'C:/temp/'):
            os.makedirs(r'C:/temp/')
        etc = os.getenv('WINDIR') + '\System32\drivers\etc\hosts'
        fname = 'win_ansi'
        hostname = os.getenv('computername')
        return hostname, etc, tmp, fname
    elif system == 'posix':
        if sys.platform == 'darwin':
            tmp = '/private/tmp/hosts'
            if not os.path.exists(r'/private/tmp/'):
                os.makedirs(r'/private/tmp/')
            etc = '/private/etc/hosts'
            fname = 'unix_utf8'
            hostname = socket.gethostname()[0:-6]
            return hostname , etc, tmp, fname
        else:
            tmp = '/tmp/hosts'
            if not os.path.exists(r'/tmp/'):
                os.makedirs(r'/tmp/')
            etc = '/etc/hosts'
            fname = 'unix_utf8'
            try:
                hostname = socket.gethostname()
            except:
                hostname = 'unknown'
            ''' #Only works on Debian Linux
            with open(etc[0:-1] + 'name','r') as hosts:
                hostname = hosts.readline()[0:-1]
                hosts.close()
            '''
            return hostname, etc, tmp, fname
    else:
        return 'Unknown System!'

def choose(etc, fname, site):
    #选择hosts文件版本(IPv4/IPv6)
    type = sys.getfilesystemencoding()
    print('请选择[1,2,3,4,5]：').decode('utf-8').encode(type),
    try:
        cmd = raw_input()
    except:
        print ('\n                                                                  安装已取消.').decode('utf-8').encode(type)
        dash()
        print ('安装未完成，请按Enter键退出.').decode('utf-8').encode(type)
        try:
            raw_input()
        except KeyboardInterrupt:
            raise
        except:
            pass
        exit()
    dash()
    if cmd == '5':
        exit()
    elif cmd == '4':
        fname = 'mobile_utf8'
        print ('当前使用移动设备简化版 hosts 文件。如需安装完整版，请退出后重新开始安装。').decode('utf-8').encode(type)
        print ('请按Enter键继续安装.').decode('utf-8').encode(type)
        try:
            raw_input()
        except KeyboardInterrupt:
            print ('                                                                  安装已取消.').decode('utf-8').encode(type)
            dash()
            print ('安装未完成，请按Enter键退出.').decode('utf-8').encode(type)
            try:
                raw_input()
            except KeyboardInterrupt:
                raise
            except:
                pass
            exit()
        except:
            pass
        print ('         ------------------------------------------------------------ ').decode('utf-8').encode(type)
        choice()
        return choose(etc, fname, site)
    elif cmd == '3':
        roll_back(etc, site)        #恢复备份hosts.bak
    system = os.name
    if system == 'nt':
        print ('您好! Windows 用户，').decode('utf-8').encode(type),
    elif system == 'posix':
        if sys.platform == 'darwin':
            print ('您好! Mac OS X 用户，').decode('utf-8').encode(type),
        else:
            print ('您好! Linux 用户，').decode('utf-8').encode(type),
    else:
        pass
    if cmd == '2':
        choose_url = site[0] + 'ipv6_' + fname + '/hosts' + site[1]
        print ('现在开始安装 IPv6 版hosts文件').decode('utf-8').encode(type)
        return choose_url
    else:
        choose_url = site[0] + 'ipv4_' + fname + '/hosts' + site[1]
        print ('现在开始安装 IPv4 版hosts文件\n').decode('utf-8').encode(type)
        return choose_url

def download(etc, tmp, fname):
    #下载hosts文件
    url = choose(etc, fname, site)
    type = sys.getfilesystemencoding()
    print ('第 1 阶段，共 3 阶段:(1/3)').decode('utf-8').encode(type)
    print ('  下载hosts文件：').decode('utf-8').encode(type)
    print ('    ' + url).decode('utf-8').encode(type)
    socket.setdefaulttimeout(20)
    try:
        urllib.urlretrieve(url, tmp, cbk)
        print ('                                                                    下载成功!').decode('utf-8').encode(type)
    except IOError:
        print ('                                          下载失败，请检查操作权限与网络连接.').decode('utf-8').encode(type)
        dash()
        print ('安装失败，请按Enter键退出.').decode('utf-8').encode(type)
        try:
            raw_input()
        except KeyboardInterrupt:
            raise
        except:
            pass
        exit()
    except KeyboardInterrupt:
        print ('                                                                  下载已取消.').decode('utf-8').encode(type)
        dash()
        print ('安装未完成，请按Enter键退出.').decode('utf-8').encode(type)
        try:
            raw_input()
        except KeyboardInterrupt:
            raise
        except:
            pass
        exit()

def move(etc, tmp):
    #移动文件到etc目录
    type = sys.getfilesystemencoding()
    print ('第 2 阶段，共 3 阶段:(2/3)').decode('utf-8').encode(type)
    print ('  移动hosts文件到: ' + etc).decode('utf-8').encode(type)
    shutil.copyfile(tmp, etc)
    print ('  删除临时文件: ' +tmp).decode('utf-8').encode(type)
    os.remove(tmp)
    print ('                                                                    操作完成!').decode('utf-8').encode(type)

def config(hostname, etc):
    #配置hosts
    type = sys.getfilesystemencoding()
    print ('第 3 阶段，共 3 阶段:(3/3)').decode('utf-8').encode(type)
    print ('  配置hosts文件：').decode('utf-8').encode(type)
    system = os.name
    if system == 'posix':
        if sys.platform == 'darwin':
            print ('    Macintosh用户无需此操作').decode('utf-8').encode(type)
        else:
            with open(etc,'a') as hosts:
                hosts.write(os.linesep)
                hosts.write('#localhost for Linux' + os.linesep)
                print ('    添加条目:(本机) ' + '127.0.1.1    ' + hostname).decode('utf-8').encode(type)
                hosts.write('127.0.1.1    ' + hostname)
                hosts.close()
    elif system == 'nt':
        print ('    Windows用户无需此操作').decode('utf-8').encode(type)
    else:
	    pass
    print ('                                                                    配置完成!').decode('utf-8').encode(type)

def roll_back(etc, site):
    #恢复备份
    type = sys.getfilesystemencoding()
    try:
        shutil.copyfile(etc[0:-5] + 'hosts.bak', etc)
        print ('备份文件已恢复. 请按Enter键继续.').decode('utf-8').encode(type)
        try:
            raw_input()
        except KeyboardInterrupt:
            print ('                                                                  安装已取消.').decode('utf-8').encode(type)
            dash()
            print ('安装未完成，请按Enter键退出.').decode('utf-8').encode(type)
            try:
                raw_input()
            except KeyboardInterrupt:
                raise
            except:
                pass
            exit()
    except IOError:
        print ('备份文件不存在，请直接进行安装. 按Enter键继续.').decode('utf-8').encode(type)
        try:
            raw_input()
        except KeyboardInterrupt:
            print ('                                                                  安装已取消.').decode('utf-8').encode(type)
            dash()
            print ('安装未完成，请按Enter键退出.').decode('utf-8').encode(type)
            try:
                raw_input()
            except KeyboardInterrupt:
                raise
            except:
                pass
            exit()
    print
    print ('         ------------------------------------------------------------ ').decode('utf-8').encode(type)
    main(site)

def argv_err():
    type = sys.getfilesystemencoding()
    print ('参数设定有误. 请使用"-h"获取帮助信息.').decode('utf-8').encode(type)
    exit()

def help():
    type = sys.getfilesystemencoding()
    print ('\n用法: python hosts_setup_OnL.py [-SFM] [-SF [server]] [-?] \n').decode('utf-8').encode(type)
    print ('选项: \n').decode('utf-8').encode(type)
    print ('    -SFM           设定使用 http://www.mirrorservice.org/ 上的 hosts 文件').decode('utf-8').encode(type)
    print ('    -SF [server]   设定使用 SourceForge 镜像服务器上的 hosts 文件').decode('utf-8').encode(type)
    print ('    server         -SF 命令可选参数, 选择 SoureForge 镜像服务器').decode('utf-8').encode(type)
    print ('                   请使用 SF 服务器短地址, 留空默认为 superb-dca2').decode('utf-8').encode(type)
    print ('                   可使用 -ListSF 查询 SF 镜像服务器').decode('utf-8').encode(type)
    print ('    -ListSF        查询 SF 镜像服务器').decode('utf-8').encode(type)
    print ('    -?             显示帮助信息').decode('utf-8').encode(type)
    print ('').decode('utf-8').encode(type)
    print ('不使用参数则默认使用 Google Code 服务器作为下载源.').decode('utf-8').encode(type)
    print ('').decode('utf-8').encode(type)
    print ('运行过程中可使用 Ctrl/Control(Mac)+C 取消操作并退出程序.').decode('utf-8').encode(type)
    print ('').decode('utf-8').encode(type)
    print ('注意: 一次只能使用一条参数, 并在使用时注意检查参数大小写.').decode('utf-8').encode(type)
    exit()

def list_sf():
    type = sys.getfilesystemencoding()
    keys = SF_mirror_list.keys()
    i = 0
    keys.sort()
    print ('\nSourceForge 镜像服务器信息( Enter键继续, P+Enter翻页, Ctrl/Control(Mac)+C退出)：').decode('utf-8').encode(type)
    dash()
    print ('    %s  %s                  %s' % ('镜像服务器短地址', '服务器提供者', '服务器所在国家地区')).decode('utf-8').encode(type)
    print ('    %s  %s                  %s' % ('----------------', '------------', '------------------')).decode('utf-8').encode(type)
    print ('    ').decode('utf-8').encode(type),
    for mirror in keys:
        print ('%-18s%-30s%-16s' % (mirror, SF_mirror_list[mirror][0], SF_mirror_list[mirror][1])).decode('utf-8').encode(type),
        i += 1
        if i < 20:
            print
            print ('    ').decode('utf-8').encode(type),
        else:
            try:
                page = getpass.getpass('')
                print '   ',
                if (page.startswith('p')) or (page.startswith('P')):
                    i = 0
            except KeyboardInterrupt:
                raise
            except:
                pass
    exit()

def main(site):
    type = sys.getfilesystemencoding()
    (hostname, etc, tmp, fname) = set_os()
    choice()
    download(etc, tmp, fname)
    shutil.copyfile(etc, etc[0:-5] + 'hosts.bak')
    move(etc, tmp)
    config(hostname, etc)
    dash()
    print ('安装成功！请按Enter键退出.').decode('utf-8').encode(type)
    try:
        raw_input()
    except KeyboardInterrupt:
        raise
    except:
        pass
    exit()


if __name__ == '__main__':
    site = ('http://huhamhire-hosts.googlecode.com/svn/trunk/core/', '')
    if len(sys.argv) > 1:
        if (sys.argv[1] == '-SFM') and (len(sys.argv) == 2):
            url_front = 'http://www.mirrorservice.org/sites/download.sourceforge.net/pub/sourceforge/h/project/hu/huhamhirehosts/latest%20hosts%20file%28only%29/'
            url_tail = ''   #尾标记，SF镜像留空
            site = (url_front, url_tail)
        elif sys.argv[1] == '-SF':
            url_front = 'http://superb-dca2.dl.sourceforge.net/project/huhamhirehosts/latest%20hosts%20file%28only%29/'
            if len(sys.argv) > 2:
                if sys.argv[2] in SF_mirror_list.keys():
                    url_front = 'http://' + sys.argv[2] + '.dl.sourceforge.net/project/huhamhirehosts/latest%20hosts%20file%28only%29/'
                else:
                    argv_err()
            url_tail = ''   #尾标记，SF留空
            site = (url_front, url_tail)
        elif sys.argv[1] == '-ListSF':
            list_sf()
        elif sys.argv[1] == '-?':
            help()
        else:
            argv_err()
    initial()
    try:
        main(site)
    except SystemExit:
        raise
    except:
        pass