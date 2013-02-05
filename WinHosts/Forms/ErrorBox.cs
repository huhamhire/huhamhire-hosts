using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Media;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;

using WinHosts.Properties;

namespace WinHosts
{
    public partial class ErrorBox : Form
    {
        #region 窗口拖移
        [DllImport("user32.dll")]
        public static extern IntPtr SendMessage(IntPtr hWnd, int msg, int wparam, int lparam);
        #endregion
        #region 鼠标拖移

        /// <summary>
        /// 鼠标拖移
        /// </summary>
        protected override void OnMouseDown(MouseEventArgs e)
        {
            base.OnMouseDown(e);
            if (e.Button == MouseButtons.Left)//按下的是鼠标左键            
            {
                Capture = false;//释放鼠标，使能够手动操作                
                SendMessage(Handle, 0x00A1, 2, 0);//拖动窗体            
            }
        }

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == 0x0201) //鼠标左键按下去的消息
            {
                m.Msg = 0x00A1;//更改消息为非客户区按下鼠标
                m.LParam = IntPtr.Zero;//默认值
                m.WParam = new IntPtr(2);//鼠标放在标题栏内
            }
            base.WndProc(ref m);
        }
        #endregion

        public ErrorBox()
        {
            InitializeComponent();
        }

        /// <summary>
        /// 确定按钮按下操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Ok_button_Click(object sender, EventArgs e)
        {
            SoundPlayer switch_tick = new SoundPlayer(Resources._switch);//开关声
            Ok_button.BackgroundImage = Resources.ok_button_off;
            switch_tick.Play();
            this.Close();
        }

        /// <summary>
        /// 配置信息对话框
        /// </summary>
        /// <param name="type">对话框类型: 0:成功; 1:提示; 2:警告; 3:错误</param>
        /// <param name="Msg">消息图片</param>
        public void SetDialog(int type, Image Msg)
        {
            Image[] Icons = new Image[4]{
                Resources.icon_success, Resources.icon_info,
                Resources.icon_warning, Resources.icon_error
            };
            SoundPlayer[] Sounds = { 
                new SoundPlayer(Resources.dingx2), new SoundPlayer(Resources.doorbell),
                new SoundPlayer(Resources.beepx4), new SoundPlayer(Resources.alert)
            };
            IconBox.BackgroundImage = Icons[type];
            MsgBox.BackgroundImage = Msg;
            if (type < 3)
                Sounds[type].Play();
            else
                Sounds[type].PlayLooping();
        }
        
        private void Ok_button_MouseHover(object sender, EventArgs e)
        {
            Ok_button.BackgroundImage = Resources.ok_button_off;
        }

        private void Ok_button_MouseLeave(object sender, EventArgs e)
        {
            Ok_button.BackgroundImage = Resources.ok_button_on;
        }
    }
}