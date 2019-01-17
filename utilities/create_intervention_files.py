
# coding: utf-8

# # Create interventions files for smif
# 
# Read the energy supply data and write it into files in the `initial_conditions` and `interventions/minimal|full` folders

# In[9]:


from csv import DictWriter, DictReader


# In[108]:


def write_elecnetwork(init_file):
    with open("data/energy_supply/interventions/minimal/es_elec_network.csv", "w") as destination_file:
        fieldnames = ['name',
                     'technical_lifetime_value',
                     'capacity_value',
                     'capacity_unit',
                     'location',
                     'table_name',
                     'to_location',
                     'location_',
                     'capital_cost_value',
                     'capital_cost_unit']
        gen_file = DictWriter(destination_file, fieldnames)
        gen_file.writeheader()
        with open ("data/energy_supply/database_minimal/LineData.csv", "r") as source_file:
            reader = DictReader(source_file)
            for row in reader:
                name = "Line{}".format(row['LineNum'])
                data = {
                    'name': name,
                    'technical_lifetime_value': 50,
                    'capacity_value': row["MaxCapacity"],
                    'capacity_unit': "MW",
                    'location': row["FromBus"],
                    'table_name': "LineData",
                    'to_location': row["ToBus"],
                    'location_': "({},{})".format(row["FromBus"], row["ToBus"]),
                    'capital_cost_value': 0,
                    'capital_cost_unit': "GBP"
                }
                    
                gen_file.writerow(data)
                init_file.writerow({"name": name, "build_year": row["Year"]})  

def write_gasterminals(init_file):
    with open("data/energy_supply/interventions/minimal/es_gasterminals.csv", "w") as destination_file:
        fieldnames = ['name',
                     'technical_lifetime_value',
                     'capacity_value',
                     'capacity_unit',
                     'location',
                     'table_name',
                     'description',
                     'lngcapacity',
                     'intercapacity',
                     'domcapacity',
                     'operational_cost_value',
                     'operational_cost_unit',
                     'capital_cost_value',
                     'capital_cost_unit']
        gen_file = DictWriter(destination_file, fieldnames)
        gen_file.writeheader()
        with open ("data/energy_supply/database_minimal/GasTerminal.csv", "r") as source_file:
            reader = DictReader(source_file)
            for row in reader:
                data = {
                    'name': row["Name"],
                    'technical_lifetime_value': 50,
                    'capacity_value': row["TerminalCapacity"],
                    'capacity_unit': "mcm",
                    'location': row["GasNode"],
                    'table_name': "GasTerminal",
                    'description': "",
                    'lngcapacity': row["LNGCapacity"],
                    'intercapacity': row["InterCapacity"],
                    'domcapacity': row["DomCapacity"],
                    'operational_cost_value': row["GasTerminalOptCost"],
                    'operational_cost_unit': "GBP/mcm",
                    'capital_cost_value': 0,
                    'capital_cost_unit': "GBP",
                }
                    
                gen_file.writerow(data)
                init_file.writerow({"name": row["Name"], "build_year": row["Year"]})  

def write_heattech(init_file):
    with open("data/energy_supply/interventions/minimal/es_heattech.csv", "w") as destination_file:
        fieldnames = [
                      'type',
                      'name',
                      'location',
                      'minpower',
                      'capacity_value',
                      'capacity_unit',
                      'table_name',
                      'technical_lifetime_value',
                      'capital_cost_value',
                      'capital_cost_unit']
        gen_file = DictWriter(destination_file, fieldnames)
        gen_file.writeheader()
        with open ("data/energy_supply/database_minimal/HeatTechData.csv", "r") as source_file:
            reader = DictReader(source_file)
            for row in reader:
                data = {
                    'type': row["Type"],
                    'name': row["HeatTechName"],
                    'location': row["EH_Conn_Num"],
                    'minpower': row["MinPower"],
                    'capacity_value': row["MaxPower"],
                    'capacity_unit': "MW",
                    'table_name': "HeatTechData",
                    'technical_lifetime_value': 7,
                    'capital_cost_value': 0,
                    'capital_cost_unit': "GBP"
                }
                    
                gen_file.writerow(data)
                init_file.writerow({"name": row["HeatTechName"], "build_year": row["Year"]})  

def write_gaspipes(init_file):
    with open("data/energy_supply/interventions/minimal/es_gaspipes.csv", "w") as destination_file:
        fieldnames = ['name',
                      'technical_lifetime_value',
                      'location',
                      'table_name',
                      'to_location',
                      'length_value',
                      'diameter_value',
                      'pipeeff',
                      'minflow',
                      'maxflow',
                      'location_',
                      'capital_cost_value',
                      'capital_cost_unit']
        gen_file = DictWriter(destination_file, fieldnames)
        gen_file.writeheader()
        with open ("data/energy_supply/database_minimal/PipeData.csv", "r") as source_file:
            reader = DictReader(source_file)
            for row in reader:
                name = "pipe" + str(row["PipeNum"])
                data = {
                        'name': name,
                        'technical_lifetime_value': 50,
                        'location': row["FromNode"],
                        'table_name': "PipeData",
                        'to_location': row["ToNode"],
                        'length_value': row["Length"],
                        'diameter_value': row["Diameter"],
                        'pipeeff': row["PipeEff"],
                        'minflow': row["MinFlow"],
                        'maxflow': row["MaxFlow"],
                        'location_': "({},{})".format(row["FromNode"], row["ToNode"]),
                        'capital_cost_value': 0,
                        'capital_cost_unit': "GBP"
                }
                    
                gen_file.writerow(data)
                init_file.writerow({"name": name, "build_year": row["Year"]})      

def write_gasstorage(init_file):
    with open("data/energy_supply/interventions/minimal/es_gasstorage.csv", "w") as destination_file:
        fieldnames = ['name',
                      'technical_lifetime_value',
                      'capacity_value',
                      'capacity_unit',
                      'location',
                      'table_name',
                      'inflowcap',
                      'outflowcap',
                      'outflowcost',
                      'description',
                      'capital_cost_value',
                      'capital_cost_unit',
                      'syslayer']
        gen_file = DictWriter(destination_file, fieldnames)
        gen_file.writeheader()
        with open ("data/energy_supply/database_minimal/GasStorage.csv", "r") as source_file:
            reader = DictReader(source_file)
            for row in reader:
                data = {
                    'name': row["Name"],
                    'technical_lifetime_value': 50,
                    'capacity_value': row["StorageCap"],
                    'capacity_unit': "mcm",
                    'location': row["region"],
                    'table_name': "GasStorage",
                    'inflowcap': row["InFlowCap"],
                    'outflowcap': row["OutFlowCap"],
                    'outflowcost': row["OutFlowCost"],
                    'description': "",
                    'capital_cost_value': 0,
                    'capital_cost_unit': "GBP/mcm",
                    'syslayer': row["Syslayer"]
                }
                    
                gen_file.writerow(data)
                init_file.writerow({"name": row["Name"], "build_year": row["Year"]})    

def write_generators(init_file):
    with open("data/energy_supply/interventions/minimal/es_generators.csv", "w") as destination_file:
        fieldnames = ['name', 'technical_lifetime_value', 'capacity_value', 'capacity_unit',
           'location', 'sys_layer', 'type', 'min_power_value', 'min_power_unit',
           'table_name', 'description', 'to_location', 'pumpstore_capacity_value',
           'pumpstore_capacity_unit', 'capital_cost_value', 'capital_cost_unit']
        gen_file = DictWriter(destination_file, fieldnames)
        gen_file.writeheader()
        with open ("data/energy_supply/database_minimal/GeneratorData.csv", "r") as source_file:
            reader = DictReader(source_file)
            for row in reader:
                data = {
                    "name": row["GeneratorName"],
                    "technical_lifetime_value": int(row["Retire"]) - int(row["Year"]),
                    "capacity_value": row["MaxPower"],
                    "capacity_unit": "MW",
                    "location": row["BusNum"],
                    "sys_layer": row["SysLayer"],
                    "type": row["Type"],
                    "min_power_value": row["MinPower"],
                    "min_power_unit": "MW",
                    "table_name": "GeneratorData",
                    "description": "",
                    "to_location": row["GasNode"],
                    "pumpstore_capacity_value": row["PumpStorageCapacity"],
                    "pumpstore_capacity_unit": "MW",
                    "capital_cost_value": 0,
                    "capital_cost_unit": "GBP/MW"
                }
                gen_file.writerow(data)
                init_file.writerow({"name": row["GeneratorName"], "build_year": row["Year"]})
                
        with open("data/energy_supply/database_minimal/WindPVData_EH.csv", "r") as wind_file:
            reader = DictReader(wind_file)
            for row in reader:
                data = [
                    {
                    "name": "Onshorewind_{}".format(row["EH_Conn_Num"]),
                    "capacity_value": row["OnshoreWindCap"],
                    "location": row["EH_Conn_Num"],
                    "sys_layer": 2,
                    "type": "onshorewind",
                    "table_name": "WindPVData_EH"
                        
                    },
                    {
                    "name": "Offshorewind_{}".format(row["EH_Conn_Num"]),
                    "capacity_value": row["OffshoreWindCap"],
                    "location": row["EH_Conn_Num"],
                    "sys_layer": 2,
                    "type": "offshorewind",
                    "table_name": "WindPVData_EH"
                    },
                    {
                    "name": "PV_{}".format(row["EH_Conn_Num"]),
                    "capacity_value": row["PVCapacity"],
                    "location": row["EH_Conn_Num"],
                    "sys_layer": 2,
                    "type": "pv",
                    "table_name": "WindPVData_EH"
                    }]
                gen_file.writerows(data)
                inter_data = [
                    {"name": "Onshorewind_{}".format(row["EH_Conn_Num"]), "build_year": row["Year"]},
                    {"name": "Offshorewind_{}".format(row["EH_Conn_Num"]), "build_year": row["Year"]},
                    {"name": "PV_{}".format(row["EH_Conn_Num"]), "build_year": row["Year"]}]
                init_file.writerows(inter_data)
  
        with open("data/energy_supply/database_minimal/WindPVData_Tran.csv", "r") as wind_file:
            reader = DictReader(wind_file)
            for row in reader:
                data = [
                    {
                    "name": "Onshorewind_{}".format(row["BusNum"]),
                    "capacity_value": row["OnshoreWindCap"],
                    "location": row["BusNum"],
                    "sys_layer": 1,
                    "type": "onshorewind",
                    "table_name": "WindPVData_EH"
                        
                    },
                    {
                    "name": "Offshorewind_{}".format(row["BusNum"]),
                    "capacity_value": row["OffshoreWindCap"],
                    "location": row["BusNum"],
                    "sys_layer": 1,
                    "type": "offshorewind",
                    "table_name": "WindPVData_EH"
                    },
                    {
                    "name": "PV_{}".format(row["BusNum"]),
                    "capacity_value": row["PVCapacity"],
                    "location": row["BusNum"],
                    "sys_layer": 1,
                    "type": "pv",
                    "table_name": "WindPVData_EH"
                    }]
                gen_file.writerows(data)
                inter_data = [
                    {"name": "Onshorewind_{}".format(row["BusNum"]), "build_year": row["Year"]},
                    {"name": "Offshorewind_{}".format(row["BusNum"]), "build_year": row["Year"]},
                    {"name": "PV_{}".format(row["BusNum"]), "build_year": row["Year"]}]
                init_file.writerows(inter_data)

with open("data/energy_supply/initial_conditions/historical_interventions_minimal2.csv", "w") as init_cond_file:
    init_file = DictWriter(init_cond_file, ["name", "build_year"])
    init_file.writeheader()
    write_generators(init_file)
    write_gasstorage(init_file)
    write_gaspipes(init_file)
    write_heattech(init_file)
    write_gasterminals(init_file)
    write_elecnetwork(init_file)

