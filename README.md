# Natural_Langauge_Classifier_IBM_Gautam

1.Install python first then create a virtual environment and activate it by running below command in terminal.

 $ sudo apt-get update

 $ sudo apt-get install python3.6

 $ sudo apt-get install python3-pip

 $ sudo pip3 install virtualenv

2. Go into the project directory and run the followng commands

 $ virtualenv venv 

 $ source venv/bin/activate

3. On terminal, go into the project directory and Install all the dependencies by running below command where the requirements.txt is placed.

 $ pip install -r requirements.txt 

4. Deploying the Flask Project by running the below command.

 $ python flask_classify.py

5. Test the deployment using the following parameters on Postman

URL: http://localhost:8000/api
Request Type: Post
For request payload, select "Body" and then "form-data"
In the Key, first select the type as "file" and then set the key as "file"
Next, select the input.xml
And click on "Send"

On getting response, click on "save to a file" from "Save Response" drop-down menu



//Helping Links/References:
https://gist.github.com/frfahim/73c0fad6350332cef7a653bcd762f08d
http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/
