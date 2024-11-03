import os
import inspect
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def help():
    print("""Ajuda:
    import avocado_manager as av
    av.Init()
    av.Init("avocado.csv")
    av.info()
    av.df("df")
    df_sorted = av.sort("df_date_price_volume", ["Date","region"], asc=[False, True])
    display(av.df("df_cp"))
    av.add(df,"df_name")
    """)
    
def init(csv='avocado.csv'):
    Manager(csv)

def df(name):
    return Manager.get_df(name)

def add(df, df_name):
    Manager.add_df(df, df_name)

def sort(dataframe, columns, asc = True):
    return Manager.sort_df(name= dataframe, columns= columns, ascending= asc)

def info():
    Manager.mostrar_info()

def get_season():
    return Manager.get_season

class Manager:            
    debug = None
    dataframes = {}

    classification_colors = {'City':'green' ,'Region':'yellow' ,'GreaterRegion':'orange', 'State':'red'}

    get_season = lambda date: '1.Primavera' if 3 <= date.month <= 5 else ('2.Verano' if 6 <= date.month <= 8 else ('3.Otoño' if 9 <= date.month <= 11 else '4.Invierno'))
    
    region_classification = {
        'Albany': 'City',
        'Atlanta': 'City',
        'BaltimoreWashington': 'Region',
        'Boise': 'City',
        'Boston': 'City',
        'BuffaloRochester': 'Region',
        'California': 'GreaterRegion',
        'Charlotte': 'City',
        'Chicago': 'City',
        'CincinnatiDayton': 'Region',
        'Columbus': 'City',
        'DallasFtWorth': 'Region',
        'Denver': 'City',
        'Detroit': 'City',
        'GrandRapids': 'City',
        'GreatLakes': 'GreaterRegion',
        'HarrisburgScranton': 'Region',
        'HartfordSpringfield': 'Region',
        'Houston': 'City',
        'Indianapolis': 'City',
        'Jacksonville': 'City',
        'LasVegas': 'City',
        'LosAngeles': 'City',
        'Louisville': 'City',
        'MiamiFtLauderdale': 'Region',
        'Midsouth': 'GreaterRegion',
        'Nashville': 'City',
        'NewOrleansMobile': 'Region',
        'NewYork': 'City',
        'Northeast': 'GreaterRegion',
        'NorthernNewEngland': 'Region',
        'Orlando': 'City',
        'Philadelphia': 'City',
        'PhoenixTucson': 'Region',
        'Pittsburgh': 'City',
        'Plains': 'GreaterRegion',
        'Portland': 'City',
        'RaleighGreensboro': 'Region',
        'RichmondNorfolk': 'Region',
        'Roanoke': 'City',
        'Sacramento': 'City',
        'SanDiego': 'City',
        'SanFrancisco': 'City',
        'Seattle': 'City',
        'SouthCarolina': 'Region',
        'SouthCentral': 'GreaterRegion',
        'Southeast': 'GreaterRegion',
        'Spokane': 'City',
        'StLouis': 'City',
        'Syracuse': 'City',
        'Tampa': 'City',
        'TotalUS': 'TotalUS',
        'West': 'GreaterRegion',
        'WestTexNewMexico': 'Region'
    }

    @classmethod
    def __init__(self, file_path='avocado.csv', debug=False):
        """
        Inicializa la clase DatasetLoader.
        
        :param debug: Booleano que indica si se debe mostrar información de depuración.
        :param csv_path: Ruta opcional a un archivo CSV para cargar inmediatamente.
        """
        self.debug = debug
        # Si se proporciona un archivo CSV, se intenta cargarlo
        if file_path is not None:
            self.load_data(file_path)
            self.format_data()

    @classmethod
    def get_df(cls, name='df'):
        """
        Retorna el DataFrame almacenado bajo un nombre específico.
        
        :param name: Nombre del DataFrame a obtener.
        :return: DataFrame correspondiente o None si no existe.
        """
        return cls.dataframes.get(name, None)

    @classmethod
    def add_df(cls, dataframe, name):
        cls.dataframes[name] = dataframe

    @classmethod
    def sort_df(cls, name, columns, ascending):
        #cls.dataframes[name] = dataframe
        return cls.dataframes.get(name, None).sort_values(columns, ascending= ascending)

    @classmethod
    def load_data(cls, file_path):
        """
        Carga un dataset desde un archivo CSV.
        
        :param file_path: Ruta del archivo CSV.
        :return: None
        """

        if not os.path.exists(file_path):
            print(f"Error: El archivo '{file_path}' no existe.")
            return
        try:
            df = pd.read_csv(file_path)
            cls.add_df(df,"df")
            if cls.debug:
                print(f"Dataset {file_path} cargado correctamente.")
                print(f"Dimensiones del dataset: {df.shape}")
                print(f"Columnas: {df.columns.tolist()}")
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")

    @classmethod
    def format_data(cls):
        """
        Formatea el dataset basado en ...
        
        :param conditions: None
        :return: Un DataFrame con los datos filtrados.
        """
        if cls.get_df("df") is None:
            print("format_data: El dataset no se ha cargado. Usa el método 'load_data' primero.")
            return None
        
        df_cp = cls.get_df("df").copy()
        df_cp['Date'] = pd.to_datetime(df_cp['Date']) #Normalizar fecha
        df_cp = df_cp.rename(columns={df_cp.columns[0]: 'Col_0'}) # Primera columna sin titulo, potencialmente eliminable
        df_cp = df_cp.rename(columns={'4046': 'Volume_Hass_S'}) # Etiquetas mas descritivas
        df_cp = df_cp.rename(columns={'4225': 'Volume_Hass_L'})
        df_cp = df_cp.rename(columns={'4770': 'Volume_Hass_XL'})
        df_cp = df_cp.drop('Col_0', axis=1) # Parecen IDs del 0 al 52. Eliminable. 
        # Col_0 = df_cp['Col_0'].unique()  print(f"Col_0: {Col_0}\n")
        df_cp = df_cp.reset_index()
        cls.add_df(df_cp ,"df_cp")

        df_type = df_cp.groupby('type')['Total Volume'].count()
        df_type = df_type.reset_index()
        cls.add_df(df_type,"df_type")

        regions = df_cp['region'].unique() 
        cls.add_df(regions, "regions")

        years = df_cp['year'].unique() 
        cls.add_df(years, "years")

        #df_weekly = df_cp.groupby(pd.Grouper(key='Date', freq='W')).count() # ['AveragePrice'].mean()
        #df_weekly = df_weekly.reset_index()
        dates = df_cp['Date'].unique() 
        cls.add_df(dates, "dates")

        df_cp['region_class']= df_cp['region'].map(cls.region_classification)

        df_date_price_volume = df_cp[['Date', 'region', 'AveragePrice', 'Total Volume']]
        df_date_price_volume = df_date_price_volume.reset_index()
        df_date_price_volume['Season'] = df_date_price_volume['Date'].apply(cls.get_season)
        cls.add_df(df_date_price_volume, "df_date_price_volume")

        # Para seleccionar unicamente las regiones propias , descartamos Total US para la vista gráfica
        cls.add_df(df_cp[df_cp.region != 'TotalUS'],"df_cp_cleaned")

        cls.add_df(df_cp[df_cp['region_class']=='City'],"df_cp_city")
        cls.add_df(df_cp[df_cp['region_class']=='Region'],"df_cp_region")
        cls.add_df(df_cp[df_cp['region_class']=='GreaterRegion'],"df_cp_greater")
        cls.add_df(df_cp[df_cp['region_class']=='TotalUS'],"df_cp_totalUS")

        cls.add_df(df_cp.groupby('region')['Total Volume'].sum().nlargest(10).index,"region_largest")


    @classmethod
    def filter_data(cls, df_name, **conditions):
        """
        Filtra el dataset basado en condiciones especificadas.
        
        :param conditions: Condiciones de filtro en formato clave=valor. 
                           Ejemplo: columna="valor"
        :return: Un DataFrame con los datos filtrados.
        """
        df = cls.get_df(df_name)
        if df is None:
            print("filter_data: El dataset no se ha encontrado.")
            return None
        
        filtered_data = df
        for column, value in conditions.items():
            if column in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[column] == value]
                if cls.debug:
                    print(f"Filtrando por {column}={value}. Dimensiones actuales: {filtered_data.shape}")
            else:
                print(f"Advertencia: La columna '{column}' no existe en el dataset.")
        
        return filtered_data

    @classmethod
    def mostrar_info(cls):
        """
        Muestra información general del dataset cargado.
        
        :return: None
        """
        
        df = cls.get_df("df")
        if df is None:
            print("mostrar_info: El dataset no se ha cargado. Usa el método 'load_data' primero.")
            return

        print(f"Lista de dataframes: {list(cls.dataframes.keys())}")
        if cls.debug:
            print("Información general del dataset:")
            print(df.info())

            print("Información estadística del dataset:")
            print(df.describe())

            years = cls.get_df("years")
            print(f"\nAños: {years}")

            regions = cls.get_df("regions")
            print(f"\nRegiones comerciales: {regions}")

            #print("\nPrimeras 5 filas del dataset df_cp:")
            #df_cp = cls.get_df("df_cp")
            #print(df_cp.head())
