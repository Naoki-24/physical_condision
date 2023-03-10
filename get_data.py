import os
import pandas as pd

def reconstract_data(df):
    values = {
        'SpO2': 'average_value',
        'HeartRateVariability': ['rmssd', 'low_frequency', 'high_frequency'],
        'RespiratoryRate': [
            'full_sleep_breathing_rate',
            'full_sleep_standard_deviation',
            'full_sleep_signal_to_noise',
            'deep_sleep_breathing_rate',
            'deep_sleep_standard_deviation',
            'deep_sleep_signal_to_noise',
            'light_sleep_breathing_rate',
            'light_sleep_standard_deviation',
            'light_sleep_signal_to_noise',
            'rem_sleep_breathing_rate',
            'rem_sleep_standard_deviation',
            'rem_sleep_signal_to_noise',
        ],
        'EstimatedOxygenVariation': 'Infrared to Red Signal Ratio'
    }

def _get_raw_data(sid, feature_type):
    """
    csvファイルからデータ取得
    args:
     sid: 被験者id
     feature_type: 取得する特徴量
    return: 各特徴量のDataFrame
    """

    root_dir = './data'
    file_name = 'physical_'+feature_type+'.csv'
    raw_data_dir = os.path.join(root_dir, sid, file_name)
    df = pd.read_csv(raw_data_dir)

    df['id'] = sid
    _add_datetime(df)
    return df

def _add_datetime(data):
    """
    indexを日付に
    """

    if 'timestamp' in data.columns:
        time_stamp = 'timestamp'
    elif 'dateTime' in data.columns:
        time_stamp = 'dateTime'
    elif 'recorded_time' in data.columns:
        time_stamp = 'recorded_time'

    data['datetime'] = pd.to_datetime(data[time_stamp].apply(lambda x: x.split('T')[0]))
    data.set_index('datetime', inplace=True)

    return

def _calc_statistics(df):
    """
    日ごとの平均・分散・最大・最小を計算
    """
    data = df.resample('1D').agg(['mean', 'var', 'max', 'min'])
    return data

def main():
    sid = '10001'
    feature = 'DailyRespiratoryRate'
    raw_data = _get_raw_data(sid, feature)

    data = _calc_statistics(raw_data)
    print(data)


if __name__ == "__main__":
    main()