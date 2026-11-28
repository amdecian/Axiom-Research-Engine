# AXIOM / Crossed-orbit startup presentation

## Visual identity

Two fixed electron-style ellipses cross at +38 and -38 degrees around the central AXIOM emblem. Each highlight follows its own path in opposite directions (2.6 and 3.1 second periods). The dark emerald and graphite splash preserves a 16:9 vector canvas. This is a conceptual atomic motif, not a model of physical electron orbitals. The preview is self-contained with no external artwork, fonts, audio, service calls or dependencies.

[Offline playable preview](splash-preview.html). Download the file and open locally. Replay and skip are available. The preview never launches the engine.

## Integrated startup behavior

- The component is embedded verbatim in the local dashboard, static portal template and generated portal. The modal dialog covers the application on initial document load; the regular browser navigation and refresh-evidence control do not restart the splash.
- Local dashboard: the existing read-only snapshot request and render proceed unchanged in the background. After successful rendering, the UI signals readiness. The existing unavailable-API notice is retained and the splash closes immediately on failure. No new API route or database operation.
- Static portal: the existing page initialization and embedded data rendering proceed unchanged. Signal readiness after the initial view and controls have been constructed. The portal remains self-contained with no external requests.
- Normal presentation lasts ten seconds of visible foreground animation time. Hidden tabs pause the presentation. If the interface loads sooner, the splash completes its cosmetic sequence; the user can skip it. Skip or reduced-motion mode removes the cosmetic hold but does not signal readiness or bypass existing initialization. The timeline measures presentation time only, not scientific progress.
- If loading remains pending beyond the presentation, the splash shows a waiting message. A twenty-second wall-clock readiness guard removes the visual obstruction and reports that readiness has not been reported; it neither cancels nor retries the existing fetch. The guard is cleared when the interface reports readiness. Unexpected UI errors release the splash and show an error notice; no engine readiness is inferred. Browsers without modal-dialog support fall back to the existing UI.
- The splash runs only in the browser. CLI, headless mode, server startup, existing mathematical algorithms, campaign execution, verification, ledger and evidence handling are unchanged. No automatic experiments, paid compute, external requests, scheduling or background research. Existing scientific and disclosure boundaries still apply.

## Validation and rollback

The exact shared component and standalone preview were exercised in Chromium using Playwright browser virtual time and isolated test documents. Passed the ten-second presentation boundary, moving electrons on two fixed crossed axes, replay, skip, delayed readiness gating, unavailable-interface dismissal, readiness timeout, reduced-motion behavior, mobile-width layout and no unexpected JavaScript errors or network requests in the test documents. Inspected a rendered desktop still. Full application/browser end-to-end integration, live hidden-tab behavior and cross-browser coverage remain review items.

The original public portal's embedded JSON payload is retained byte-for-byte; the updated portal is the updated template expanded with that same payload. The deterministic generator is unchanged. Verify with `python scripts/build_portal.py --check` on a checkout. No scientific results are regenerated and no math or experiment source is edited. A rollback of this startup commit restores the prior preview and original application startup surfaces. Keep original brand concepts unchanged; name and rights remain provisional.
