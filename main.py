import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import csv
import datetime
from scipy.stats import mannwhitneyu
palette = {
    'manual': sns.color_palette()[1],
    'auto': sns.color_palette()[0],
}
MAX_DURATION = 24 * 3600


def analyze_duration_stats(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "duration_analysis.txt")

    manual = df[df['open_type'] == 'manual']['duration'].dropna()
    auto = df[df['open_type'] == 'auto']['duration'].dropna()

    summary = df.groupby('open_type')['duration'].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.99])

    stat, p_value = mannwhitneyu(manual, auto, alternative='two-sided')

    rbc = 1 - (2 * stat) / (len(manual) * len(auto))


    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Summary Statistics by open_type\n\n")
        f.write(summary.to_string())
        f.write("\n\n")

        f.write("=== Mann–Whitney U Test ===\n")
        f.write(f"U statistic: {stat:.2f}\n")
        f.write(f"P-value: {p_value:.4e}\n")
        f.write(f"Effect size: {rbc:.3f}\n")



def match_events_mult(df):
    cr_open=[]
    result=[]
    for row in df.itertuples():
        if row.event == 'opened':
            cr_open.append(row)
        if row.event == 'closed':
            valid_match_found=False
            for i, open_event in enumerate(cr_open):
                length = (row.timestamp - open_event.timestamp) / 1000
                if length < MAX_DURATION:
                    result.append({'open_type': cr_open[0].open_type, 'duration': length, 'user_id': cr_open[0].user_id})
                    cr_open = cr_open[i + 1:]
                    valid_match_found = True
                    break
            if not valid_match_found:
                cr_open = []
    return result

def get_stats_for_dataframe(df, stage_name):
    total_size = df.shape[0]
    if 'open_type' in df.columns:
        open_type_counts = df['open_type'].value_counts()
        manual_count = open_type_counts.get('manual', 0)
        auto_count = open_type_counts.get('auto', 0)
    else:
        manual_count = auto_count  = 0

    return {
        'stage_name': stage_name,
        'total_records': total_size,
        'manual_count': manual_count,
        'auto_count': auto_count,
    }


def process_data(data_url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    csv_entries=[]
    df= pd.read_csv(data_url)
    csv_entries.append(get_stats_for_dataframe(df, "initial_dataframe"))
    df.drop_duplicates(inplace=True)
    csv_entries.append(get_stats_for_dataframe(df, "delete_duplicates"))
    df= df.sort_values(['user_id','timestamp'], ascending=True)
    all_episodes_lists= df.groupby('user_id').apply(match_events_mult, include_groups=True)
    all_episodes = all_episodes_lists.explode().dropna()
    cleaned_df= pd.DataFrame(all_episodes.to_list())
    csv_entries.append(get_stats_for_dataframe(cleaned_df, "final_dataframe"))
    output_file="datasets_stats.csv"
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(f"{output_dir}/{output_file}", 'w',newline='') as csvfile:
        fieldnames = csv_entries[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        writer.writerows(csv_entries)
    return cleaned_df

def draw_plots_og_dataset(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df= pd.read_csv(file_path)
    df = df.dropna(subset=['open_type'])
    plt.figure(figsize=(6,6))
    plt.title('Count by open_type original')
    sns.countplot(x='open_type', hue='open_type', data=df, order=['manual', 'auto'], palette=palette)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/og_count_by_open_type.png")
    plt.close()

def draw_plots(df, dir_name):
    os.makedirs(dir_name, exist_ok=True)


    plt.figure(figsize=(6, 6))
    plt.title("Count by open_type processed")
    sns.countplot(x='open_type', hue='open_type' ,data=df, order=['manual', 'auto'], palette=palette)
    plt.tight_layout()
    plt.savefig(f"{dir_name}/count_by_open_type.png")
    plt.close()


    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12,6))
    plt.suptitle("Boxplot by open_type")
    ax1.set_title('showFliers=true')
    ax2.set_title('showFliers=false')
    sns.set_color_codes("pastel")
    sns.boxplot(y='duration', x='open_type', hue='open_type', data=df, showfliers=True, ax=ax1)
    sns.boxplot(y='duration', x='open_type', hue='open_type', data=df, showfliers=False, ax=ax2 )
    plt.savefig(f"{dir_name}/boxplot.png")
    plt.close()




    user_stats = df.groupby(['user_id', 'open_type'])['duration'].agg(['count', 'median'])
    user_stats = user_stats.reset_index()

    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 6))
    plt.suptitle("Median durations per user")
    ax1.set_title('showFliers=true')
    ax2.set_title('showFliers=false')
    sns.boxplot(x='open_type', y='median', hue='open_type', hue_order=['manual', 'auto'], data=user_stats, showfliers=True, ax=ax1, palette=palette)
    sns.boxplot(x='open_type', y='median', hue='open_type', hue_order=['manual', 'auto'], data=user_stats, showfliers=False, ax=ax2, palette=palette)
    plt.savefig(f"{dir_name}/boxplot_user_median.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(data=df, x='duration', hue='open_type', log_scale=True)
    plt.title("Histogram of duration log scale")
    plt.savefig(f"{dir_name}/histplot_log_scale.png")
    plt.tight_layout()
    plt.close()



if __name__ == "__main__":
    gen_dir="generated"
    df=process_data("toolwindow_data.csv", f'{gen_dir}/csv')
    draw_plots_og_dataset("toolwindow_data.csv", f"{gen_dir}/orinal_dataset")
    draw_plots(df, f'{gen_dir}/processed_dataset')
    analyze_duration_stats(df,gen_dir)

