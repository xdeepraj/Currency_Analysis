import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd



# Function to fetch filtered_data from yahoo finance
def fetch_data(currency="EURINR=X", start_date="2023-01-01", end_date="2023-12-15"):
    filtered_data = yf.download(currency, start_date, end_date)
    filtered_data.reset_index(inplace=True)
    return filtered_data


# Function to perform technical analysis
def technical_analysis(filtered_data, window = 5):
    
    # Calculate SMA
    filtered_data[f'sma_{window}d'] = filtered_data['Close'].rolling(window, min_periods=1).mean()
    
    # Calculate Standard Deviation, Upper band & Lower band
    if window == 1:
        filtered_data[f'sd_{window}d'] = 0  # Set standard deviation to Close values for window=1
    else:
        filtered_data[f'sd_{window}d'] = filtered_data['Close'].rolling(window, min_periods=1).std()
 
    filtered_data[f'ub_{window}d'] = filtered_data[f'sma_{window}d'] + 2 * filtered_data[f'sd_{window}d']
    filtered_data[f'lb_{window}d'] = filtered_data[f'sma_{window}d'] - 2 * filtered_data[f'sd_{window}d']

    # Calculate CCI
    typical_price = (filtered_data['High'] + filtered_data['Low'] + filtered_data['Close']) / 3
    sma_typical_price = typical_price.rolling(window, min_periods=1).mean()
    mean_deviation = abs(typical_price - sma_typical_price).rolling(window, min_periods=1).mean()
    filtered_data[f'cci_{window}d'] = (typical_price - sma_typical_price) / (0.015 * mean_deviation)

    # Fill NaN values with 0
    filtered_data.fillna(0, inplace = True)


# Function to visualize data using graph
def show_data(filtered_data, window, currency="EURINR=X"):
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(12, 8))

    # Plot Closing Price
    plt.subplot(3, 1, 1)
    plt.plot(filtered_data['Close'], label='Close Price')
    plt.title(f'"{currency}" Closing Price for {window}d')

    # Plot Moving Average
    plt.subplot(3, 1, 2)
    plt.plot(filtered_data['Close'], label='Close Price')
    plt.plot(filtered_data[f'sma_{window}d'], label='Moving Average', color='orange')
    plt.title(f'"{currency}" Moving Average for {window}d')

    # Plot Bollinger Bands
    plt.subplot(3, 1, 3)
    plt.plot(filtered_data['Close'], label='Close Price')
    plt.plot(filtered_data[f'ub_{window}d'], label='Upper Band', color='red', linestyle='--')
    plt.plot(filtered_data[f'sma_{window}d'], label='Middle Band', color='orange')
    plt.plot(filtered_data[f'lb_{window}d'], label='Lower Band', color='green', linestyle='--')
    plt.title(f'"{currency}" Bollinger Bands for {window}d')

    plt.tight_layout(pad=2.0, h_pad=1.0)
    plt.show()

    # Plot Commodity Channel Index (CCI)
    plt.figure(figsize=(12, 4))
    plt.plot(filtered_data.index, filtered_data[f'cci_{window}d'], label='CCI', color='purple')
    plt.axhline(100, color='red', linestyle='--', label='Overbought (CCI > 100)')
    plt.axhline(-100, color='green', linestyle='--', label='Oversold (CCI < -100)')
    plt.title(f'"{currency}" Commodity Channel Index (CCI) for {window}d')
    
    plt.legend()
    plt.show()


# Making a combined decision using SMA, Bollinger Band & CCI
def combined_trading_decision(row, filtered_data, window):
    if (row > filtered_data[f'sma_{window}d'].iloc[-1]) and (row <= filtered_data[f'lb_{window}d'].iloc[-1]) and ((filtered_data[f'cci_{window}d'] > -100) and (filtered_data[f'cci_{window}d'].shift(1) <= -100)):
        return 'BUY'
    elif (row < filtered_data[f'sma_{window}d'].iloc[-1]) and (row >= filtered_data[f'ub_{window}d'].iloc[-1]) and ((filtered_data[f'cci_{window}d'] > 100) and (filtered_data[f'cci_{window}d'].shift(1) <= 100)):
        return 'SELL'
    else:
        return 'NEUTRAL'


# Making individual decision using SMA
def sma_trading_decision(row, filtered_data, window):
    if row > filtered_data[f'sma_{window}d'].iloc[-1]:
        return 'BUY'
    elif row < filtered_data[f'sma_{window}d'].iloc[-1]:
        return 'SELL' 
    else:
        return 'NEUTRAL'
    

# Making individual decision using Bollinger Band
def bb_trading_decision(row, filtered_data, window):
    if row >= filtered_data[f'ub_{window}d'].iloc[-1]:
        return 'SELL'
    elif row <= filtered_data[f'lb_{window}d'].iloc[-1]:
        return 'BUY'
    else:
        return 'NEUTRAL'
    

# Making individual decision using CCI
def cci_trading_decision(row, filtered_data, window):
    cci_value = row
    previous_cci_value = filtered_data[f'cci_{window}d'].shift(1).iloc[-1]
    if (cci_value > -100) and (previous_cci_value <= -100) :
        return 'BUY'
    elif (cci_value > 100) and (previous_cci_value <= 100) :
        return 'SELL'
    else:
        return 'NEUTRAL'
        


# Main function
def main():
    currency = "EURINR=X"

    start_date = "2023-01-01"
    end_date = "2023-12-15"
    target_day = "2023-12-07"

    window_one_day = 1
    window_one_week = 5
    
    
    # Fetching data from Yahoo Finance for timeframe "2023-01-01" to "2023-12-07"
    filtered_data = fetch_data(currency, start_date, end_date)

    # Performing technical analysis for one day and one week
    technical_analysis(filtered_data, window_one_day)
    technical_analysis(filtered_data, window_one_week)

    # Extracting data from filtered_data dataset for mentioned week
    filtered_data = filtered_data[(filtered_data['Date'] >= target_day) & (filtered_data['Date'] <= end_date)]
    
    # Visualizing the filtered_data
    show_data(filtered_data, window_one_day, currency)
    show_data(filtered_data, window_one_week, currency)


    # Making a combined trading decisions using SMA, Bollinger Band & CCI
    filtered_data['combined_decision_1d'] = filtered_data['Close'].apply(
        lambda row: combined_trading_decision(row, filtered_data, window=window_one_day)
    )
    filtered_data['combined_decision_5d'] = filtered_data['Close'].apply(
        lambda row: combined_trading_decision(row, filtered_data, window=window_one_week)
    )


    # Making trading decisions using SMA  
    filtered_data['sma_decision_1d'] = filtered_data['Close'].apply(
        lambda row: sma_trading_decision(row, filtered_data, window=window_one_day)
    )
    filtered_data['sma_decision_5d'] = filtered_data['Close'].apply(
        lambda row: sma_trading_decision(row, filtered_data, window=window_one_week)
    )

    # Making trading decisions using Bollinger Band  
    filtered_data['bb_decision_1d'] = filtered_data['Close'].apply(
        lambda row: bb_trading_decision(row, filtered_data, window=window_one_day)
    )
    filtered_data['bb_decision_5d'] = filtered_data['Close'].apply(
        lambda row: bb_trading_decision(row, filtered_data, window=window_one_week)
    )

    # Making trading decisions using CCI  
    filtered_data['cci_decision_1d'] = filtered_data['cci_1d'].apply(
        lambda row: cci_trading_decision(row, filtered_data, window=window_one_day)
    )
    filtered_data['cci_decision_5d'] = filtered_data['cci_5d'].apply(
        lambda row: cci_trading_decision(row, filtered_data, window=window_one_week)
    )

    # Storing the dataframe with trading decisions in a excel file
    filtered_data.to_excel('output.xlsx', index=False)




if __name__ == "__main__":
    main()