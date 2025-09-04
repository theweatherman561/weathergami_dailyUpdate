# Written By Jared Rennie, modified by Michael Gonzalez

# Import packages
import json,requests,sys
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

now = datetime.now()
yesterday = now - timedelta(days = 1)
twoDaysAgo = now - timedelta(days = 2)
threeDaysAgo = now - timedelta(days = 3)

stationList = ["KBIS", "KMOT", "KDIK", "KXWA"]

for i in range(0, len(stationList)):
    stationID = stationList[i]
    
    yesterdayString = yesterday.strftime("%Y-%m-%d")
    twoDaysAgoString = twoDaysAgo.strftime("%Y-%m-%d")
    
    # Retrieve yesterday's high/low      
    acis_url = 'http://data.rcc-acis.org/StnData'
    payload = {
    "output": "json",
    "params": {"elems":[{"name":"maxt","interval":"dly","prec":1},{"name":"mint","interval":"dly","prec":1}],
            "sid":stationID,
            "date":yesterdayString
            } 
    }
    # Make Request
    try:
        r = requests.post(acis_url, json=payload,timeout=3)
        acisData = r.json()
    except Exception as e:
        sys.exit('\nSomething Went Wrong With Accessing API after 3 seconds, Try Again')
        
    # Convert Data to Pandas, get start and end year
    acisPandasYesterday = pd.DataFrame(acisData['data'], columns=['Date','Tmax','Tmin'])
    ydayTmax=acisPandasYesterday.iloc[[0]]['Tmax'].values[0]
    ydayTmin=acisPandasYesterday.iloc[[0]]['Tmin'].values[0]
    
    # IN CASE THERE'S NO DATA FOR YESTERDAY YET:
    #=================================================  
    if ydayTmax == "M" or ydayTmin == "M":
        # Retrieve yesterday's high/low      
        acis_url = 'http://data.rcc-acis.org/StnData'
        payload = {
        "output": "json",
        "params": {"elems":[{"name":"maxt","interval":"dly","prec":1},{"name":"mint","interval":"dly","prec":1}],
                "sid":stationID,
                "date":twoDaysAgoString
                } 
        }
        # Make Request
        try:
            r = requests.post(acis_url, json=payload,timeout=3)
            acisData = r.json()
        except Exception as e:
            sys.exit('\nSomething Went Wrong With Accessing API after 3 seconds, Try Again')   
        
        acisPandasYesterday = pd.DataFrame(acisData['data'], columns=['Date','Tmax','Tmin'])
        ydayTmax=acisPandasYesterday.iloc[[0]]['Tmax'].values[0]
        ydayTmin=acisPandasYesterday.iloc[[0]]['Tmin'].values[0]    

        twoDaysAgoString = threeDaysAgo.strftime("%Y-%m-%d")
    #=================================================  
    
    # Read in Arguments 
    #if len(sys.argv) < 4:
    #    sys.exit("USAGE: <ID> <Tmax> <Tmin>\n Example: python weathergami.py ATL 90 70")  
    inTmax= "%.1f" % (int(float(ydayTmax)))
    inTmin= "%.1f" % (int(float((ydayTmin))))
    constantAxis = True
    
    # Other Arguments that can be changed
    author='Michael Gonzalez'
    dpi=100
    
    # Build JSON to access ACIS API (from https://www.rcc-acis.org/docs_webservices.html)
    acis_url = 'http://data.rcc-acis.org/StnData'
    payload = {
    "output": "json",
    "params": {"elems":[{"name":"maxt","interval":"dly","prec":1},{"name":"mint","interval":"dly","prec":1}],
            "sid":stationID,
            "sdate":"por",
            "edate":twoDaysAgoString
            } 
    }
    
    # Make Request
    try:
        r = requests.post(acis_url, json=payload,timeout=3)
        acisData = r.json()
    except Exception as e:
        sys.exit('\nSomething Went Wrong With Accessing API after 3 seconds, Try Again')
    
    # Get Station Info
    stationName=acisData['meta']['name'].title()
    stationState=acisData['meta']['state']
    print("\nSuccessfully Got Data for: ",stationName,'\n')
    
    # Convert Data to Pandas, get start and end year
    acisPandas = pd.DataFrame(acisData['data'], columns=['Date','Tmax','Tmin'])
    stationStart=acisPandas.iloc[[0]]['Date'].values[0][0:4]
    stationEnd=acisPandas.iloc[[-1]]['Date'].values[0][0:4] 
 
    # The Williston Correction (merge KISN and KXWA)
    #=================================================     
    if stationID == "KXWA":
        # Build JSON to access ACIS API (from https://www.rcc-acis.org/docs_webservices.html)
        acis_url = 'http://data.rcc-acis.org/StnData'
        payload = {
        "output": "json",
        "params": {"elems":[{"name":"maxt","interval":"dly","prec":1},{"name":"mint","interval":"dly","prec":1}],
                "sid":"KISN",
                "sdate":"por",
                "edate":"2019-10-22"
                } 
        }
        
        # Make Request
        try:
            r = requests.post(acis_url, json=payload,timeout=3)
            acisDataKISN = r.json()
        except Exception as e:
            sys.exit('\nSomething Went Wrong With Accessing API after 3 seconds, Try Again')    
           
        # Build JSON to access ACIS API (from https://www.rcc-acis.org/docs_webservices.html)
        acis_url = 'http://data.rcc-acis.org/StnData'
        payload = {
        "output": "json",
        "params": {"elems":[{"name":"maxt","interval":"dly","prec":1},{"name":"mint","interval":"dly","prec":1}],
                "sid":"KXWA",
                "sdate":"2019-10-23",
                "edate":twoDaysAgoString
                } 
        }
        
        # Make Request
        try:
            r = requests.post(acis_url, json=payload,timeout=3)
            acisData = r.json()
        except Exception as e:
            sys.exit('\nSomething Went Wrong With Accessing API after 3 seconds, Try Again')    
            
        # Convert Data to Pandas, get start and end year
        acisPandasKISN = pd.DataFrame(acisDataKISN['data'], columns=['Date','Tmax','Tmin'])
        acisPandasKXWA = pd.DataFrame(acisData['data'], columns=['Date','Tmax','Tmin'])
        acisPandas = pd.concat([acisPandasKISN, acisPandasKXWA])
        stationStart=acisPandas.iloc[[0]]['Date'].values[0][0:4]
        stationEnd=acisPandas.iloc[[-1]]['Date'].values[0][0:4]

    #=================================================     
    
    # Now Find if the Tmax/Tmin combo has happened in the record before (ie WeatherGami).
    wgTest=acisPandas[(acisPandas['Tmax'] == inTmax) & (acisPandas['Tmin']==inTmin)]
    
    logFile = "log_" + str(stationID) + ".txt"
    log = open(logFile, "w")
    
    if len(wgTest) == 0:
        wgResult="It's a WeatherGami!"
        print(inTmax,'/',inTmin,': ',wgResult)
        print("It has never happened before!")
        log.write(str(inTmax)+'/'+str(inTmin)+': '+str(wgResult) + "\n")
        log.write("It has never happened before!")
    elif len(wgTest) == 1:
        wgResult="It's a WeatherGami!"
        for index, row in wgTest.iterrows():
            print(row['Date'])
            log.write(str(row['Date']) + "\n")
        print(inTmax,'/',inTmin,': ',wgResult)
        print("It has happened ",len(wgTest)," time before")
        log.write(str(inTmax)+'/'+str(inTmin)+': '+str(wgResult) + "\n")
        log.write("It has happened "+str(len(wgTest))+" time before")
    else:
        wgResult="It's NOT a WeatherGami!"
        for index, row in wgTest.iterrows():
            print(row['Date'])
            log.write(str(row['Date']) + "\n")
        print(inTmax,'/',inTmin,': ',wgResult)
        print("It has happened ",len(wgTest)," times before")
        log.write(str(inTmax)+'/'+str(inTmin)+': '+str(wgResult) + "\n")
        log.write("It has happened "+str(len(wgTest))+" times before")
    
    # Get Frequency and Percentage Info needed for Plotting
    frequency_counts = acisPandas.groupby(['Tmax', 'Tmin']).size().reset_index(name='Frequency')
    frequency_counts['Percentage'] = (frequency_counts['Frequency'] / len(acisPandas)) * 100
    
    # Remove Missing Data
    frequency_counts=frequency_counts[(frequency_counts['Tmax']!='M') & (frequency_counts['Tmin']!='M')].sort_values('Percentage', ascending=True)
    
    # Get Frequency of input tmax/tmin and most frequent
    currFreq=frequency_counts[(frequency_counts['Tmax'] == inTmax) & (frequency_counts['Tmin']==inTmin)]
    if len(currFreq)==0:
        currFreq=str(inTmax)+'/'+str(inTmin)+': '+wgResult+' (It has never happened before!)'
    elif currFreq['Frequency'].values[0]==1:
        currFreq=str(inTmax)+'/'+str(inTmin)+': '+wgResult+' ('+str(currFreq.iloc[-1]['Frequency'])+' Occurrence)'
    else:
        currFreq=str(inTmax)+'/'+str(inTmin)+': '+wgResult+' ('+str(currFreq.iloc[-1]['Frequency'])+' Occurrences)'
    mostFreq=str(frequency_counts.iloc[-1]['Tmax'])+'/'+str(frequency_counts.iloc[-1]['Tmin'])+' ('+str(frequency_counts.iloc[-1]['Frequency'])+' Occurrences)'
    
    # Plot
    print("PLOTTING")
    
    # Set up the scatter plot
    fig, axf = plt.subplots(figsize=(10, 8), edgecolor='white', facecolor='black', dpi=dpi)
    plt.style.use("dark_background")
    
    # Add grid lines
    plt.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.3)
    axf.set_facecolor('#808080')
    
    # Sort and Extract the values from the DataFrame
    tmax_values = frequency_counts['Tmax'].astype('f')
    tmin_values = frequency_counts['Tmin'].astype('f')
    percentage = frequency_counts['Percentage'].astype('f')
    
    # Plot the tmax/tmin locationns, colorized by percentage. Also plot input tmax/tmiin as separate color
    plt.scatter(tmax_values, tmin_values, c=percentage, cmap='viridis', s=40, alpha=0.6,zorder=9)
    plt.scatter(float(inTmax), float(inTmin), c='red',s=40, alpha=0.6,zorder=10)
    
    # Get X/Y Limits to help with plotting axes
    ymin=int(5 * round(float((min(tmin_values) - 10))/5))
    ymax=int(5 * round(float((max(tmin_values) + 10))/5))
    xmin=int(5 * round(float((min(tmax_values) - 10))/5))
    xmax=int(5 * round(float((max(tmax_values) + 10))/5))
    
    if constantAxis == True:
        ymin = -60
        ymax = 130
        xmin = -40
        xmax = 150
    
    # Plot X/Y-Axis Label
    plt.yticks(range(ymin, ymax, 10), [r'{}'.format(x) for x in range(ymin, ymax, 10)], fontsize=12, color='white')
    plt.ylabel(r'Minimum Temperature (°F)', fontsize=15, color='white')
    plt.xticks(range(xmin, xmax, 10), [r'{}'.format(x) for x in range(xmin, xmax, 10)], fontsize=12, color='white')
    plt.xlabel(r'Maximum Temperature (°F)', fontsize=15, color='white')
    
    # Plot Title/Subtitle/Annotations
    plt.suptitle('WeatherGami For '+stationName+', '+stationState, fontsize=15,y=0.95)
    plt.annotate('Source: ACIS | Generated by '+author+' | Inspired By Kahl (2023)',xy=(0.995, 0.01), xycoords='axes fraction', fontsize=7,horizontalalignment='right', verticalalignment='bottom')
    plt.annotate(currFreq+'\nMost Common: '+mostFreq+'\nPeriod of Record= '+str(stationStart)+'-'+str(stationEnd),xy=(0.01, 0.995), xycoords='axes fraction', fontsize=7,horizontalalignment='left', verticalalignment='top')
    
    # Add labels and a colorbar
    cbar = plt.colorbar(orientation='vertical')
    cbar.set_label('Frequency (%)',fontsize=12)
    
    # Save Figure
    plt.savefig('./'+stationID+'_weathergami.png', dpi=dpi,bbox_inches='tight')
    plt.clf()
    plt.close()
    
    # Done! Close Program
    print('DONE!')
sys.exit()
