"""
Item counter — Streamlit app.

Counts objects in an image using the OpenCV contour pipeline:
grayscale -> blur -> threshold -> morphological cleanup -> find contours ->
filter by area -> count. Works with an uploaded image, a generated sample,
or a camera snapshot.

Local run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import cv2
import numpy as np
import streamlit as st


# ---------------------------------------------------------------- pipeline
def count_items(bgr, invert, auto, thresh_v, blur_k, clean_k,
                min_frac, max_frac, show_mask):
    """Return (annotated_bgr_image, count)."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    if blur_k > 0:
        k = blur_k * 2 + 1                      # kernel size must be odd
        gray = cv2.GaussianBlur(gray, (k, k), 0)

    flag = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    if auto:
        flag |= cv2.THRESH_OTSU                 # thresh_v ignored; chosen automatically
        _, mask = cv2.threshold(gray, 0, 255, flag)
    else:
        _, mask = cv2.threshold(gray, thresh_v, 255, flag)

    if clean_k > 0:
        kernel = np.ones((clean_k, clean_k), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # drop speckle
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # fill small holes

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    total = bgr.shape[0] * bgr.shape[1]
    min_area, max_area = min_frac * total, max_frac * total

    out = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) if show_mask else bgr.copy()

    n = 0
    for c in contours:
        area = cv2.contourArea(c)
        if not (min_area <= area <= max_area):
            continue
        n += 1
        cv2.drawContours(out, [c], -1, (208, 224, 0), 2, cv2.LINE_AA)  # cyan (BGR)

        m = cv2.moments(c)
        if m["m00"] != 0:
            cx, cy = int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])
        else:
            x, y, w, h = cv2.boundingRect(c)
            cx, cy = x + w // 2, y + h // 2

        label = str(n)
        org = (cx - 6 * len(label), cy + 6)
        cv2.putText(out, label, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (31, 26, 10), 4, cv2.LINE_AA)
        cv2.putText(out, label, org, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    return out, n


# ---------------------------------------------------------------- helpers
def decode(uploaded):
    """UploadedFile (from uploader or camera) -> BGR image."""
    data = np.frombuffer(uploaded.getvalue(), np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def make_sample(w=640, h=480):
    """Dark discs on a light background, so the app works with no upload."""
    img = np.full((h, w, 3), (230, 239, 243), np.uint8)
    rng = np.random.default_rng()
    placed = []
    target = int(rng.integers(18, 24))
    tries = 0
    while len(placed) < target and tries < 4000:
        tries += 1
        r = int(rng.integers(14, 36))
        x = int(rng.integers(r, w - r))
        y = int(rng.integers(r, h - r))
        if any((px - x) ** 2 + (py - y) ** 2 < (pr + r + 8) ** 2 for px, py, pr in placed):
            continue
        placed.append((x, y, r))
        shade = int(rng.integers(40, 100))
        cv2.circle(img, (x, y), r, (shade + 14, shade + 8, shade), -1, cv2.LINE_AA)
    return img


# ---------------------------------------------------------------- UI
st.set_page_config(page_title="Item counter", page_icon="●", layout="wide")
st.title("Count")
st.caption("Counts objects in an image by finding their outlines. "
           "Tune the controls until each item is circled exactly once.")

# --- pick an image source ---
source = st.radio("Image source", ["Upload", "Sample", "Camera"],
                  horizontal=True, label_visibility="collapsed")

bgr = None
if source == "Upload":
    f = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "bmp", "webp"])
    if f:
        bgr = decode(f)
elif source == "Sample":
    if "sample" not in st.session_state:
        st.session_state.sample = make_sample()
    if st.button("Generate new sample"):
        st.session_state.sample = make_sample()
    bgr = st.session_state.sample
else:  # Camera
    shot = st.camera_input("Take a photo of the items")
    if shot:
        bgr = decode(shot)

# --- controls ---
with st.sidebar:
    st.header("Controls")
    invert = st.checkbox("Detect dark items on a light background", value=True)
    auto = st.checkbox("Pick threshold automatically (Otsu)", value=True)
    thresh_v = st.slider("Brightness threshold", 0, 255, 128, disabled=auto)
    blur_k = st.slider("Smoothing", 0, 10, 2)
    clean_k = st.slider("Noise cleanup", 0, 12, 2)
    min_pct = st.slider("Ignore blobs smaller than (% of image)", 0.0, 3.0, 0.05, 0.01)
    max_pct = st.slider("Ignore blobs larger than (% of image)", 1, 100, 60)
    show_mask = st.checkbox("Show the detection mask")
    st.markdown(
        "<small>Touching items merge into one outline — leave gaps between them, "
        "or raise <b>Noise cleanup</b>. Turn the mask on to see what's being "
        "measured.</small>", unsafe_allow_html=True)

# --- run + show ---
if bgr is None:
    st.info("Choose an image source above to start counting.")
else:
    out, n = count_items(
        bgr, invert=invert, auto=auto, thresh_v=thresh_v,
        blur_k=blur_k, clean_k=clean_k,
        min_frac=min_pct / 100.0, max_frac=max_pct / 100.0,
        show_mask=show_mask,
    )

    left, right = st.columns([1, 3])
    left.metric("Items detected", n)
    png = cv2.imencode(".png", out)[1].tobytes()
    left.download_button("Save result", data=png,
                         file_name="count-result.png", mime="image/png")

    right.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB), use_container_width=True)
