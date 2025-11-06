import os
import pandas as pd
import csv

def create_report_for_time_windows(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    windows = [1, 12, 24, 48, 72, 96]
    results = []

    total_opens = len(df[df['event'] == 'opened'])
    total_closes = len(df[df['event'] == 'closed'])

    for window_hours in windows:
        window_seconds = window_hours * 3600
        all_episodes_lists = df.groupby('user_id').apply(
            lambda user_df: match_events_mult_with_window(user_df, window_seconds), include_groups=False
        )
        all_episodes = all_episodes_lists.explode().dropna()
        cleaned_df = pd.DataFrame(all_episodes.to_list())

        matched_pairs = cleaned_df.shape[0]
        discarded_opens = total_opens - matched_pairs
        discarded_closes = total_closes - matched_pairs
        discarded_opens_percentage = (discarded_opens / total_opens) * 100
        discarded_closes_percentage = (discarded_closes / total_closes) * 100

        results.append({
            'time_window': window_hours,
            'discarded_opens': discarded_opens,
            'discarded_closes': discarded_closes,
            'discarded_opens_percentage': round(discarded_opens_percentage, 2),
            'discarded_closes_percentage': round(discarded_closes_percentage, 2),
            'matched_pairs': matched_pairs,
            'matched_pairs_percentage': round((matched_pairs / min(total_opens, total_closes)) * 100, 2)
        })
    with open(f"{output_dir}/time_window_analysis.csv", 'w',newline='') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        writer.writerows(results)


def match_events_mult_with_window(df, MAX_DURATION):
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
                    result.append({'open_type': cr_open[0].open_type, 'duration': length})
                    cr_open = cr_open[i + 1:]
                    valid_match_found = True
                    break
            if not valid_match_found:
                cr_open = []
    return result

if __name__ == "__main__":
    df=pd.read_csv('toolwindow_data.csv')
    df.sort_values(by=['timestamp', 'user_id'], ascending=True, inplace=True)
    create_report_for_time_windows(df, 'generated/csv')