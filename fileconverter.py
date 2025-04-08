import os
import pandas as pd
import pymysql


root = "RBI_Data"
supported_formats = ["XLS","XLSX"]
metric = "NEFT"
neft_headers = ['Sr. No','Bank Name','No. Of Outward Transactions','Amount(Outward)','No. Of Inward Transactions','Amount(Inward)']

root_path = os.path.join(os.getcwd(),root)
os.chdir(root_path)
folders  = [year for year in os.listdir() if year.isdigit()]


conn = pymysql.connect(
    host="localhost",
    port=3306,         
    user="root",
    password="2102005",
    charset="utf8mb4",
    autocommit=True
)

try:
    with conn.cursor() as cursor:
        cursor.execute("SHOW DATABASES LIKE 'rbi_metric_%';")
        databases = cursor.fetchall()
        
        for (db_name,) in databases:
            drop_query = f"DROP DATABASE `{db_name}`;"
            cursor.execute(drop_query)
        
        new_db_name = f"rbi_metric_{metric}"
        create_query = f"CREATE DATABASE `{new_db_name}`;"
        cursor.execute(create_query)
        
        use_query = f"USE `{new_db_name}`;"
        cursor.execute(use_query)

except Exception as e:
    print(e)


try:
    with conn.cursor() as cursor:
        
        for folder in folders:
            current_path = os.path.join(root_path,folder)
            os.chdir(current_path)
            for year_data in os.listdir():
                year = year_data.split(".")[0]
                extension = year_data.split(".")[-1]
                if extension == "XLS":
                    #df = pd.read_excel(year_data,engine="xlrd",sheet_name="NEFT",header=None)
                    engine = "xlrd"
                elif extension == "XLSX":
                    #df = pd.read_excel(year_data,engine="openpyxl",sheet_name="NEFT",header=None)
                    engine = "openpyxl"
                elif extension not in supported_formats:
                    print("File Format Not Supported")
                    continue      
                df = pd.read_excel(year_data,engine=engine,sheet_name="NEFT",header=None)
                search_area = df.head()
                row_idx = df.where((search_area == "Sr. No.") | (search_area == "Sr. No")| (search_area == "Sr.No")).stack().index[0][0]
                #replace later with .isfind and .idxmax, accoutn for all possible permutatios of the col name we are searching for

                df = df.iloc[row_idx+2:-2,:]
                df = df.dropna(axis=1, how='all')
                df.columns = neft_headers
                df = df.reset_index(drop=True)

                query =  f"""
                    CREATE TABLE `{metric}_{year}_{folder}` (
                        sr_no INT,
                        bank_name VARCHAR(255),
                        no_of_outward_transactions BIGINT,
                        amount_outward DOUBLE,
                        no_of_inward_transactions BIGINT,
                        amount_inward DOUBLE
                    );
                """

                cursor.execute(query)
                print(query)

except Exception as e:
    print(e)

