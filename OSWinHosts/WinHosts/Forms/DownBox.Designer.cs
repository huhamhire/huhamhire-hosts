namespace WinHosts
{
    partial class DownBox
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.downPoint = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.downPoint)).BeginInit();
            this.SuspendLayout();
            // 
            // downPoint
            // 
            this.downPoint.BackColor = System.Drawing.Color.Transparent;
            this.downPoint.BackgroundImage = global::WinHosts.Properties.Resources.point;
            this.downPoint.Location = new System.Drawing.Point(119, 17);
            this.downPoint.Name = "downPoint";
            this.downPoint.Size = new System.Drawing.Size(256, 256);
            this.downPoint.TabIndex = 0;
            this.downPoint.TabStop = false;
            // 
            // DownBox
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.BackgroundImage = global::WinHosts.Properties.Resources.downbox;
            this.ClientSize = new System.Drawing.Size(420, 240);
            this.ControlBox = false;
            this.Controls.Add(this.downPoint);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "DownBox";
            this.ShowIcon = false;
            this.ShowInTaskbar = false;
            this.StartPosition = System.Windows.Forms.FormStartPosition.Manual;
            this.Text = "下载";
            this.TransparencyKey = System.Drawing.SystemColors.ControlDarkDark;
            ((System.ComponentModel.ISupportInitialize)(this.downPoint)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox downPoint;

    }
}