
# User Management and Email Sending Application

This application facilitates the management of candidate and the automatic sending of emails based on their tenure. 

## Features

- **Automatic Email Sending:** Sends personalized emails to users based on their tenure (3 months, 6 months, more than 6 months).
- **Graphical User Interface:** An intuitive user interface to ease the management of users and the sending of emails.
- **Error Reporting:** Displays error messages in case of issues during data insertion or email sending.

## Prerequisites

- Python 3.8 or higher
- Pip for managing Python packages

## Installation

1. Clone the GitHub repository: ` git clone https://github.com/MG1222/Relance_Email.git`

### Setting Up a Virtual Environment

After forking the repository, it's recommended to set up a virtual environment for the project. This helps in managing dependencies and ensuring that the project runs smoothly on your machine.

1. **Navigate to the project directory**:
   - Open a terminal and change to the project directory with `cd path/to/project`.

2. **Create the virtual environment**:
   - Run `python -m venv env` to create a new virtual environment named `env`.

3. **Activate the virtual environment**:
   - On Windows, execute `.\env\Scripts\activate`.
   - On macOS and Linux, use `source env/bin/activate`.

4. **Install dependencies**:
   - With the virtual environment activated, install the project dependencies by running `pip install -r requirements.txt`.

## Configuration

Before launching the application, ensure to configure the email settings in the `app/config/config_example.json` file. Replace the default values with your SMTP authentication information and email details.

## Usage

To start the application, run the main file from the command line:
```
python app/main.py
```

## Development

- **main_page.py:** Contains the logic for the user interface and interactions with the user.
- **config_example.json:** Configuration file for email settings and email templates.
- **main.py:** The entry point of the application, initializes the user interface and the database.

