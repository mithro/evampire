# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Design documentation for evampire, a gf180mcu chip made through wafer.space.
It is a three-port gigabit Ethernet hub with a RISC-V processor that moves
power between Power over Ethernet and USB Type-C. There is no silicon and no
RTL yet. The repository is a Sphinx site published on Read the Docs
(https://evampire.readthedocs.io/). Every pull request gets a preview at
`https://evampire--<PR>.org.readthedocs.build/en/<PR>/`.

## Commands

All commands need `uv` and Graphviz (`dot`).

```sh
make -C docs check      # what CI and Read the Docs run; must pass before merging
make -C docs html       # plain build into docs/_build/html
make -C docs linkcheck  # external links (CI reports but does not fail on it)
make -C docs clean
uv run python docs/check_source.py docs   # fast: source-only check, no build
```

`make check` runs three steps, and any one failing fails it:

1. `check_source.py` finds standards referred to as plain text instead of
   with a role:
   - clause numbers such as "Clause 40";
   - USB specification sections such as "PD Table 5.10";
   - IEEE table, figure and annex numbers such as "Table 145-24" or
     "Annex 33A";
   - named standards such as IEEE 802.1AB or IEC 61000-4-2, which need
     `:std:`.

   `docs/standards.rst` is exempt.
2. `sphinx-build -W --keep-going` turns every warning into an error. Common
   failures are an undefined `:term:`, an unresolved `:ref:`, `:clause:` or
   `:std:`, and bad indentation in the glossary.
3. `check_html.py` reads the built HTML for problems Sphinx misses:
   - Furo's red `.. contents::` box, which is drawn by CSS and invisible in
     the text;
   - docutils system-message boxes, and unresolved references or roles
     (`class="problematic"`);
   - numbered figures and tables that no link points to;
   - diagrams without `:alt:`.

`check_html.py` checks links across the whole site, so it needs a full
build; no check renders a single page on its own.

Chain commit and push after the check with `&&`, never `;`. A failing check
must stop the push.

### Generated figures and numbers

The build does not run these scripts. When you change their inputs, re-run
them and commit what they write:

```sh
uv run python docs/index/overview.py docs/index/overview.svg
uv run python docs/power/poe/voltage_timeline.py docs/power/poe/voltage-timeline.svg
uv run docs/power/usb-pd/masks.py          # writes tx-mask.svg and rx-mask.svg
uv run docs/power/converters/waveforms.py  # writes buck-waveforms.dot
uv run python docs/high-voltage/figures.py docs/high-voltage  # cross-sections
uv run docs/esd/sim/schematic.py           # writes docs/esd/figures/io-cell.svg
```

The ESD simulation (`docs/esd/sim/esd_sim.py`) writes the ESD figures and
the tables in `docs/esd/sim/results/`. It needs ngspice and the gf180mcu
model and I/O cell repositories at pinned commits, and takes about twenty
minutes; `docs/esd/simulation.rst` gives the command. With `--reuse` it
rebuilds the tables and figures from the waveforms of its last run.

Four scripts print the numbers their pages quote, so re-run one after
changing an input and update the page to match:

- `docs/power/usb-pd/calc.py`
- `docs/power/converters/calc.py`
- `docs/high-voltage/calc.py`
- `docs/usb-serial/calc.py`

`docs/usb-serial/calc.py` prints its last table only when given the path to
the gf180mcu I/O liberty file `gf180mcu_fd_io__bi_t__tt_025C_3v30.lib`, which
comes from the gf180mcu PDK and is not in this repository.

## Structure

- Each topic is a folder with an `index.rst` and short child pages of about
  five A4 pages each, ordered simplest first. The topics are
  `ethernet/{rgmii,phy-electrical,magnetics}`, `power/{poe,usb-pd,converters}`,
  `esd`, `high-voltage` and `usb-serial`. `power/index.rst` holds what the
  power topics share:
  roles, modes, the budget, translation, sharing, and the board
  configurations table (`tab-power-board-configs`). Pages link to that table
  rather than restating the configurations.
- Each topic has its own `references.rst`. Citation keys carry a per-topic
  prefix (`PHY-`, `MAG-`, `RGMII-`, `POE-`, `USBPD-`, `CONV-`, `ESD-`, `HV-`,
  `USBSER-`)
  so they don't clash across the site. A new topic picks its own prefix.
- `docs/glossary.rst` is one site-wide `.. glossary::` with `:sorted:`. Every
  `:term:` resolves there. When merging branches, keep the terms from both
  sides, merge any term defined twice into one entry, and keep a blank line
  between entries.
- `docs/requirements.rst` is the single list of requirements (`req-*`
  labels). `docs/standards.rst` has one entry per standard that the roles
  link to.
- `docs/_ext/` holds the Sphinx extensions written for this site.
  `conf.py` adds the folder to the import path.
- Diagrams are Graphviz `.dot` files next to the page, rendered as SVG.
  Prefer `layout=neato` with pinned `pos` and `splines=false`. Free layouts
  come out too wide to read. The front-page block diagram is the one
  exception: `docs/index/overview.py` draws it directly as SVG, for the die
  outline, pads and wire hops that Graphviz can't draw. WaveDrom is rendered to SVG at build time
  (`render_using_wavedrompy`).
- `docs/_static/custom.css` makes the page use the full window width (Furo
  centres a fixed 46em column by default), sets figure and table captions
  smaller and grey with a bold number, puts a white panel behind diagrams
  in dark mode and limits diagrams to the column width.
  `diagram-links.js` adds an "Open diagram at full size" link that shows on
  narrow screens only.

## Roles defined in `docs/conf.py`

| Role | Example | Links to |
|---|---|---|
| `:clause:` | `` :clause:`40.8.3.1` ``, `` :clause:`Table 145-24 <145>` `` | IEEE 802.3-2022 clause entry |
| `:pd:` | `` :pd:`Table 5.10` `` | USB Power Delivery specification |
| `:typec:` | `` :typec:`Section 4.5.2.2` `` | USB Type-C specification |
| `:std:` | `` :std:`802.1AB` ``, `` :std:`IEC 61000-4-2` `` | label `std-<slug>` on the standards page |
| `:wikipedia:` | `` :wikipedia:`frames <Ethernet_frame>` `` | English Wikipedia |

A `:clause:` or `:std:` target with no entry in `docs/standards.rst` is a
build error, so add the entry first:

- **`:clause:`** links to the clause's row in the table
  `tab-ieee8023-clauses`. To cite a new clause, add a row labelled
  `.. _ieee8023-clause-<N>:`.
- **`:std:`** links to the label `std-<slug>`. The slug is the target in
  lower case, with each run of characters other than letters and digits
  turned into `-`, and a leading `ieee-` or `ansi-` dropped. So
  `` :std:`IEEE 802.1AB` `` links to `std-802-1ab`. The comment in
  `conf.py` gives the details.

Titles in `.. [KEY]` citation blocks are exempt from `check_source.py`.

IEEE 802.3-2022 and the USB specifications are copyrighted. Never commit or
publish copies of them, or quote from them at length.

## Writing rules

- **Readers:** ASIC engineers who are new to Ethernet and USB-PD. Neutral
  tone and British spelling ("analogue", "-ise"). Describe the current
  design with no history or changelog. Don't invent terms: use the
  standard's names.
- **Plain sentences:** at most 45 words each.
- **Each fact in one place:** link to it instead of restating it.
- **Page shape:** each page opens with one sentence saying what it covers.
  A page that leaves design decisions open ends with one "Open questions"
  section, which lists them all. Explanatory pages with nothing open have
  none.
- **Numbering:** every figure and table has a caption, a label, a
  `:numref:` reference and `:alt:` text. The label is its identifier:
  `docs/_ext/stable_ids.py` replaces Sphinx's running number with the label,
  less its `fig-` or `tab-` prefix, so `tab-poe-pairs` is captioned
  "Table poe-pairs:" and linked as "Table poe-pairs", and adding a table
  renumbers nothing. Start a label with
  `fig-` or `tab-` and the topic's prefix, and keep it short, since readers
  see it. Renaming a label changes the identifier readers see. Label
  diagrams with the `:name:` option; a `.. _label:` line before a captioned
  `graphviz` or `wavedrom` directive does not reach the figure, and the
  build reports it.
- **Equations:** each equation has a Symbol/Meaning/Unit table and a worked
  example. Split long equations over aligned lines so they fit a 400 px
  screen.
- **Sources:** cite IEEE 802.3-2022 directly, at the claim, using the roles.
  Datasheets and earlier designs are reference examples, not evidence.
- **Negative claims:** "can't be done" needs a documented physical limit,
  with the arithmetic. Leave positive claims light, since building the
  design validates them. Don't assume gf180mcu limits: custom transistors,
  non-standard logic cells and parasitic bipolar transistors are in scope.
- **Alternatives:** always cover them, including approaches others discarded,
  and say why they were discarded.
- **Unknowns:** don't assume the processor core, its clock or the core
  voltage; state what is needed as a function of those parameters. Die area
  and power consumption are unknown. Give the power available as ranges and
  never conclude that it is "enough".
- **Layout checks:** check each page as rendered, at 1280 px and 400 px, in
  light and dark mode, with full-page screenshots. Text-only checks have
  missed CSS-drawn error boxes and pages that scroll sideways.

## Repository conventions

- **Always work in an isolated worktree on its own branch.** Never edit,
  commit or switch branches in the primary checkout (the directory the
  repository was cloned into).
- **Keep the primary checkout pristine:** on `main`, with no local changes or
  untracked files, and in sync with `origin/main` on GitHub. The only
  commands to run there are `git fetch`, `git pull --ff-only` (to bring it up
  to date after a merge), and `git worktree add` and `git worktree remove`.
- **Start each piece of work** with a new worktree from `origin/main`. Run
  these from the root of the primary checkout, so the worktree lands under
  `.worktrees/` (git-ignored; `.claude/worktrees/` is also ignored):

  ```sh
  git fetch origin
  git worktree add .worktrees/<name> -b <branch> origin/main
  ```

  Once the branch is merged, remove the worktree with
  `git worktree remove .worktrees/<name>`, again from the primary checkout.
- **Topic branches:** each topic is developed on its own `docs/<topic>`
  branch and merged through a pull request once CI and the Read the Docs
  preview pass. Small site-wide fixes also go on their own branch and pull
  request.
- Some publishers refuse automated link checkers (IEEE, JEDEC, AIP, Wiley,
  IOP, MDPI, ST and others). They are listed in `linkcheck_ignore` in
  `conf.py`. When the link checker reports a 403, check the link in a
  browser, then add the publisher's domain there. If the link is a DOI, also
  add its `doi.org/<prefix>` pattern, since the DOI redirects to the
  publisher.
- Keep scratch files in `tmp/` (git-ignored), and delete it when you finish.
