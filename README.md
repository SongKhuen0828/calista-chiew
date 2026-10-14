# Calista Chiew — profile page

Static one-page profile for Calista Chiew Yung Xuan (BSc (Hons) Architecture, SEGi University).
Live at https://calista-chiew.vercel.app/ (also mirrored on GitHub Pages at
https://songkhuen0828.github.io/calista-chiew/)

- `index.html` — all page content
- `assets/css/style.css`, `assets/js/main.js` — styling and the image viewer
- `assets/img/` — web images extracted from the portfolio PDF
- `assets/docs/` — downloadable CV and portfolio
- `assets/icons/`, `assets/img/places/` — software icons and school/place photos; sources and
  licences are credited in the page footer

## Updating

Edit `index.html`, then redeploy with `npx vercel deploy --prod` (and push to `main`
to update the GitHub Pages copy).

To regenerate images and PDFs after the CV or portfolio changes, put the new
`CV_Calista Chiew.pdf` and `Portfolio_Calista Chiew.pdf` in the project root and run:

    pip install pymupdf pillow
    python3 tools/build_assets.py

The image list (which PDF image goes where) is the `MANIFEST` in that script.
