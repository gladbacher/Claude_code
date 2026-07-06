# Site — Follow the Money landing pages

Static landing pages for the four content series. No build step, no dependencies: plain HTML + one stylesheet (`css/style.css`).

## Pages

- `index.html` — hub page, all four series + combined newsletter signup
- `inequality.html`, `water.html`, `energy.html`, `transfers.html` — one per series

## Deploying

Any static host works, unchanged:

- **GitHub Pages**: Settings → Pages → deploy from branch, folder `/site` (or copy `site/` to its own repo). Custom domain via a `CNAME` file.
- **Netlify / Cloudflare Pages**: point at the repo, publish directory `site`, no build command.

## Before launch checklist

1. **Email forms** — every page has a form with `action="#"` and an HTML comment marking it. Point it at your provider:
   - Buttondown: `action="https://buttondown.com/api/emails/embed-subscribe/YOUR_USERNAME"`
   - Beehiiv/Substack: replace the form with the provider's embed snippet, keeping the surrounding `.signup` div for styling.
2. **Social preview images** — pages carry Open Graph titles/descriptions but no `og:image` yet. Add one 1200×630 image per series (a number card in house style works perfectly) and an `og:image` tag per page.
3. **Analytics** — add a privacy-respecting counter (Plausible/GoatCounter) if wanted; nothing is included by default.

## House style

White on black, Georgia for body, Helvetica for numbers/labels, one accent per series (set on `<body class="...">` in `css/style.css`). The `.numbercard` block mirrors the on-screen number cards from the videos — keep new page content inside that system.
