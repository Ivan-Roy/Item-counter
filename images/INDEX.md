# Test images

The true count is in each filename. What each one tests:

- **01_easy_circles_count-20.png** — true count **20**. Baseline. Default settings should get this exactly.
- **02_mixed_sizes_count-15.png** — true count **15**. 15 real items plus 3 tiny specks. Raise 'ignore smaller than' to drop the specks.
- **03_shapes_count-12.png** — true count **12**. Circles, squares, triangles, stars. Counting is shape-agnostic.
- **04_light_on_dark_count-18.png** — true count **18**. Uncheck 'detect dark items on light background' for this one.
- **05_touching_clusters_count-24.png** — true count **24**. Hard case. 24 real items, but touching ones merge into one outline — contour counting will report fewer. This is what watershed would fix.
- **06_noisy_background_count-16.png** — true count **16**. Grainy background with speckle. Raise 'smoothing' and 'noise cleanup'.
- **07_many_dots_count-60.png** — true count **60**. High count of small dots (beads/seeds). Lower 'ignore smaller than'.
- **08_coins_shaded_count-10.png** — true count **10**. Shaded, shadowed discs — more photo-like. Blur helps even out the shading.

`00_contact_sheet.png` shows all of them at a glance.
