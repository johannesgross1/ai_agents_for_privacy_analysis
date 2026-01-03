import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sns


def pii_transmission_plot(data_source, column_name, x_label):
    # Apply Seaborn style for aesthetic improvements
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'Linux Libertine'

    data_types = data_source[column_name].unique()
    categories = ['auto', 'manual']
    sub_categories = ['non_tracker', 'tracker']
    custom_labels = ['Automated crawl, transmitted to Non-Tracker', 'Automated crawl, transmitted to Tracker',
                     'Interactive crawl, transmitted to Non-Tracker', 'Interactive crawl, transmitted to Tracker']
    colors = ['lightblue', 'lightcoral', 'blue', 'orange']

    # Create custom legend handles
    #custom_handles = [mpatches.Patch(label=custom_labels[i]) for i in range(len(custom_labels))]

    # Initialize a figure
    plt.figure(figsize=(16, 6))

    # Positions of the bars on the x-axis
    ind = np.arange(len(data_types))
    width = 0.25  # Width of a bar

    for i, category in enumerate(categories):
        bar_positions = ind + i * width
        bottoms = np.zeros(len(data_types))

        for j, sub_category in enumerate(sub_categories):
            values = data_source[f'{category}_{sub_category}'].values
            plt.bar(bar_positions, values, width, bottom=bottoms, label=f'{category} {sub_category}',
                    #color=colors[i * 2 + j]
                    )
            bottoms += values

    # Adding some aesthetics
    plt.xlabel(x_label)
    plt.ylabel('Number of transmitting apps')
    plt.title(
        'Number of apps that transmitted PHI by data type and tracker classification of remote hosts, comparing the three crawls')
    plt.xticks(ind + width, data_types, rotation=90)
    handles, labels = plt.gca().get_legend_handles_labels()
    # Assuming you have 6 unique combinations as per custom_labels, and they are in the correct order
    # If not, you may need to sort or manually adjust this
    adjusted_handles = [handles[i] for i in range(len(custom_labels))]
    plt.legend(adjusted_handles, custom_labels, loc='best')
    plt.tight_layout()

    return plt


def pii_transmission_plot_manual(data_source, column_name, x_label):
    # Apply Seaborn style for aesthetic improvements
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'Linux Libertine'

    data_types = data_source[column_name].unique()
    categories = ['auto', 'manual']
    sub_categories = ['non_tracker', 'tracker']
    custom_labels = ['2022 Interactive crawl, transmitted to Non-Tracker', '2022 Interactive crawl, transmitted to Tracker',
                     '2024 Interactive crawl, transmitted to Non-Tracker', '2024 Interactive crawl, transmitted to Tracker']
    colors = ['lightblue', 'lightcoral', 'blue', 'orange', 'cyan', 'yellow']

    # Create custom legend handles
    #custom_handles = [mpatches.Patch(label=custom_labels[i]) for i in range(len(custom_labels))]

    # Initialize a figure
    plt.figure(figsize=(16, 6))

    # Positions of the bars on the x-axis
    ind = np.arange(len(data_types))
    width = 0.25  # Width of a bar

    for i, category in enumerate(categories):
        bar_positions = ind + i * width + (0.5 * width)
        bottoms = np.zeros(len(data_types))

        for j, sub_category in enumerate(sub_categories):
            values = data_source[f'{category}_{sub_category}'].values
            plt.bar(bar_positions, values, width, bottom=bottoms, label=f'{category} {sub_category}',
                    #color=colors[i * 2 + j]
                    )
            bottoms += values

    # Adding some aesthetics
    plt.xlabel(x_label)
    plt.ylabel('Number of transmitting apps')
    plt.title(
        'Number of apps that transmitted PHI by data type and tracker classification of remote hosts, comparing the three crawls')
    plt.xticks(ind + width, data_types, rotation=90)
    handles, labels = plt.gca().get_legend_handles_labels()
    # Assuming you have 6 unique combinations as per custom_labels, and they are in the correct order
    # If not, you may need to sort or manually adjust this
    adjusted_handles = [handles[i] for i in range(len(custom_labels))]
    plt.legend(adjusted_handles, custom_labels, loc='best')
    plt.tight_layout()

    return plt
