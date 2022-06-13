#!/bin/bash

echo "Compiling UI..."
pyside6-uic data/template/mainwindow.ui -o mainwindow.py
pyside6-uic data/template/resize.ui -o resize.py
pyside6-uic data/template/info.ui -o info.py
pyside6-uic data/template/settings.ui -o settings.py

echo "Merging File..."
cat mainwindow.py > data/template/design.py
cat resize.py >> data/template/design.py
cat info.py >> data/template/design.py
cat settings.py >> data/template/design.py

echo "Removing Garbage..."
rm -rf mainwindow.py resize.py info.py settings.py

echo "Process complete!"

