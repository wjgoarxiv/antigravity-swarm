---
name: asw-ui-ux
description: Product-aware frontend and README presentation guidance for Antigravity Swarm work.
---

# Antigravity Swarm UI UX

Use this skill when the work changes a visual interface, README presentation, cover image, or installer output.

- Match the product's audience and purpose before choosing visual style.
- Build the usable surface first; avoid marketing-only screens for tools.
- Keep controls familiar, dense enough for repeated use, and clear at small widths.
- Use real screenshots, generated bitmap art, or meaningful product visuals where imagery matters.
- Verify text does not overlap and the interface renders across relevant terminal or browser widths.

## README And Visual Assets

- Make the first viewport communicate the product immediately.
- Use a cover image only when it carries the repo identity better than text alone.
- Keep badges and navigation useful; remove novelty labels that make the repo sound unserious.
- Do not include internal QA, package allowlist, or implementation notes in marketing-facing sections.
- Match screenshots, status-line examples, and installer output to real current output.

## Terminal UI

- Keep panels within common terminal widths.
- Use color as emphasis, not as the only information carrier.
- Use spinners only while work is actually happening.
- Make menu choices visibly selectable and self-explanatory.
- Test with color enabled and disabled.

## Design Process

1. Identify the surface: README, cover, installer, HUD, web UI, or IDE flow.
2. Identify the audience: maintainer, npm user, Antigravity CLI user, reviewer, or first-time visitor.
3. Inspect the current visual language before changing it.
4. Choose one primary hierarchy and one secondary hierarchy.
5. Build the real usable surface first.
6. Verify at the actual display width.
7. Compare docs/screenshots/examples with current output.

For README and cover work, the first viewport must communicate:

- product name,
- what it does,
- how to start,
- why the project is credible,
- current version or major update when relevant.

## Aesthetic Guidelines

Typography:

- keep headings readable at GitHub width,
- avoid huge type inside small panels,
- use code styling only for commands and aliases,
- avoid novelty wording that makes operational tooling feel unserious.

Color:

- use color to create hierarchy,
- keep contrast high,
- avoid single-hue monotony,
- make ANSI output useful with color disabled,
- keep HUD palette choices consistent across every segment.

Motion and terminal feedback:

- spinners indicate active work only,
- completed steps become stable checkmarks,
- menus should not shift layout while selecting,
- progress indicators should represent real progress or be omitted.

Spatial composition:

- center hero art intentionally,
- keep panels aligned,
- avoid nested boxes unless the nesting communicates structure,
- leave enough breathing room around code blocks,
- make terminal boxes fit common widths.

Visual details:

- generated images should look intentional, not like random decoration,
- cover images should match repo identity,
- README badges should carry useful metadata,
- screenshots and examples must be current.

## Anti-Patterns

Never:

- ship internal QA notes in public README sections,
- describe installer implementation details as a feature,
- use empty marketing claims,
- show HUD examples that do not match actual output,
- make a terminal menu whose color choices are invisible,
- use a cover that fights the repo's established style,
- hide the product name below the fold,
- make aliases look like jokes when they are commands,
- leave stale screenshots after changing UI,
- rely on color alone for selected state.

## Execution

When changing visuals:

1. Update the asset or UI.
2. Run the generator or render path.
3. Inspect the image or terminal output.
4. Test color on and off when ANSI is involved.
5. Test a narrow width when terminal boxes are involved.
6. Update README examples only after real output exists.
7. Run docs tests.
8. Include the visual QA evidence in the report.

For cover generation:

- use the repo generator,
- keep deterministic dimensions,
- verify file size and image load,
- inspect the rendered image,
- avoid committing temporary previews.
