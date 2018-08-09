#!/bin/bash
cur_version=$(pip --version)
echo $cur_version
pip uninstall --yes ColabGDrive
pip install -U -q git+https://github.com/drdavidrace/ColabGdrive.git
pip list | grep -i Colab
pip install -U -q PyDrive
pip list | grep -i pydrive