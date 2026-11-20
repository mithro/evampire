# evampire

evampire is a three-port gigabit Ethernet hub integrated circuit for the
GlobalFoundries 180 nm MCU (gf180mcu) process, manufactured through
[wafer.space](https://wafer.space/).

Two external ports, each connected over RGMII to an external Ethernet
transceiver, forward all traffic to each other using cut-through forwarding.
A small internal RISC-V microcontroller receives frames selected by a
destination MAC address mask and can send frames of its own.

Documentation: <https://evampire.readthedocs.io/>

## Building the documentation

The documentation uses [Sphinx](https://www.sphinx-doc.org/) and needs
[uv](https://docs.astral.sh/uv/) and [Graphviz](https://graphviz.org/).

```sh
make -C docs html     # output in docs/_build/html
make -C docs check    # same build with warnings treated as errors
```

## License

Apache License 2.0. See [LICENSE](LICENSE).
