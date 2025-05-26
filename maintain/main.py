from data_maintain import BigQueryDataManager

def main(request):
    manager = BigQueryDataManager(
            project_id="iter-data-storage-pv-uat",
            dataset_id="temp",
            bucket_input="demo-input-hb",
            bucket_backup="demo-backup-hb"
        )
    result = manager.backup_all()
    return result