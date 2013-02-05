using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Data;


namespace WinHosts
{
    class Utilities
    {

        /// <summary>
        /// 将c# DateTime时间格式转换为Unix时间戳格式
        /// </summary>
        /// <param name="time">时间</param>
        /// <returns>int</returns>
        public static int ConvertDateTimeStamp(System.DateTime time)
        {
            double intResult = 0;
            System.DateTime startTime = TimeZone.CurrentTimeZone.ToLocalTime(new System.DateTime(1970, 1, 1));
            intResult = (time - startTime).TotalSeconds;
            return (int)Math.Round(intResult);
        }

        /// <summary>
        /// 生成字符串时间戳
        /// </summary>
        /// <returns>unix时间戳</returns>
        public static string CreateStrTimeStamp()
        {
            System.DateTime currentTime = new System.DateTime();
            currentTime = System.DateTime.Now;
            string time_stamp = ConvertDateTimeStamp(currentTime).ToString();
            return time_stamp;
        }

        /// <summary>
        /// 获取文件编码
        /// </summary>
        /// <param name="FILE_NAME">文件</param>
        /// <returns>编码类型</returns>
        public static System.Text.Encoding GetType(string FILE_NAME)
        {
            FileStream fs = new FileStream(FILE_NAME, FileMode.Open, FileAccess.Read);
            System.Text.Encoding r = GetType(fs);
            fs.Close();
            return r;
        }

        /// <summary>
        /// 获取数据流编码
        /// </summary>
        /// <param name="fs">文件流</param>
        /// <returns>编码类型</returns>
        public static System.Text.Encoding GetType(FileStream fs)
        {
            /*byte[] Unicode=new byte[]{0xFF,0xFE};  
            byte[] UnicodeBIG=new byte[]{0xFE,0xFF};  
            byte[] UTF8=new byte[]{0xEF,0xBB,0xBF};*/

            BinaryReader r = new BinaryReader(fs, System.Text.Encoding.Default);
            byte[] ss = r.ReadBytes(3);
            r.Close();
            //编码类型 Coding=编码类型.ASCII;   
            if (ss[0] >= 0xEF)
            {
                if (ss[0] == 0xEF && ss[1] == 0xBB && ss[2] == 0xBF)
                {
                    return System.Text.Encoding.UTF8;
                }
                else if (ss[0] == 0xFE && ss[1] == 0xFF)
                {
                    return System.Text.Encoding.BigEndianUnicode;
                }
                else if (ss[0] == 0xFF && ss[1] == 0xFE)
                {
                    return System.Text.Encoding.Unicode;
                }
                else
                {
                    return System.Text.Encoding.Default;
                }
            }
            else
            {
                return System.Text.Encoding.Default;
            }
        }   
    }
}
