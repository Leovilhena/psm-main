# How to run scripts and install dependencies

## OS
All the examples were created on a Linux machine.

### Python ^3.8
From the website: https://www.python.org/downloads/release/python-3811/

or with apt:
```shell
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.8
```

### PIP
```shell
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

PIP can be run from python as well:
```shell
python -m pip --version
```

### Python packages
The Python packages needed are declared in the "requirements.txt" file and 
can be installed with the following commands:

```shell
pip install -r requirements.txt
```

or

```shell
python -m pip install -r requirements.txt
```