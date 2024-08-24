import pandas as pd
import re
def preprocess(data):
    pattern = '\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s\w{2}\]'

    messages = re.split(pattern, data)[1:]  # splitting data based on data exluding first empty string

    dates = re.findall(pattern, data)
    dates = [date.strip("[]") for date in dates]

    df = pd.DataFrame({'user_message': messages, 'date': dates})

    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%y, %I:%M:%S %p')  # converting to datetime

    df['user_message'] = df['user_message'].str.lstrip(' ~')

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['min'] = df['date'].dt.minute

    return df