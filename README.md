## Installation
Platform : Linux


Python version : 3.5.x or 3.6.x

pip version : pip3 

To install pip3 use following command
```bash
sudo apt-get install python3-pip
```

Python3 packages: To install required packages please run following command:

```bash
 sudo pip3 install -r requirement.txt
```

## Usage

List of files:-
 requirement.txt - Contains list of all packages required to python program


 config.json - Configuration file for program.


 README - README file


 getUniversityInfo.py - File which contains actual python code.


 How to run:
 ```bash
 python3 getUniversityInfo.py config.json
 ```

 Here getUniversityInfo.py takes config.json as argument

 Output:
     All required data will be stored in MYSQL database. University details are stored in UniversityDetails table and
     Highlights are stored in Highlights table.
     
     Also output.json will be created in same folder which contains output data in JSON format


     To see data in mysql, Use following steps

     > mysql -u Username -pPassword
     > use databaseName
     > select * from UniversityDetails;
     > select * from Highlights;
  
