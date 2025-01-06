''' main file for running the mhs-etl script '''
import argparse
import json
import etl.ex_dsg_db_pull as extractor
import etl.tr_jqa_network as jqa_network
import etl.tr_cms_rbt_network as cms_rbt_network
import etl.tr_subject_headings as subject
import etl.topics as topic
import etl.timeline_util as timeline_util

def main():
    ''' Main runner function for ETL Script '''
    with open("config.json", "r", encoding="utf-8") as f:
        parameters = json.load(f)
    parser = argparse.ArgumentParser(description="ETL Pipeline")
    parser.add_argument("--extract", action="store_true", help="Run the extract step")
    parser.add_argument("--network_jqa", action="store_true", help="Run the JQA network step")
    parser.add_argument("--network_cms", action="store_true", help="Run the CMS network step")
    parser.add_argument("--network_rbt", action="store_true", help="Run the RBT network step")
    parser.add_argument("--subjects", action="store_true", help="Run the Subject Timeline step")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    args = parser.parse_args()
    if args.all:
        print("Starting Extraction...")
        for params in parameters['extract']:
            extractor.extract(params)
        print("Starting JQA Network Transformation...")
        for params in parameters['network_jqa']:
            jqa_network.network_transform(params)
        print("Starting CMS Network Transformation...")
        for params in parameters['network_cms']:
            cms_rbt_network.network_transform(params)
        print("Starting RBT Network Transformation...")
        for params in parameters['network_rbt']:
            cms_rbt_network.network_transform(params)
        print("Starting Subject Timeline Creation...")
        for params in parameters['subjects']:
            subject.subject_creation(params)
        for params in parameters['topics']:
            topic.create_topics(params)
        for params in parameters['timeline_util']:
            timeline_util.timeline_data_creation(params)
    elif args.extract:
        print("Starting Extraction...")
        for params in parameters['extract']:
            extractor.extract(params)
    elif args.network_jqa:
        print("Starting JQA Network Transformation...")
        for params in parameters['network_jqa']:
            jqa_network.network_transform(params)
    elif args.network_cms:
        print("Starting CMS Network Transformation...")
        for params in parameters['network_cms']:
            cms_rbt_network.network_transform(params)
    elif args.network_rbt:
        print("Starting RBT Network Transformation...")
        for params in parameters['network_rbt']:
            cms_rbt_network.network_transform(params)
    elif args.subjects:
        print("Starting Subject Timeline Creation...")
        for params in parameters['subjects']:
            subject.subject_creation(params)
        for params in parameters['topics']:
            topic.create_topics(params)
        for params in parameters['timeline_util']:
            timeline_util.timeline_data_creation(params)

if __name__ == "__main__":
    main()
