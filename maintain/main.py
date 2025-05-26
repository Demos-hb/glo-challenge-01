from data_maintain import BigQueryDataManager

def main(request):
    manager = BigQueryDataManager()
    result = manager.backup()
    return result