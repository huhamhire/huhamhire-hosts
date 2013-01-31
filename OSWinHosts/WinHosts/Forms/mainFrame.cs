using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Media;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace WinHosts
{
    public partial class mainFrame : Form
    {
        /// <summary>
        /// 窗体UI相关
        /// </summary>

        #region 窗体边框阴影效果变量申明
        const int CS_DropSHADOW = 0x20000;
        const int GCL_STYLE = (-26);
        //声明Win32 API
        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        public static extern int SetClassLong(IntPtr hwnd, int nIndex, int dwNewLong);
        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        public static extern int GetClassLong(IntPtr hwnd, int nIndex);
        #endregion
        
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

        #region 窗体加载操作
        /// <summary>
        /// 窗体初始化
        /// </summary>
        public mainFrame()
        {
            control = default_cfg;  //初始化控制码
            this.Opacity = 0;       //窗口延时显示
            InitializeComponent();

            //窗体阴影
            //SetClassLong(this.Handle, GCL_STYLE, GetClassLong(this.Handle, GCL_STYLE) | CS_DropSHADOW); //API函数加载，实现窗体边框阴影效果
            //this.SuspendLayout();
        }

        /// <summary>
        /// 窗体加载操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Main_Load(object sender, EventArgs e)
        {
            Set_Config(control);
            InitializeButtonArray();
            InitializeButton();
        }
        #endregion

        #region 延时显示操作
        /// <summary>
        /// 加载时启动延时定时器
        /// </summary>
        /// <param name="e"></param>
        protected override void OnLoad(EventArgs e)
        {
            ini_timer.Elapsed += new System.Timers.ElapsedEventHandler(show_form);
            ini_timer.AutoReset = true;
            ini_timer.Enabled = true;

            base.OnLoad(e);
        }

        /// <summary>
        /// 窗口加载完成后显示
        /// </summary>
        /// <param name="source"></param>
        /// <param name="e"></param>
        private void show_form(object source, System.Timers.ElapsedEventArgs e)
        {
            this.Opacity = 1;
        }
        #endregion

        #region 开关维护

        /// <summary>
        /// 选项控制开关数组设定
        /// </summary>
        System.Windows.Forms.Button[] switches = new Button[9];
        System.Windows.Forms.Button[] icon_buttons = new Button[9];

        /// <summary>
        /// 顶部指示开关贴图设定
        /// </summary>
        Image[] switch_img = new Image[2];
        Image[] wifi_img = new Image[2];
        Image[] start_img = new Image[2];
        Image[] backup_img = new Image[2];
        Image[] recover_img = new Image[2];
        Image[] icon_imgs_on = new Image[9];
        Image[] icon_imgs_off = new Image[9];
        Image[] icon_imgs_green = new Image[9];
        Image[] icon_imgs_red = new Image[9];
        Bitmap switch_rotate = new Bitmap(global::WinHosts.Properties.Resources.switch_rotate);
        Bitmap switch_push = new Bitmap(global::WinHosts.Properties.Resources.push);
        private void InitializeButtonArray()
        {
            //下方开关
            switches[0] = button_switch_gog;
            switches[1] = button_switch_fb;
            switches[2] = button_switch_twi;
            switches[3] = button_switch_ytb;
            switches[4] = button_switch_act;
            switches[5] = button_switch_adblk;
            switches[6] = button_switch_app;
            switches[7] = button_switch_wiki;
            switches[8] = button_switch_other;

            //下方开关图标
            switch_img[0] = global::WinHosts.Properties.Resources.off;
            switch_img[1] = global::WinHosts.Properties.Resources.on;

            //上部图标开关
            icon_buttons[0] = button_icon_gog;
            icon_buttons[1] = button_icon_fb;
            icon_buttons[2] = button_icon_twi;
            icon_buttons[3] = button_icon_ytb;
            icon_buttons[4] = button_icon_act;
            icon_buttons[5] = button_icon_adblk;
            icon_buttons[6] = button_icon_app;
            icon_buttons[7] = button_icon_wiki;
            icon_buttons[8] = button_icon_other;

            //图标开关点亮图标
            icon_imgs_on[0] = global::WinHosts.Properties.Resources.Google_on;
            icon_imgs_on[1] = global::WinHosts.Properties.Resources.Facebook_on;
            icon_imgs_on[2] = global::WinHosts.Properties.Resources.Twitter_on;
            icon_imgs_on[3] = global::WinHosts.Properties.Resources.YouTube_on;
            icon_imgs_on[4] = global::WinHosts.Properties.Resources.Activation_on;
            icon_imgs_on[5] = global::WinHosts.Properties.Resources.ADblock_on;
            icon_imgs_on[6] = global::WinHosts.Properties.Resources.Apple_on;
            icon_imgs_on[7] = global::WinHosts.Properties.Resources.Wikipedia_on;
            icon_imgs_on[8] = global::WinHosts.Properties.Resources.Other_on;

            //图标开关熄灭图标
            icon_imgs_off[0] = global::WinHosts.Properties.Resources.Google_off;
            icon_imgs_off[1] = global::WinHosts.Properties.Resources.Facebook_off;
            icon_imgs_off[2] = global::WinHosts.Properties.Resources.Twitter_off;
            icon_imgs_off[3] = global::WinHosts.Properties.Resources.YouTube_off;
            icon_imgs_off[4] = global::WinHosts.Properties.Resources.Activation_off;
            icon_imgs_off[5] = global::WinHosts.Properties.Resources.ADblock_off;
            icon_imgs_off[6] = global::WinHosts.Properties.Resources.Apple_off;
            icon_imgs_off[7] = global::WinHosts.Properties.Resources.Wikipedia_off;
            icon_imgs_off[8] = global::WinHosts.Properties.Resources.Other_off;

            //图标开关绿色图标
            icon_imgs_green[0] = global::WinHosts.Properties.Resources.Google_green;
            icon_imgs_green[1] = global::WinHosts.Properties.Resources.Facebook_green;
            icon_imgs_green[2] = global::WinHosts.Properties.Resources.Twitter_green;
            icon_imgs_green[3] = global::WinHosts.Properties.Resources.YouTube_green;
            icon_imgs_green[4] = global::WinHosts.Properties.Resources.Activation_green;
            icon_imgs_green[5] = global::WinHosts.Properties.Resources.ADblock_green;
            icon_imgs_green[6] = global::WinHosts.Properties.Resources.Apple_green;
            icon_imgs_green[7] = global::WinHosts.Properties.Resources.Wikipedia_green;
            icon_imgs_green[8] = global::WinHosts.Properties.Resources.Other_green;

            //图标开关红色图标
            icon_imgs_red[0] = global::WinHosts.Properties.Resources.Google_red;
            icon_imgs_red[1] = global::WinHosts.Properties.Resources.Facebook_red;
            icon_imgs_red[2] = global::WinHosts.Properties.Resources.Twitter_red;
            icon_imgs_red[3] = global::WinHosts.Properties.Resources.YouTube_red;
            icon_imgs_red[4] = global::WinHosts.Properties.Resources.Activation_red;
            icon_imgs_red[5] = global::WinHosts.Properties.Resources.ADblock_red;
            icon_imgs_red[6] = global::WinHosts.Properties.Resources.Apple_red;
            icon_imgs_red[7] = global::WinHosts.Properties.Resources.Wikipedia_red;
            icon_imgs_red[8] = global::WinHosts.Properties.Resources.Other_red;

            //网络访问指示图标
            wifi_img[0] = global::WinHosts.Properties.Resources.wifi_off;
            wifi_img[1] = global::WinHosts.Properties.Resources.wifi_on;

            //启动开关图标
            start_img[0] = global::WinHosts.Properties.Resources.start_metal_off;
            start_img[1] = global::WinHosts.Properties.Resources.start_metal_on;

            //备份开关图标
            backup_img[0] = global::WinHosts.Properties.Resources.backup_metal_off;
            backup_img[1] = global::WinHosts.Properties.Resources.backup_metal_on;

            //还原开关图标
            recover_img[0] = global::WinHosts.Properties.Resources.recover_metal_off;
            recover_img[1] = global::WinHosts.Properties.Resources.recover_metal_on;
        }

        /// <summary>
        /// 按钮初始化设置
        /// </summary>
        private void InitializeButton()
        {
            for (int i = 0; i < 9; i++)
            {
                switches[i].BackgroundImage = switch_img[switch_flags[i]];
                if (switch_flags[i] == 1)
                    icon_buttons[i].BackgroundImage = icon_imgs_on[i];
                else
                    icon_buttons[i].BackgroundImage = icon_imgs_off[i];
            }
            
            button_rotate.BackgroundImage = ImgTrans.Rotate(switch_rotate, angle_arr[insmode]);
            button_rotate.Refresh();

            button_IP.BackgroundImage = ImgTrans.MoveIMG(switch_push, 0, Convert.ToInt32(IP_flag) * (-28));
            button_IP.Refresh();

            wifi_button.BackgroundImage = insmode == 0 ? wifi_img[0] : wifi_img[1];

            recover_button.BackgroundImage = recover_flag == false ? recover_img[0] : recover_img[1];
            backup_button.BackgroundImage = backup_flag == false ? backup_img[0] : backup_img[1];
        }

        /// <summary>
        /// 选项开关操作
        /// </summary>
        /// <param name="button_id">按钮id</param>
        private void SwitchButton(int button_id)
        {
            if (switch_flags[button_id] == 1)
            {
                icon_buttons[button_id].BackgroundImage = icon_imgs_off[button_id];
                switch_flags[button_id] = 0;   //熄灭顶部图标
            }
            else
            {
                icon_buttons[button_id].BackgroundImage = icon_imgs_on[button_id];
                switch_flags[button_id] = 1;   //点亮顶部图标
            }
            switches[button_id].BackgroundImage = switch_img[switch_flags[button_id]];
            switch_tick.Play();

        }

        #endregion

        #region 快捷键操作

        /// <summary>
        /// 开关快捷键列表A, S, D, F, G, H, J, K, L
        /// </summary>
        Keys[] KeyList = new Keys[9] { Keys.A, Keys.S, Keys.D, Keys.F, Keys.G,
                                       Keys.H, Keys.J, Keys.K, Keys.L };

        /// <summary>
        /// 按键操作
        /// </summary>
        /// <param name="msg"></param>
        /// <param name="keyData"></param>
        /// <returns></returns>
        protected override bool ProcessCmdKey(ref Message msg, Keys keyData)
        {
            for (int i = 0; i < 9;i++ )
            {
                if (keyData == KeyList[i])
                {
                    this.switches[i].PerformClick();
                }
            }

            if (keyData == Keys.W)          //安装源选择旋钮快捷键
                this.Do_switch_rotate(1);
            if (keyData == Keys.E)          //IP协议选择快捷键
                this.Do_change_IP(true);
            if (keyData == Keys.R)          //还原默认设置快捷键
                this.reset_button.PerformClick();
            if (keyData == Keys.F2)         //备份快捷键
                this.backup_button.PerformClick();
            if (keyData == Keys.F3)         //恢复备份快捷键
                this.recover_button.PerformClick();
            if (keyData == Keys.F4)         //执行快捷键
                this.start_button.PerformClick();
            if (keyData == Keys.Escape)     //程序退出快捷键
                Application.Exit();
            
            return base.ProcessCmdKey(ref msg, keyData);
        }

        #endregion

        #region 电源按钮操作
        private void power_button_MouseHover(object sender, EventArgs e)
        {
            power_button.BackgroundImage = global::WinHosts.Properties.Resources.power_hover;
        }
        private void power_button_MouseDown(object sender, MouseEventArgs e)
        {
            ding.Play();
            power_button.BackgroundImage = global::WinHosts.Properties.Resources.power_off;
        }
        private void power_button_MouseLeave(object sender, EventArgs e)
        {
            power_button.BackgroundImage = global::WinHosts.Properties.Resources.power_on;
        }
        private void power_button_MouseUp(object sender, MouseEventArgs e)
        {
            Application.Exit();
        }
        #endregion

        #region IP推钮操作

        /// <summary>
        /// IP选择钮变化操作
        /// </summary>
        /// <param name="change">是否进行操作</param>
        public void Do_change_IP(bool change)
        {
            button_IP.BackgroundImage = ImgTrans.MoveIMG(switch_push, 0,
                Convert.ToInt32(IP_flag ^ change) * (-28));
            button_IP.Refresh();
            IP_flag = change ^ IP_flag;
            if (change) { switch_ro_tick.Play(); }
        }

        /// <summary>
        /// IP选择钮鼠标按下操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button_IP_MouseDown(object sender, MouseEventArgs e)
        {
            p0 = new Point(Cursor.Position.X, Cursor.Position.Y);
            drag_flag = true;
        }

        /// <summary>
        /// IP选择钮鼠标抬起操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button_IP_MouseUp(object sender, MouseEventArgs e)
        {
            delta.X = Cursor.Position.X - p0.X;
            delta.Y = Cursor.Position.Y - p0.Y;
            if (((IP_flag && (delta.Y > 0)) || (!IP_flag && (delta.Y < 0)))
                && (Math.Abs(delta.Y) <= 28))
            {
                this.Do_change_IP(Math.Abs(delta.Y) > 3);
            }
            drag_flag = false;
        }

        /// <summary>
        /// IP选择钮鼠标拖移操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button_IP_MouseMove(object sender, MouseEventArgs e)
        {
            if (drag_flag)
            {
                delta.X = Cursor.Position.X - p0.X;
                delta.Y = Cursor.Position.Y - p0.Y;

                if ((IP_flag ^ delta.Y < 0) && Math.Abs(delta.Y) > 0)
                {
                    if (Math.Abs(delta.Y) <= 25)
                    {
                        button_IP.BackgroundImage = ImgTrans.MoveIMG(switch_push, 0, 
                            delta.Y > 0 ? delta.Y - 28 : delta.Y);
                    }
                    else
                    {
                        this.Do_change_IP(true);
                        p0.Y = p0.Y + Math.Sign(delta.Y) * 28;
                    }
                }
            }
        }

        #endregion

        #region 安装源选择旋钮操作

        /// <summary>
        /// 按钮旋转操作
        /// </summary>
        /// <param name="rotate">角度，单位：度</param>
        private void Do_switch_rotate(int rotate)
        {
            insmode += rotate;
            if (insmode > 3) { insmode = 0; }
            button_rotate.BackgroundImage = ImgTrans.Rotate(switch_rotate, angle_arr[insmode]);
            button_rotate.Refresh();
            wifi_button.BackgroundImage = insmode == 0 ? wifi_img[0] : wifi_img[1];
            if (rotate != 0) { switch_ro_tick.Play(); }
        }

        /// <summary>
        /// 鼠标按下动作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button_rotate_MouseDown(object sender, MouseEventArgs e)
        {
            p0 = new Point(Cursor.Position.X, Cursor.Position.Y);
            pc.X += this.Location.X;
            pc.Y += this.Location.Y;
            select_flag = true;
        }

        /// <summary>
        /// 鼠标拖移旋转动作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button_rotate_MouseMove(object sender, MouseEventArgs e)
        {
            if (select_flag)
            {
                p1 = new Point(Cursor.Position.X, Cursor.Position.Y);
                int angle = GeometryCalc.RadToDeg(GeometryCalc.Angle(pc, p0, p1));
                if (Math.Abs(angle) <= 20)
                {
                    if (angle_arr[insmode] + angle < 30) { angle = 0; }
                    if (angle_arr[insmode] + angle > 150) { angle = 0; }
                    button_rotate.BackgroundImage = ImgTrans.Rotate(switch_rotate, angle_arr[insmode] + angle);
                    button_rotate.Refresh();
                }
                else
                {
                    if ((angle < 0 && insmode == 0) || (angle > 0 && insmode == 3))
                        angle = 0;
                    this.Do_switch_rotate(Math.Sign(angle) * 1);
                    p0 = p1;
                }
            }
        }

        /// <summary>
        /// 鼠标抬起动作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void button_rotate_MouseUp(object sender, MouseEventArgs e)
        {
            p1 = new Point(Cursor.Position.X, Cursor.Position.Y);
            if (p0 != p1)
            {
                int angle = GeometryCalc.RadToDeg(GeometryCalc.Angle(pc, p0, p1));
                if ((angle < 0 && insmode == 0) || (angle > 0 && insmode == 3) || (Math.Abs(angle) <= 10))
                    angle = 0;
                this.Do_switch_rotate(Math.Sign(angle) * 1);
                p0 = p1;
            }

            pc.X = (int)(button_rotate.Location.X + button_rotate.Width / 2);
            pc.Y = (int)(button_rotate.Location.Y + button_rotate.Height / 2);
            select_flag = false;
        }

        #endregion

        #region 开关操作
        /// <summary>
        /// 选项设置开关按钮执行操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Switch_Click(object sender, EventArgs e)
        {
            SwitchButton(Int32.Parse(((Button)sender).Tag.ToString()));
        }

        /// <summary>
        /// reset按钮操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void reset_button_Click(object sender, EventArgs e)
        {
            control = default_cfg;
            UnLockPanel(); 
            Set_Config(control);
            InitializeButton();
            switch_tick.Play();
        }

        /// <summary>
        /// 启动按钮操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void start_button_Click(object sender, EventArgs e)
        {
            Build_config();
            start_flag = !start_flag;
            start_button.BackgroundImage = start_flag == false ? start_img[0] : start_img[1];
            ding.Play();

            //启动hosts操作
            HostsOps.ProceedHostsOps(control, this);

            start_flag = !start_flag;
            start_button.BackgroundImage = start_flag == false ? start_img[0] : start_img[1];
        }

        /// <summary>
        /// 恢复按钮操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void recover_button_Click(object sender, EventArgs e)
        {
            recover_button.Enabled = false;
            ding.Play();
            if (!recover_flag)
            {                           //备份状态
                control = 0x0001;
                LockPanel();            //锁定控件
            }
            else
            {                           //取消备份状态
                control = default_cfg;
                UnLockPanel();          //解锁控件
            }

            //设定面板参数
            Set_Config(control);
            InitializeButton();
            recover_button.BackgroundImage = recover_flag == false ? recover_img[0] : recover_img[1];
            recover_button.Enabled = true;
        }

        /// <summary>
        /// 备份按钮操作
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void backup_button_Click(object sender, EventArgs e)
        {
            backup_button.Enabled = false;
            ding.Play();
            if (!backup_flag)
            {                           //备份状态
                control = 0x0002;
                LockPanel();            //锁定控件
            }
            else
            {                           //取消备份状态
                control = default_cfg;
                UnLockPanel();          //解锁控件
            }

            //设定面板参数
            Set_Config(control);
            InitializeButton();
            backup_button.BackgroundImage = backup_flag == false ? backup_img[0] : backup_img[1];
            backup_button.Enabled = true;
        }
        #endregion

        #region 控制码操作
        /// <summary>
        /// 默认设置
        /// 初值  1111:1111:1000:0000 [FF80]
        /// 构成  top_flags[9], IP_flag[1], drag_flag[1], select_flag[1], insmode[2], backup_flag[1], recover_flag[1]
        /// </summary>
        int default_cfg = 0xFF80;
        int control;

        /// <summary>
        /// 本地标志位
        /// </summary>
        bool IP_flag = false;       //IP选择推钮默认值 IPv4:false
        bool drag_flag = false;     //IP选择推钮拖移状态
        bool select_flag = false;   //安装源选择旋钮旋转状态
        int insmode = 0;            //安装源选择模式 默认:离线

        bool backup_flag = false;   //备份按钮置零
        bool recover_flag = false;  //恢复备份按钮置零

        bool start_flag = false;    //执行按钮置零

        int[] switch_flags = new int[9] { 1, 1, 1, 1, 1, 1, 1, 1, 1 };  //顶部指示灯初始设定
        int[] angle_arr = new int[4] { 30, 75, 105, 150 };              //安装源选择旋钮旋转角，单位：度
        Point pc, p0, p1,delta;                                         //点变量初始化

        /// <summary>
        /// 启动加载延时，防闪屏
        /// </summary>
        System.Timers.Timer ini_timer = new System.Timers.Timer(500);  

        /// <summary>
        /// 按钮音效设置
        /// </summary>
        SoundPlayer switch_tick = new SoundPlayer(global::WinHosts.Properties.Resources._switch);//开关声
        SoundPlayer button_tick = new SoundPlayer(global::WinHosts.Properties.Resources.button_tick);//按钮声
        SoundPlayer switch_ro_tick = new SoundPlayer(global::WinHosts.Properties.Resources.switch_ro);//按钮声
        SoundPlayer ding = new SoundPlayer(global::WinHosts.Properties.Resources.ding);//钉铃声

        /// <summary>
        /// 由control数据生成控制标志位
        /// </summary>
        /// <param name="setting">控制码</param>
        private void Set_Config(int setting)
        {
            string config_stream = Convert.ToString(setting, 2).PadLeft(16, '0');
            for (int i = 0; i < 9; i++)
                switch_flags[i] = config_stream[i] - 0x30;                          //根据第1至9位设置顶部指示灯初始设定
            IP_flag = Convert.ToBoolean(config_stream[9] - 0x30);                   //根据第10位设置IP选择推钮设定
            drag_flag = Convert.ToBoolean(config_stream[10] - 0x30);                //根据第11位设置IP选择推钮拖移状态
            select_flag = Convert.ToBoolean(config_stream[11] - 0x30);              //根据第12位设置安装源选择旋钮旋转状态
            insmode = (config_stream[12] - 0x30) * 2 + (config_stream[13] - 0x30);  //根据第13, 14位设置安装源选择模式
            backup_flag = Convert.ToBoolean(config_stream[14] - 0x30);              //根据第15位设置备份文件状态
            recover_flag = Convert.ToBoolean(config_stream[15] - 0x30);             //根据第16位设置恢复备份状态

            pc = new Point((int)(button_rotate.Location.X + button_rotate.Width / 2), 
                           (int)(button_rotate.Location.Y + button_rotate.Height / 2));   //设置旋钮中心
        }

        /// <summary>
        /// 生成控制码
        /// </summary>
        public void Build_config()
        {
            byte[] stream = new byte[16];
            for (int i = 0; i < 9; i++)
                stream[i] = (byte)(switch_flags[i] + 0x30);                         //根据顶部指示灯初始设定设置第1至9位
            stream[9] = (byte)(IP_flag == true ? 0x31 : 0x30);                      //根据IP选择推钮设定设置第10位
            stream[10] = (byte)(drag_flag == true ? 0x31 : 0x30);                   //根据IP选择推钮拖移状态设置第11位
            stream[11] = (byte)(select_flag == true ? 0x31 : 0x30);                 //根据安装源选择旋钮旋转状态设置第12位
            stream[12] = (byte)(insmode / 2 + 0x30);                                //根据安装源选择模式设置第13, 14位
            stream[13] = (byte)(insmode % 2 + 0x30);
            for (int i = 14; i < 16; i++)
                stream[i] = (byte)(0x30);                                           //第15, 16保留位置零
            stream[14] = (byte)(backup_flag == true ? 0x31 : 0x30);                 //根据备份文件状态设置第15位
            stream[15] = (byte)(recover_flag == true ? 0x31 : 0x30);                //根据恢复备份状态设置第16位

            string cfg_str = System.Text.Encoding.Default.GetString(stream);
            control = Convert.ToInt32(cfg_str, 2);                                  //生成控制码
        }

        #endregion

        #region 按钮访问权限设置
        /// <summary>
        /// 锁定面板按钮
        /// </summary>
        public void LockPanel()
        {
            foreach (Button butt in switches)
                butt.Enabled = false;
            foreach (Button butt in icon_buttons)
                butt.Enabled = false;
            button_rotate.Enabled = false;
            button_IP.Enabled = false;
        }

        /// <summary>
        /// 面板按钮解锁
        /// </summary>
        public void UnLockPanel()
        {
            foreach (Button butt in switches)
                butt.Enabled = true;
            foreach (Button butt in icon_buttons)
                butt.Enabled = true;
            button_rotate.Enabled = true;
            button_IP.Enabled = true;
        }
        #endregion

        #region 图标控制
        /// <summary>
        /// 将指示灯变绿
        /// </summary>
        /// <param name="Num">编号</param>
        public void TurnGreen(int Num)
        {
            icon_buttons[Num].BackgroundImage = icon_imgs_green[Num];
        }

        /// <summary>
        /// 将指示灯变红
        /// </summary>
        /// <param name="Num">编号</param>
        public void TurnRed(int Num)
        {
            icon_buttons[Num].BackgroundImage = icon_imgs_red[Num];
        }

        /// <summary>
        /// 将指示灯变蓝
        /// </summary>
        /// <param name="Num">编号</param>
        public void TurnOn(int Num)
        {
            icon_buttons[Num].BackgroundImage = icon_imgs_on[Num];
        }
        #endregion
    }
}