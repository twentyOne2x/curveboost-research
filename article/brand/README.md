# Shared CurveBoost artwork

The accepted flat article cover is the identity master. `cover-master.png` is byte-identical to `../cover.png`.

`curveboost-header.svg` embeds that exact image and clips the thin curve/spark, CurveBoost wordmark and By attn.markets attribution from their original pixels. `clip-regions.json` records the regions and aspect-preserving target positions. No logo redraw or replacement font is used.

Both chart renderers call `brand_header.py`, placing this same header at (68,35). Their rendered header pixels are identical; hashes and source bindings are in `verification.json`. Native SVG output is self-contained. Optional PNG rendering uses Pillow. Keep the repository layout when rendering study charts.

The account handle is **@attndotmarkets**, linked to https://x.com/attndotmarkets. The cover and chart attribution retain the approved **By attn.markets** wording.
