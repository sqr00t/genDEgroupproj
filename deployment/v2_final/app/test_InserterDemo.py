from InserterDemo import s3filename_to_tablename

def test_s3filename_to_tablename():
    s3_file_name = '2022216ayr_16-02-2022_09-00-00.csv_stores.csv'
    
    expected = '_stores'
    
    actual = s3filename_to_tablename(s3_file_name)
    
    print(actual)
    
    assert actual == expected