#Buttons:
#*Update database from SAGE
#*Run simulation
#*Run optimization
#*Save outputs

import subprocess
import tkinter as tk
import pandas as pd
import threading
import sqlalchemy
#import sqlalchemy_hana

def connectToHANA():
    conn = None
    try:
        conn = sqlalchemy.create_engine('hana://DBADMIN:HANAtest2908@8969f818-750f-468f-afff-3dc99a6e805b.hana.trial-us10.hanacloud.ondemand.com:443/?encrypt=true&validateCertificate=false').connect()
        print('Connection established.')
    except Exception as e:
        print('Connection failed! ' + str(e))        

    return conn

def update_db_from_SAGE(uploadToHana):

    table_urls = {'BOM': r'http://10.4.240.65/api/IntegrationAPI/GetBOM',
              'Inventory': r'http://10.4.240.65/api/IntegrationAPI/GetInventory',
              'Facility': r'http://10.4.240.65/api/IntegrationAPI/GetItemFacility',
              'ItemMaster': r'http://10.4.240.65/api/IntegrationAPI/GetItemMstr2',
              'RoutingAndRates': r'http://10.4.240.65/api/IntegrationAPI/GetRoutingAndRates',
              'WorkCenters': r'http://10.4.240.65/api/IntegrationAPI/GetWorkCenters',
              'WorkOrders': r'http://10.4.240.65/api/IntegrationAPI/GetWorkOrders'}

    for table in table_urls:
        try:
            globals()[table] = pd.read_json(table_urls[table])
            print(f'Table {table} succesfully loaded.')
        except Exception as e:
            print(f'Couldn\'t load table {table}: ' + str(e))
            #try to read from HANA

    if uploadToHana:
        connection = connectToHANA()
        for table in table_urls:
            try:
                connection.execute(f'DELETE FROM {table}')
                globals()[table].to_sql(table.lower(), con = connection, if_exists = 'append', index = False)
                print(f'Table {table} was uploaded to HANA succesfully.')
            except Exception as e:
                print(f'Couldn\'t save {table} table into HANA. ' + str(e))
        connection.close()

def run_experiment(experiment):
    subprocess.run(f'Model\CJFoods_windows-{experiment}.bat')

window = tk.Tk()
window.title('Alphia Launcher')
window.state("zoomed")

update_db_from_SAGE_btn = tk.Button(text = 'Read from SAGE', command = threading.Thread(target = update_db_from_SAGE, args = (True,)).start)
update_db_from_SAGE_btn.pack(pady = 10)

run_simulation_btn = tk.Button(text = 'Run simulation', command = threading.Thread(target = run_experiment, args = ('simulation',)).start)
run_simulation_btn.pack(pady = 10)

run_optimization_btn = tk.Button(text = 'Run optimization', command = threading.Thread(target = run_experiment, args = ('optimization',)).start)
run_optimization_btn.pack(pady = 10)

window.mainloop()
