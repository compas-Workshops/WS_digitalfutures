# DigitalFUTURES 2019: Workshop Group 1

*Computational design and engineering of tensioned formworks for concrete shells*

During this workshop we will use COMPAS to design and realise a concrete shell with complex geometry. The shell will be built using a cablenet-and-fabric formwork.

* https://github.com/compas-dev/compas
* https://compas-dev.github.io/main
* https://forum.compas-framework.org/
* https://github.com/BlockResearchGroup/WS_digitalfutures
* https://github.com/BlockResearchGroup/compas_fofin
* https://github.com/BlockResearchGroup/compas_fofin-UI

## Schedule

Day       | Morning             | Afternoon
---       | -------             | ---------
Saturday  | -                   | COMPAS basics & `compas_fofin`
Sunday    | Design explorations | Physical tests
Monday    | Materialisation     | Detailing
Tuesday   | Assembly            | Assembly
Wednesday | Casting             | Casting
Thursday  | Documentation       | COMPAS advanced
Friday    | Demoulding          | Demoulding


## Installation

* [Instructions for Mac](mac.md)
* [Instructions for Windows](windows.md)

## Examples

The examples are in the following folders of the workshop repository.

* `examples/01_shortestpath_plot`
* `examples/02_dynamicrelaxation_live`
* `examples/03_smoothingonsurface_rhino`
* `examples/04_interactivesubd_rhino`
* `examples/07_numpy_rhino`

## Fixes

On Windows, use the Anaconda Prompt (**run as administrator**). On Mac, use the Terminal.

Download a fresh copy of `WS_digitalfutures` and `compas_fofin-UI`. Replace the old copies in your Workshop folder.

Change the Anaconda Prompt or Terminal to the folder `compas_fofin-UI` (the folder containing `FOFIN{7ea0207d-965a-4982-abc7-f60810ae2626}`). Then with the `base` environment active (`base` is active by default), do

```bash
conda remove -n digitalfutures --all
```

```bash
conda create -n DF2019 python=3.6 numpy=1.15.4
```

> On Mac, add `python.app` to the end of the above command.

```bash
conda activate DF2019
```

```bash
conda install COMPAS=0.7.1
```

```bash
pip install git+https:://www.github.com/BlockResearchGroup/compas_fofin.git#egg=compas_fofin --upgrade
```

```bash
python
```

```python
>>> import compas
>>> import compas_plotters
>>> compas.__version__
'0.7.1'
>>> exit()
```

```bash
python -m compas_rhino.uninstall
```

```bash
python -m compas_rhino.install
```

```bash
python -m compas_rhino.install -p compas_fofin
```

```bash
python -m compas_rhino.uninstall_plugin FOFIN{7ea0207d-965a-4982-abc7-f60810ae2626}
```

```bash
python -m compas_rhino.install_plugin FOFIN{7ea0207d-965a-4982-abc7-f60810ae2626}
```

> If you are using Rhino 5 on Windows, add the `-v 5.0` flag.
