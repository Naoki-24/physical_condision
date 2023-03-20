import os
import pandas as pd

def feature_list():
    """
    return: 特徴量のリスト
    """
    features = [
        'SpO2', 
        'HeartRateVariability', 
        'RespiratoryRate',
        'EstimatedOxygenVariation',
        'HeartRate_all',
        'WristTemperature_all',
        'steps_all'
    ]
    return features

def id_list():
    """
    return: 被験者idのリスト
    """
    ids = ['10001', '10007', '10009', '10010', '10019', '10023', '10024', '30020', '30021']
    return ids

def _needed_values(feature):
    """
    return 必要な項目のリスト
    """
    values = {
        'SpO2': ['average_value', 'lower_bound', 'upper_bound'],
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
        'HeartRate_all': ['value.bpm', 'state'],
        'EstimatedOxygenVariation': 'Infrared to Red Signal Ratio',
        'WristTemperature_all': ['temperature', 'state'],
        'steps_all': ['value', 'state'],
    }
    return values[feature]

def _to_datetime_index(data):
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
    data.pop(time_stamp)
    return

def _get_raw_data(sid, feature):
    """
    csvファイルからデータ取得
    args:
     sid: 被験者id
     feature_type: 取得する特徴量
    return: 各特徴量のDataFrame
    """

    # データが格納されているディレクトリのパス
    root_dir = './raw_data'

    file_name = 'physical_'+feature+'.csv'

    # root_dir/sid(id)/physical_feature.csv
    raw_data_dir = os.path.join(root_dir, sid, file_name)
    df = pd.read_csv(raw_data_dir)

    _to_datetime_index(df)
    df = df[_needed_values(feature)]
    return df

def _is_statistics(feature):
    """
    return: 統計量の計算が必要か否か(bool)
    """
    is_statics_dict = {
        "SpO2": False,
        "HeartRateVariability": False,
        "RespiratoryRate": False,
        "EstimatedOxygenVariation": False,
        "HeartRate_all": True,
        "WristTemperature_all": True,
        "steps_all": True
    }

    return is_statics_dict[feature]

def _separate_state(raw_data):
    """
    stateによってデータを分割
    return: normal, exercize, sleep (DataFrame)
    """
    states = raw_data.groupby('state')

    normal = states.get_group(0)
    exercize = states.get_group(1)
    sleep = states.get_group(2)

    normal.pop('state')
    exercize.pop('state')
    sleep.pop('state')

    return normal, exercize, sleep

def _calc_statistics(df):
    """
    日ごとの平均・分散・最大・最小を計算
    """
    data = df.resample('1D').agg(['mean', 'var', 'max', 'min'])
    return data

def save_csv(sid, df):
    """
    特徴量をcsvで保存
    """
    root_dir = './extracted_features'
    file_name = f'features_{sid}.csv'

    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    saved_path = os.path.join(root_dir, file_name)

    df.to_csv(saved_path)

def get_statistics():
    """
    被験者の特徴量（統計量）を取得
    """
    sids = id_list()
    features = feature_list()

    data_list = []
    for sid in sids:
        print(f'shaping: {sid} data')
        for feature in features:
            raw_data = _get_raw_data(sid, feature)
            
            if _is_statistics(feature):
                normal, exercise, sleep = _separate_state(raw_data)
                
                normal = _calc_statistics(normal)
                exercise = _calc_statistics(exercise)
                sleep = _calc_statistics(sleep)

                data = pd.concat([normal, exercise, sleep], axis=1)

            else:
                data = raw_data

            data = data.loc[~data.index.duplicated(keep='first')]
            data_list.append(data)

        data_df = pd.concat(data_list, axis=1)
        print(data_df.head())
        save_csv(sid, data_df)

if __name__ == "__main__":
    get_statistics()