import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as font_manager
import seaborn as sns
import os
import pandas as pd


#This method loads the Linux Libertine font from the fonts/linux_libertine folder.
def _load_linux_libertine_font():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    font_dir = os.path.join(project_root, "fonts", "linux_libertine")
    
    if os.path.exists(font_dir):
        font_files = font_manager.findSystemFonts(fontpaths=[font_dir])
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)
        return True
    return False

#This method plots a diverging bar chart (Evaluation 6.1)
def plot_horizobtal_diverging_bars(data, category_col='Category', value_col='Difference',
                        title='Diverging Bar Chart: AI vs. Regex Total Detection Count',
                        x_label='Category', 
                        y_label='Difference (AI Count - Regex Count)', 
                        save_pdf=True, pdf_filename='diverging_bars'):
    sns.set_theme(style="whitegrid")
    _load_linux_libertine_font()
    plt.rcParams['font.family'] = 'Linux Libertine'
    data_sorted = data.sort_values(value_col, ascending=False)
    data_sorted['Dominant_Method'] = data_sorted[value_col].apply(
        lambda x: 'AI detected more' if x >= 0 else 'Regex detected more'
    )
    plt.figure(figsize=(max(10, len(data_sorted) * 0.3), 6))
    ax = sns.barplot(
        x=category_col,     # categories on x axis
        y=value_col,        # values on y axis
        data=data_sorted,
        hue='Dominant_Method',
        dodge=False,
        palette={'AI detected more': '#4c72b0', 'Regex detected more': '#c44e52'} 
    )
    plt.axhline(0, color='black', linewidth=1.2, linestyle='-')
    plt.title(title, fontsize=14, pad=20)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Difference Direction', loc='upper right')
    plt.tight_layout()  
    if save_pdf:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        figures_dir = os.path.join(project_root, 'figures', 'thesis')
        os.makedirs(figures_dir, exist_ok=True)
        pdf_path = os.path.join(figures_dir, f"{pdf_filename}.pdf")
        plt.savefig(pdf_path, bbox_inches='tight', format='pdf')
        print(f"Plot saved: {pdf_path}")
    return plt

def plot_overlap_comparison(data, category_name, filename=None, save_pdf=True):
    sns.set_theme(style="whitegrid")
    _load_linux_libertine_font()
    plt.rcParams['font.family'] = 'Linux Libertine'
    if filename is None:
        filename = f"overlap_{category_name.lower().replace(' ', '_')}"
    regex_col = f"detected_{category_name}"
    ai_col = f"ai_detected_{category_name}"

    if regex_col not in data.columns or ai_col not in data.columns:
        print(f"Warnung: Spalten für {category_name} nicht gefunden.")
        return None
    both = ((data[regex_col] == True) & (data[ai_col] == True)).sum()
    regex_only = ((data[regex_col] == True) & (data[ai_col] == False)).sum()
    ai_only = ((data[regex_col] == False) & (data[ai_col] == True)).sum()
    regex_total = both + regex_only
    ai_total = both + ai_only
    total_any = both + regex_only + ai_only
    plot_data = pd.DataFrame({
        'Subset': ['Regex only', 'Both', 'AI only'],
        'Count': [regex_only, both, ai_only]
    })
    table_data = [
        ['Total Detections', regex_total, ai_total],
        ['Unique (Exclusive)', regex_only, ai_only],
        ['Share of Total (%)', 
         f"{regex_total/total_any*100:.1f}%" if total_any else "0%", 
         f"{ai_total/total_any*100:.1f}%" if total_any else "0%"]
    ]
    table_cols = ['Metric', 'Regex', 'AI']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={'width_ratios': [1.5, 1]})
    colors = ['#c44e52', '#55a868', '#4c72b0'] # same ones as in the diverging bar chart
    sns.barplot(x='Subset', y='Count', data=plot_data, ax=ax1, palette=colors)
    ax1.set_title(f'Overlap Analysis: {category_name}', pad=15, fontsize=12, fontweight='bold')
    ax1.set_xlabel('')
    ax1.set_ylabel('Number of Requests')
    for i, v in enumerate(plot_data['Count']):
        ax1.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
    ax2.axis('off')
    table = ax2.table(
        cellText=table_data, 
        colLabels=table_cols, 
        cellLoc='center', 
        loc='center',
        colWidths=[0.4, 0.3, 0.3]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8) 
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#e6e6e6')
        elif col == 0: 
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#f9f9f9')
    plt.tight_layout()
    if save_pdf:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        figures_dir = os.path.join(project_root, 'figures', 'thesis')
        os.makedirs(figures_dir, exist_ok=True)
        pdf_path = os.path.join(figures_dir, f"{filename}.pdf")
        plt.savefig(pdf_path, bbox_inches='tight', format='pdf')
        print(f"Plot saved: {pdf_path}")
    return plt



########################################This method was partially generated with the help of cursor AI feature##############################################
def analyze_category(df, category, mode="ai_only", sample_size=20, random_seed=42, show_full_body=False):    
    regex_col = f"detected_{category}"
    ai_col = f"ai_detected_{category}"
    reasoning_col = f"ai_reasoning_{category}"
    val_reasoning_col = f"ai_validation_reasoning_{category}"
    content_col = 'request_content'
    if mode == "ai_only":
        subset_df = df[(df[regex_col] == False) & (df[ai_col] == True)]
        title = f"AI-Only Detections (AI=True, Regex=False)"
    elif mode == "regex_only":
        subset_df = df[(df[regex_col] == True) & (df[ai_col] == False)]
        title = f"Regex-Only Detections (Regex=True, AI=False)"
    else:
        print(f"Error: {mode}")
        return
    print(f"\n=== Qualitative Analysis of Sample in Category: {category} ===")
    print(f"Mode: {title}")
    print(f"Total detections: {len(subset_df)}")
    
    if len(subset_df) > 0:
        n = min(len(subset_df), sample_size)
        sample_df = subset_df.sample(n=n, random_state=random_seed).copy()        
        display_data = []
        for idx, row in sample_df.iterrows():
            content_full = str(row[content_col])
            if show_full_body:
                content_display = content_full
            else:
                content_display = content_full[:300] + "..." if len(content_full) > 300 else content_full
            display_data.append({
                'Index': idx,
                'App': row['package_name'],
                'Host': row['remote_host'],
                'AI Reasoning': row[reasoning_col] if pd.notna(row[reasoning_col]) else "N/A",
                'Validation Reasoning': row[val_reasoning_col] if val_reasoning_col in row and pd.notna(row[val_reasoning_col]) else None,
                'Body Content': content_display
            })
        
        display_df = pd.DataFrame(display_data)
        
        with pd.option_context('display.max_colwidth', None):
            display(display_df)
            
    else:
        print("No results found for this category and mode")
###################until this part for debugging of this method, cursor was used to generate parts of the ##############################################


def plot_summary_table(data, filename='summary_table', save_pdf=True):
    sns.set_theme(style="white")
    _load_linux_libertine_font()
    plt.rcParams['font.family'] = 'Linux Libertine'
    df = data.copy()
    df = df.rename(columns={
        'Pattern': 'Category',
        'Regex Detections': 'Regex',
        'AI Detections': 'AI',
        'Differenz': 'Diff (Abs)'
    })  
    df['Total'] = df['AI'] + df['Regex']
    df['Diff (%)'] = df.apply(
        lambda x: round((x['Diff (Abs)'] / x['Total'] * 100), 1) if x['Total'] > 0 else 0, 
        axis=1
    )   
    df = df.sort_values('Diff (%)', ascending=False)    
    plot_data = df[['Category', 'Regex', 'AI', 'Diff (Abs)', 'Diff (%)']]
    fig, ax = plt.subplots(figsize=(10, len(df) * 0.35 + 1))
    ax.axis('off')

    col_widths = [0.3, 0.175, 0.175, 0.175, 0.175]
    table = ax.table(
        cellText=plot_data.values, 
        colLabels=plot_data.columns, 
        cellLoc='center', 
        loc='center',
        colWidths=col_widths
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#e6e6e6')
            cell.set_linewidth(1.5)
        elif row % 2 == 0:
            cell.set_facecolor('#f8f9fa')
        else:
            cell.set_facecolor('white')
    if save_pdf:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        figures_dir = os.path.join(project_root, 'figures', 'thesis')
        os.makedirs(figures_dir, exist_ok=True)
        pdf_path = os.path.join(figures_dir, f"{filename}.pdf")
        plt.savefig(pdf_path, bbox_inches='tight', format='pdf')
        print(f"Tabelle saved: {pdf_path}")
    return plt