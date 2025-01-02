# MHS-ETL

MHS-ETL is an extract, transform, load script for the DSG Lab space in collaboration with the Massachusetts Historical Society.

## Description

In 2024, the DSG worked with the MHS to revive some of Bill Quinn's previous explorations into the MHS collections. This repository reflects the data processing step that pulls data from the XML Database, transforms it via Python scripts, and loads it into the NEU-DSG/mhs-web repository for serving on the web. The processing for this repository currently covers the network graph transformation, and the subject timeline transformation.

## Getting Started

### Dependencies

* All the development and testing for this repository was done on Mac with ARM processing chips.

* You will also need a `.config` file in the root directory of the repository with the credentials for accessing the DSG database, in the format:

    ```
    [PSC]
    USERNAME=ABC
    PASSWORD=XYZ
    ```

### Installation

Clone the repository:

```
git clone https://github.com/NEU-DSG/mhs-etl
```

Navigate to the directory and install the requirements (in a Python virtual environment if you'd like):

```
pip install -r requirements.txt
```

### Executing the program

All of the extractions and transformations are run through the `main.py` file and the `config.json` file. The `main.py` file is the main "runner" of the ETL script, and it is called with flags to run each part of the ETL script. The individual files run can be found in the `etl/` folder. The `config.json` file is the file with all of the parameters to run each parts of the ETL script. These can be altered based on the specifications within the respective files in the `etl/` folder. 

#### Extraction

Extraction is the extraction of the edition XML files from the DSG XML Database into this repository. It is performed with the `etl/ex_dsg_db_pull.py` file. To run this file, you can use the runner to run `python3 main.py --extract`. This will take the arguments in the "extract" object of the `config.json` and create a folder with the date of the pull, including the editions specified in the `config.json` file. In the `config.json` file, you can put `["all"]` to pull all of the editions, or any arrangement of the current editions, for example `['cms', 'jqa']` if you only want to pull the `cms` and `jqa` editions.

#### Transformation


## Authors

Joel Lee, Data Engineer, Digital Scholarship Group, Northeastern University Library

## Version History

* 0.1
    * Initial Release, Database Extraction, Network Graph, and Subject Timeline.

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

I would like to thank Bill Quinn for his initial work into the MHS and DSG collaboration.