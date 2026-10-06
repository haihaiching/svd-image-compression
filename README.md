# SVD Image Compression Demo (Flask + Nginx)

A web application running on Linux that demonstrates lossy image compression with **Singular Value Decomposition (SVD)**. Nginx serves as a reverse proxy, and a Flask backend performs the computation. Users upload an image, and the app shows rank-k approximations that keep 20%, 50%, and 80% of the total singular value sum, previewing how the image would look after compression and decompression.

## How It Works

Any m×n matrix A can be factored as **A = U S V\***, where U and V are unitary (orthogonal for real matrices) and S is diagonal with singular values σ₁ ≥ σ₂ ≥ … ≥ 0. Equivalently, A = σ₁u₁v₁\* + σ₂u₂v₂\* + … + σᵣuᵣvᵣ\*, where r is the rank of A. Keeping only the first k terms gives the best rank-k approximation of A (Eckart–Young theorem).

Storing u₁…uₖ, σ₁…σₖ, and v₁…vₖ takes k(m + n + 1) numbers instead of m·n, so this saves space only when k < mn / (m + n + 1).

A color image is split into its R, G, and B channels, and each channel is processed separately. For a ratio p, the app keeps the leading singular values until their cumulative sum exceeds p times the total.

## Results

| Original | Reconstructed (p = 0.2 / 0.5 / 0.8) |
|---|---|
| ![](examples/original.jpg) | ![](examples/processed.png) |

At p = 0.2 the image is unrecognizable, at 0.5 the outline of the cat appears, and at 0.8 it is close to the original.

Measured on the 1800×1800 sample image (1800 singular values per channel):

| p | Singular values kept per channel | Numbers to store vs. raw pixels |
|---|---|---|
| 0.2 | 3 | 0.33% |
| 0.5 | 62–65 | 7.08% |
| 0.8 | 301–305 | 33.68% |

The singular values are highly concentrated: the first 3 already exceed 20% of the total, but going from p = 0.5 to p = 0.8 requires about five times as many terms. At p = 0.8, the truncated U, S, V would take about one third as many numbers as the raw pixels, while the reconstruction is visually close to the original.

Percentages compare the stored numbers with the raw pixel values, not with the original JPEG file, which is already compressed. Raw pixels use 1 byte each, so storing U, S, V as 16-bit floats would double these figures (for example, 67.35% at p = 0.8).

## Limitations

- The app displays the reconstructed images but does not save the compressed form (the truncated U, S, V). Each reconstructed image has the same dimensions as the original, so the output files are not smaller.
- SVD compression is lossy: discarded singular values cannot be recovered.
- Formats such as JPEG use a fixed basis (DCT) that does not need to be stored with each image, which makes them more efficient as file formats.

## Project Structure

```
.
├── upload_pictures.py      # Flask app and SVD reconstruction
├── templates/
│   ├── upload.html         # Upload page
│   └── upload_ok.html      # Result page
├── static/images/          # Runtime image storage
├── nginx/flask_app.conf    # Nginx reverse proxy config
├── examples/               # Sample input and output
└── requirements.txt
```

## Getting Started

```bash
pip install -r requirements.txt
python3 upload_pictures.py
```

Then open `http://127.0.0.1:5000/upload/` in your browser.

## Deploying Behind Nginx

Edit `server_name` in `nginx/flask_app.conf` to match your server's IP address or domain, then run:

```bash
sudo cp nginx/flask_app.conf /etc/nginx/sites-available/flask_app
sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Keep the Flask app running, then visit `http://YOUR_SERVER_IP/upload/`.
