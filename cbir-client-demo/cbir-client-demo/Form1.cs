using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Threading;

namespace cbir_client_demo
{
    public partial class Form1 : Form
    {
        string web_root = "http://192.168.77.247:8080/";
        string color_histogram_api = "http://192.168.77.247:8080/color-histogram-search";
        string hash_api = "http://192.168.77.247:8080/hash-search";

        public Form1()
        {
            InitializeComponent();
        }

        // region-based color histogram
        private void button2_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog f = new OpenFileDialog())
            {
                f.Filter = "jpg图片|*.jpg|jpeg图片|*.jpeg|png图片|*.png";
                if(f.ShowDialog() == DialogResult.OK)
                {
                    pictureBox2.ImageLocation = f.FileName;

                    // image file
                    Dictionary<string, string> query_image_dic = new Dictionary<string, string>();
                    query_image_dic.Add("query_image", f.FileName);
                    
                    // form data
                    Dictionary<string, string> form_dic = new Dictionary<string, string>();
                    form_dic.Add("limit", numericUpDown2.Value.ToString());

                    new Thread((ThreadStart)(() => {
                        string json = HttpHelper.HttpPost(color_histogram_api, form_dic, query_image_dic);
                        JObject j = JObject.Parse(json);
                        System.Console.WriteLine(json);

                        // display
                        this.Invoke((Action)(() => {
                            // display json string
                            textBox1.Text = json.Replace("\n", "\r\n");

                            flowLayoutPanel1.Controls.Clear();

                            // display image
                            if (int.Parse(j["similar_images_count"].ToString()) > 0)
                            {
                                JToken[] images = j.GetValue("similar_images").ToArray();
                                for (int i = 0; i < images.Count(); ++i)
                                {
                                    PictureBox p = new PictureBox();
                                    p.ImageLocation = web_root + images[i]["image_url"].ToString();
                                    p.Width = 300;
                                    p.Height = (int)(300 * 0.618);
                                    p.SizeMode = PictureBoxSizeMode.Zoom;
                                    flowLayoutPanel1.Controls.Add(p);
                                }
                            }
                        }));
                    })).Start();
                }
            }
        }


        // image hash
        private void button1_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog f = new OpenFileDialog())
            {
                f.Filter = "jpg图片|*.jpg|jpeg图片|*.jpeg|png图片|*.png";
                if (f.ShowDialog() == DialogResult.OK)
                {
                    pictureBox1.ImageLocation = f.FileName;

                    // image file
                    Dictionary<string, string> query_image_dic = new Dictionary<string, string>();
                    query_image_dic.Add("query_image", f.FileName);

                    // form data
                    Dictionary<string, string> form_dic = new Dictionary<string, string>();
                    form_dic.Add("query_hash_type", comboBox1.SelectedIndex.ToString());
                    form_dic.Add("max_distance", numericUpDown1.Value.ToString());

                    new Thread((ThreadStart)(() => {
                        string json = HttpHelper.HttpPost(hash_api, form_dic, query_image_dic);
                        JObject j = JObject.Parse(json);
                        System.Console.WriteLine(json);

                        // display
                        this.Invoke((Action)(() => {
                            // display json string
                            textBox1.Text = json.Replace("\n", "\r\n");

                            flowLayoutPanel1.Controls.Clear();

                            // display image
                            if (int.Parse(j["similar_images_count"].ToString()) > 0)
                            {
                                JToken[] images = j.GetValue("similar_images").ToArray();
                                for (int i = 0; i < images.Count(); ++i)
                                {
                                    PictureBox p = new PictureBox();
                                    p.ImageLocation = web_root + images[i]["image_url"].ToString();
                                    p.Width = 300;
                                    p.Height = (int)(300 * 0.618);
                                    p.SizeMode = PictureBoxSizeMode.Zoom;
                                    flowLayoutPanel1.Controls.Add(p);
                                }
                            }
                        }));
                    })).Start();
                }
            }
        }
    }
}
