# MHS-ETL

MHS-ETL is an extract, transform, load script for the DSG Lab space in collaboration with the Massachusetts Historical Society.

## Description

In 2024, the DSG worked with the MHS to revive some of Bill Quinn's previous explorations into the MHS collections. This repository reflects the data processing step that pulls data from the XML Database, transforms it via Python scripts, and loads it into the NEU-DSG/mhs-web repository for serving on the web. The processing for this repository currently covers the network graph transformation, and the subject timeline transformation.

## Getting Started

### Dependencies

* All the development and testing for this repository was done on Mac with ARM processing chips.

### Installation

Clone the repository:

```
git clone https://github.com/NEU-DSG/mhs-etl
```

Navigate to the directory and install the requirements:

```
pip install -r requirements.txt
```

### Executing the program

All of the extractions and transformations are run through the `main.py` file and the `config.json` file.

## Authors

Joel Lee, Data Engineer, Digital Scholarship Group, Northeastern University Library

## Version History

* 0.1
    * Initial Release, Database Extraction, Network Graph, and Subject Timeline.

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

I would like to thank Bill Quinn for his initial work into the MHS and DSG collaboration.