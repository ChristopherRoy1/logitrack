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

The last step is to go to localhost, port 8000 in your browser to start interacting with Logitrack!

## Quickstart - Iteracting with Logitrack
Logitrack's user interface is still very much a work in progress.

### Creating a company
Before you can interact with items, you'll need to create a company that you can associate the items to. You can do so at the following URL

http://localhost:8000/create-company/

### View all companies
After creating the company, you'll see it in the list of companies at the following url: (after create of a company, your browser will automatically re-direct to this URL as well)
http://localhost:8000/view-all-companies/


### Creating an item
To create an item, visit the following URL:

http://localhost:8000/create-item/

### View all items
To view all items in Logitrack, across all companies, visit the following URL:
http://localhost:8000/view-all-items/

You can click on the 'View' link in one of the table rows to view the corresponding item.

## Edit an item
Navigate to the view all items view, and click on the 'Edit' link (right next to view)

## Delete an Item
From the view all items page, click on the 'Delete' link in the last column.


## Shipments - view
To view a company's shipments, click on the 'View Companies' page and select the 'View Shipments link'

## Shipments - create

### Shipment types
There are two types of shipments supported by Logitrack
  - Inbound shipments, which increase the available quantity for an item on receipt at the warehouse,
  - Outbound shipments, which decrease the available quantity for an item when they are shipped from the warehouse



Before items can be assigned to a shipment, you must create a shipment in the sytem first.
