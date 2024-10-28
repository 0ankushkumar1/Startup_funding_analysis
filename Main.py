import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# Data Cleaning and Pre-processing

df = pd.read_csv("startup_funding.csv")
# Renaming Columns
df.rename(columns={"Date dd/mm/yyyy":"Date",
                   "InvestmentnType":"Investment Type",
                   "City  Location":"City",
                   "SubVertical":"Sub vertical"                  
                   },inplace=True)
df.drop(columns=['Remarks'],inplace=True)

# Processing Dates
df["Date"].replace({'05/072018':'05/07/2018'})
df.loc[[2606,3029,192,2571],"Date"]=['10/7/2015','22/01/2015','05/07/2018','01/07/2015']
df['Date'] = pd.to_datetime(df['Date'],format='mixed')
df['Date'] = df['Date'].dt.date
# Processing Textual Data
df["Startup Name"] = df["Startup Name"].str.replace('https://www.','').str.replace('.in','').str.replace('/','').str.strip().str.lower().str.split('  ').str[0].str.replace('.com','').str.capitalize()
df.fillna({'Industry Vertical': 'Others', 'Sub vertical': 'Others', 'City': 'N/A'}, inplace=True)
df["Investment Type"] = df["Investment Type"].str.lower().str.strip()
df["Investment Type"].replace({'seed':'seed round',
                               'single venture':'seed round',
                               'pre-series a':'seed round',
                               'seed funding':'seed round',
                               'maiden round':'seed round',
                               'funding round':'seed round',
                               'seed funding round':'seed round',
                               'seed\\\\nfunding':'seed round',
                               'angel / seed funding':'angel/seed funding',
                               'seed / angel funding':'angel/seed funding',
                               'private equity round':'private equity',
                               'private funding':'private equity',
                               'privateequity':'private equity',
                               'private\\\\nequity':'private equity',
                               'equity':'private equity',
                               'equity based funding':'private equity',
                               'corporate round':'series a',
                               'angel funding':'angel',
                               'single venture':'venture',
                               'venture round':'venture',
                               'venture - series unknown':'venture'
                               },inplace=True)
df["Investment Type"].fillna('N/A',inplace=True)
df["Investment Type"]=df["Investment Type"].str.capitalize()
df["Industry Vertical"].replace({'E-commerce':'E-Commerce',
                                 'eCommece':'E-Commerce',
                                 'Ecommerce':'E-Commerce',
                                 'ECommerce':'E-Commerce',
                                 'eCommerce':'E-Commerce',
                                 'Health and wellness':'Health and Wellness',
                                 'Tele-Shopping / eCommerce':'E-Commerce',
                                 'E-Tech':'Ed-Tech',
                                 'Ed-tech':'Ed-Tech',
                                 'Fiinance':'Finance',
                                 'Financial Markets Software':'Fin-Tech',
                                 'Consumer Interne':'Consumer Internet',
                                 'Financial Tech':'Fin-Tech',
                                 'Services Platform':'Saas',      
                                 },inplace=True)

df['City'] = df['City'].apply(lambda x : x.split('/')[0] if isinstance(x,str) and  '/' in x else x)
df['City'] = df['City'].str.strip().apply(lambda x : x.split('0')[1] if  isinstance(x,str) and'0' in x else x)
df['City'].replace({'Gurgaon':'Gurugram',
                    'Nw Delhi':'New Delhi',
                    'Delhi': 'New Delhi',
                    'N':'Other',
                    'USA':'US',
                    'Bangalore':'Bengaluru'
                    },inplace=True)

df['Investors Name'] = df['Investors Name'].str.strip().fillna('Undisclosed')
df['Amount in USD']=df['Amount in USD'].str.replace(r'[^0-9]','',regex=True).str.strip()
df['Amount in USD'] = pd.to_numeric(df['Amount in USD'],errors ='coerce')
df['Amount in USD'] = df['Amount in USD'].fillna(0).astype(int)
def convert_to_readable(amount):
    if amount >= 10**7:  # 1 crore = 10 million
        return f"{amount / 10**7:.1f} crores"
    elif amount >= 10**5:  # 1 lakh = 100,000
        return f"{amount / 10**5:.1f} lakhs"
    else:
        return f"{amount} Rs"
df["Amount in Rs."] = (df['Amount in USD']*84.08).apply(convert_to_readable)

# Unique Investors
unique_investors = pd.Series([investor.strip() for sublist in df["Investors Name"] for investor in (sublist if isinstance(sublist, list) else [sublist])]).unique().tolist()


st.sidebar.title("Startup Funding Analysis")
options = st.sidebar.selectbox("Select One",['Overall Analysis','Startup','Investor'])
if options == 'Overall Analysis':
    st.title('Overall Analysis')
    st.header(f"Biggest Funding (till now) :   {df.sort_values(by="Amount in USD",ascending=False)["Amount in Rs."].iloc[0]} ")
    converted_to_Rs = convert_to_readable((df["Amount in USD"].sum()/df["Amount in USD"].shape[0]).astype(int))
    st.header(f"Average Funding  : {converted_to_Rs}")
    st.header(f"Total Startups Funded  :  {str(df["Startup Name"].unique().shape[0]-1)+'+'}")
    st.subheader("Cities with Most Fundings")
    Max_fundings = df[["Amount in USD","City"]].groupby("City").agg({"Amount in USD":"sum"}).sort_values(by=["Amount in USD"],ascending=False).reset_index().head(20)
    df["Date"] = pd.to_datetime(df["Date"],errors='coerce')
    plt.barh(Max_fundings["City"],Max_fundings['Amount in USD'],color='red',log=True)
    plt.ylabel("City")
    plt.xlabel('Amount (in USD)')
    plt.title("Cities with Most fundings")
    st.pyplot(plt)
    plt.clf()
    st.subheader("Number of funded Start-ups over a period")
    new_df = df[["Date","Startup Name","Investment Type","Amount in USD"]]
    new_df["Month"] = new_df["Date"].dt.month_name()
    new_df["Year"] = new_df["Date"].dt.year
    new_mom_df = new_df.groupby(["Month","Year"]).agg({'Startup Name':'count',"Amount in USD":"sum"}).reset_index()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December']
    new_mom_df['Month'] = pd.Categorical(new_mom_df['Month'],categories=month_order,ordered=True)
    new_mom_df = new_mom_df.sort_values(['Year', 'Month'])
    plt.xlabel("Months and Years")
    plt.ylabel("Number of Funded Startups")
    plt.plot(range(new_mom_df.shape[0]),new_mom_df["Startup Name"],linewidth=2,marker='o',markersize=2,color='black')
    st.pyplot(plt)
    plt.clf()
    st.subheader("Total amount Raised by Startups over a period")
    plt.xlabel("Months and Years")
    plt.ylabel("Amount Funded")
    plt.plot(range(new_mom_df.shape[0]),new_mom_df["Amount in USD"],linewidth=2,marker='o',markersize=2,color='black')
    st.pyplot(plt)
    plt.clf()
    st.header("Sectors With Heavy Investments")
    sectoral_df = df.groupby("Industry Vertical").agg({"Industry Vertical":"count","Amount in USD":"sum"}).rename(columns={"Industry Vertical":"Count"}).reset_index().sort_values(by=["Count","Amount in USD"],ascending=False).head(10).drop(columns='Count')
    sectoral_df.rename(columns={"Industry Vertical":"Sector","Amount in USD":"Total Funding"},inplace=True)
    plt.bar(sectoral_df["Sector"],sectoral_df["Total Funding"])
    plt.xlabel("Sector")
    plt.ylabel("Funding in Hundred crores (Scaled down)")
    plt.title("Sector Wise Investments")
    plt.xticks(rotation='vertical')
    plt.plot()
    st.pyplot(plt)
    plt.clf()
    st.header("Round wise Funding")
    invest_df = df[['Investment Type','Amount in USD']].groupby("Investment Type").agg({"Amount in USD":"sum"}).sort_values(by="Amount in USD",ascending=False).head(6)
    plt.pie(invest_df["Amount in USD"],labels=invest_df.index,autopct='%0.2f%%')
    st.pyplot(plt)
    plt.clf()


elif options == 'Startup' :
    st.title('Startup Analysis')
    startup_name = st.sidebar.selectbox('Select the company',df['Startup Name'].unique().tolist())
    Industry = df[df['Startup Name']==startup_name]['Industry Vertical'].iloc[0]
    subvertical = df[df['Startup Name']==startup_name]['Sub vertical'].iloc[0]
    location = 'Location(s): ' +'  ' + ' || '.join(df[df['Startup Name']==startup_name]["City"].unique().tolist()[0:4])
    btn1 =  st.sidebar.button("Find Startup Details")
    show_df = df[df['Startup Name']==startup_name][['Sr No','Date','Investors Name','Investment Type','Amount in Rs.']].drop(columns = ['Sr No'])
    show_df.reset_index(drop=True,inplace=True)
    show_df.index = show_df.index + 1
    Industry_compete = df[df['Startup Name']==startup_name]["Industry Vertical"].iloc[0]
    competitors = ',\n'.join(name.strip() for name in df[(df["Industry Vertical"]==Industry_compete)&(df['Startup Name']!=startup_name)]['Startup Name'].unique()[0:5])

    if btn1:
        st.header(startup_name)
        string = str(Industry) + ' '*2 +  '-'+' '*2  + str(subvertical) +'   '*5
        st.subheader(string)
        st.subheader(location)
        st.write("Funding Details")
        st.dataframe(show_df)
        st.subheader("Similar Companies: ")
        st.write(competitors)

else:
    st.title('Investor Analysis')
    investor_name = st.sidebar.selectbox('Select Investor',unique_investors)
    btn2 = st.sidebar.button("Find Investor Details")
    investor_df = df[df["Investors Name"].str.contains(rf'\b{investor_name}\b',case=False,na=False)]
    Highest_Investments = investor_df[["Date","Startup Name","Industry Vertical","Sub vertical","City","Investment Type","Amount in USD","Amount in Rs."]].sort_values(["Amount in USD"],ascending=False).reset_index().drop(columns = ["Amount in USD","index"]).iloc[0:5]
    Highest_Investments.index = Highest_Investments.index + 1
    Recent_Investments = investor_df[["Date","Startup Name","Industry Vertical","Sub vertical","City","Investment Type","Amount in Rs."]].sort_values(["Date"],ascending=False).reset_index().drop(columns = ["index"]).iloc[0:5]
    Recent_Investments.index = Recent_Investments.index + 1
    invests_in = ', '.join(investor_df["Industry Vertical"].value_counts().index[0:3])
    plot_pie = investor_df[["Industry Vertical","Amount in USD"]].sort_values("Amount in USD",ascending=False).reset_index().drop(columns=["index"]).set_index(['Industry Vertical']).reset_index()

    if btn2:
        st.header(investor_name)
        st.subheader('Recent Investments')
        st.dataframe(Recent_Investments)
        st.subheader('Biggest Investments')
        st.dataframe(Highest_Investments)
        st.subheader("Generally Invests in : ")
        st.write(invests_in)
        st.header("Sectoral Analysis")
        plot_pie = plot_pie.groupby("Industry Vertical").sum().head(5)
        plt.figure(figsize=(8,6))
        plt.pie(plot_pie["Amount in USD"],autopct='%0.1f%%')
        plt.legend(plot_pie.index,title="Sectoral Investments")
        st.pyplot(plt)
        plt.clf()
        st.header("Series Wise Investments")
        type_df = investor_df.groupby("Investment Type").agg({"Amount in USD":"sum"}).head(5)
        plt.pie(type_df["Amount in USD"],autopct='%0.1f%%')
        plt.legend(type_df.index,title="Series Wise Investments")
        st.pyplot(plt)
        plt.clf()
        st.header("City wise Investments")
        city_df = investor_df.groupby("City").agg({"Amount in USD":"sum"}).head(5)
        plt.pie(city_df["Amount in USD"],autopct='%0.1f%%')
        plt.legend(city_df.index,title="City wise Investments")
        st.pyplot(plt)
        plt.clf()
        st.header("YoY - Investments")
        investor_df["Date"] = pd.to_datetime(investor_df["Date"],errors='coerce')
        investor_df["Year"] = investor_df["Date"].dt.year
        date_df =investor_df[["Year","Amount in USD"]]
        date_df = date_df.groupby("Year").agg({"Amount in USD":"sum"})
        plt.plot(date_df,marker='o',linewidth=2,color='Red')
        plt.xlabel("Year")
        plt.ylabel("Amount (in USD)")
        plt.title("YOY Investments")
        st.pyplot(plt)



