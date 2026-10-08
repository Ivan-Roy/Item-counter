---
title: Item Counter
emoji: "\u25CF"
colorFrom: blue
colorTo: pink
sdk: streamlit
app_file: app.py
pinned: false
---

# Item counter

Counts objects in an image using OpenCV. Upload a photo, generate a sample,
or snap one with your camera, then tune the sliders until each item is
circled exactly once.

How it works: grayscale, then threshold to separate items from the
background, clean up noise with morphology, find the contours, and count the
ones whose area falls inside your size range.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501.

## Deploy to Hugging Face Spaces

1. Create a new Space at https://huggingface.co/new-space, SDK = **Streamlit**.
2. Upload `app.py`, `requirements.txt`, `README.md`, and the `.streamlit`
   folder (keep the YAML header at the top of this README — Spaces reads it).
3. The Space builds and goes live at
   `https://huggingface.co/spaces/<your-username>/<space-name>`.

## Deploy to Streamlit Community Cloud

1. Push these files to a GitHub repo.
2. At https://share.streamlit.io, click **New app**, pick the repo, and set
   the main file to `app.py`.
3. It builds and gives you a public `*.streamlit.app` URL.

## Note on the OpenCV dependency

`requirements.txt` uses `opencv-python-headless`, not `opencv-python`.
Servers have no display, and the regular package fails to import looking for
GUI libraries. The headless build is the same OpenCV without that dependency.
