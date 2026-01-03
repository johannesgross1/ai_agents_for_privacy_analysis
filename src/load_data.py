import json
import sqlite3
import pandas as pd
from tld import get_fld


def parse_domain(remote_host):
    domain = get_fld(remote_host, fix_protocol=True, fail_silently=True)
    if domain is None:
        domain = remote_host
    return domain


class DataLoader:
    def __init__(self, db_path_auto: str, db_path_manual: str, json_path_data_handling: str, manual_log_path: str, tracker_domains_path: str):
        self.tracker_domains_path = tracker_domains_path
        self.__conn_auto = sqlite3.connect(db_path_auto)
        self.__conn_manual = sqlite3.connect(db_path_manual)
        self.apps = pd.read_csv(manual_log_path)
        self.__apps_string = ', '.join(['"{}"'.format(value) for value in set(self.apps['package_name'])])
        self.data_handling = self.__load_data_handling(json_path_data_handling)
        self.traffic_auto = self.__load_traffic_auto()
        self.traffic_manual = self.__load_traffic_manual()
        self.third_party = self.__load_3p()
        self.permissions = self.__load_perms()

        self.auto_domain_count = len(set(self.traffic_auto['remote_domain']))
        self.manual_domain_count = len(set(self.traffic_manual['remote_domain']))
        self.auto_tracker_domain_count = len(set(self.traffic_auto[self.traffic_auto['is_tracker'] == 1]['remote_domain']))
        self.manual_tracker_domain_count = len(set(self.traffic_manual[self.traffic_manual['is_tracker'] == 1]['remote_domain']))
        self.auto_host_count = len(set(self.traffic_auto['remote_host']))
        self.manual_host_count = len(set(self.traffic_manual['remote_host']))
        self.auto_tracker_host_count = len(set(self.traffic_auto[self.traffic_auto['is_tracker'] == 1]['remote_host']))
        self.manual_tracker_host_count = len(set(self.traffic_manual[self.traffic_manual['is_tracker'] == 1]['remote_host']))

    def __load_data_handling(self, json_path_data_handling: str):
        with open(json_path_data_handling, 'r') as file:
            # parse json and filter it to only include apps that are in self.apps
            return list(json.load(file))

    def __load_apps(self):
        apps_auto = pd.read_sql_query('SELECT packageName as package_name, label FROM App', self.__conn_auto)
        apps_manual = pd.read_sql_query('SELECT packageName as package_name, label FROM App', self.__conn_manual)

        # return list of results that are in both databases, add the label from the auto database
        apps_combined = apps_auto.merge(apps_manual, on='package_name', how='inner')
        apps_combined['label'] = apps_combined['label_x']
        # drop the label_x and label_y columns
        apps_combined = apps_combined.drop(columns=['label_x', 'label_y'])
        return apps_combined

    def __load_traffic_auto(self):
        query = 'SELECT * FROM JoinedRequest WHERE package_name IN (%s)' % self.__apps_string
        df = pd.read_sql_query(query, self.__conn_auto)
        df['remote_domain'] = df['remote_host'].apply(parse_domain)
        with open(self.tracker_domains_path, 'r') as file:
            domains = file.read().splitlines()
            df['is_tracker'] = df['remote_domain'].apply(lambda x: 1 if x in domains else 0)
        return df

    def __load_traffic_manual(self):
        query = 'SELECT * FROM JoinedRequest WHERE package_name IN (%s)' % self.__apps_string
        df = pd.read_sql_query(query, self.__conn_manual)
        df['remote_domain'] = df['remote_host'].apply(parse_domain)
        with open(self.tracker_domains_path, 'r') as file:
            domains = file.read().splitlines()
            df['is_tracker'] = df['remote_domain'].apply(lambda x: 1 if x in domains else 0)
        return pd.concat([df, self.traffic_auto], axis=0).reset_index(drop=True)

    def __load_3p(self):
        query = 'SELECT * FROM JoinedTrackerLibrary WHERE package_name IN (%s)' % self.__apps_string
        df = pd.read_sql_query(query, self.__conn_auto)
        return df

    def __load_perms(self):
        query = 'SELECT * FROM JoinedPermission WHERE package_name IN (%s)' % self.__apps_string
        df = pd.read_sql_query(query, self.__conn_auto)
        return df
