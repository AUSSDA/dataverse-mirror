import json
import os
from pyDataverse.api import Api
from pyDataverse.utils import dict_to_json
from pyDataverse.utils import read_datasets_csv
from pyDataverse.utils import read_json_file
from pyDataverse.utils import write_file
import time


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    DOWNLOAD_DATA = False
    UPLOAD_DATA = False

    # Download data
    if DOWNLOAD_DATA:
        # Setup working directory
        if not os.path.isdir(ROOT_DIR+'/data/down'):
            os.mkdir(ROOT_DIR+'/data/down')
        down_dir = ROOT_DIR+'/data/down'

        # Connect to Dataverse Api
        api_token_down = os.environ["API_TOKEN_DOWN"]
        api_host_down = os.environ["API_HOST_DOWN"]
        api_down = Api(api_host_down, api_token=api_token_down)

        # Extract dois and dataverse of the datastes.
        datasets_list = read_datasets_csv(ROOT_DIR+'/data/datasets.csv')
        dv_list = [ds['dataverse'] for ds in datasets_list]
        dv_list = set(dv_list)

        # Create directories for all dataverses and download the metadata
        for dv in dv_list:
            down_dataverse_dir = down_dir+'/dv_{0}'.format(dv)
            if not os.path.isdir(down_dataverse_dir):
                os.mkdir(down_dataverse_dir)
            resp_dv = api_down.get_dataverse(dv)
            write_file(down_dataverse_dir+'/dv_'+dv+'_metadata.json',
                       json.dumps(resp_dv['data']))

        # Loop over all datasets
        for ds in datasets_list:
            # Get metadata of dataset
            resp_ds = api_down.get_dataset(ds['doi'])
            identifier = ds['doi'].split('/')[1]

            # Create directory for dataset
            down_dataset_dir = down_dir+'/dv_'+ds['dataverse']+'/ds_'+identifier
            if not os.path.isdir(down_dataset_dir):
                os.mkdir(down_dataset_dir)

            # Save dataset metadata as json file
            filename_metadata = down_dataset_dir+'/ds_'+identifier+'_metadata.json'
            write_file(filename_metadata, json.dumps(resp_ds['data']))

            # Loop over all datafiles of a dataset
            for df in resp_ds['data']['latestVersion']['files']:
                file_id = str(df['dataFile']['id'])

                # Create directory for datafile
                datafile_dir = down_dataset_dir+'/df_'+file_id
                if not os.path.isdir(datafile_dir):
                    os.mkdir(datafile_dir)

                # Download and save datafile file
                resp = api_down.get_datafile(file_id, 'content')
                filename_datafile = datafile_dir+'/df_'+str(df['dataFile']['filename'])
                write_file(filename_datafile, resp.content, 'wb')

    if UPLOAD_DATA:
        CREATE_DV = False
        DELETE_DV = False
        CREATE_DS = False
        ADD_FILE = False
        DELETE_DS = False
        CREATE_DF = False

        api_token_up = os.environ["API_TOKEN_UP"]
        api_host_up = os.environ["API_HOST_UP"]
        api_up = Api(api_host_up, api_token=api_token_up,
                     use_https=False)

        # create dataverse
        if CREATE_DV:
            dv_json = read_json_file('data/down/dv_AUSSDA/dv_AUSSDA_metadata.json')
            api_up.create_dataverse(dv_json['alias'], dict_to_json(dv_json))
            time.sleep(0.2)

        # create dataset
        if CREATE_DS:
            ds_json = read_json_file('data/down/dv_AUSSDA/ds_VKYZPD/ds_VKYZPD_metadata.json')
            resp = api_up.create_dataset('science', dict_to_json(ds_json))
            time.sleep(0.2)

        if ADD_FILE:
            doi = 'doi:10.5072/FK2/PF6EMS'
            filename = 'dev/cat.jpg'
            resp = api_up.upload_file(doi, filename)
