#!/bin/bash

venv_name=aqxWeb-env
first_time_install=0

while getopts ":i" opt; do
  case $opt in
    i)
      first_time_install=1; echo "Running initial install..." >&2
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2; exit 1
      ;;
  esac
done

if test -e "$venv_name"
then
  echo "Pre-existing virtualenv found."
else
  echo "Creating virtual environment..."
  virtualenv $venv_name
  echo "Done!"
fi

source $venv_name/bin/activate

if ((first_time_install))
then
  echo "Installing aqxWeb..."
  if test -e requirements.txt
  then
    echo "Checking to see if any dependencies need to be installed..."
    pip install -r requirements.txt --egg
  else
    echo "ERROR: No requirements.txt found."
    exit 1
  fi
  if test -e setup.py
  then
    echo "Building..."
    python setup.py build
    python setup.py install
  else
    echo "ERROR: Could not find setup.py."
    exit 1
  fi
fi

echo "Starting aqxWeb..."
python aqxWeb/run.py



