# SVD Image Compression Web App (Flask + Nginx)

A web application running on Linux that compresses images using
**Singular Value Decomposition (SVD)**. Nginx serves as a reverse proxy,
and a Flask backend performs the computation. Users upload an image,
and the app shows reconstructions that keep 20%, 50%, and 80% of the
total singular value sum, so you can compare quality against compression.

## How It Works

Any m×n matrix A can be factored as **A = U S V\***, where U and V are
unitary and S is diagonal with singular values σ₁ ≥ σ₂ ≥ … ≥ 0. Equivalently,

A = σ₁u₁v₁\* + σ₂u₂v₂\* + … + σₘuₘvₘ\*

Since the singular values decrease, the first few terms capture most of
the image. Keeping only the first k terms gives a rank-k approximation,
which needs k(m + n + 1) numbers instead of m·n.

A color image is split into its R, G, and B channels, and each channel is
compressed separately. For a ratio p, the app keeps the leading singular
values until their cumulative sum exceeds p times the total.

## Results

| Original | Compressed (p = 0.2 / 0.5 / 0.8) |
|---|---|
| ![](examples/original.jpg) | ![](examples/processed.png) |

At p = 0.2 the image is unrecognizable, at 0.5 the outline of the cat
appears, and at 0.8 it is close to the original.

## Project Structure

```
.
├── upload_pictures.py      # Flask app and SVD compression
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

Then open http://127.0.0.1:5000/upload/ in your browser.

## Deploying Behind Nginx

Edit `server_name` in `nginx/flask_app.conf` to match your server's IP
address or domain, then run:

```bash
sudo cp nginx/flask_app.conf /etc/nginx/sites-available/flask_app
sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Keep the Flask app running, then visit `http://<your-server>/upload/`.

