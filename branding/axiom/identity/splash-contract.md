# AXIOM / Startup animation contract (design preview)

## Intent

A centered dark splash with the working AXIOM emblem, a stationary horizontal ellipse, an emerald highlight traveling along the path, a softly illuminated evidence node and a crisp wordmark. Use the established identity palette; preserve the fixed 16:9 artwork proportions with contain scaling. No external artwork, font downloads, network requests, audio or paid service. This is an offline design preview, not an engine startup, research run or production loader.

## Preview and timing

Download [splash-preview.html](splash-preview.html), open locally in a modern browser, and replay or skip. Normal playback lasts ten seconds of visible foreground time after the initial rendered frames. Hidden tabs pause the timeline and resume without counting the hidden interval. The orbit geometry stays fixed; the highlight moves along its path approximately once per 2.6 seconds. The timeline is explicitly labeled as presentation time, never as measured initialization or verification progress. Reduced-motion preference hides the traveling effect and stops the pulse; replay and skip remain available. Completion shows a clear preview handoff placeholder; no engine process is started.

| Time | Preview sequence |
| --- | --- |
| 0–2.5 s | Identity sequence |
| 2.5–7 s | Research engine brand preview |
| 7–10 s | Startup handoff preview |
| 10 s | Completion placeholder |

## Future integration acceptance contract (not implemented)

- Splash must own the initial visual presentation; avoid a blank console or duplicate startup window. The application must not appear behind the splash.
- Begin the normal ten-second visual sequence only once the splash is visible. Keep the event loop responsive while bounded initialization runs independently.
- Do not force a fixed cosmetic delay on CLI, automated CI, headless use or ordinary navigation within the existing web portal. Startup errors take precedence over any branding hold. A user skip or reduced-motion preference must not bypass initialization or readiness checks.
- Once the normal sequence finishes and actual application readiness is confirmed, close the splash immediately before showing the main application. If initialization is still active, show its real status without fabricated percentages; allow safe cancellation or error recovery. No background research, model calls, paid compute, or auto-execution is authorized by the splash.
- No runtime integration or deployment settings in this slice. Decide which supported application surface should own startup before implementation; preserve offline and public disclosure boundaries.

## Preview qualification

The exact HTML source was rendered in Chromium with Playwright. Checked the ten-second completion boundary using browser virtual time; replay; skip; reduced-motion behavior; narrow viewport overflow; absence of JavaScript runtime errors and network requests. Manually inspected a 960:540 rendered still. Real OS window lifecycle and actual application readiness/handoff are not tested. Browser coverage beyond Chromium and live visibility pause/resume behavior require follow-up review.

Keep the original concepts and engine files unchanged. The identity remains provisional pending name, ownership and rights review.
