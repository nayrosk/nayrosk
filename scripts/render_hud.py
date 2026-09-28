#!/usr/bin/env python3
"""Render the static HUD SVGs used by the profile README.

Style follows nayrosk/orbital-hud: black canvas, monospace type, hairline
white chrome, color reserved for data domains.

Usage: python3 scripts/render_hud.py   (writes into profile/hud/)
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "profile" / "hud"

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG = "#000"
PANEL = "#090b0f"
LINE = "rgba(255,255,255,.14)"
LINE2 = "rgba(255,255,255,.07)"
TXT = "#eef2f7"
BODY = "#cdd6e2"
DIM = "#7c8595"

# Data domains: the only saturated colors.
DOMAIN = {
    "rust": "#ff6b3d",
    "chain": "#3fe0ff",
    "ai": "#ff66d8",
    "sec": "#ffc24d",
}

CHAR_W = 0.6  # monospace advance, in em


def text_w(s, size, tracking=0.0):
    return len(s) * size * (CHAR_W + tracking)


def base_style(extra=""):
    return f"""<style>
  text{{font-family:{FONT};}}
  .eyebrow{{font-size:11px;letter-spacing:.2em;fill:{DIM}}}
  .pulse{{animation:pulse 2.4s ease-in-out infinite}}
  @keyframes pulse{{50%{{opacity:.25}}}}
  .scan{{animation:scan 7s linear infinite}}
  @keyframes scan{{from{{transform:translateY(-60px)}}to{{transform:translateY(var(--h))}}}}
  {extra}
</style>"""


def defs(w, h, uid):
    return f"""<defs>
  <pattern id="lines-{uid}" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="rgba(255,255,255,.03)"/>
  </pattern>
  <radialGradient id="vig-{uid}" cx="50%" cy="50%" r="75%">
    <stop offset="60%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity=".7"/>
  </radialGradient>
  <linearGradient id="band-{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".035"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="clip-{uid}"><rect width="{w}" height="{h}" rx="12"/></clipPath>
</defs>"""


def crt(w, h, uid):
    """Scanlines, a slow moving light band and a vignette."""
    return f"""<g clip-path="url(#clip-{uid})" pointer-events="none">
  <rect width="{w}" height="{h}" fill="url(#lines-{uid})"/>
  <rect class="scan" style="--h:{h + 60}px" width="{w}" height="60" fill="url(#band-{uid})"/>
  <rect width="{w}" height="{h}" fill="url(#vig-{uid})"/>
</g>"""


def svg(w, h, body, label, extra_style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">\n'
        f"<title>{escape(label)}</title>\n{base_style(extra_style)}\n{body}\n</svg>\n"
    )


def panel(w, h, uid):
    return (
        f'<rect width="{w}" height="{h}" rx="12" fill="{BG}"/>'
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="11.5" '
        f'fill="{PANEL}" stroke="{LINE}"/>'
        f'<line x1="12" y1="1.5" x2="{w - 12}" y2="1.5" stroke="rgba(255,255,255,.05)"/>'
    )


def corner_ticks(w, h, inset=14, size=8):
    c = f'stroke="{DIM}" stroke-width="1" fill="none" opacity=".6"'
    i, s = inset, size
    return (
        f'<path d="M{i} {i + s}V{i}H{i + s}" {c}/>'
        f'<path d="M{w - i - s} {i}H{w - i}V{i + s}" {c}/>'
        f'<path d="M{i} {h - i - s}V{h - i}H{i + s}" {c}/>'
        f'<path d="M{w - i - s} {h - i}H{w - i}V{h - i - s}" {c}/>'
    )


# --------------------------------------------------------------------------
# Banner
# --------------------------------------------------------------------------

def banner():
    w, h, uid = 1200, 320, "banner"
    stars = []
    # Deterministic star field (no randomness so re-renders do not churn git).
    for k in range(70):
        x = (k * 7919 * 31 + k * k * 104729) % w
        y = (k * k * 6007 + k * 2741 + 37) % h
        r = 0.6 if k % 5 else 1.1
        o = 0.18 + (k % 7) * 0.05
        stars.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{o:.2f}"/>')

    cx, cy = 940, 168
    orbits = [
        (150, 56, -14, DOMAIN["rust"], 18, "RUST SYSTEMS"),
        (118, 40, 22, DOMAIN["chain"], 12, "BLOCKCHAIN INFRA"),
        (86, 28, -38, DOMAIN["ai"], 9, "LLM TOOLING"),
    ]
    orbit_svg = []
    for i, (rx, ry, rot, col, dur, _) in enumerate(orbits):
        path = f"M{cx - rx},{cy} a{rx},{ry} 0 1,0 {2 * rx},0 a{rx},{ry} 0 1,0 {-2 * rx},0"
        orbit_svg.append(
            f'<g transform="rotate({rot} {cx} {cy})">'
            f'<path id="orb{i}" d="{path}" fill="none" stroke="{LINE}" stroke-dasharray="2 5"/>'
            f'<circle r="4.5" fill="{col}"><animateMotion dur="{dur}s" repeatCount="indefinite">'
            f'<mpath href="#orb{i}"/></animateMotion></circle>'
            f'<circle r="12" fill="{col}" opacity=".18"><animateMotion dur="{dur}s" '
            f'repeatCount="indefinite"><mpath href="#orb{i}"/></animateMotion></circle>'
            f"</g>"
        )
    core = (
        f'<circle cx="{cx}" cy="{cy}" r="26" fill="#0d1117" stroke="rgba(255,255,255,.35)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{LINE2}"/>'
        f'<text x="{cx}" y="{cy + 4}" text-anchor="middle" font-size="11" '
        f'letter-spacing=".2em" fill="{TXT}">NRK</text>'
    )

    legend = []
    lx, ly = 1000, 250
    for i, (*_, col, _d, name) in enumerate(orbits):
        y = ly + i * 18
        legend.append(
            f'<circle cx="{lx}" cy="{y - 4}" r="3.5" fill="{col}"/>'
            f'<text x="{lx + 12}" y="{y}" font-size="10" letter-spacing=".16em" fill="{DIM}">{name}</text>'
        )

    tagline = "Rust engineer — blockchain infra & LLM tooling"
    cursor_x = 64 + text_w(tagline, 20) + 6

    body = f"""{defs(w, h, uid)}
{panel(w, h, uid)}
<g clip-path="url(#clip-{uid})">{''.join(stars)}</g>
{corner_ticks(w, h)}
<text x="64" y="70" class="eyebrow">// PROFILE · MARSEILLE, FR</text>
<text x="64" y="150" font-size="64" font-weight="700" letter-spacing=".22em" fill="#fff">NAYROSK</text>
<text x="64" y="196" font-size="20" fill="{BODY}">{escape(tagline)}</text>
<rect class="blink" x="{cursor_x:.0f}" y="180" width="11" height="20" fill="{DOMAIN['rust']}"/>
<line x1="64" y1="232" x2="700" y2="232" stroke="{LINE}"/>
<circle class="pulse" cx="70" cy="262" r="4" fill="#3fdc7e"/>
<text x="84" y="266" font-size="11" letter-spacing=".16em" fill="{DIM}">OPEN TO · FULL-TIME · FREELANCE · OSS COLLABORATION</text>
<text x="64" y="290" font-size="11" letter-spacing=".16em" fill="{DIM}">CEO @ DOCKERMINT · NODE OPERATOR</text>
{''.join(orbit_svg)}
{core}
{''.join(legend)}
{crt(w, h, uid)}"""
    extra = ".blink{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    return svg(w, h, body, "Nayrosk — Rust engineer, blockchain infra and LLM tooling", extra)


# --------------------------------------------------------------------------
# Section headers
# --------------------------------------------------------------------------

def section(idx, title, meta=""):
    w, h = 1200, 48
    label = f"{idx:02d} · {title.upper()}"
    lw = text_w(label, 13, 0.24)
    body = (
        f'<text x="2" y="30" font-size="13" letter-spacing=".24em" fill="{TXT}">{escape(label)}</text>'
        f'<line x1="{lw + 20:.0f}" y1="25.5" x2="{w - 30 - text_w(meta, 11, .16):.0f}" '
        f'y2="25.5" stroke="{LINE}"/>'
        f'<text x="{w - 2}" y="29" text-anchor="end" font-size="11" letter-spacing=".16em" '
        f'fill="{DIM}">{escape(meta.upper())}</text>'
    )
    return svg(w, h, body, title)


# --------------------------------------------------------------------------
# Project cards
# --------------------------------------------------------------------------

PROJECTS = [
    {
        "slug": "overbrainer",
        "domain": "ai",
        "kind": "rust · llm · cli",
        "title": "overbrainer",
        "lines": [
            "Distill a large LLM into a small open-weights",
            "model: generate questions, capture reasoning,",
            "fine-tune with Axolotl locally, over SSH or Runpod.",
        ],
        "tags": ["crates.io v0.3.1", "ratatui tui", "ci"],
    },
    {
        "slug": "pebblify",
        "domain": "chain",
        "kind": "go · cosmos · dockermint",
        "title": "pebblify",
        "lines": [
            "Crash-safe LevelDB → PebbleDB migration for",
            "Cosmos/CometBFT nodes. Adaptive batching,",
            "checkpoint recovery and data verification.",
        ],
        "tags": ["v0.4.3", "180+ commits", "60+ prs"],
    },
    {
        "slug": "evm-indexer",
        "domain": "rust",
        "kind": "rust · evm · tokio",
        "title": "evm-indexer",
        "lines": [
            "Fault-tolerant multi-chain EVM event indexer.",
            "WebSocket/HTTP RPC failover, circuit breaker,",
            "MongoDB storage, Prometheus metrics.",
        ],
        "tags": ["multi-chain", "prometheus", "docker"],
    },
    {
        "slug": "malware-analysis",
        "domain": "sec",
        "kind": "security · write-up",
        "title": "the take-home was the malware",
        "lines": [
            "Teardown of a fake Web3 recruiter repo: two",
            "hidden loaders, an AES stage, a RAT and a wallet",
            "stealer. Decoded offline, never executed.",
        ],
        "tags": ["reverse engineering", "node.js", "2026"],
    },
    {
        "slug": "skills-marketplace",
        "domain": "ai",
        "kind": "claude code · plugins",
        "title": "skills-marketplace",
        "lines": [
            "Claude Code plugin marketplace. Ships",
            "podman-quadlet-service: rootless systemd units",
            "with pinned images, secrets and healthchecks.",
        ],
        "tags": ["claude code", "podman", "systemd"],
    },
    {
        "slug": "crazysol",
        "domain": "chain",
        "kind": "rust · solana · anchor",
        "title": "crazysol",
        "lines": [
            "On-chain economy game program: bonding curve",
            "tokenomics, yield, multi-level referrals and",
            "streak rewards. Was live at crazysol.io, archived.",
        ],
        "tags": ["anchor", "pda", "defi"],
    },
]


def card(i, p):
    w, h, uid = 600, 230, f"c{i}"
    col = DOMAIN[p["domain"]]
    lines = "".join(
        f'<text x="28" y="{112 + k * 22}" font-size="14" fill="{BODY}">{escape(t)}</text>'
        for k, t in enumerate(p["lines"])
    )
    tags, x = [], 28
    for t in p["tags"]:
        label = t.upper()
        tw = text_w(label, 10, 0.08) + 18
        tags.append(
            f'<rect x="{x}" y="186" width="{tw:.0f}" height="22" rx="11" fill="none" stroke="{LINE}"/>'
            f'<text x="{x + 9}" y="201" font-size="10" letter-spacing=".08em" fill="{DIM}">{escape(label)}</text>'
        )
        x += tw + 8
    body = f"""{defs(w, h, uid)}
{panel(w, h, uid)}
<rect x="1" y="1" width="{w - 2}" height="3" rx="1.5" fill="{col}" clip-path="url(#clip-{uid})"/>
<circle class="pulse" cx="32" cy="36" r="3.5" fill="{col}"/>
<text x="44" y="40" class="eyebrow">{i + 1:02d} · {escape(p['kind'].upper())}</text>
<text x="{w - 28}" y="41" text-anchor="end" font-size="15" fill="{DIM}">↗</text>
<text x="28" y="78" font-size="22" font-weight="700" fill="#fff">{escape(p['title'])}</text>
{lines}
{''.join(tags)}
{crt(w, h, uid)}"""
    return svg(w, h, body, f"{p['title']}: {' '.join(p['lines'])}")


# --------------------------------------------------------------------------
# Stack panel
# --------------------------------------------------------------------------

STACK = [
    ("systems", "rust", ["Rust", "C", "Go", "Zig"]),
    ("blockchain", "chain", ["Solana · Anchor", "EVM · Solidity", "Cosmos · CometBFT", "MultiversX"]),
    ("ai tooling", "ai", ["Claude Code", "Axolotl", "Runpod", "OpenClaw"]),
    ("infra", None, ["Docker · Podman", "Kubernetes · Helm", "Terraform", "GitHub Actions"]),
    ("data", None, ["PostgreSQL", "Redis", "MongoDB", "Prometheus"]),
    ("web", None, ["TypeScript", "React · Next.js", "Node.js", "tRPC"]),
]


def stack():
    w, uid = 1200, "stack"
    row_h, top = 34, 58
    h = top + row_h * len(STACK) - 4
    rows = []
    for r, (name, dom, items) in enumerate(STACK):
        y = top + r * row_h
        col = DOMAIN[dom] if dom else "rgba(255,255,255,.5)"
        rows.append(
            f'<line x1="28" y1="{y - 22}" x2="{w - 28}" y2="{y - 22}" stroke="{LINE2}"/>'
            f'<circle cx="34" cy="{y - 4}" r="3.5" fill="{col}"/>'
            f'<text x="48" y="{y}" font-size="11" letter-spacing=".2em" fill="{DIM}">{name.upper()}</text>'
        )
        for c, item in enumerate(items):
            rows.append(
                f'<text x="{250 + c * 235}" y="{y}" font-size="14" fill="{TXT}">{escape(item)}</text>'
            )
    body = f"""{defs(w, h, uid)}
{panel(w, h, uid)}
<text x="28" y="30" class="eyebrow">// STACK · DAILY DRIVERS</text>
<text x="{w - 28}" y="30" text-anchor="end" class="eyebrow">ARCH LINUX · KDE · ZSH · VIM</text>
{''.join(rows)}
{crt(w, h, uid)}"""
    return svg(w, h, body, "Stack: " + "; ".join(f"{n}: {', '.join(i)}" for n, _, i in STACK))


# --------------------------------------------------------------------------
# Contact
# --------------------------------------------------------------------------

def contact():
    w, h, uid = 1200, 120, "contact"
    body = f"""{defs(w, h, uid)}
{panel(w, h, uid)}
{corner_ticks(w, h, 12, 6)}
<circle class="pulse" cx="44" cy="56" r="5" fill="#3fdc7e"/>
<text x="62" y="52" class="eyebrow">CHANNEL OPEN</text>
<text x="62" y="80" font-size="22" fill="#fff">linktr.ee/nayrosk</text>
<text x="{w - 44}" y="60" text-anchor="end" font-size="13" fill="{BODY}">Hiring, freelance work or an OSS idea?</text>
<text x="{w - 44}" y="82" text-anchor="end" font-size="13" fill="{DIM}">Every link to reach me is one click away  ↗</text>
{crt(w, h, uid)}"""
    return svg(w, h, body, "Contact: linktr.ee/nayrosk")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "banner.svg": banner(),
        "stack.svg": stack(),
        "contact.svg": contact(),
        "section-work.svg": section(1, "Featured work", "6 projects"),
        "section-upstream.svg": section(2, "Upstream contributions", "merged prs"),
        "section-stack.svg": section(3, "Stack"),
        "section-telemetry.svg": section(4, "Telemetry", "auto-updated daily"),
        "section-contact.svg": section(5, "Contact"),
    }
    for i, p in enumerate(PROJECTS):
        files[f"card-{p['slug']}.svg"] = card(i, p)
    for name, content in files.items():
        (OUT / name).write_text(content)
    print(f"wrote {len(files)} files to {OUT}")


if __name__ == "__main__":
    main()
