import pandas as pd


def transform_traffic_combined_apps(traffic_combined, pre1, pre2, pre3=None):
    series = traffic_combined.drop('package_name', axis=1).sum().filter(regex='_detected_')
    numeric_cols = [pre1 + '_non_tracker', pre1 + '_tracker',
                    pre2 + '_non_tracker', pre2 + '_tracker']

    if pre3:
        numeric_cols += [pre3 + '_non_tracker', pre3 + '_tracker']

    df_cols = ['data_type'] + numeric_cols

    rows_dict = {}

    for index, value in series.items():
        # Split the index and determine the base parts (auto/manual and tracker/non_tracker)
        parts = index.split('_')
        detection_method = parts[0]  # 'auto' or 'manual'
        if parts[2] == 'non':  # We have a 'non_tracker' case
            detection_category = 'non_tracker'
            data_type_parts = parts[4:]  # Data type starts from the 5th part onwards
        else:  # We have a 'tracker' case
            detection_category = 'tracker'
            data_type_parts = parts[3:]  # Data type starts from the 4th part onwards

        data_type = '_'.join(data_type_parts)
        column_name = f"{detection_method}_{detection_category}"

        # Initialize or update the row for the data_type
        if data_type not in rows_dict:
            rows_dict[data_type] = {col: pd.NA for col in df_cols}
            rows_dict[data_type]['data_type'] = data_type
        rows_dict[data_type][column_name] = value

    # Create DataFrame from rows_dict
    df = pd.DataFrame(list(rows_dict.values()), columns=df_cols)

    # Convert numeric columns to appropriate type

    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    return df


def aggregate_data_types(data_types_combined, r_combined, mapping_target: str):
    data_types_combined = data_types_combined.copy()
    # Strip the mapping_target string to remove leading/trailing whitespaces or hidden characters
    mapping_target_clean = mapping_target.strip()

    # Create data_type to target mapping
    data_type_to_target = {d['name']: d[mapping_target_clean] for d in r_combined}

    # Map data_type to target in the DataFrame
    data_types_combined[mapping_target_clean] = data_types_combined['data_type'].map(data_type_to_target)

    # Aggregate by target
    aggregated_by_target = data_types_combined.groupby(mapping_target_clean).sum()

    # Drop the data_type column from aggregation, if present
    aggregated_by_target.drop(columns=['data_type'], errors='ignore', inplace=True)

    # Reset the index to make the mapping_target a column
    aggregated_by_target = aggregated_by_target.reset_index()

    return aggregated_by_target
