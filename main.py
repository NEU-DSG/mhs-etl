''' main file for running the mhs-etl script '''
import argparse
import json
import etl.ex_dsg_db_pull as extractor
import etl.tr_jqa_network as jqa_network

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        parameters = json.load(f)
    parser = argparse.ArgumentParser(description="ETL Pipeline")
    parser.add_argument("--extract", action="store_true", help="Run the extract step")
    parser.add_argument("--network", action="store_true", help="Run the extract step")
    parser.add_argument("--ner", action="store_true", help="Run the extract step")
    parser.add_argument("--all", action="store_true", help="Run the extract step")
    args = parser.parse_args()
    if args.all:
        pass
    elif args.extract:
        for params in parameters['extract']:
            extractor.extract(params)
    elif args.network:
        for params in parameters['network']:
            jqa_network.network_transform(params)


if __name__ == "__main__":
    main()
