# Cisco IOS Command Automation Script

This Python script automates the execution of commands on Cisco IOS devices using Netmiko. It is the GUI on top of the [cisco-ssh-py](https://github.com/Ahsxka/cisco-ssh-py) project. To use this GUI, first clone the 

## Input File Format:

### IP Address File:
- One IP address per line.

### Credentials File:
- CSV (Comma-Separated Values) format.
- Each line should contain the following fields: username, password, enable. The first line of the file should contain the field names

Example of password file :

username,password,enable<br>
admin,cisco,cisco<br>
sysAdmin,cisco2,cisco2

### Command File (for Configuration Mode):
- One command per line.
- If a confirmation step is required (e.g. deleting a username), add "\n" to the end of the command for the script to handle it.

## How to Use the Script:
1. Select the execution mode: "Show Commands Mode" or "Configurations Mode".
2. Choose the input files (IP addresses, credentials, commands).
3. Select a destination folder for logging files.
4. Choose verbose mode (optional).
5. Confirm the selected parameters.
6. Wait for the script to execute and check the logs for details.

Ensure that the input files are correctly formatted according to the specifications above to ensure the smooth operation of the script.
