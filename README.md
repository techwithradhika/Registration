Download the Xammp server, and start both apach and mysql services. click on Admin in mysql which will take you to the localhost of phpmyadmin in the browser.

Download VisualStudio and Python, Clone the Repository "git clone https://github.com/techwithradhika/Registration.git" in terminal from VSC.

Now first to create the Registration table to store the data in database, open file sql_db.py.
In terminal navigate to the current folder and install virtual environment "pip install virtualenv", Create new VENV "python -m virtualenv venv", 
Activate the VENV ".\venv\Scripts\activate" and also install the dependencies using pip "pip install mysql-connector-python fastapi sqlalchemy pydantic uvicorn".
Nou run the sql_db python file from terminal "python sql_db.py".
after successful running of the pyhon file check if the database "Registration" is created with the table "register" inside it in the localhost.

open the api python file and at the "line 17", replace the path with the path of templates file "templates_directory = Path("C:/Users/radhi/Downloads/New folder/templates")".
from terminal run api python file "python api.py".

Now to perform CURD operations enter "uvicorn api:app --reload" in terminal which will start the Fastapi Application.
In the browser open the link "http://127.0.0.1:8000/docs"  It allows you to interact with the API request to perforn CURD operations.
follow this link "http://127.0.0.1:8000/static/index.html" to perforn CURD operations from the customized UI for Registration.
and you can verify if the data is updated at database accordingly.
