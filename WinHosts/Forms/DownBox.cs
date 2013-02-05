using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;

namespace WinHosts
{
    public partial class DownBox : Form
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
            if (e.Button == MouseButtons.Left) //按下的是鼠标左键            
            {
                Capture = false; //释放鼠标，使能够手动操作                
                SendMessage(Handle, 0x00A1, 2, 0); //拖动窗体            
            }
        }

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == 0x0201) //鼠标左键按下去的消息
            {
                m.Msg = 0x00A1; //更改消息为非客户区按下鼠标
                m.LParam = IntPtr.Zero; //默认值
                m.WParam = new IntPtr(2); //鼠标放在标题栏内
            }
            base.WndProc(ref m);
        }
        #endregion

        public void SetPoint(int percent)
        {
            Bitmap pointImg = new Bitmap(global::WinHosts.Properties.Resources.point);
            downPoint.BackgroundImage = ImgTrans.Rotate(pointImg, percent * 2);
            downPoint.Refresh();
        }

        //构造函数
        public DownBox(Form mainForm)
        {
            InitializeComponent();
            //设置DownBox位置
            this.Location = new Point(mainForm.Location.X + (mainForm.Size.Width - this.Size.Width) / 2,
                mainForm.Location.Y + (mainForm.Size.Height - this.Size.Height) / 2);
        }

        

    }
}
