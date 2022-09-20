

# TODO: TEST
# from conftest import TEST_DATA_DIR, TMP_DATA_DIR

#if bucket:
#
#
#    for filename in ["mock_graph.gpickle", "mock_network.csv"]:
#
#        remote_filepath = os.path.join("storage", "data", filename)
#
#        print("------------")
#        print("UPLOADING LOCAL FILE...")
#        local_filepath = os.path.join(TEST_DATA_DIR, filename)
#        #blob = bucket.blob(remote_filepath)
#        #print(blob) #> <Blob: impeachment-analysis-2020, storage/data/mock_graph.gpickle, None>
#        #blob.upload_from_filename(local_filepath)
#        #print(blob.exists()) #> True
#        blob = service.upload(local_filepath, remote_filepath)
#        print(blob) #> <Blob: impeachment-analysis-2020, storage/data/mock_graph.gpickle, 1590433751346995>
#
#        print("------------")
#        print("DOWNLOADING REMOTE FILE (TEMPORARY)...")
#        tmp_local_filepath = os.path.join(TMP_DATA_DIR, filename)
#        blob = service.download(remote_filepath, tmp_local_filepath)
#        print(os.path.isfile(tmp_local_filepath))
#        os.remove(tmp_local_filepath)
#
