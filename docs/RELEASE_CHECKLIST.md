# Antigravity Swarm Release Checklist

Current release candidate: `antigravity-swarm@0.2.3`.

Do not run `npm publish` during preflight. Publishing is a separate human-gated step after the version bump is committed, pushed, and reviewed.

## Required preflight commands

Run these from the repository root and keep the outputs in the release note:

```bash
node scripts/check-version-lockstep.mjs
npm test
npm run pack:dry-run
agy plugin validate plugins/antigravity-swarm
npm view antigravity-swarm version
node bin/antigravity-swarm.js --help
node bin/antigravity-swarm.js --dry-run install --target <temp-dir> --hud --settings-target <temp-json>
```

## Hook and HUD probes

Pipe representative JSON payloads into the shipped scripts:

```bash
node plugins/antigravity-swarm/scripts/asw-hook.mjs
node plugins/antigravity-swarm/scripts/asw-stop-check.mjs
node plugins/antigravity-swarm/scripts/asw-statusline.mjs
```

Probe alias routing, malformed JSON, stale transcript paths, `ASW_SAFE_MODE=1`, and secret-like HUD values. Tests are required but not sufficient; capture real CLI/plugin/package output before release.

## Package policy

- Keep `package.json`, `package-lock.json`, `plugin.json`, HUD version text, README badges/examples, and this checklist in version lockstep.
- Confirm `npm run pack:dry-run` excludes local research, private references, runtime evidence, `.asw/`, `.litopencode/`, and test artifacts.
- If npm already has the current version, bump one patch version, regenerate `package-lock.json`, and rerun every gate.

## Manual publish command

After all gates pass and the release commit is on the intended branch, the manual publish command is:

```bash
npm publish
```
