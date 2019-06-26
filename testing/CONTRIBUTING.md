# Contributing to TDXLIB

If you'd like to contribute to the development of TDXLib, we're happy to have you on board. 
Here are a few things to help you get set up and going.

## Setting up a development environment

In order to work on TDXLIB, you'll need to get the latest version of Python installed. Any version > 3.6 should work, 
but we prefer to make sure things are functional on the latest release

### IDE Suggestions

I've mostly used [PyCharm CE](https://www.jetbrains.com/pycharm/download/#section=windows) for this project. It's got a lot of nice features, debugging, etc. 
For a lighter-weight feel, try 
[Visual Studio Code](https://code.visualstudio.com/download) or 
[Sublime Text](https://www.sublimetext.com/3), but for the real lightweight experience, use 
[vi](https://en.wikipedia.org/wiki/Vi).

### Cloning the repo (Collaborators Only)

First, go and get the latest tdxlib code.

    git clone https://github.com/cedarville-university/tdxlib

Checkout the develop branch (which has latest tested code), and create a local branch of your own to begin development on. 

    cd tdxlib
    git checkout develop
    git branch my-new-feature
    git checkout my-new-feature

### Setting up a virtual environment

If you'd like to work in a virtual environment, use pip to install virtualenv. 
If not, skip to [Install dependencies](#install-dependencies) below 

    pip install virtualenv
    
Then create a virtual environment in the root of the folder, called 'venv'. 
(This repository is configured to ignore that folder name.)

    virtualenv venv
    
Next, activate your virtual environment: 

**Windows:**

    venv\Scripts\activate.bat

**MacOS/Linux:**

    source venv/Scripts/activate

### Install Dependencies

Then, install the dependencies into your environment with pip: 

    pip install requests python-dateutil
    
For testing your in-code documentation, install the following as well: 

    pip install sphinx
    
If you'd like to test interactions with Google Sheets (per the ticket generation script in ```examples/```), install the following: 

    pip install gspread oauth2client
    
## Coding Guidelines

In no particular order: 

- This project adheres to PEP8 pretty rigidly. 
- Module, variable, and method names are snake_case
- Class names are PascalCase
- Use typing hints wherever possible for code clarity
- In-code documentation should use the following form:
    ~~~~
    """
    Short description of method. 
    
    Long description of method or clarification on purpose.
    
    :param example: This is a description of a boolean parameter, example. (Required)
    :param other: This is a description of a  string  parameter, other. (Default: 'other')
    
    :return: a list of string objects as examples
    
    :rtype: list
    
    """
    ~~~~
    In-code documentation in ```develop``` or ```master``` will automatically trigger a build at tdxlib.readthedocs.io,
    but documentation can be manually generated using the make commands in the ```docs/``` folder.
    
- A unit test should be written for every method, and stored in a testing file in ```testing/module_name_testing.py```:
  - Use the unittest Python library
  - Test for any use case you'd like the code to work for
  - Add the following code to any unit test that edits or creates anything in TDX:
        
    ```python
    # protect prod from testing:
    if not tdx.sandbox:
        return
    ```
  - All unit tests should pass before making a pull request to develop
  - Unit tests should use values from a copy of the ```testing/sample_testing_vars``` file (as ```testing_vars.json``` in the root tdxlib 
  folder) .json files are ignored in this repository, so you can safely add your own TDX ID's, names, and other data to
  the file so that you can test TDXLib against your own environment.
  
