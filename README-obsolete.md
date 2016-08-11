#How to Run ?   

Make sure you have permissions to run start-aqxWeb.sh as an executable
$ chmod +x ./start-aqxWeb.sh

For first-time install, use the -i option:
$ ./start-aqxWeb.sh -i

Otherwise run start-aqxWeb.sh with no options
to run the app normally.
$ ./start-aqxWeb.sh


(Without using the script...)
For the first time :    
1. python setup.py build    
2. python setup.py install    

To run the application :    
python aqxWeb/run.py    

# Navigational and website functionality tests
## How to run selenium java class under tests/ui/SeleniumTest? - Terminal
* Run in the following order as it first creates a system in one test, later in other test it uses the created system.
  * 1. MeasurementTest.java 2. AnnotationsDAVTest 3. DavSystemTest
* Edit file AnnotationsDAVTest. Enter you gmail id at YOUR_GMAIL_ID = "" and YOUR_PASSWORD = ""
* cd to **cs6510** folder.
* Step 1: run command with yourdirectory **javac -cp ".:/Users/yourdirectory/aqxWeb-NEU/tests/ui/SeleniumTests:/Users/yourdirectory/aqxWeb-NEU/jar/*" MeasurementTest.java**
* Step 2: run command with yourdirectory **java -cp ".:/Users/yourdirectory/aqxWeb-NEU/tests/ui/SeleniumTests:/Users/yourdirectory/aqxWeb-NEU/jar/*" com.neu.edu.cs6510.MeasurementTest.java**
* Repeat Step-1 and Step-2 for other files too.

## How to run robot testing? - Terminal
* pip install robotframework
* pip install robotframework-selenium2library
* cd to folder ui
* run command **robot WebPages_Tests**

 

