using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;

namespace WinHosts
{
    class ImgTrans
    {
        #region 图片旋转函数
        /// <summary>
        /// 以顺时针为方向对图像进行旋转
        /// </summary>
        /// <param name="b">位图流</param>
        /// <param name="angle">旋转角度[0,360](前台给的)</param>
        /// <returns></returns>
        public static Bitmap Rotate(Bitmap b, int angle)
        {
            angle = angle % 360;

            //弧度转换
            double radian = angle * Math.PI / 180.0;
            double cos = Math.Cos(radian);
            double sin = Math.Sin(radian);

            //原图的宽和高
            int w = b.Width;
            int h = b.Height;
            int W = w;
            int H = h;
            //int W = (int)(Math.Max(Math.Abs(w * cos - h * sin), Math.Abs(w * cos + h * sin)));
            //int H = (int)(Math.Max(Math.Abs(w * sin - h * cos), Math.Abs(w * sin + h * cos)));

            //目标位图
            Bitmap dsImage = new Bitmap(W, H);
            System.Drawing.Graphics g = System.Drawing.Graphics.FromImage(dsImage);
            g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.Bilinear;
            g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality;

            //计算偏移量
            Point Offset = new Point((W - w) / 2, (H - h) / 2);

            //构造图像显示区域：让图像的中心与窗口的中心点一致
            Rectangle rect = new Rectangle(Offset.X, Offset.Y, w, h);
            Point center = new Point(rect.X + rect.Width / 2, rect.Y + rect.Height / 2);

            g.TranslateTransform(center.X, center.Y);
            g.RotateTransform(angle);

            //恢复图像在水平和垂直方向的平移
            g.TranslateTransform(-center.X, -center.Y);
            g.DrawImage(b, rect);

            //重至绘图的所有变换
            g.ResetTransform();

            g.Save();
            g.Dispose();
            return dsImage;
        }
        #endregion
        #region 图片移动

        /// <summary>
        /// 图片移动
        /// </summary>
        /// <param name="bitmap">原图</param>
        /// <param name="x">水平方向</param>
        /// <param name="y">竖直方向</param>
        /// <returns></returns>
        public static Bitmap MoveIMG(Bitmap bitmap, int x, int y)
        {
            Bitmap bm = new Bitmap(bitmap.Size.Width - Math.Abs(x), bitmap.Size.Height - Math.Abs(y));//新建一个图片    长宽高都等于 原图
            Color c = new Color();
            if (x >= 0 && y >= 0)//以远点坐标
            {
                for (int i = 0; i < bitmap.Width - x; i++)
                {
                    for (int j = 0; j < bitmap.Height - y; j++)
                    {
                        c = bitmap.GetPixel(i, j);
                        bm.SetPixel(i, j, c);
                    }
                }
            }
            else if (x >= 0 && y <= 0)
            {
                for (int i = 0; i < bitmap.Width - x; i++)
                {
                    for (int j = Math.Abs(y); j < bitmap.Height; j++)
                    {
                        c = bitmap.GetPixel(i, j);
                        bm.SetPixel(i + x, j - Math.Abs(y), c);
                    }
                }
            }
            else if (x <= 0 && y >= 0)
            {
                for (int i = Math.Abs(x); i < bitmap.Width; i++)
                {
                    for (int j = 0; j < bitmap.Height - y; j++)
                    {
                        c = bitmap.GetPixel(i, j);
                        bm.SetPixel(i - Math.Abs(x), j + y, c);
                    }
                }
            }
            else if (x <= 0 & y <= 0)
            {
                for (int i = Math.Abs(x); i < bitmap.Width; i++)
                {
                    for (int j = Math.Abs(y); j < bitmap.Height; j++)
                    {
                        c = bitmap.GetPixel(i, j);
                        bm.SetPixel(i - Math.Abs(x), j - Math.Abs(y), c);
                    }
                }
            }
            return bm;
        }
        #endregion
    }
}
