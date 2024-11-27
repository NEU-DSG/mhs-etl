''' main file for running the mhs-etl script '''
import etl.extract.dsg_db_pull
import etl.transform.network.jqa_network as jqa_network
print(etl.extract.dsg_db_pull.pull_index)

jqa_network.main()


