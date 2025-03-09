# Open Uranus Tools

> In this directory you will find some tools and tutorials how to prepare the enviroment.



## Common Passwords

To make users save we need to setup a table to store common german passwords into our database.


### Prerequisites

Before running the tools, make sure to install the necessary system dependencies on your Ubuntu machine.

```sh
sudo apt update
sudo apt install wget
sudo apt install git git-lfs
sudo apt install python3 python3-pip python3-venv
sudo apt install postgresql-16 postgresql-postgis gdal-bin
```


### Enviroment Setup

Ceate an `.env` file inside the project root. Make sure to add the following content and repace values accordingly.

```sh
DB_PASS=oklab
DB_HOST=localhost
DB_USER=oklab
DB_NAME=oklab
DB_PORT=5432
```


### Create Tables

```psql
CREATE TABLE uranus.common_passwords (password VARCHAR(255) PRIMARY KEY);
```


### Download and Insert

Make sure you are in the tools directory and you have clone this project. Follow these steps 


```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 insert_common_passwords.py --env ../.env --target /tmp --url https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Common-Credentials/Language-Specific/German_common-password-list.txt --verbose
deactivate
```