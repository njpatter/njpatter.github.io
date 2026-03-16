from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "content" / "projects.json"
PROJECTS_DIR = ROOT / "projects"
MEDIA_DIR = ROOT / "assets" / "img" / "projects"
STYLE_PATH = "assets/css/styles.css"
SCRIPT_PATH = "assets/js/site.js"
IMAGE_NAMES = ("cover.jpg", "cover.jpeg", "cover.png", "cover.webp")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
CNAME_VALUE = "www.drnjp.com"


def load_projects() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def ensure_media_dirs(projects: list[dict]) -> None:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    for project in projects:
        directory = MEDIA_DIR / project["slug"]
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        if not any(item.name != ".gitkeep" for item in directory.iterdir()) and not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def rel(depth: int, path: str) -> str:
    prefix = "../" * depth
    return f"{prefix}{path}"


def cover_path(slug: str, depth: int) -> str | None:
    directory = MEDIA_DIR / slug
    for name in IMAGE_NAMES:
        candidate = directory / name
        if candidate.exists():
            return rel(depth, f"assets/img/projects/{slug}/{name}")
    for candidate in sorted(directory.iterdir()):
        if candidate.suffix.lower() in IMAGE_EXTENSIONS:
            return rel(depth, f"assets/img/projects/{slug}/{candidate.name}")
    return None


def media_items(slug: str, depth: int) -> list[dict]:
    directory = MEDIA_DIR / slug
    items = []
    for candidate in sorted(directory.iterdir()):
        if candidate.name.startswith("."):
            continue
        suffix = candidate.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            kind = "image"
        elif suffix in VIDEO_EXTENSIONS:
            kind = "video"
        else:
            continue
        label = candidate.stem.replace("_", " ").replace("-", " ")
        items.append(
            {
                "kind": kind,
                "src": rel(depth, f"assets/img/projects/{slug}/{candidate.name}"),
                "label": label,
            }
        )
    return items


def render_tags(tags: list[str]) -> str:
    return "".join(f'<span class="chip">{escape(tag)}</span>' for tag in tags)


def render_links(links: list[dict] | None) -> str:
    if not links:
        return ""

    items = "".join(
        f'<li><a href="{escape(link["url"])}" target="_blank" rel="noreferrer">{escape(link["label"])}</a></li>'
        for link in links
    )
    return f"""
    <section class="panel link-card">
      <p class="eyebrow">Related links</p>
      <ul class="link-list">
        {items}
      </ul>
    </section>
    """


def render_notes(notes: list[str] | None) -> str:
    if not notes:
        return ""

    items = "".join(f"<li>{escape(note)}</li>" for note in notes)
    return f"""
    <section class="panel link-card">
      <p class="eyebrow">Archive notes</p>
      <ul class="simple-list">
        {items}
      </ul>
    </section>
    """


def render_gallery(items: list[dict]) -> str:
    if not items:
        return ""

    cards = []
    for item in items:
        label = escape(item["label"])
        src = escape(item["src"])
        if item["kind"] == "image":
            media = f'<img src="{src}" alt="{label}">'
        else:
            media = f'<video controls preload="metadata" playsinline src="{src}"></video>'

        cards.append(
            f"""
            <figure class="media-card">
              <div class="media-frame">
                {media}
              </div>
              <figcaption>{label}</figcaption>
            </figure>
            """
        )

    return f"""
    <section class="panel project-gallery">
      <p class="eyebrow">Media</p>
      <h2 class="subheading">Images and videos</h2>
      <div class="media-grid">
        {''.join(cards)}
      </div>
    </section>
    """


def render_page(*, title: str, description: str, body: str, depth: int, page_class: str = "") -> str:
    body_class = f' class="{page_class}"' if page_class else ""
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(description)}">
    <link rel="stylesheet" href="{rel(depth, STYLE_PATH)}">
    <script defer src="{rel(depth, SCRIPT_PATH)}"></script>
  </head>
  <body{body_class}>
    {body}
  </body>
</html>
"""


def render_header(depth: int) -> str:
    return f"""
    <header class="site-header">
      <div class="shell">
        <a class="brand" href="{rel(depth, 'index.html')}">
          <span class="brand-mark">Project journal</span>
          <span class="brand-title">Nathan Patterson</span>
          <span class="brand-subtitle">Research, teaching, and build notes</span>
        </a>
        <nav class="nav" aria-label="Primary">
          <a class="nav-link" href="{rel(depth, 'index.html')}#projects">Projects</a>
          <a class="nav-link" href="{rel(depth, 'index.html')}#about">About</a>
          <a class="nav-link" href="mailto:nathanjpatterson@gmail.com">Email</a>
        </nav>
      </div>
    </header>
    """


def render_footer(depth: int) -> str:
    return f"""
    <footer class="site-footer">
      <div class="shell">
        <p class="footer-note">Built as a simple GitHub Pages notebook so projects stay easy to document and update.</p>
        <a class="footer-note" href="mailto:nathanjpatterson@gmail.com">nathanjpatterson@gmail.com</a>
      </div>
    </footer>
    """


def render_home(projects: list[dict]) -> str:
    project_cards = []
    for project in projects:
        tags = " ".join(project["tags"])
        tag_markup = render_tags(project["tags"])
        project_cards.append(
            f"""
            <article class="panel project-card reveal theme-{escape(project['theme'])}" data-tags="{escape(tags)}">
              <a href="projects/{escape(project['slug'])}/">
                <div>
                  <p class="project-card-label">{escape(project['period'])}</p>
                  <h3 class="project-card-title">{escape(project['title'])}</h3>
                </div>
                <p class="project-card-summary">{escape(project['summary'])}</p>
                <div class="tag-row">{tag_markup}</div>
                <p class="project-card-period">Open notes</p>
              </a>
            </article>
            """
        )

    body = f"""
    {render_header(0)}
    <main>
      <section class="hero">
        <div class="shell hero-grid">
          <div class="panel hero-copy">
            <p class="eyebrow">GitHub Pages refresh</p>
            <h1 class="headline">Things I've built, taught, tested, and occasionally overcomplicated.</h1>
            <p class="lede">This site is less a formal portfolio and more a running notebook. It gathers the projects I keep coming back to when I want to explain how I work: teaching tools, automation builds, simulation work, startup scars, and a few projects that only happened because they sounded fun.</p>
            <div class="button-row">
              <a class="button button-primary" href="#projects">Browse the journal</a>
              <a class="button button-secondary" href="mailto:nathanjpatterson@gmail.com">Say hello</a>
            </div>
            <div class="hero-stats" aria-label="Site stats">
              <div class="stat">
                <span class="mini-label">Entries</span>
                <strong>{len(projects)}</strong>
                <span class="lede-muted">documented projects</span>
              </div>
              <div class="stat">
                <span class="mini-label">Threads</span>
                <strong>4</strong>
                <span class="lede-muted">research, teaching, automation, fabrication</span>
              </div>
              <div class="stat">
                <span class="mini-label">Style</span>
                <strong>Notebook</strong>
                <span class="lede-muted">more journal than brochure</span>
              </div>
            </div>
          </div>
          <aside class="panel hero-note">
            <p class="eyebrow">How to read this</p>
            <ul class="note-list">
              <li>Every project has its own page so notes, media, and updates can stay grouped together.</li>
              <li>Filters below make it easier to jump between teaching work, automation builds, and older experiments.</li>
              <li>Images can be added over time without changing the structure of the site again.</li>
            </ul>
          </aside>
        </div>
      </section>

      <section class="section" id="about">
        <div class="shell">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Working themes</p>
              <h2 class="section-title">The projects tend to cluster in a few directions.</h2>
            </div>
          </div>
          <div class="section-grid">
            <article class="panel section-card reveal">
              <p class="eyebrow">Research + simulation</p>
              <p class="section-copy">Tools for understanding physical systems better, whether that means wind tunnel fixtures, CFD pipelines, or remote lab environments.</p>
            </article>
            <article class="panel section-card reveal">
              <p class="eyebrow">Teaching builds</p>
              <p class="section-copy">Projects that exist because students learn more when lab gear is accessible, playful, and a little more ambitious than it strictly needs to be.</p>
            </article>
            <article class="panel section-card reveal">
              <p class="eyebrow">Automation for fun</p>
              <p class="section-copy">Machines that serve drinks, route printer jobs, or otherwise solve problems nobody asked me to solve in the most entertaining way available.</p>
            </article>
          </div>
        </div>
      </section>

      <section class="section" id="projects">
        <div class="shell">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Project index</p>
              <h2 class="section-title">Browse by idea, not by resume category.</h2>
            </div>
            <p class="count-label" data-count>{len(projects)} entries showing</p>
          </div>
          <div class="filters" role="toolbar" aria-label="Project filters">
            <button class="filter-button is-active" data-filter="all" type="button">All</button>
            <button class="filter-button" data-filter="teaching" type="button">Teaching</button>
            <button class="filter-button" data-filter="automation" type="button">Automation</button>
            <button class="filter-button" data-filter="research" type="button">Research</button>
            <button class="filter-button" data-filter="simulation" type="button">Simulation</button>
            <button class="filter-button" data-filter="fabrication" type="button">Fabrication</button>
            <button class="filter-button" data-filter="startup" type="button">Startup</button>
            <button class="filter-button" data-filter="games" type="button">Games</button>
          </div>
          <div class="project-grid">
            {''.join(project_cards)}
          </div>
        </div>
      </section>
    </main>
    {render_footer(0)}
    """
    return render_page(
        title="Nathan Patterson | Project Journal",
        description="A journal-style archive of Nathan Patterson's projects in research, teaching, automation, fabrication, and simulation.",
        body=body,
        depth=0,
    )


def render_project(project: dict, previous_project: dict | None, next_project: dict | None) -> str:
    slug = project["slug"]
    cover = cover_path(slug, 2)
    gallery = media_items(slug, 2)
    story = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in project["body"])
    highlights = "".join(f"<li>{escape(item)}</li>" for item in project["highlights"])
    tools = ", ".join(project["tools"])
    languages = ", ".join(project["languages"])
    tags = render_tags(project["tags"])
    extra_links = render_links(project.get("links"))
    extra_notes = render_notes(project.get("notes"))

    if cover:
        visual = f'<figure class="project-cover"><img src="{escape(cover)}" alt="{escape(project["title"])} project image"></figure>'
    else:
        visual = f"""
        <div class="project-banner">
          <div class="banner-mark">{escape(project['title'][:1])}</div>
          <div class="banner-copy">
            <p class="eyebrow">{escape(project['status'])}</p>
            <h2 class="subheading">{escape(project['title'])}</h2>
            <p class="project-summary">Image archive coming soon. The page is ready for project photos whenever they are added.</p>
          </div>
        </div>
        """

    footer_links = ['<a class="footer-chip" href="../../index.html#projects">Back to all entries</a>']
    if previous_project:
        footer_links.insert(
            0,
            f'<a class="footer-chip" href="../{escape(previous_project["slug"])}/">Previous: {escape(previous_project["title"])}</a>',
        )
    if next_project:
        footer_links.append(
            f'<a class="footer-chip" href="../{escape(next_project["slug"])}/">Next: {escape(next_project["title"])}</a>'
        )

    body = f"""
    {render_header(2)}
    <main class="project-page">
      <div class="shell">
        <a class="back-link" href="../../index.html#projects">Back to project journal</a>
        <section class="project-head">
          <article class="panel project-intro">
            <p class="eyebrow">Project notes</p>
            <div class="meta-pills">
              <span class="chip chip-status">{escape(project['status'])}</span>
              <span class="chip">{escape(project['period'])}</span>
            </div>
            <h1 class="project-title">{escape(project['title'])}</h1>
            <p class="project-summary">{escape(project['summary'])}</p>
            <div class="tag-row">{tags}</div>
          </article>
          {visual}
        </section>

        <section class="project-layout">
          <div class="stack">
            <article class="panel project-story">
              <p class="eyebrow">What happened</p>
              <h2 class="subheading">Build story</h2>
              <div class="story-copy">
                {story}
              </div>
            </article>

            <article class="panel project-highlights">
              <p class="eyebrow">Why it mattered</p>
              <h2 class="subheading">Project notes</h2>
              <ul class="highlight-list">
                {highlights}
              </ul>
            </article>
            {render_gallery(gallery)}
          </div>

          <aside class="stack">
            <section class="panel sidebar-card">
              <p class="eyebrow">Snapshot</p>
              <ul class="meta-list">
                <li><strong>Period</strong><span class="meta-text">{escape(project['period'])}</span></li>
                <li><strong>Status</strong><span class="meta-text">{escape(project['status'])}</span></li>
                <li><strong>Tools</strong><span class="meta-text">{escape(tools)}</span></li>
                <li><strong>Languages</strong><span class="meta-text">{escape(languages)}</span></li>
              </ul>
            </section>
            {extra_links}
            {extra_notes}
          </aside>
        </section>

        <nav class="project-footer-nav" aria-label="Project navigation">
          {' '.join(footer_links)}
        </nav>
      </div>
    </main>
    {render_footer(2)}
    """
    return render_page(
        title=f"{project['title']} | Nathan Patterson",
        description=project["summary"],
        body=body,
        depth=2,
        page_class="project-body",
    )


def render_not_found() -> str:
    body = f"""
    {render_header(0)}
    <main class="project-page">
      <div class="shell">
        <section class="panel not-found">
          <p class="eyebrow">404</p>
          <h1 class="not-found-title">That page wandered off.</h1>
          <p class="project-summary">The journal entry you were looking for is not here, but the full project index is still intact.</p>
          <div class="button-row">
            <a class="button button-primary" href="index.html#projects">Go to the project index</a>
            <a class="button button-secondary" href="mailto:nathanjpatterson@gmail.com">Email Nathan</a>
          </div>
        </section>
      </div>
    </main>
    {render_footer(0)}
    """
    return render_page(
        title="Page not found | Nathan Patterson",
        description="The requested page could not be found.",
        body=body,
        depth=0,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    projects = load_projects()
    ensure_media_dirs(projects)

    write(ROOT / "index.html", render_home(projects))
    write(ROOT / "404.html", render_not_found())
    write(ROOT / "CNAME", CNAME_VALUE + "\n")

    for index, project in enumerate(projects):
        previous_project = projects[index - 1] if index > 0 else None
        next_project = projects[index + 1] if index < len(projects) - 1 else None
        write(PROJECTS_DIR / project["slug"] / "index.html", render_project(project, previous_project, next_project))


if __name__ == "__main__":
    main()
