
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from flask import Flask,render_template,request
import io
import base64

app=Flask(__name__)

def plot_to_html_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/')
def data_plots():
    df=pd.read_excel('notebooks\data\LoanDeafaulterData1.xlsx')
    df['Status']=df['Status'].replace(['G','D'],[0,1])
    income_bins=[0,10,20,30,40,50,60,70,80,90,101]
    income_labels=['0-10','10-20','20-30','30-40','40-50','50-60','60-70','70-80','80-90','90-101']
    loan_bins=[1000,2000,3000,4000,5000]
    loan_labels=['1k-2k','2k-3k','3k-4k','4k-5k']
    collateral_bins=[1000,2000,3000,4000,5000,6000]
    collateral_labels=['1k-2k','2k-3k','3k-4k','4k-5k','5k-6k']
    exp_bins=[0,4,8,12,16,21]
    exp_label=['0-4','4-8','8-12','12-16','16-21']

    df['Years in current occupation grp']= pd.cut(df['Years in current occupation' ],bins=exp_bins,labels=exp_label,right=False)
    df['Income grp']=pd.cut(df['Monthly income'],bins=income_bins,labels=income_labels,right=False)
    df['Loan grp']=pd.cut(df['Loan application amount'],bins=loan_bins,labels=loan_labels,right=False)
    df['Collateral grp']=pd.cut(df['Collateral'],bins=collateral_bins,labels=collateral_labels,right=False)

    cat_groups=['Years in current occupation grp','Income grp','Loan grp','Collateral grp']
    for grp in cat_groups:
        df[grp]=df[grp].astype('object')

    cat_cols = df.select_dtypes(include='object')
    num_cols=  df.select_dtypes(exclude='object')
    plots = []

    for i in cat_cols.columns:
        
        default_rate2=df.groupby(i)['Status'].mean().reset_index()
        fig, axes = plt.subplots(1, 3, figsize=(14, 5))

      
        sns.lineplot(x=cat_cols[i].value_counts().sort_index().index, y=cat_cols[i].value_counts().values,palette='husl', linestyle='-', color='b',marker='o', ax=axes[0])
        axes[0].set_title(f"Count of {i}")
        axes[0].set_xlabel(i)
        axes[0].set_ylabel('Count')
        axes[0].tick_params(axis='x', rotation=60)
        axes[0].grid()

       
        sns.barplot(x=cat_cols[i].value_counts().sort_index().index, y=cat_cols[i].value_counts().values,palette='magma', ax=axes[1])
        axes[1].set_title(f"Count of {i}")
        axes[1].set_xlabel(i)
        axes[1].set_ylabel('Count')
        axes[1].tick_params(axis='x', rotation=60)
        

        sns.lineplot(x=i, y='Status', data= default_rate2, palette='husl', linestyle='-', color='b',marker='o', ax=axes[2])
        axes[2].set_title(f'Default Rate for {i}')
        axes[2].set_xlabel(i)
        axes[2].set_ylabel('Default Rate')
        axes[2].tick_params(axis='x', rotation=60)
        axes[2].grid()

        
        plt.tight_layout()
        graph_html=plot_to_html_image(fig)
        plots.append(graph_html)

    for i in num_cols.columns:
        if i == 'Status':
            continue
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        sns.boxplot(x='Status', y=i, data=df, palette='magma', ax=axes[0])
        axes[0].set_title(f"Boxplot of {i}")
        axes[0].grid()
        sns.histplot(x=i, data=df, palette='magma',kde=True, ax=axes[1])
        axes[1].set_title(f"Histogram of {i}")
        axes[1].grid()

        plt.tight_layout()
        graph_html=plot_to_html_image(fig)

        plots.append(graph_html)
       

    return render_template('plots.html',plots=plots)


if __name__=='__main__':
   app.run(debug=True)




