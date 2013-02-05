using System;
using System.Drawing;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace WinHosts
{
    class GeometryCalc
    {
        /// <summary>
        /// 根据三点坐标计算向量夹角
        /// </summary>
        /// <param name="cen">中心点</param>
        /// <param name="first">始边端点</param>
        /// <param name="second">终边端点</param>
        /// <returns>夹角弧度</returns>
        public static float Angle(Point cen, Point first, Point second)
        {
            float dx1, dx2, dy1, dy2;
            float angle;

            dx1 = first.X - cen.X;
            dy1 = first.Y - cen.Y;

            dx2 = second.X - cen.X;
            dy2 = second.Y - cen.Y;

            float c = (float)Math.Sqrt(dx1 * dx1 + dy1 * dy1) * (float)Math.Sqrt(dx2 * dx2 + dy2 * dy2);

            if (c != 0)
                angle = (float)Math.Acos((dx1 * dx2 + dy1 * dy2) / c);
            else
                angle = 1;

            if (dx1*dy2 - dx2*dy1 > 0)
                return angle;
            else if (dx1*dy2 - dx2*dy1 < 0)
                return -angle;
            else
                return 1;
        }

        /// <summary>
        /// 弧度转换为角度
        /// </summary>
        /// <param name="radian">弧度值</param>
        /// <returns>角度值</returns>
        public static int RadToDeg(float radian)
        {
            return (int)Math.Round(radian * 180.0 / Math.PI);
        }
    }
}
