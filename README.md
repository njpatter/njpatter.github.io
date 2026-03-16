# njpatter.github.io

A GitHub Pages project journal for documenting completed projects and the notes around them.

## Structure

- `content/projects.json` is the source of truth for project copy and metadata.
- `scripts/generate_site.py` builds the static pages from that data.
- `projects/<slug>/index.html` contains each generated project page.
- `assets/css/styles.css` and `assets/js/site.js` hold the shared site styling and interactions.
- `assets/img/projects/<slug>/` is where project-specific images can be added later.

## Updating the site

1. Edit `content/projects.json`.
2. Add project images to `assets/img/projects/<slug>/` using one of these filenames: `cover.jpg`, `cover.jpeg`, `cover.png`, or `cover.webp`.
3. Run `python3 scripts/generate_site.py`.
