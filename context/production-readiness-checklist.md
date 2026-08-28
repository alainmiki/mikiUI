# MikiUI Production Readiness & Adoption Checklist

## Purpose

This document is the hard production gate for MikiUI. It exists to prevent agent drift, weak feature claims, and premature public release decisions.

This checklist is for AI agents, contributors, and maintainers. It is intentionally strict.

The goal is not to be "good enough to demo." The goal is to be "good enough to trust in real projects, across web, desktop, and mobile assumptions."

If a checkpoint is not true, do not claim the project is production-ready.

---

## Core Rule: No Release Claims Without Gate Completion

The project may be considered:

- Alpha: concept is valid, but reliability and coverage still weak.
- Beta: core flows work, but not enough breadth or confidence yet.
- Production-ready: all critical adoption gates are satisfied.
- Highly adoptable: production-ready plus ecosystem, docs, trust, and quality standards are strong enough for real users.

A project is not production-ready if any of these are true:

- critical widgets are still inconsistent
- browser/runtime edge cases remain unresolved
- mobile assumptions are not clearly designed and tested
- accessibility is incomplete on key flows
- install/build/process is flaky or unclear
- documentation and examples do not support independent usage
- public claims exceed verified reality

---

## Mandatory Reading Order for Agents

Before making changes, agents must read in this order:

1. `agent.md`
2. `context/plan.md`
3. `context/PRD.md`
4. `context/project-structure.md`
5. `context/components.md`
6. `context/mobile.md`
7. `context/production-readiness-checklist.md`

This file is the enforcement layer. It defines what must be true before the project is called strong, stable, and publicly trustworthy.

---

## Agent Operating Rules

### Rule 1: Do not optimize for demo success alone

Do not stop at a working demo. The system must work reliably across repeated use, rerender cycles, browser interactions, and real app patterns.

### Rule 2: Prefer real behavior over superficial correctness

A component is not valid because it renders once. It is valid because it behaves correctly under repeated input, updates, focus changes, resizing, and state changes.

### Rule 3: Do not hide weakness behind examples

A small demo does not prove framework strength. Real adoption requires coverage across layouts, forms, navigation, dialogs, responsiveness, and state transitions.

### Rule 4: Fix root cause, not symptom

If an issue is caused by runtime duplication, stale event binding, incorrect focus handling, or uncontrolled update patterns, fix the root cause and verify the specific failing path.

### Rule 5: A widget is not complete until it is stable in use

Each widget must be stable in at least these conditions:

- first render
- rerender
- data updates
- user interaction
- keyboard interaction
- resize and viewport change
- repeated mounting/unmounting
- mobile and desktop conditions

### Rule 6: Mobile is not a side feature

Mobile readiness is a production-level requirement, not a nice extra.

### Rule 7: Accessibility is a launch requirement

If a user cannot use a control with keyboard or assistive technology, the component is not production-ready.

### Rule 8: Packaging must be reproducible

If a user cannot create a fresh environment and install the project without special workaround, the project is not release-ready.

---

## Level 3 Production Standard

This is the minimum standard for a framework that is highly adoptable and production-ready.

The project passes Level 3 only if ALL required areas are true.

---

## A. Product and Positioning Readiness

### Must be true

- the project has a clear purpose and a narrow, honest scope
- the target user is explicit
- the framework does not claim capabilities it cannot prove
- the roadmap is realistic and maintainable
- the public story matches actual maturity

### Blocker conditions

- vague product claims
- “works in theory” messaging instead of verified capability
- no clear target audience
- no release philosophy or support model

### Agent expectation

When working on framework features, do not broaden the scope into unsupported claims. Keep the product honest and credible.

---

## B. Architecture and API Quality

### Must be true

- component architecture is coherent and modular
- widgets are built from stable primitives, not ad hoc markup
- APIs are predictable across multiple renders
- lifecycle semantics are clear: init, update, cleanup
- route/data flow remains stable under repeated use
- app structure matches the intended architecture in `context/project-structure.md`

### Required checks

- repeated renders do not duplicate events or state
- state updates remain consistent after navigation or rerender
- partial updates do not leave stale markup behind
- components are not built on hidden global state traps
- the framework exposes a clear developer mental model

### Blocker conditions

- state drift across rerenders
- hidden global coupling between widgets
- duplicate listeners or initialization side effects
- fragile API that only works in happy-path demos

---

## C. Runtime Stability and Browser Reliability

### Must be true

- JS bridge does not double-initialize widgets
- DOM events are correctly attached and cleaned up
- repeated hydration or render attempts do not cause duplicate bindings
- focus handling is stable
- overlays, modals, dialogs, drawers, and sheets behave correctly
- route transitions and full-page updates do not leave stale listeners behind

### Required checks

- click handlers fire once per event
- input widgets respond predictably
- dialogs can open and close reliably
- focus returns to the correct element when closed
- state remains consistent after multiple interactions
- slow or repeated interactions do not break runtime behavior

### Blocker conditions

- event duplication
- stale DOM references
- broken overlay behavior
- focus trap issues
- “works once, fails on second interaction” patterns

---

## D. Widget Contract Quality

Every widget must satisfy the same contract.

### Required contract

- stable initialization
- predictable update semantics
- clean teardown behavior
- consistent props and output shape
- expected action behavior
- expected accessibility behavior
- expected responsive behavior

### Minimum widget quality gate

The project must not ship with a widget set where some widgets are stable and others are obviously experimental.

### Blocker conditions

- widget quality is uneven across the framework
- some widgets require hidden hacks or manual JS patching to function
- a widget is only usable in one narrow demo path
- widget behavior differs wildly from similar components in other UI toolkits

### Minimum release expectation

Core widgets must behave like mature UI primitives: tabs, nav, menu, sidebar, modal, dialog, form controls, progress, tabs, layout containers, file input, alerts, and panels.

---

## E. Styling, Theming, and Visual Consistency

### Must be true

- core components have coherent styling architecture
- themes are predictable and consistent
- visual states are implemented correctly: default, hover, focus, active, disabled, invalid
- layout primitives behave reliably across different screen sizes
- a consistent visual language exists across widgets

### Required checks

- no broken spacing or layout collapse
- no hidden overflow issues in common layouts
- no unclear disabled, active, or selected states
- no one-off styles that break theme consistency
- no style-only hacks that mask structural problems

### Blocker conditions

- inconsistent theme behavior across widgets
- visual drift between similar controls
- unstable layout under different viewport widths
- hard-coded styles that ignore the theme system

---

## F. Accessibility and Inclusive Design

### Must be true

- keyboard navigation exists for essential controls
- focus states are visible and understandable
- dialogs and overlays trap focus correctly
- menus and navigation are keyboard operable
- forms have labels and error states
- semantic roles and states are implemented for key UI patterns
- screen-reader use is considered in component design

### Required critical patterns

- tabs
- dialogs and modals
- drawers and sheets
- forms and validators
- nav and menu behavior
- selectable lists and tables
- action buttons and destructive actions

### Blocker conditions

- click-only interactions with no keyboard path
- inaccessible dialogs
- unlabeled form controls
- broken focus restoration
- hidden or unclear state for assistive technologies

---

## G. Mobile Readiness (Mandatory at Level 3)

### Mobile readiness is not optional

If a framework intends to be adoptable for real projects, it must handle mobile as a serious target, not as a late afterthought.
### Mobile phase gate: this must be enforced

The mobile implementation is not a free-for-all feature branch. It is a deployment target that ships only after the core framework is mature.

This project must not begin or continue mobile implementation before all of the following are true:

- all base HTML components are implemented and tested
- all advanced widgets are mature
- web build is stable and production-ready
- desktop build is stable and production-ready
- plugin system is security-reviewed
- CI/CD passes on the target operating systems
- no critical web/desktop launch blockers remain

If any of the above are false, mobile is not eligible for a production claim.
### Must be true

- layouts adapt for small screens without breakage
- touch targets are usable
- popovers, drawers, dialogs, and sheets work on touch devices
- pointer events are normalized correctly
- mobile scrolling and viewport behavior are handled carefully
- forms work correctly on mobile browsers
- orientation changes do not break the app
- navigation patterns are usable on small screens

### Mobile must cover

- responsive layout primitives
- stacked forms and long content
- sticky navigation or drawers
- bottom sheets and mobile overlays
- tables and list views on narrow layouts
- touch interactions without accidental double events
- mobile keyboard behavior

### Blocker conditions

- desktop-only assumptions in the UI
- touch devices causing double triggers or bad gestures
- layouts that overflow or hide content on mobile
- poor performance on mid-range mobile hardware
- mobile-only broken states not accounted for in design or tests

### Mobile-specific release requirement

At Level 3, the project must have a defensible mobile plan and at least clear, validated mobile-risk handling for the core UI patterns. It does not need full perfect parity on day one, but it must not be visibly broken or unsafe.

### Mobile deployment rules that must hold

- mobile is a deployment target, not a feature
- web and desktop are the maturity gate for mobile
- mobile cloud mode and mobile on-device mode must remain clearly separated
- Android on-device mode must not introduce listening sockets or unsafe runtime behavior
- iOS on-device mode must be rejected by design and build guardrails
- cloud mode remains the default unless explicit advanced requirements justify on-device mode
- the frontend must remain transport-agnostic through a unified bridge layer

---

## H. Security and Safe Runtime Behavior

### Must be true

- plugins are validated and permissioned
- untrusted content is handled safely
- runtime boundaries are not weak or permissive by default
- user input is validated at boundary points
- plugin discovery and registration are secure
- marketplace or app plugin workflows are not vulnerable by default

### Required checks

- no unsafe arbitrary code execution by default
- no insecure plugin assumptions
- no hidden network or filesystem access without explicit intent
- no unsafe markup or unauthorized runtime access
- no broad default permissions that break trust

### Blocker conditions

- plugin system that accepts anything silently
- lack of validation around app/plugin capabilities
- unbounded runtime access without review
- unsafe assumptions about browser or local runtime behavior

---

## I. Performance and Resource Efficiency

### Must be true

- common app interactions stay responsive
- repeated render/update cycles do not degrade badly
- heavy widgets do not cause obvious UI lag
- large data views remain manageable
- runtime overhead stays reasonable for a Python-first framework

### Required checks

- lazy loading where appropriate
- no unnecessary re-binding on every update
- no excessive DOM churn
- no big hidden JavaScript cost in common flows
- scaling assumptions are realistic for modest application sizes

### Blocker conditions

- every interaction triggers expensive full reinitialization
- large lists or tables become unusable
- performance becomes unacceptable in normal app flow
- framework feels demo-only due to lag and reflow issues

---

## J. Testing and Regression Confidence

### Must be true

- real behavior tests exist for critical UI paths
- regressions are caught before release
- key flows are tested in browser E2E
- components are verified under user interaction
- there is meaningful coverage beyond initial smoke checks

### Minimum required test classes

- core component tests
- layout and rendering tests
- form and validation tests
- dialog/modal interaction tests
- nav/menu/tabs tests
- responsive/mobile behavior tests
- event handling tests
- widget behavior tests
- build and install path tests

### Blocker conditions

- only static smoke tests exist
- tests check markup generation but not actual behavior
- no browser-level validation for interaction and focus flows
- no safeguards against reinit or duplicate event problems

---

## K. Packaging, Installation, and Developer Workflow

### Must be true

- fresh environment installation works reliably
- the project builds successfully from source
- CLI commands work predictably
- new app generation is valid and reproducible
- development workflow is documented and practical
- build outputs are straightforward to understand

### Required commands

- project install
- app creation
- local dev run
- build process
- packaging verification
- import validation

### Blocker conditions

- local-only setup assumptions
- hidden environment requirements
- the project only works on one developer machine
- build commands are unclear or inconsistent
- the app fails to import or run after packaging

---

## L. Documentation and Developer Experience

### Must be true

- installation is easy
- getting started is clear
- basic app examples are valid and runnable
- the architecture is understandable
- main patterns are explained with examples
- troubleshooting and debugging guidance exists
- docs are trustworthy and up-to-date

### Required documentation quality

- project overview
- installation steps
- first app tutorial
- component and widget catalog
- routing and state usage
- theming guidance
- mobile plan or constraints
- plugin and extension model
- security and release notes

### Blocker conditions

- docs are stale, thin, or too abstract to be useful
- examples do not actually work
- users must read source code to understand use
- there is no onboarding path for new developers

---

## M. Maintainers and Release Discipline

### Must be true

- there is a clear release policy
- there is a process for review and regression safety
- changes are validated before merging
- major capabilities are not merged without evidence
- contributors follow documented architecture and release standards

### Blocker conditions

- no quality bar for changes
- features merge without validation
- architecture gets ignored in favor of patchwork fixes
- no gate for release confidence

---

## N. Release Gate: Final Decision Matrix

The project is highly adoptable and production-ready only if ALL of the following are true:

### Critical pass list

- [ ] core architecture is stable and coherent
- [ ] widgets behave consistently and predictably
- [ ] runtime event handling is safe and deduplicated
- [ ] the UI is usable across common browser scenarios
- [ ] the UI is meaningful on mobile devices
- [ ] accessibility is not missing from critical flows
- [ ] security boundaries are respected
- [ ] performance is acceptable for common app use
- [ ] builds and installs are clean and repeatable
- [ ] tests cover real behavior, not just markup
- [ ] docs are complete enough for new developers to succeed
- [ ] public claims match real verified status

If any one of these is false, the project is not ready for large-scale public adoption.

---

## O. Agent Decision Rule

When an agent is assigned a task, it must check this file before doing any feature work.

### Before implementation, an agent must ask:

- Does this change improve production readiness?
- Does it keep the framework consistent with the architecture?
- Does it maintain accessibility and mobile safety?
- Does it contribute to adoption quality rather than demo-only polish?
- Does it remain safe under repeated interactions and updates?
- Does it improve trust, not just visual output?

### If the answer is no, stop and escalate.

Do not merge feature work that only makes the demo look better while weakening the framework contract.

---

## Final Standard

This project should only be called highly adoptable and production-ready when it is:

- stable enough for real use
- consistent enough to trust
- accessible enough to be inclusive
- mobile-aware enough to be practical
- documented enough for independent adoption
- tested enough to protect against regressions
- honest enough to avoid overclaiming

Anything less is still an ambitious framework in progress.

This is the standard.
