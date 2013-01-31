using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Media;
using System.Text;
using System.Windows.Forms;

using WinHosts.Properties;

namespace WinHosts
{
    class FileOps
    {
        #region 必要文件及目录检查
        /// <summary>
        /// 检查依赖文件是否存在
        /// </summary>
        /// <returns>所需问价是否齐全</returns>
        private static bool CheckFiles()
        {
            bool check = true;
            string[] fileList = new string[2]{
                @"resources\ipv4_win_ansi\hosts",
                @"resources\ipv6_win_ansi\hosts"
            };
            string CurrentDir = Environment.CurrentDirectory;

            foreach (string entry in fileList)
            {
                string TargetFile = Path.Combine(CurrentDir, entry);
                check &= File.Exists(TargetFile);
            }

            return check;
        }

        /// <summary>
        /// 检查单个依赖文件是否存在
        /// </summary>
        /// <param name="id">文件号： 0:ipv4; 1:ipv6;</param>
        /// <returns>是否存在</returns>
        private static bool CheckFile(int id)
        {
            bool check = true;
            string[] fileList = new string[2]{
                @"resources\ipv4_win_ansi\hosts",
                @"resources\ipv6_win_ansi\hosts",
            };
            string CurrentDir = Environment.CurrentDirectory;

            string TargetFile = Path.Combine(CurrentDir, fileList[id]);
            check &= File.Exists(TargetFile);

            return check;
        }

        /// <summary>
        /// 检查并建立必要目录
        /// </summary>
        private static void CheckDirs()
        {
            string CurrentDir = Environment.CurrentDirectory;
            string[] dirs = new string[3] 
                { @"resources", @"resources\ipv4_win_ansi", @"resources\ipv6_win_ansi" };
            foreach (string entry in dirs)
            {
                string dir = Path.Combine(CurrentDir, entry);
                if (!Directory.Exists(dir))
                    Directory.CreateDirectory(dir);//文件夹不存在，创建该文件夹
            }
        }
        #endregion

        #region 下载hosts文件
        /// <summary>
        /// 从服务器获取hosts文件
        /// </summary>
        /// <param name="URL">统一资源定位符</param>
        /// <param name="filename">本地文件路径</param>
        /// <param name="prog">窗体进度条，若无，可为null</param>
        private static void GetFile(string URL, string filename, DownBox prog)
        {
            try
            {
                HttpWebRequest DownLink = (HttpWebRequest)HttpWebRequest.Create(URL);
                DownLink.Timeout = 10000;       //请求超时时间10s

                HttpWebResponse Source = (HttpWebResponse)DownLink.GetResponse();
                long totalBytes = Source.ContentLength;
                if (totalBytes == -1) totalBytes = 2 * 1024 * 1024;     //若无法获取文件大小，设默认为2MB

                Stream StreamTotal = Source.GetResponseStream();
                Stream StreamOut = new FileStream(filename, FileMode.Create);
                long totalDownloadedByte = 0;
                byte[] by = new byte[1024];
                int OutSize = StreamTotal.Read(by, 0, (int)by.Length);
                while (OutSize > 0)
                {
                    totalDownloadedByte = OutSize + totalDownloadedByte;
                    Application.DoEvents();
                    StreamOut.Write(by, 0, OutSize);
                    if (prog != null)
                    {
                        prog.SetPoint((int)(totalDownloadedByte * 100 / totalBytes));
                    }
                    OutSize = StreamTotal.Read(by, 0, (int)by.Length);
                }
                //完成进度条
                if (prog != null)
                {
                    prog.SetPoint(100);
                }
                SoundPlayer snd = new SoundPlayer(Resources.ding);
                snd.Play();

                StreamOut.Close();
                StreamTotal.Close();
            }
            catch
            {
                //网络错误操作
                msg.SetDialog(3, Resources.msg_err_net);
                msg.ShowDialog();
                throw;
            }
        }

        /// <summary>
        /// 根据模式设定下载hosts文件
        /// </summary>
        /// <param name="insmode">选择hosts文件来源：0:本地; 1:Googlecode; 2: Sourceforge; 3: Github</param>
        /// <param name="IPmode">IP协议选择: false:IPv4; true:IPv6</param>
        /// <param name="downForm">下载反馈窗口</param>
        private static void DownFile(int insmode, bool IPmode, DownBox downForm)
        {
            string[] DownPath = new string[4] {
                "", @"http://huhamhire-hosts.googlecode.com/git/downloads/raw/",
                @"http://hosts.huhamhire.com/downfile/raw/",
                @"https://github.com/huhamhire/huhamhire-hosts/raw/master/downloads/raw/"};
            string[] IpPath = new string[2] { @"ipv4", @"ipv6" };

            //初始化路径
            string url;
            string localPath = Path.Combine(Environment.CurrentDirectory, @"resources");

            if (insmode > 0)
            {
                url = DownPath[insmode] + IpPath[(IPmode ? 1 : 0)] + @"_win_ansi/hosts";
                localPath = Path.Combine(localPath, (IpPath[(IPmode ? 1 : 0)] + @"_win_ansi"), @"hosts");
                if (downForm != null)
                {
                    downForm.SetPoint(0);
                }
                GetFile(url, localPath, downForm);

                //对来自GoogleCode的文件转码
                if (insmode == 1)
                    ReEncode(localPath);
                return;
            }
            else
                return;
        }

        /// <summary>
        /// 重新编码下载后的文件
        /// </summary>
        /// <param name="FilePath">文件路径</param>
        private static void ReEncode(string FilePath)
        {
            List<string> hostsStream = new List<string>();
            hostsStream.Clear();
            using (StreamReader reader = new StreamReader(FilePath, Encoding.Default))
            {
                string line = reader.ReadLine();
                while (line != null)
                {
                    hostsStream.Add(line);
                    line = reader.ReadLine();
                }
            }
            File.Delete(FilePath);

            //缓存文件流
            FileStream outfile = new FileStream(FilePath, FileMode.Append);
            StreamWriter fileWriter = new StreamWriter(outfile, Encoding.Default);
            fileWriter.BaseStream.Seek(0, SeekOrigin.End);

            //输出文件
            string[] region = hostsStream.ToArray();
            for (int i = 0; i < region.Length; i++)
            {
                if (i < region.Length - 1)
                    fileWriter.WriteLine(region[i]);
                else
                    fileWriter.Write((region[i]));
            }
            fileWriter.Flush();
            fileWriter.Close();
        }
        #endregion

        /// <summary>
        /// 信息提示窗口
        /// </summary>
        private static ErrorBox msg = new ErrorBox();

        /// <summary>
        /// 文件操作主入口
        /// </summary>
        public static void ProceedFileOps(int setting, mainFrame mainForm)
        {
            string config_stream = Convert.ToString(setting, 2).PadLeft(16, '0');
            bool IP_flag = Convert.ToBoolean(config_stream[9] - 0x30);                   //根据第10位设置IP协议模式
            int insmode = (config_stream[12] - 0x30) * 2 + (config_stream[13] - 0x30);  //根据第13, 14位设置安装源

            CheckDirs();                            //检查依赖文件目录
            if (insmode == 0)                       //判断是否为本地安装模式
            {
                if (CheckFile(IP_flag ? 1 : 0))     //检查依赖文件是否存在
                    return;
                else
                {
                    //依赖文件不存在时自动下载相关文件
                    insmode = 1;
                    msg.SetDialog(1, Resources.msg_info_ins);
                    msg.ShowDialog();
                }
            }

            DownBox downprog = new DownBox(mainForm);
            mainForm.Enabled = false;       //锁定主窗口
            downprog.Show();
            try
            {
                DownFile(insmode, IP_flag, downprog);
                downprog.Close();
                mainForm.Enabled = true;        //解锁主窗口
                mainForm.BringToFront();        //前置主窗口
                return;
            }
            catch
            {                                   //异常操作
                downprog.Close();
                mainForm.Enabled = true;        //解锁主窗口
                mainForm.BringToFront();        //前置主窗口
                throw;
            }

        }

    }
}