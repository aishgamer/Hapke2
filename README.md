# Hapke2

Can you smell what the rock is cooking?


# Installation Instructions

## Python Environments
- Ensure Python 3 is installed and available

## Recommended Software
- VS Code (Install latest from VS Code online)
- Go to Extensions Tab
    - Install Python and Powershell extensions

## Creating virtual environment
### If python and python3 are available
Open a new terminal in VS Code (Shortcut: Ctrl+Shift+`)
1. python3 -m venv .name_of_your_virtual_environment
2. A folder with the same name as your virtual environment is created
3. Navigate to Lib under the virtual environment folder
4. Copy path of activate.bat
5. Paste and execute in your command terminal
6. The terminal prompt should change to (.name_of_your_virtual_environment) C:/>
7. Execute pip3 install -r requirements.txt
8. Once all libraries are installed, click the Select Python Interpreter in the lower left blue status bar
9. Choose the environment in folder of your virtual environmnet in the palette pop up at the top

### If only python (version 3) is available
1. python -m venv .name_of_your_virtual_environment
2. A folder with the same name as your virtual environment is created
3. Navigate to Lib under the virtual environment folder
4. Copy path of activate.bat
5. Paste and execute in your command terminal
6. The terminal prompt should change to (.name_of_your_virtual_environment) C:/>
7. Execute pip install -r requirements.txt
8. Once all libraries are installed, click the Select Python Interpreter in the lower left blue status bar
9. Choose the environment in folder of your virtual environmnet in the palette pop up at the top