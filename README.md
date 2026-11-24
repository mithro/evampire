# evampire

evampire is an integrated circuit for the
[GlobalFoundries 180 nm MCU (gf180mcu)](https://gf180mcu-pdk.readthedocs.io/)
process, manufactured through [wafer.space](https://wafer.space/). It is a
three-port gigabit Ethernet hub with a small
[RISC-V](https://en.wikipedia.org/wiki/RISC-V) processor that also moves power
between [Power over Ethernet](https://en.wikipedia.org/wiki/Power_over_Ethernet)
and [USB Type-C](https://en.wikipedia.org/wiki/USB-C). This repository holds
its design documentation.

Status: in design. No silicon exists; the documentation describes the design
target.

The chip passes traffic straight through between two Ethernet ports, using
[cut-through forwarding](https://en.wikipedia.org/wiki/Cut-through_switching):
each byte is sent on a few clock cycles after it arrives, without storing
the whole frame. Each port connects to an Ethernet transceiver, either an
external chip over
[RGMII](https://en.wikipedia.org/wiki/Media-independent_interface#RGMII) (a
digital interface with 4 data bits each way) or one integrated on evampire.
The processor receives the frames whose destination address matches a
programmed address under a mask, which selects the address bits that must
match, and it can send frames of its own.

The same documentation describes
[ebat](https://evampire.readthedocs.io/en/latest/ebat/index.html):
evampire with the Ethernet data functions removed, keeping the same Power
over Ethernet and USB Type-C functions.

The [block diagram in the evampire documentation](https://evampire.readthedocs.io/en/latest/architecture/index.html#fig-block-diagram)
shows the blocks inside the chip.

## Building the documentation

The documentation uses [Sphinx](https://www.sphinx-doc.org/) and needs
[uv](https://docs.astral.sh/uv/) and [Graphviz](https://graphviz.org/).

```sh
make -C docs html       # output in docs/_build/html
make -C docs check      # the checks that CI runs
make -C docs linkcheck  # check every external link
```

`make -C docs check` builds with warnings treated as errors and runs both
checkers listed below.

## Contents

| Path | Contents |
|---|---|
| [`docs/`](docs/) | The documentation source, published as the [evampire documentation](https://evampire.readthedocs.io/) |
| [`docs/check_source.py`](docs/check_source.py) | Fails when a page names part of a standard as plain text instead of linking to it |
| [`docs/check_html.py`](docs/check_html.py) | Fails when the built pages have error boxes, unreferenced figure and table numbers, diagrams without alt text, or pages that the sidebar does not link to |
| [`.github/workflows/docs.yml`](.github/workflows/docs.yml) | Builds and checks the documentation on every push and pull request, and runs the link checker |

## Licence, citing and contributing

Apache License 2.0. See [LICENSE](LICENSE).

To cite evampire, cite this repository, <https://github.com/mithro/evampire>.

Contributions are made as pull requests on GitHub. Documentation follows the
maintainers' documentation writing rules: British spelling, each fact in one
place, every claim sourced at the claim, and sentences of at most 45 words.
Every standard is referenced with the roles described in
[`docs/conf.py`](docs/conf.py). `make -C docs check` must pass before a pull
request is merged.
