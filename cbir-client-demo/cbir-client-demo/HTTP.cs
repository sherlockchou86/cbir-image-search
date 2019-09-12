using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;

namespace cbir_client_demo
{
    class HttpHelper
    {
        public static string HttpPost(string url, Dictionary<string, string> postData, Dictionary<string, string> files)
        {
            HttpWebRequest request = WebRequest.Create(url) as HttpWebRequest;
            CookieContainer cookieContainer = new CookieContainer();
            request.CookieContainer = cookieContainer;
            request.AllowAutoRedirect = true;
            request.Method = "POST";
            string boundary = DateTime.Now.Ticks.ToString("X"); // bound
            request.ContentType = "multipart/form-data;charset=utf-8;boundary=" + boundary;

            byte[] itemBoundaryBytes = Encoding.UTF8.GetBytes("\r\n--" + boundary + "\r\n");
            byte[] endBoundaryBytes = Encoding.UTF8.GetBytes("\r\n--" + boundary + "--\r\n");

            Stream postStream = request.GetRequestStream();
            //postStream.Write(itemBoundaryBytes, 0, itemBoundaryBytes.Length);

            // form data
            if (postData != null && postData.Count > 0)
            {

                var keys = postData.Keys;
                foreach (var key in keys)
                {
                    postStream.Write(itemBoundaryBytes, 0, itemBoundaryBytes.Length);
                    string strHeader = string.Format("Content-Disposition: form-data; name=\"{0}\"\r\n\r\n", key);
                    byte[] strByte = System.Text.Encoding.UTF8.GetBytes(strHeader);
                    postStream.Write(strByte, 0, strByte.Length);

                    byte[] value = System.Text.Encoding.UTF8.GetBytes(string.Format("{0}", postData[key]));
                    postStream.Write(value, 0, value.Length);
                }
            }
            //postStream.Write(itemBoundaryBytes, 0, itemBoundaryBytes.Length);

            // file data
            if (files != null && files.Count > 0)
            {
                var keys = files.Keys;

                foreach (var key in keys)
                {
                    postStream.Write(itemBoundaryBytes, 0, itemBoundaryBytes.Length);
                    string filePath = files[key];
                    int pos = filePath.LastIndexOf("\\");
                    string fileName = filePath.Substring(pos + 1);
                    StringBuilder sbHeader = new StringBuilder(string.Format("Content-Disposition:form-data;name=\"{0}\";filename=\"{1}\"\r\nContent-Type:application/octet-stream\r\n\r\n", key, fileName));
                    byte[] postHeaderBytes = Encoding.UTF8.GetBytes(sbHeader.ToString());

                    FileStream fs = new FileStream(files[key], FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
                    byte[] bArr = new byte[fs.Length];
                    fs.Read(bArr, 0, bArr.Length);
                    fs.Close();
                    postStream.Write(postHeaderBytes, 0, postHeaderBytes.Length);
                    postStream.Write(bArr, 0, bArr.Length);

                }

            }
            postStream.Write(endBoundaryBytes, 0, endBoundaryBytes.Length); // end flag
            postStream.Close();
            // send http request
            HttpWebResponse response = request.GetResponse() as HttpWebResponse;
            // receive http response
            Stream instream = response.GetResponseStream();
            StreamReader sr = new StreamReader(instream, Encoding.UTF8);
            // return result
            string content = sr.ReadToEnd();
            return content;

        }

    }
}