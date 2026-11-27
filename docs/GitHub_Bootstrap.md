# GitHub bootstrap / Free Open Research Edition

## 1. Account and publication gate (owner only)

Use the existing ordinary personal GitHub identity only if personally owned and permitted by employer policy. Add and verify a personal email, ensure personal MFA/recovery, and use a new independent Free organization or personal namespace. Do not import to an employer organization. Confirm ownership and rights to code, research evidence, name and assets. Review every proposed public file; the separately delivered review-only archive must remain outside the repository. Choose a license: `LICENSE.proposed` is the unapproved Apache-2.0 candidate. After approval, rename to `LICENSE` or install your selected license and update the package metadata. A public repository without approved licensing is not an open-source release. Do not publish if ownership is unresolved.

Verify current billing in GitHub Settings → Billing and licensing. Use standard public runners only, avoid paid add-ons, and configure $0 metered-product spending stops where available; confirm any existing payment method and shared usage. Do not enable a paid Codespace beyond its personal allowance. GitHub Free suffices; Pro is optional, not required.

## 2. New repository — from extracted distribution

Open PowerShell inside `axiom-research`. First verify the original archive before changing anything:

```powershell
python scripts/bootstrap.py --verify-only
python scripts/bootstrap.py
python scripts/build_portal.py --check
```

The second command qualifies locally and initializes `main`, not a remote repo. For a browser-only workflow, create the approved public repository in GitHub UI and use browser editor or a Codespace within its allowance; upload **only reviewed source files**, preserving hidden `.github` files, not the distribution ZIP. The local CLI method is the simplest first import; it is not self-hosted infrastructure.

After owner approval of Apache 2.0, for example, rename `LICENSE.proposed` to `LICENSE` (or use the selected alternative); make any required rights/metadata changes. The distribution checksum is a snapshot of the original package, so rerunning its original check after edits correctly fails. Remove the snapshot manifest before your initial source commit or regenerate it for the reviewed distribution only. Never copy over an existing repo's `.git` metadata.

```powershell
git status --short --untracked-files=all
git add --all; git diff --cached --stat; git diff --cached --name-only
```

Review the actual staged content, secrets, binary evidence contents and file ownership; there is no substitute for owner review. Configure Git identity to your personal email or GitHub noreply for this repo. Commit only after review:

```powershell
git commit -m "Bootstrap AXIOM Free Open Research v0.4.0"
```

The following explicitly publishes your reviewed repository. Replace `YOUR-OWNER` and confirm `gh auth status` and target independently; this command is **not** executed by any package script:

```powershell
gh repo create YOUR-OWNER/Axiom-Research-Engine --public --source=. --remote=origin --push
```

Do not use the public flag before the publication gate passes. For an existing repository import into a reviewed branch, not an initializer. If GitHub requires Actions approval, review the exact workflow source before enabling. Remote CI is not pre-qualified.

## 3. Enable the portal and security controls

Repository Settings → Pages → Build and deployment → **Deploy from a branch**, choose `main`, `/docs`, Save. No custom deployment workflow, access token or database needed; the built-in Pages deployment is managed by GitHub. Verify the published URL. The repository itself remains public, not just `/docs`.

Settings → Actions → General: read-only default workflow permissions, disable Actions creating/approving PRs, require approval for external contributors as appropriate; no repository secrets in initial profile. Verify default GitHub-hosted labels. Settings → Rules → Rulesets: protect main, require PR, require passing qualification matrix checks once they exist, block force push/deletion, resolve conversations; zero required external reviewers only during solo-maintainer phase. Keep release publication manual. Enable supported public secret scanning/push protection and Dependabot; CodeQL setup and pin review is an outstanding slice. These controls are manual owner settings; no package script has configured them.

## 4. First hosted tests

Push/PR triggers `Free-tier qualification`: four standard hosted configurations (Linux x64, Windows x64, macOS ARM, Linux ARM), at most two simultaneous matrix jobs per workflow. Checks: legacy suite, new exact math and contract tests, local ledger and generated portal validation. Actions → **Bounded research regression** → Run workflow on main, choose `loop-replay` or `pattern-regression`. The latter validates weighted XOR identity, CRT and modular division. No scheduled workflows. Use job logs and summaries; outputs are not automatically uploaded. To preserve a result, review a source-pinned evidence entry and submit a separate PR. Do not paste secrets or private research into logs, issues, Pages, or releases.

## 5. Backlog

Preview all 132 work items: `python scripts/backlog.py`. After owner approval of the public issue content:

```powershell
python scripts/backlog.py --repo YOUR-OWNER/Axiom-Research-Engine --visibility public --ack-publication --apply --batch 15
```

Each invocation creates at most 15 missing IDs (hard cap 25). Verify response/rate limits before rerunning; no automatic retries; one importer at a time. No GitHub Project is created automatically. Add issues to a project via GitHub UI after import.

## 6. Daily operating model

Use ChatGPT manually for research hypotheses and code; no paid provider connector is required by the repo. Create an issue and branch for each bounded test; run CI, examine exact verification and work metrics, and submit a reviewed evidence entry. Git is the persistent notebook, Pages is its read-only view. Rebuild it via `python scripts/build_portal.py` and commit the reviewed generated diff. CI rejects stale portal or altered evidence hashes. For a higher-cost campaign, stop and choose an appropriate authorized platform instead of splitting jobs to bypass service policy. No unattended process continues when Actions ends.
