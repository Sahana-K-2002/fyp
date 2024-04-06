## Resume Chatbot Assistant
Welcome to the Resume Chatbot Assistant repository! This project aims to create a chatbot assistant that helps users in generating resumes. The chatbot utilizes natural language processing (NLP) techniques to understand user queries and preferences, and it generates tailored resumes accordingly.
Contributing
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:



### Requirements(Minimum)

Download and install Python, make sure to check the box Add Python to PATH on the installation setup screen. </p>
Download and install MySQL Community Server and MySQL Workbench, you can skip this step if you already have a MySQL server set up. </p>



### Requirements ,Packages used and Installation
Download and install Python,MySQL
 
### Installation
Navigate to your current project directory for this case it will be **fyp**. <br>

### 1 .Fork the repository and Clone it into your local machine
```csharp
git clone https://github.com/{your-Github-Username }/fyp.git
```
          
### 2 .Create an environment
> Check to make sure you are in the same directory where you did the git clone,if not navigate to that specific directory.

Depending on your operating system,make a virtual environment to avoid messing with your machine's primary dependencies
          
**Windows**
          
```csharp
cd fyp
py -3 -m venv venv

```
          
**macOS/Linux**
          
```csharp
cd fyp
python3 -m venv venv

```

### 3 .Activate the environment
          
**Windows** 

```venv\Scripts\activate```
          
**macOS/Linux**

```. venv/bin/activate```
or
```source venv/bin/activate```

### 4 .Install the requirements

Applies for windows/macOS/Linux

```csharp
pip install -r requirements.txt
```


### 6. Create the database and table 

```sql
-- Create the  database named "loginapp"
CREATE DATABASE loginapp;


-- Switch to 'loginapp' database; 
USE loginapp; 


-- Create 'account' table with id, username,email, password columns. 
CREATE TABLE accounts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL
); 
```

### 6. Run the application 

**For linux and macOS**
Make the run file executable by running the code

```chmod 777 run```

Then start the application by executing the run file

```./run```

**On windows**
```
set FLASK_APP=main
flask run
```

### 7.Contribution

Fork the repository.

Create a new branch for your feature or bug fix:
```
git checkout -b feature-new-feature
```
Make your changes and commit them:
```
git commit -m "Add new feature"
```
Push to your branch:
```
git push origin feature-new-feature
```

Submit a pull request detailing your changes.

