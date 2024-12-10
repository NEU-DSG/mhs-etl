''' main file for running the mhs-etl script '''
import argparse
import json
import etl.ex_dsg_db_pull as extractor
import etl.tr_jqa_network as jqa_network
import etl.tr_cms_rbt_network as cms_rbt_network

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        parameters = json.load(f)
    parser = argparse.ArgumentParser(description="ETL Pipeline")
    parser.add_argument("--extract", action="store_true", help="Run the extract step")
    parser.add_argument("--network_jqa", action="store_true", help="Run the extract step")
    parser.add_argument("--network_cms", action="store_true", help="Run the extract step")
    parser.add_argument("--network_rbt", action="store_true", help="Run the extract step")
    parser.add_argument("--ner", action="store_true", help="Run the extract step")
    parser.add_argument("--all", action="store_true", help="Run the extract step")
    args = parser.parse_args()
    if args.all:
        pass
    elif args.extract:
        for params in parameters['extract']:
            extractor.extract(params)
    elif args.network_jqa:
        for params in parameters['network_jqa']:
            jqa_network.network_transform(params)
    elif args.network_cms:
        for params in parameters['network_cms']:
            cms_rbt_network.network_transform(params)



if __name__ == "__main__":
    main()
