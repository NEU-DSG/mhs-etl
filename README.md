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

## Executing the program

All of the extractions and transformations are run through the `main.py` file and the `config.json` file. The `main.py` file is the main "runner" of the ETL script, and it is called with flags to run each part of the ETL script. The individual files run can be found in the `etl/` folder. The `config.json` file is the file with all of the parameters to run each parts of the ETL script. These can be altered based on the specifications within the respective files in the `etl/` folder. 

### Extraction

Extraction is the extraction of the edition XML files from the DSG XML Database into this repository. It is performed with the `etl/ex_dsg_db_pull.py` file. To run this file, you can use the runner to run `python3 main.py --extract`. This will take the arguments in the "extract" object of the `config.json` and create a folder with the date of the pull, including the editions specified in the `config.json` file. In the `config.json` file, you can put `["all"]` to pull all of the editions, or any arrangement of the current editions, for example `['cms', 'jqa']` if you only want to pull the `cms` and `jqa` editions.

### Transformation

Transformation involves the transformation of the data into both the network graph and the subject timeline.

#### Network Graph

The network graph takes the XML data, extracts the `<persRef>` tags and runs a series of mathematical calculations to generate a node and edge list in json format. This gets sent to the front end web application. The network graph transformations are run for each of the three editions, jqa, cms, and rbt. You can run them by running `python3 main.py` with the flags `--network_jqa`, `--network_cms`, or `network_rbt`. The configurations for these runs can be set in the `config.json` file. Note that for `jqa`, it is split up into time periods, which are parameters that can be altered. All of the network graph transformations are assigned a `weight` value. This is the value that removes connections under a certain "weight", which represents the amount of times two people are referenced within the selection of entries. This is to ensure that the network graph is legible, as some time periods would have too many nodes for the graph to be usable.

#### Subject Timeline

The subject timeline takes the editor-assigned subjects, and creates a chronological timeline that displays when those topics were being discussed in their respective entries. This can be run with the command `python3 main.py --subjects`. The related scripts to this that are run in sucession are `etl/tr_subject_headings.py`, `etl/topics.py`, and `etl/timeline_util.py`. These should stay relatively the same for the parameters in the `config.json` file, apart from the initial extraction folder dates which should be edited when a new pull is run.

### Loading

Loading is the loading of the json and csv files into the web application. The web application can be found at [NEU-DSG/mhs-web](https://github.com/NEU-DSG/mhs-web). The loading is done through a manual Github action. This can be found at `.github/push_to_web_repo.yml`. The secrets to that action are tied to this repository, and the current username and email secrets are set up for Joel Lee, although this can be altered in the Github settings. Running this action will take all of the necessary files in the `data` folder, and copy it over to the `NEU-DSG/mhs-web` folders where they need to go. Once this is done, the ETL script is complete and the `NEU-DSG/mhs-web` repository handles the push to AWS.

## Authors

Joel Lee, Data Engineer, Digital Scholarship Group, Northeastern University Library

Misha Ankudovych, Digital Project Specialist Co-Op, Digital Scholarship Group, Northeastern University Library

## Version History

* 0.1
    * Initial Release, Database Extraction, Network Graph, and Subject Timeline.

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

I would like to thank Bill Quinn for his initial work into the MHS and DSG collaboration, and the editors and staff at the MHS for their guidance.