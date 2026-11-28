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
   - diagrams without `:alt:`;
   - pages that the left sidebar does not link to. The home page is in
     the sidebar through the `Home <self>` entry of its own `toctree`.
     Furo calls that page "Home" in its previous-page link, so the entry
     uses the same name. Pages that only redirect, such as
     `docs/_extra/overview.html`, are exempt.

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
uv run python docs/high-voltage/figures.py docs/high-voltage  # every high-voltage figure
uv run python docs/architecture/figures.py docs/architecture
uv run docs/esd/sim/schematic.py           # writes io-cell.svg and io-cell-*.svg
uv run docs/esd/sim/tlp_plot.py
uv run docs/esd/sim/circuits.py
uv run docs/esd/sim/paths.py
uv run python docs/esd/sim/sections.py
uv run docs/esd/sim/plots.py
uv run docs/esd/sim/model_figs.py
GF180_IO=<fd_io checkout> uv run docs/esd/gds/figures.py  # the gds-*.svg layout figures
GF180_IO=<fd_io checkout> uv run docs/esd/gds/check.py    # writes docs/esd/gds/layout-check.csv
uv run docs/ethernet/rgmii/figures.py
uv run docs/ethernet/magnetics/plots.py
uv run docs/ethernet/magnetics/drawings.py
uv run docs/ethernet/phy-electrical/cable_figures.py
uv run docs/ethernet/phy-electrical/channel_graphs.py
uv run docs/ethernet/phy-electrical/coding_graphs.py
uv run docs/ethernet/phy-electrical/driver_figures.py
uv run docs/ethernet/phy-electrical/signal_graphs.py
uv run docs/ethernet/phy-electrical/startup_timeline.py
uv run docs/ethernet/phy-electrical/timing_figures.py
uv run docs/ethernet/phy-electrical/integration/int_graphs.py
uv run docs/power/converters/waves.py
uv run docs/power/converters/control_waves.py
uv run docs/power/converters/fv_figures.py
uv run docs/power/converters/graphs.py
uv run docs/power/converters/sections.py
uv run docs/power/poe/drawings_pairs.py
uv run docs/power/poe/drawings_pd.py
uv run docs/power/poe/drawings_hv.py
uv run docs/power/poe/graphs_sequence.py
uv run docs/power/poe/graphs_signature.py
uv run docs/power/poe/graphs_limits.py
uv run docs/power/poe/graphs_power.py
uv run docs/power/poe/graphs_budget.py
uv run docs/power/usb-pd/graphs_cc.py
uv run docs/power/usb-pd/graphs_levels.py
uv run docs/power/usb-pd/graphs_power.py
uv run docs/power/usb-pd/graphs_protection.py
uv run docs/power/usb-pd/graphs_signal.py
uv run docs/power/usb-pd/sections.py
uv run docs/usb-serial/figures.py
uv run docs/usb-serial/sequences.py        # writes the sequence .dot files
uv run docs/usb-serial/timing_figs.py
```

Each script's docstring names the files it writes. These modules are
helpers that the scripts above import, so run the script, not the helper:

- `docs/high-voltage/`: `svgdraw.py` and every `fig_*.py`;
- `docs/esd/gds/`: `gdskit.py`, `layfig.py`, `laykey.py` and every `figs_*.py`;
- `docs/ethernet/rgmii/`: `svgkit.py`, `board_figs.py`,
  `interface_figs.py`, `logic_figs.py` and `timing_figs.py`;
- `docs/ethernet/magnetics/`: `plotkit.py`, `plots_rl.py`, `plots_gb.py`
  and `drawings_cap.py`;
- `svgplot.py` in `docs/ethernet/phy-electrical/`,
  `docs/power/converters/` and `docs/usb-serial/`, and `svgfig.py` in
  `docs/power/usb-pd/` and `docs/power/poe/`.

`FONT_SCALE` in `docs/power/usb-pd/svgfig.py` sets the text size of every
USB Power Delivery graph. Every script reproduces its committed files byte
for byte, so a rerun that changes a file means its inputs changed.

The ESD simulation (`docs/esd/sim/esd_sim.py`) writes the ESD figures and
the tables in `docs/esd/sim/results/`. It needs ngspice and the gf180mcu
model and I/O cell repositories at pinned commits, and takes about twenty
minutes; `docs/esd/simulation.rst` gives the command. With `--reuse` it
rebuilds the tables and figures from the waveforms of its last run.

The layout figures (`docs/esd/gds/figures.py`) and the netlist-against-layout
table (`docs/esd/gds/check.py`) read the foundry's GDS files. `GF180_IO`
names a checkout of the gf180mcu I/O cell repository at the commit
`docs/esd/simulation.rst` pins. Every layout figure uses the palette of
`layfig.py` and the scale bar and legend of `laykey.py`, and is drawn with
the bond pad at the left.
`check.py` fails if a device's size in the layout differs from its netlist.

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
- The sidebar nests the way the index pages do. The root `index.rst` has one
  captioned `toctree` per group of topics (The chip, Data interfaces, Power,
  Silicon, Reference). Sphinx shows captions only for the root page, so a
  topic with more than about seven pages groups them under small group
  pages instead (for example `power/poe/fundamentals.rst`). A group page
  opens with one sentence about the subject, lists its pages with one line
  each, and holds the `toctree` for them; the topic index lists the groups. A new page goes
  into the group page that fits it.
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
  `diagram-viewer.js` opens a diagram over the whole window when it is
  clicked, where the reader zooms with the wheel or a pinch and pans by
  dragging. Its styles are in `custom.css`.

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
- **Headings:** short noun phrases in sentence case with no end
  punctuation, usually 2 to 6 words ("Breakdown at curved edges", not
  "Curved edges break down first"). Page titles must read well in the
  sidebar. Keep "Open questions" and "References". A heading is never the
  only place a fact is stated: the section's text states it.
- **Diagrams:** every section that describes a layout, a set of
  connections, a sequence, a change of state, a waveform or how one
  quantity depends on another has its own figure. Never send the reader to
  a standard, datasheet or other site for a picture; redraw it from the
  numbers on the page and cite the source of the numbers.
- **Each fact in one place:** link to it instead of restating it.
- **Page shape:** the first paragraph starts on the subject and states
  facts about it, so that what the page covers is clear from it. Pages
  never describe themselves or address the writer: no "This page
  describes…", "These pages cover…", "this section", "below we", notes to
  the author or TODOs. Write "A powered device limits its inrush current so
  that …", not "This page describes how a powered device limits its inrush
  current." A page that leaves design decisions open ends with one "Open
  questions" section, which lists them all. Explanatory pages with nothing open have
  none.
- **Numbering:** every figure and table is numbered, referenced with
  `:numref:`, and has `:alt:` text.
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
