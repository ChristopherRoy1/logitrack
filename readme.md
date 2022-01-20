# Logitrack
by Christopher Roy


## About
Logitrack is an inventory management system that allows a logistics company to manage their warehouse's inventory.

It implements basic CRUD functionality for items, along with the ability to assign inventory to shipments. Company models were also created to allow for the logistics company running Logitrack to serve more than one client!


## Stack
Logitrack is implemented in Django and developed on an Ubuntu machine.

The interface leverages Django's built-in templating system and the database is sqllite3.

## Django project structure

In case the reader is not familiar with Django & the role that each files play,
I've included a short description below of the more important files:

- `logitrack\urls.py` and `inventory\urls.py`: Files used to map urls to the views that should handle them
- `inventory\views.py`: Python functions and classes that receive HTTP requests and prepare HTTP responses
- `inventory\forms.py`: Python classes that control the forms displayed to the user to prepare form submissions for the server
- `inventory\models.py`: Python classes that provide an abstraction over the underlying database, allowing for db field definitions & relationships
- `inventory\tests.py`: A series of Python classes and functions that are used to execute automated tests against the web application
- `inventory\templates\*`: All files in this directory correspond to template files which contain tags that are interpreted by Django's templating engine and returned as responses to requests made to the server



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
git clone git@github.com:ChristopherRoy1/logitrack.git
```

Next, create & activate a virtual environment. If you have virtualenvwrapper installed, you can execute the following command to create & activate a virtual environment, but Python virtual environment tools like venv should work fine as well. :

```shell
mkvirtualenv logitrack_env
```

After ensuring the shell is in the repository's root directory, you can install the required python packages with the following command:

```shell
python3 -m pip install -r requirements.txt
```

## Launching Logitrack for the first time
To launch for the first time, you'll need to execute some extra commands
first.

While not strictly necessary as all migration files are included in the
repository, execute the following command to ensure any that any missing migrations files
are generated.
```shell
python3 manage.py makemigrations
```
Once complete, we need to create the database (which is not included in the repository)& update the database schema using the migrations files. This will all be handled by the following command

```shell
python3 manage.py migrate
```

### Optional command
> In order to view Logitrack's admin panel, you'll need to add yourself to the database as a super user. Execute the following command and provide input to the prompts to do so!

>```shell
> python3 manage.py createsuperuser
>```

## Tests
A series of automated tests have been prepared to help keep Logitrack stable
as features are added.

To launch the tests, simply run the following command from the project root.
```shell
python3 manage.py test
```

## Launching Logitrack

With the database generated, we can now launch Logitrack! Execute the following command

```shell
python3 manage.py runserver
```

The last step is to go to localhost, port 8000 in your browser to start interacting with Logitrack!



## Quickstart - Interacting with Logitrack
Logitrack's user interface is still very much a work in progress, and the developer apologizes for the lack of CSS.


You'll find below some more information about its functionality.

To view the full list of URLs, refer to the files `logitrack\urls.py`
and `inventory\urls.py`

### Skipping the user interface:
While the user interface is functional (and described in more detail in the following sections) you can use the list of urls below to quickly navigate across logitrack's pages.

Create a company: http://localhost:8000/create-company/
Create an item: http://localhost:8000/create-item/

View all items: http://localhost:8000/view-all-items/
View all companies: http://localhost:8000/view-all-companies/

Assuming an ID of 1 for the company, item, and shipment, these models can be interacted with using the following links:

View an item: http://localhost:8000/item/1
Update an item: http://localhost:8000/item/1/edit/
Delete an item: http://localhost:8000/item/1/delete/

View a company: http://localhost:8000/company/1
View shipments for a company: http://localhost:8000/company/1/shipments/
Create a new shipment (for a company): http://localhost:8000/company/1/shipments/create/
Edit a shipment & add items: http://localhost:8000/company/1/shipments/1/items/

Finally, you can access Django's built-in admin pages by navigating to the following URL: http://localhost:8000/admin
Make sure that you added yourself as a superuser to the application, otherwise you won't be able to log in.


### Creating a company
Before you can interact with items, you'll need to create a company that you can associate the items to. You can do so at the following URL:

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

### Edit an item
Navigate to the view all items view, and click on the 'Edit' link (right next to view)

### Delete an Item
From the view all items page, click on the 'Delete' link in the last column. Be sure to click the 'Delete Item' on this page button!

For example, to delete an item with ID 1, you can navigate to the following URL:
http://localhost:8000/item/1/delete/



### Shipments - view
To view a company's shipments, click on the 'View Companies' page and select the 'View Shipments link'

Ex: For a company with ID 1, their shipments can be viewed here: http://localhost:8000/company/1/shipments/

### Shipments - create
To create a shipment, visit http://localhost:8000/view-all-companies/ and click on the 'View Shipments' link for the company that you wish to create a shipment for.

For example, to create a shipment for company with ID 1, this can be done at the following link:
http://localhost:8000/company/1/shipments/create/

### Shipment types
There are two types of shipments supported by Logitrack
  - Inbound shipments, which increase the available quantity for an item on receipt at the warehouse,
  - Outbound shipments, which decrease the available quantity for an item when they are shipped from the warehouse


Before items can be assigned to a shipment, you must create a shipment in the sytem first.

# Next steps & future improvements

There are many improvements that can be made to Logitrack. Here are a few that come to mind:

- Test coverage
  - More tests for the models are needed
  - There are no tests written to validate forms
  - Similarly, there are no tests to validate the behavior of Logitrack's views

- SKU Validation
   - To improve for the efficiency of pick, pack, and shipping, a model (or field) to capture supported SKU formatting is planned to be added to the application. This would allow clients of the logistics company to force a SKU format on their items.

- Remove the SECRET_KEY from the `settings.py` file when this application is eventually deployed into production!

- Update the Shipment & ShipmentItem models to allow for a single shipment to contain items belonging to different companies
