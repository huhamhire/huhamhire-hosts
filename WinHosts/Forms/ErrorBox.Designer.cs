namespace WinHosts
{
    partial class ErrorBox
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
            this.IconBox = new System.Windows.Forms.PictureBox();
            this.Ok_button = new System.Windows.Forms.Button();
            this.MsgBox = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.IconBox)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.MsgBox)).BeginInit();
            this.SuspendLayout();
            // 
            // IconBox
            // 
            this.IconBox.BackColor = System.Drawing.Color.Transparent;
            this.IconBox.Location = new System.Drawing.Point(24, 43);
            this.IconBox.Margin = new System.Windows.Forms.Padding(20);
            this.IconBox.Name = "IconBox";
            this.IconBox.Size = new System.Drawing.Size(96, 96);
            this.IconBox.TabIndex = 0;
            this.IconBox.TabStop = false;
            // 
            // Ok_button
            // 
            this.Ok_button.BackColor = System.Drawing.Color.Transparent;
            this.Ok_button.BackgroundImage = global::WinHosts.Properties.Resources.ok_button_on;
            this.Ok_button.Cursor = System.Windows.Forms.Cursors.Hand;
            this.Ok_button.FlatAppearance.BorderSize = 0;
            this.Ok_button.FlatAppearance.MouseDownBackColor = System.Drawing.Color.Transparent;
            this.Ok_button.FlatAppearance.MouseOverBackColor = System.Drawing.Color.Transparent;
            this.Ok_button.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.Ok_button.ImeMode = System.Windows.Forms.ImeMode.NoControl;
            this.Ok_button.Location = new System.Drawing.Point(180, 159);
            this.Ok_button.Name = "Ok_button";
            this.Ok_button.Size = new System.Drawing.Size(67, 48);
            this.Ok_button.TabIndex = 24;
            this.Ok_button.UseVisualStyleBackColor = false;
            this.Ok_button.Click += new System.EventHandler(this.Ok_button_Click);
            this.Ok_button.MouseLeave += new System.EventHandler(this.Ok_button_MouseLeave);
            this.Ok_button.MouseHover += new System.EventHandler(this.Ok_button_MouseHover);
            // 
            // MsgBox
            // 
            this.MsgBox.BackColor = System.Drawing.Color.Transparent;
            this.MsgBox.Location = new System.Drawing.Point(138, 41);
            this.MsgBox.Margin = new System.Windows.Forms.Padding(20);
            this.MsgBox.Name = "MsgBox";
            this.MsgBox.Size = new System.Drawing.Size(256, 100);
            this.MsgBox.TabIndex = 25;
            this.MsgBox.TabStop = false;
            // 
            // ErrorBox
            // 
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.None;
            this.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.BackgroundImage = global::WinHosts.Properties.Resources.errorback;
            this.ClientSize = new System.Drawing.Size(420, 240);
            this.Controls.Add(this.MsgBox);
            this.Controls.Add(this.Ok_button);
            this.Controls.Add(this.IconBox);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "ErrorBox";
            this.ShowIcon = false;
            this.ShowInTaskbar = false;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "消息";
            this.TransparencyKey = System.Drawing.SystemColors.ControlDarkDark;
            ((System.ComponentModel.ISupportInitialize)(this.IconBox)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.MsgBox)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox IconBox;
        private System.Windows.Forms.Button Ok_button;
        private System.Windows.Forms.PictureBox MsgBox;
    }
}