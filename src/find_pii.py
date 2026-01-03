import ipaddress

import pandas as pd


def search_pattern(row, pattern):
    return bool(pattern['regex'].search(row['request_content']))


def apply_regexes(traffic, regexes):
    traffic_copy = traffic.copy()
    for pattern in regexes:
        column_name = f"detected_{pattern['name']}"
        traffic_copy[column_name] = traffic_copy.apply(search_pattern, axis=1, pattern=pattern)

    return traffic_copy


def aggregate_pii_by_app(traffic, regexes, is_tracker):
    # Filter rows based on is_tracker status
    filtered_traffic = traffic[traffic['is_tracker'] == is_tracker]

    # Initialize an empty list to store the result rows
    result_rows = []

    tracker_string = 'tracker' if is_tracker else 'non_tracker'

    # Group by package_name
    package_groups = filtered_traffic.groupby('package_name')

    # For each package, calculate the count of distinct hosts for detected PII
    for package_name, group in package_groups:
        result_row = {'package_name': package_name}
        for pattern in regexes:
            column_name = f"detected_{pattern['name']}"
            column_name_out = f"detected_{tracker_string}_{pattern['name']}"
            # Calculate the count of distinct hosts where the PII pattern was detected
            pii_detected_hosts = group[group[column_name].astype(bool)]['remote_host'].nunique()
            result_row[column_name_out] = pii_detected_hosts
        result_rows.append(result_row)

    # Convert the list of dictionaries to a DataFrame
    result_df = pd.DataFrame(result_rows)

    # Set the column order as package_name followed by detected_ columns
    column_order = ['package_name'] + [f"detected_{tracker_string}_{pattern['name']}" for pattern in regexes]
    result_df = result_df[column_order]

    return result_df


def aggregate_pii_by_host(traffic, regexes):
    # Initialize an empty list to store the result rows
    result_rows = []

    # Group by remote_host
    host_groups = traffic.groupby('remote_host')

    # For each remote host, calculate the count of distinct package_names for detected PII
    for remote_host, group in host_groups:
        result_row = {'remote_host': remote_host, 'remote_domain': group['remote_domain'].iloc[0],
                      'is_tracker': group['is_tracker'].iloc[0]}
        for pattern in regexes:
            column_name = f"detected_{pattern['name']}"
            # Calculate the count of distinct package_names where the PII pattern was detected
            pii_detected_packages = group[group[column_name].astype(bool)]['package_name'].nunique()
            result_row[column_name] = pii_detected_packages
        result_rows.append(result_row)

    # Convert the list of dictionaries to a DataFrame
    result_df = pd.DataFrame(result_rows)

    # Set the column order as remote_host, is_tracker followed by detected_ columns
    column_order = ['remote_host', 'remote_domain', 'is_tracker'] + [f"detected_{pattern['name']}" for pattern in
                                                                     regexes]
    result_df = result_df.reindex(columns=column_order)

    return result_df


def aggregate_pii_by_domain(traffic, regexes):
    # Initialize an empty list to store the result rows
    result_rows = []

    # Group by remote_host
    domain_groups = traffic.groupby('remote_domain')

    # For each remote host, calculate the count of distinct package_names for detected PII
    for domain, group in domain_groups:
        result_row = {'remote_domain': domain, 'is_tracker': group['is_tracker'].iloc[0]}
        for pattern in regexes:
            column_name = f"detected_{pattern['name']}"
            # Calculate the count of distinct package_names where the PII pattern was detected
            pii_detected_packages = group[group[column_name].astype(bool)]['package_name'].nunique()
            result_row[column_name] = pii_detected_packages
        result_rows.append(result_row)

    # Convert the list of dictionaries to a DataFrame
    result_df = pd.DataFrame(result_rows)

    # Set the column order as remote_host, is_tracker followed by detected_ columns
    column_order = ['remote_domain', 'is_tracker'] + [f"detected_{pattern['name']}" for pattern in regexes]
    result_df = result_df.reindex(columns=column_order)

    return result_df


def is_ip_address(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def aggregate_data_safety_types(data_safety):
    # Set to store all unique data points
    all_data_points = set()

    # Iterate through each app entry
    for app in data_safety:
        # Aggregate shared data points
        for shared in app.get('shared_data', []):  # Default to empty list if key doesn't exist
            for data in shared.get('data', []):  # Default to empty list if key doesn't exist
                all_data_points.add(data['data'])  # Add the data point to the set

        # Aggregate collected data points
        for collected in app.get('collected_data', []):  # Default to empty list if key doesn't exist
            for data in collected.get('data', []):  # Default to empty list if key doesn't exist
                all_data_points.add(data['data'])  # Add the data point to the set

    return all_data_points


def aggregate_collected_data_types(data_safety):
    # Set to store all unique data points
    data_points = set()

    # Iterate through each app entry
    for app in data_safety:
        # Aggregate collected data points
        for collected in app.get('collected_data', []):  # Default to empty list if key doesn't exist
            for data in collected.get('data', []):  # Default to empty list if key doesn't exist
                data_points.add(data['data'])  # Add the data point to the set

    return data_points


def aggregate_shared_data_types(data_safety):
    # Set to store all unique data points
    data_points = set()

    # Iterate through each app entry
    for app in data_safety:
        # Aggregate shared data points
        for shared in app.get('shared_data', []):  # Default to empty list if key doesn't exist
            for data in shared.get('data', []):  # Default to empty list if key doesn't exist
                data_points.add(data['data'])  # Add the data point to the set

    return data_points


def to_snake_case(string):
    """Convert a string to snake_case."""
    return string.lower().replace(" ", "_").replace("-", "_").replace(".", "_")


def data_safety_to_dataframe(data_safety):
    # First, find all unique data points across all apps
    all_data_points = aggregate_data_safety_types(data_safety)

    # Initialize empty DataFrame with columns for pkg, data_deletable, data_encrypted, independently_reviewed
    df_cols = ['pkg', 'data_deletable', 'data_encrypted', 'independently_reviewed']
    df_cols += [f'collected_{point}' for point in all_data_points]
    df_cols += [f'shared_{point}' for point in all_data_points]
    apps_df = pd.DataFrame(columns=df_cols)

    # Iterate through each app in the data_safety list
    for app in data_safety:
        app_row = {col: False for col in df_cols}  # Initialize all data points to False
        app_row['pkg'] = app['pkg']
        app_row['data_deletable'] = app['data_deletable']
        app_row['data_encrypted'] = app['data_encrypted']
        app_row['independently_reviewed'] = app['independently_reviewed']

        # Mark collected data points as True
        for collected in app.get('collected_data', []):
            for data in collected.get('data', []):
                col_name = f'collected_{data["data"]}'
                app_row[col_name] = True

        # Mark shared data points as True
        for shared in app.get('shared_data', []):
            for data in shared.get('data', []):
                col_name = f'shared_{data["data"]}'
                app_row[col_name] = True

        # Append the app's row to the DataFrame
        app_df = pd.DataFrame([app_row], columns=df_cols)
        apps_df = pd.concat([apps_df, app_df], ignore_index=True)

    return apps_df
