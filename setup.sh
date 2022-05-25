#! /bin/sh

exec pyside6-uic data/template/mainwindow.ui -o mainwindow.py & pid=$!
wait $pid

exec pyside6-uic data/template/resize.ui -o resize.py & pid=$!
wait $pid

exec pyside6-uic data/template/info.ui -o info.py & pid=$!
wait $pid

exec pyside6-uic data/template/settings.ui -o settings.py & pid=$!
wait $pid

exec tail -n +11 mainwindow.py > data/template/design.py & pid=$!
wait $pid

exec tail -n +15 resize.py >> data/template/design.py & pid=$!
wait $pid

exec tail -n +15 info.py >> data/template/design.py & pid=$!
wait $pid

exec tail -n +15 settings.py >> data/template/design.py & pid=$!
wait $pid

exec rm -rf mainwindow.py resize.py info.py settings.py & pid=$!
wait $pid

exec sed -i '/^\s*#/ d' data/template/design.py & pid=$!
wait $pid

exec sed -i '1i\"""Auto generated Qt User Interface"""\n' data/template/design.py & pid=$!
wait $pid

echo "-- Process complete --"
