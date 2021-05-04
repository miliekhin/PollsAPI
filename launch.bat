@echo.
@echo.
@echo ---------------------------------------------
@echo Installing virtual environment...
py -m venv venv
@echo.
@echo.
@echo ---------------------------------------------
@echo Activating virtual environment...
call venv\Scripts\activate.bat
@echo.
@echo.
@echo ---------------------------------------------
@echo Updating pip...
easy_install.exe pip
@echo.
@echo.
@echo ---------------------------------------------
@echo Installing requirements...
pip install -r requirements.txt
@echo.
@echo.
@echo ---------------------------------------------
@echo Configurating project...
manage.py configure
@echo.
@echo.
@echo ---------------------------------------------
@echo Launching server...
start chrome "http://127.0.0.1:8000/docs/"
manage.py runserver
