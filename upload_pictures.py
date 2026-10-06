
from flask import Flask, render_template, request, send_file, redirect, url_for, make_response,jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import time
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io

from datetime import timedelta

#设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp','jpeg','gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)

@app.route('/upload/', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "The supported image types for upload are limited to : png、PNG、jpg、JPG、bmp"})

        basepath = os.path.dirname(__file__)  # 当前文件所在路径

        upload_path = os.path.join(basepath, 'static/images', 'original.jpg')  
        f.save(upload_path)

        # 使用Opencv读取图片
        img = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images', 'original.jpg'), img)

        # 圖片處理
        img = Image.open(upload_path)
        a = np.array(img)
        plt.figure(figsize=(12, 8))
        for idx, i in enumerate(np.arange(0.2, 0.9, 0.3), start=1):
            u, sigma, v = np.linalg.svd(a[:, :, 0], full_matrices=False)
            R = rebuild_img(u, sigma, v, i)

            u, sigma, v = np.linalg.svd(a[:, :, 1], full_matrices=False)
            G = rebuild_img(u, sigma, v, i)

            u, sigma, v = np.linalg.svd(a[:, :, 2], full_matrices=False)
            B = rebuild_img(u, sigma, v, i)

            I = np.stack((R, G, B), 2)
            plt.subplot(2,3,idx)
            plt.title(f"{i:.1f}")
            plt.imshow(I)
            plt.axis('off')

        # 保存處理後的圖片
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        processed_image_path = os.path.join(basepath, 'static/images', 'processed.png')
        with open(processed_image_path, 'wb') as f:
            f.write(buffer.read())

        return render_template('upload_ok.html')
    return render_template('upload.html')

def rebuild_img(u, sigma, v, p):
    m=len(u)
    n=v.shape[1]
    a=np.zeros((m,n))
 
    count=(int)(sum(sigma))
    curSum=0
    k=0
 
    while curSum<=count*p and k<len(sigma):
        uk=u[:,k].reshape(m,1)
        vk=v[k].reshape(1,n)
        a+=sigma[k]*np.dot(uk,vk)
        curSum+=sigma[k]
        k+=1
 
    a[a<0]=0
    a[a>255]=255
    return np.rint(a).astype(np.uint8)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
 
