import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import date


st.title('S&P 500 Stock Price App')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and shows the corresponding 
**stock closing price** for the companies. 
* **Python libraries:** streamlit, pandas, yfinance, numpy
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
""")

st.sidebar.header('Customize Stock Price')

# Get data using pandas
# and store it for later use
@st.cache_data
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection
sorted_sectors = sorted(df['GICS Sector'].unique())
selector_bar = st.sidebar.multiselect('Sector', sorted_sectors, help="Choose the sectors you want to generate the table for.")

# Generate data for the selected sectors
df_selected_sectors = df[df['GICS Sector'].isin(selector_bar)]

# Display the dataframe
st.header('Companies in the Selected Sectors')
if len(selector_bar) > 0:
    st.write('Table dimension: ' + str(df_selected_sectors.shape[0]) + 'x' + str(df_selected_sectors.shape[1]))
    st.dataframe(df_selected_sectors)

    symbols = list(df_selected_sectors['Symbol'])

    data = yf.download(
        tickers = symbols,
        period = 'ytd',
        interval = '1d',
        group_by = 'ticker',
        auto_adjust = True,
        threads = True,
        proxy = False
    )

    def price_plot(symbol, opt, start, end):
        # Get dataframe
        df = data[symbol]
        # Set the index
        df.set_index=('Date')
        df.index = pd.to_datetime(df.index)
        # Set the start and end date
        df2 = df.loc[start:end]
        st.line_chart(df2[opt]) # Side effect
        return df2

    # Select symbols
    sorted_symbols = sorted(symbols)
    symbol_bar = st.sidebar.multiselect('Symbols', sorted_symbols, help="Choose the symbols of the companies you want to generate stock prices for.")

    if(len(symbol_bar)) > 0:

        for symbol in symbol_bar:
            # options to customize
            st.sidebar.write(symbol)
            type_price = st.sidebar.selectbox('Type', ['Open', 'Close', 'High', 'Low', 'Volume'], index=0,
            help="What kind of price do you want to display?")
            start_date = st.sidebar.date_input('Start Date', value=date(date.today().year, 1, 1), min_value=date(2015, 1, 1), max_value=date.today(), help="From what date do you want to generate the stock price?")
            end_date = st.sidebar.date_input('End Date', value="today", min_value=date(2015, 1, 1), max_value=date.today(), help="To what date do you want to generate the stock price?")
            # Plot the graphs for the chosen symbols
            st.subheader(f'{type_price} stock price for {symbol}')
            price_plot(symbol, type_price, start_date, end_date)

    else:
        st.write('Generate customized stock prices for companies by selecting symbols in the sidebar on the left. The prices are in (year-to-date) format.')

else:
    st.write('No sectors have been selected. Use the side bar on the left side to select sectors.')
