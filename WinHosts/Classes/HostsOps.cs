using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Reflection;

using WinHosts.Properties;

namespace WinHosts
{
    class HostsOps
    {
        /// hosts文件相关操作

        #region 备份还原删除操作
        /// <summary>
        /// 备份hosts文件
        /// </summary>
        public static void BackUpHosts()
        {
            //设置操作目录
            string filename = @"hosts";
            string SourcePath = Environment.SystemDirectory + @"\drivers\etc";
            string TargetPath = Environment.CurrentDirectory;

            //设置操作文件
            string SourceFile = Path.Combine(SourcePath, filename);
            string TargetFile = Path.Combine(TargetPath, filename);

            //增加备份时间戳
            string time_stamp = Utilities.CreateStrTimeStamp().ToString();
            TargetFile = TargetFile + @"_" + time_stamp + @".bak";

            //备份hosts文件
            try
            {
                File.Copy(SourceFile, TargetFile, true);
            }
            catch
            {
                //Error hosts文件不存在
                msg.SetDialog(3, Resources.msg_err_back);
            }
        }

        /// <summary>
        /// 删除现有hosts文件
        /// </summary>
        public static void DeleteHosts()
        {
            //设置操作目录
            string filename = @"hosts";
            string SourcePath = Environment.SystemDirectory + @"\drivers\etc";

            //设置操作文件
            string SourceFile = Path.Combine(SourcePath, filename);

            if (File.Exists(SourceFile))
                File.Delete(SourceFile);
        }

        /// <summary>
        /// 恢复hosts文件
        /// </summary>
        public static void RecoverHosts()
        {
            //设置操作目录
            string filename = @"hosts";
            string TargetPath = Environment.SystemDirectory + @"\drivers\etc";
            string SourcePath = Environment.CurrentDirectory;

            //设置操作文件
            string TargetFile = Path.Combine(TargetPath, filename);

            string[] files = Directory.GetFiles(SourcePath);
            string latest = @"";
            foreach (string s in files)
            {
                if (Path.GetExtension(s) == @".bak")
                {
                    if (latest == @"") latest = s;
                    if (s.CompareTo(latest) > 0)
                        latest = s;
                }
            }
            string SourceFile = Path.Combine(SourcePath, latest);

            //还原hosts文件
            if (File.Exists(SourceFile))
            {
                File.Copy(SourceFile, TargetFile, true);
            }
            else
            {
                //Info 独立备份文件不存在，恢复系统初始文件
                msg.SetDialog(1, Resources.msg_info_rec);
                RecoverDefaultHosts();
            }
        }

        /// <summary>
        /// 恢复hosts文件为系统默认
        /// </summary>
        private static void RecoverDefaultHosts()
        {
            string sourceName = "windows_default_hosts";   //资源名
            Assembly asm = Assembly.GetExecutingAssembly();
            Stream pStream = asm.GetManifestResourceStream("WinHosts.Resources.hosts." + sourceName);
            
            //读取内嵌资源
            hostsStream.Clear();
            using (StreamReader reader = new StreamReader(pStream, System.Text.Encoding.Default))
            {
                string line = reader.ReadLine();
                while (line != null)
                {
                    hostsStream.Add(line);
                    line = reader.ReadLine();
                }
            }

            //输出文件
            string TargetFile = Environment.SystemDirectory + @"\drivers\etc";
            TargetFile = Path.Combine(TargetFile, @"hosts");
            FileStream outfile = new FileStream(TargetFile, FileMode.Create);
            StreamWriter fileWriter = new StreamWriter(outfile, Encoding.Default);
            fileWriter.BaseStream.Seek(0, SeekOrigin.End);

            string[] region = hostsStream.ToArray();
            foreach (string entry in region)
            {
                fileWriter.WriteLine(entry);
            }
            fileWriter.Flush();
            fileWriter.Close();
        }

        #endregion

        #region hosts文件生成相关操作
        //hosts文件流容器
        private static List<string> hostsStream = new List<string>();
        private static string[] sectionName = new string[9]
        {
            "google", "facebook", "twitter", "youtube", "activation", 
            "adblock", "apple", "wikipedia", "other"
        };
        //输出顺序设定
        private static int[] regionOrder = new int[9] { 4, 0, 3, 1, 2, 6, 7, 8, 5 };

        /// <summary>
        /// 读取hosts源文件
        /// </summary>
        private static void ReadHosts(string LocalPath)
        {
            //设置操作目录
            string filename = @"hosts";
            string SourcePath = Environment.CurrentDirectory;
            SourcePath = Path.Combine(SourcePath, LocalPath);
            string SourceFile = Path.Combine(SourcePath, filename);

            hostsStream.Clear();
            using (StreamReader reader = new StreamReader(SourceFile, Encoding.Default))
            {
                string line = reader.ReadLine();
                while (line != null)
                {
                    hostsStream.Add(line);
                    line = reader.ReadLine();
                }
            }
        }

        /// <summary>
        /// 生成头部段
        /// </summary>
        private static void AssembleHead()
        {
            string filename = @"hosts.tmp";
            string TargetPath = Environment.CurrentDirectory;
            //设置缓存文件
            string TargetFile = Path.Combine(TargetPath, filename);

            //删除已有temp文件
            if (File.Exists(TargetFile))
                File.Delete(TargetFile);

            //缓存文件流
            FileStream outfile = new FileStream(TargetFile, FileMode.Append);
            StreamWriter fileWriter = new StreamWriter(outfile, Encoding.Default);
            fileWriter.BaseStream.Seek(0, SeekOrigin.End);

            try
            {
                //选取头部段
                string prefix = "# region ";
                int regionStart = 0;
                int regionEnd = hostsStream.IndexOf(prefix + sectionName[regionOrder[0]]);
                int regionCount = regionEnd - regionStart;
                string[] region = hostsStream.GetRange(regionStart, regionCount).ToArray();

                //重新修订时间戳
                for (int i = 0; i < regionCount; i++)
                {
                    Regex rex = new Regex(@"^# Creation Timestamp : \d{10}$");
                    Match mat = rex.Match(region[i]);
                    if (mat.Success)
                    {
                        region[i] = Regex.Replace(region[i], @"\d{10}$", Utilities.CreateStrTimeStamp());
                        break;
                    }
                }

                //输出头部信息
                foreach (string entry in region)
                {
                    fileWriter.WriteLine(entry);
                }
            }
            catch
            {
                //错误的文件
                fileWriter.Flush();
                fileWriter.Close();
                if (File.Exists(TargetFile))
                    File.Delete(TargetFile);
                throw;
            }
            fileWriter.Flush();
            fileWriter.Close();
        }

        /// <summary>
        /// 生成hosts文件缓存
        /// </summary>
        /// <param name="AsmFlags">标志位</param>
        private static void AssembleHosts(int[] AsmFlags, mainFrame mainForm)
        {
            string filename = @"hosts.tmp";
            string TargetPath = Environment.CurrentDirectory;
            //设置缓存文件
            string TargetFile = Path.Combine(TargetPath, filename);

            //缓存文件流
            FileStream outfile = new FileStream(TargetFile, FileMode.Append);
            StreamWriter fileWriter = new StreamWriter(outfile, Encoding.Default);
            fileWriter.BaseStream.Seek(0, SeekOrigin.End);

            foreach (int asmCount in regionOrder)
            {
                bool hasError = false;
                if (AsmFlags[asmCount] == 1)
                {
                    string prefix = "# region ";
                    int regionStart = hostsStream.IndexOf(prefix + sectionName[asmCount]);
                    if (regionStart != -1)
                    {
                        int regionEnd = hostsStream.IndexOf("# endregion", regionStart);
                        int regionCount = regionEnd - regionStart + 1;
                        string[] region = hostsStream.GetRange(regionStart, regionCount).ToArray();

                        //输出asmCount对应块hosts列表
                        foreach (string entry in region)
                        {
                            fileWriter.WriteLine(entry);
                        }
                        fileWriter.Flush();

                        //修改主窗口图标
                        mainForm.TurnGreen(asmCount);
                    }
                    else
                    {
                        //Error 文件缺少内容
                        hasError = true;
                        mainForm.TurnRed(asmCount);
                    }
                }
                if (hasError)
                {
                    //Error 文件缺少内容
                    msg.SetDialog(2, Resources.msg_err_res);
                    msg.ShowDialog();
                }
            }
            fileWriter.Close();
        }

        /// <summary>
        /// 将生成的临时hosts文件移动到\etc目录
        /// </summary>
        private static void ApplyHosts()
        {
            string SourcePath = Environment.CurrentDirectory;
            string TargetPath = Environment.SystemDirectory + @"\drivers\etc";
            //设置缓存文件
            string SourceFile = Path.Combine(SourcePath, @"hosts.tmp");
            string TargetFile = Path.Combine(TargetPath, @"hosts");

            DeleteHosts();
            File.Copy(SourceFile, TargetFile, true);
            File.Delete(SourceFile);
        }

        #endregion

        #region 模块操作入口

        /// <summary>
        /// 本地标志位
        /// </summary>
        static bool IP_flag = false;       //IP适应模式 默认值: IPv4:false
        static int insmode = 0;            //安装源选择模式 默认值: 离线
        static bool backup_flag = false;   //备份模式默认禁用
        static bool recover_flag = false;  //恢复备份模式默认禁用

        static int[] region_flags = new int[9] { 1, 1, 1, 1, 1, 1, 1, 1, 1 };  //模块选择初始设定

        /// <summary>
        /// 由控制码生成控制标志位
        /// </summary>
        /// <param name="setting">控制码</param>
        private static void SetConfig(int setting)
        {
            string config_stream = Convert.ToString(setting, 2).PadLeft(16, '0');
            for (int i = 0; i < 9; i++)
                region_flags[i] = config_stream[i] - 0x30;                          //根据第1至9位设置模块设定
            IP_flag = Convert.ToBoolean(config_stream[9] - 0x30);                   //根据第10位设置IP协议模式
            insmode = (config_stream[12] - 0x30) * 2 + (config_stream[13] - 0x30);  //根据第13, 14位设置安装源
            backup_flag = Convert.ToBoolean(config_stream[14] - 0x30);              //根据第15位设置备份文件状态
            recover_flag = Convert.ToBoolean(config_stream[15] - 0x30);             //根据第16位设置恢复备份状态
        }

        /// <summary>
        /// 设置二级目录
        /// </summary>
        /// <returns>相对路径</returns>
        private static string SetSecondaryPath()
        {
            string path = @"resources/";
            path += IP_flag ? @"ipv6_win_ansi" : @"ipv4_win_ansi";
            return path;
        }

        /// <summary>
        /// 检查控制码设置
        /// </summary>
        /// <param name="setting">控制码</param>
        /// <returns>真假</returns>
        private static bool CheckConfig(int setting)
        {
            bool flag = true;
            //检查备份模式设置
            flag &= (!backup_flag || setting == 0x0002);
            
            //检查恢复模式设置
            flag &= (!recover_flag || setting == 0x0001);

            return flag;
        }


        private static ErrorBox msg = new ErrorBox();

        /// <summary>
        /// 执行操作
        /// </summary>
        /// <param name="setting">控制码</param>
        public static void ProceedHostsOps(int setting, mainFrame mainForm)
        {
            SetConfig(setting);
            msg.SetDialog(0, Resources.msg_succ_ops);
            if (CheckConfig(setting))       //验证配置码
            {
                if (backup_flag)
                {
                    BackUpHosts();          //文件备份
                    msg.ShowDialog();
                    return;
                }
                if (recover_flag)
                {
                    RecoverHosts();         //恢复备份
                    msg.ShowDialog();
                    return;
                }

                try
                {
                    FileOps.ProceedFileOps(setting, mainForm);
                }
                catch
                {
                    return;
                }
                mainForm.Enabled = false;
                msg.SetDialog(0, Resources.msg_succ_ops);
                ReadHosts(SetSecondaryPath());
                try
                {
                    AssembleHead();
                    AssembleHosts(region_flags, mainForm);
                    ApplyHosts();
                }
                catch
                {
                    //Error 错误的文件
                    msg.SetDialog(3, Resources.msg_err_unr);
                }

                mainForm.Enabled = true;
            }
            else
            {
                //Error 错误的配置
                msg.SetDialog(2, Resources.msg_alert_cfg);
            }
            msg.ShowDialog();
            //修正主面板只是灯色彩
            foreach (int asmCount in regionOrder)
            {
                if (region_flags[asmCount] == 1)
                {
                    mainForm.TurnOn(asmCount);
                }
            }
        }

        #endregion
    }
}