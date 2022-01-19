# Logitrack
by Christopher Roy


## About
Logitrack is an inventory management system developed for the Shopify Summer 2022 Backend Developer Intern Challenge!

It implements basic CRUD functionality for items, along with the ability to assign inventory to shipments.


## Stack
Logitrack is implemented in Django and developed on an Ubuntu machine.

The interface leverages Django's built-in templating system and the database is sqllite3.

## Build instructions
These build instructions can followed using a Unix terminal to install Logitrack on your local machine. It's possible that you may need superuser priviledges to install the project's dependencies on your computer.


### Prelim

First, ensure that you have a relatively new version of python3 installed. It should be installed by default on Ubuntu distros. You can check your installed version with the following command, or download it here: https://python.org/downloads/


```shell
python3 --version
```
Ex output:
`Python 3.8.10`

Next, be sure to have `pip3` installed. You can check if it's installed with the following command:

```shell
whereis pip3
```
Ex output:
`pip: /usr/bin/pip3 /usr/share/man/man1/pip3.1.gz`

Pip3 can be installed with the following command (using Ubuntu). You
```shell
sudo apt install python3-pip
```

Finally, it's recommended that you use a virtual environment, to keep python package versions seperate across projects.

You can install the CLI tool `virtualenvwrapper` here:
https://virtualenv.pypa.io/en/latest/

### Start

With everything installed, clone the repository to download a copy to the current working directory.

```shell
git clone git@github.com:ChristopherRoy1/shopify-challenge-s2022.git
```

Next, create & activate a virtualenvironment. If you have virtualenvwrapper installed, you can execute the following commands to create & activate a virtual environment:

```shell
mkvirtualenv logitrack_env
```

After ensuring the shell is in the repository's root directory, you can install the required python packages with the following command:

```shell
python3 -m pip install -r requirements.txt
```

## Launching Logitrack
To launch Logictrack, you'll need to execute a few commands.

First, the database migrations must be generated to update the database schema (as well as generate the database file!)

```shell
python3 manage.py makemigrations
```


```shell
python3 manage.py migrate
```

In order to view Logitrack's admin panel, you'll need to add yourself as a super user. Execute the following command and provide input to the prompts.

```shell
python3 manage.py createsuperuser
```

Finally, to launch Logitrack, start the server!
```shell
python3 manage.py runserver
```

The last step is to go to localhost, port 8000 in your browswer to start interacting with Logitrack!
