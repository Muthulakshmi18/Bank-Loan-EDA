import dash             #(version 1.9.1) pip install dash==1.9.1
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import ast
import pathlib

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

#=========read excel file
Bank=pd.read_excel(DATA_PATH.joinpath("Bank Loan Data.xlsx"))
Des_lis=["Age in years","Level of education","Years with current employer","Years at current address","Household income in thousands","Debt to income ratio (x100)","Credit card debt in thousands","Other debt in thousands","Default"]

def Table(bins,column_name,analysis):
    if analysis=="Univariate":
    	#Col_lis=list(Bank.columns[1:])   #===========get the list of columns

    	Cat_col=['ED', 'DEFAULT']  #============lis of categorical variable
    	Con_col=['AGE', 'EMPLOY', 'ADDRESS', 'INCOME', 'DEBTINC', 'CREDDEBT', 'OTHDEBT'] #============lis of continous variable


    elif analysis=="Bivariate":
    	#Col_lis=list(Bank.columns[1:-1])  #============split x values
    	Dependent=Bank.columns[-1]   #==========split y values

    	Cat_col=['ED'] #============lis of categorical variable
    	Con_col=['AGE', 'EMPLOY', 'ADDRESS', 'INCOME', 'DEBTINC', 'CREDDEBT', 'OTHDEBT']    #============lis of continous variable

            
    #============shows data index as multiple of 10's
    def num(n):
        q=n//10
        if n<10:
            return n
        else:
            return q*10
        
    #===================convert string into interval    
    def interval_type(s):
        """Parse interval string to Interval"""
        
        table = str.maketrans({'[': '(', ']': ')'})
        left_closed = s.startswith('[')
        right_closed = s.endswith(']')
    
        left, right = ast.literal_eval(s.translate(table))
    
        t = 'neither'
        if left_closed and right_closed:
            t = 'both'
        elif left_closed:
            t = 'left'
        elif right_closed:
            t = 'right'
    
        return pd.Interval(left, right, closed=t)    
        
  
    
    
    
    if column_name in Con_col:  #============if column is in list of continous variable
        #==============display pivot table
    
        bins = bins  
        bin_range=(int(round((Bank[column_name].max()-Bank[column_name].min())/bins,0)))-1 #==========calulate range of each row based on bin value
        if bin_range <=0:
            bin_range=1
        else:
            bin_range=bin_range
        bin_lis1=[i for i in range(int(Bank[column_name].min()),int(Bank[column_name].max())+1,bin_range)]   #===========list of label
    
        #===========================list of lables
        edges=bin_lis1
        edges1=edges[1:]
        
        
        labels=[str(edges[0])+"-"+str(edges[1])]
        edges1=edges[1:]
        for i in range(0,len(edges1)-1):
            label=(f'{edges1[i]+i+1}-{edges1[i]+bin_range+1+i}')
            if (edges1[i]+i+1) >Bank[column_name].max():
                break
            else:
                labels.append(label)
    
    	#=====================list of bins in interval notation
        bin_lis2=["["+str(edges[0])+","+str(edges[1])+"]"]
        for i in range(0,len(edges1)-1):
            bin_label=(f'[{edges1[i]+i+1},{edges1[i]+bin_range+1+i}]')
            if (edges1[i]+i+1) >Bank[column_name].max():
                break
            else:
                bin_lis2.append(bin_label)
                
        bin_lis=pd.IntervalIndex(pd.DataFrame(bin_lis2)[0].apply(interval_type)) 
        
        #==============create copy of bank loan data
        Bank_new=Bank.copy()


        if analysis=="Univariate":
    
            dff = pd.DataFrame({'Grand Total' : Bank.groupby([pd.cut(Bank[column_name], bins=bin_lis,labels=labels,include_lowest=True,ordered=False)]).count()[column_name]}).reset_index()
            dff['%'] = ((dff["Grand Total"]/Bank[column_name].count())*100).round(0).astype(int).astype(str) + '%'
            dff[column_name]=labels
            data_table=dff
 
        
        elif analysis=="Bivariate":
            Bank_new["Group"]=pd.cut(Bank_new[column_name], bins=bin_lis,labels=list(Bank_new[Dependent]),include_lowest=True,ordered=False)
            Bank_new1=Bank_new[["Group",Dependent,column_name]]
            pivot=pd.pivot_table(Bank_new1,index="Group",columns=Dependent, aggfunc='count',fill_value=0)
            pivot.columns =[s1 for (s1) in  pivot.columns.tolist()]  
            pivot.reset_index(inplace=True)  #============reset index
            pivot.columns=[column_name,"Non Default","Default"] #===========reset pivot column name
           
           #===============Grand total
            pivot["Grand Total"]=pivot["Default"]+pivot["Non Default"]  
           
           #=============find percentage
            pivot['Non Default%'] =((pivot['Non Default']/pivot["Grand Total"])*100).round(0).astype(int).astype(str) + '%'
            pivot['Default%'] = ((pivot['Default']/pivot["Grand Total"])*100).round(0).astype(int).astype(str) + '%'
            pivot['Grand Total%']=((pivot["Default"]+pivot["Non Default"])/pivot["Grand Total"]*100).round(0).astype(int).astype(str) + '%'
           
           #==============change Age column as range of values (Display purpose)
          
            pivot[column_name]=pivot[column_name].astype(str)
            pivot[column_name]=pivot[column_name].astype(str).str.replace(", ","-").str.replace("[","").str.replace("]","")
            data_table=pivot
        






    elif column_name in Cat_col: 
        Bank_new=Bank.copy()
        Bank_new["Group"]= Bank_new[column_name]
            
            #=============create new dataframe contains only necessary columns
    
        if analysis=="Univariate":
            Bank_new1=Bank_new[["Group",column_name]]
            dff=pd.pivot_table(Bank_new1,index="Group",values=column_name, aggfunc='count',fill_value=0)
            dff.columns =[s1 for (s1) in  dff.columns.tolist()]  
            dff.reset_index(inplace=True)  #============reset index
            dff.columns=[column_name,"Grand Total"]
       
            dff['%'] = ((dff["Grand Total"]/Bank[column_name].count())*100).round(0).astype(int).astype(str) + '%'
            data_table=dff
        elif analysis=="Bivariate":
            Bank_new1=Bank_new[["Group",Dependent,column_name]]
            pivot=pd.pivot_table(Bank_new1,index="Group",columns=Dependent, aggfunc='count',fill_value=0)
            pivot.columns =[s1 for (s1) in  pivot.columns.tolist()]  
            pivot.reset_index(inplace=True)  #============reset index
            pivot.columns=[column_name,"Non Default","Default"] #===========reset pivot column name
           
           #===============Grand total
            pivot["Grand Total"]=pivot["Default"]+pivot["Non Default"]  
           
           #=============find percentage
            pivot['Non Default%'] =((pivot['Non Default']/pivot["Grand Total"])*100).round(0).astype(int).astype(str) + '%'
            pivot['Default%'] = ((pivot['Default']/pivot["Grand Total"])*100).round(0).astype(int).astype(str) + '%'
            pivot['Grand Total%']=((pivot["Default"]+pivot["Non Default"])/pivot["Grand Total"]*100).round(0).astype(int).astype(str) + '%'
           
           #==============change Age column as range of values (Display purpose)
          
            pivot[column_name]=pivot[column_name].astype(str)
            pivot[column_name]=pivot[column_name].astype(str).str.replace(", ","-").str.replace("[","").str.replace("]","")
            data_table=pivot
    return data_table        
Col_lis=list(Bank.columns[1:])    
    
options = []
for col in Col_lis:
     options.append({'label':'{}'.format(col, col), 'value':col})   
#=============list of bins
#Bin_lis=[i for i in range(1,int(sqrt(len(Bank))))]
Bin_lis=[i for i in range(1,11)]
#=========================dash
#==========create app
app = dash.Dash(__name__)
server=app.server
app.layout = html.Div([
    
    
     html.H1(children="Data Visualization",  #============heading for graph
            style={
                
                'textAlign' : 'center',   #===========align the header text
                
                'color': '#0C4590'  #==============color of header text
                
                }
            
            
            
            ),
    
    
    
    html.Br(),html.Br(),
#==========================dropdown for bins    
    html.Div([
        html.Div([
            html.Label(['Select number of bins'], style={'font-size':17,'font-weight': 'bold', "text-align": "center"}),   #==========title of drop down
            
            html.Br(),html.Br(), #==========two line break
            
            
            dcc.Dropdown(id='Bins',
                options=[
                    
                    {'label': i, 'value': i} for i in Bin_lis
                         ],  #===========value refer to column name of data frame
                                         
                value=5,  #==============default value
                multi=False,
                clearable=False,
                style={'width': '50%'}
            ),
        ],style={'verticalAlign': 'middle', 'width': '25%', 'display': 'inline-block'},className='three columns'),

#==========================dropdown for columns
        html.Div([
            html.Label(['Select column name from list'], style={'font-size':17,'font-weight': 'bold', "text-align": "center"}),   #==========title of drop down
            
            html.Br(),html.Br(), #==========two line break   
            
            
        dcc.Dropdown(id='Columns',
            options=options,
            value="ED",   #==============default value
            multi=False,
            clearable=False,
            style={'width': '60%'}
        ),
        ],style={'verticalAlign': 'middle', 'width': '25%', 'display': 'inline-block'},className='three columns'),


#==========================dropdown for option univriate or bivriate
        html.Div([
            html.Label(['Select the option'], style={'font-size':17,'font-weight': 'bold', "text-align": "center"}),   #==========title of drop down
            
            html.Br(),html.Br(), #==========two line break   
            
            
        dcc.Dropdown(id='Analysis',
                     options=[                    
                    {'label': i, 'value': i} for i in ["Univariate","Bivariate"]],
            value="Univariate",   #==============default value
            multi=False,
            clearable=False,
            style={'width': '60%'}
        ),
        ],style={'verticalAlign': 'middle', 'width': '25%', 'display': 'inline-block'},className='three columns'),



    

#==========================dropdown for option Graphs
        html.Div([
            html.Label(['Select types of graphs'], style={'font-size':17,'font-weight': 'bold', "text-align": "center"}),   #==========title of drop down
            
            html.Br(),html.Br(), #==========two line break   
            
            
        dcc.Dropdown(id='Graphs',
                     options=[                    
                    {'label': i, 'value': i} for i in ["Bar Chart","Pie Chart","Box Plot"]],
            value="Box Plot",   #==============default value
            multi=False,
            clearable=False,
            style={'width': '60%'}
        ),
        ],style={'verticalAlign': 'middle', 'width': '25%', 'display': 'inline-block'},className='three columns'),


    ],className = "row", 
        style = dict(horizontalAlign = 'center')),
 



     html.Br(),
     html.Br(),
#==============================data Table    
    
      html.Div([
        dash_table.DataTable(id='datatable_id',editable=False,  #===========id refers graph name
            page_action="native",
            page_current= 0,
            page_size= 6,  #===================6 rows only display in each page
            
            #================column alignment
            style_cell={'textAlign': 'center','width': '15%','padding': '5px'}, #style_cell refers to the whole table
           
            #style_as_list_view=True,  #===============remove vertical gridlines
            
            #===========border of header
            style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'border': '1px solid black'
     },
            #============border of data
            style_data={ 'border': '1px solid black' },
            
            
            #===============
            style_data_conditional=[         #style_data.c refers only to data rows
         {
             'if': {'row_index': 'odd'},
             'backgroundColor': 'rgb(248, 248, 248)'
         }
     ],
            
            
            
            ) 
    ]), 

#==================Histogram graph
   html.Br(),
   html.Br(),
    html.Div([
        dcc.Graph(id='Chart')   #=============graph name 
    ]),  
   
   
    ])

#======================for graph


@app.callback(
    Output(component_id='Chart', component_property='figure'),  #=========component id refers graph name
    
    [Input(component_id='Bins', component_property='value'),
    Input(component_id='Columns', component_property='value') ,
    Input(component_id='Analysis', component_property='value'),
    Input(component_id='Graphs', component_property='value')]  #=========component id drop down name and component_property refers "value" in drop down options
)





def update_graph(bins,column,analysis,graph_drop):  #===============refers input component id "Input(component_id='my_dropdown')"
    if (len(str(bins))==0) |(len(str(column))==0) | (len(str(analysis))==0) |(len(str(graph_drop))==0) :
        table=Table(5,"ED",analysis)    #================default display graph
        graph_drop="Box Plot"
    else:
        table=Table(bins,column,analysis)
        graph_drop=graph_drop
        
    #-============change column name as in description    
    for each_col in range(len(Col_lis)):    
        if column==Col_lis[each_col]:
            table.rename(columns={Col_lis[each_col]:Des_lis[each_col]},inplace=True)
            column=Des_lis[each_col]
            column1=Col_lis[each_col]
            








    
#====================steps for graph
    if analysis=="Bivariate":
       table["Non Default%"]=table["Non Default%"].str.replace("%","")
       table["Default%"]=table["Default%"].str.replace("%","")
       table["Non Default%"]= table["Non Default%"].astype(int)
       Dependent=Bank.columns[-1]
      #===================split default and non default
       Bank_default=Bank[Bank[Dependent]==1]
       Bank_non_default=Bank[Bank[Dependent]==0]
    
    elif analysis=="Univariate":
        table["%"]=table["%"].str.replace("%","")

        table["%"]= table["%"].astype(int)	



#====================change numerical education variable to categorical
    try:
         if column==Col_lis[1]:
             table[column]=table[column].astype(int)
             table[column] = table[column].map({1: 'Did not complete high school', 2: 'High school', 3: 'Partime college', 4: 'Full time college',5: 'Pg degree'})
         elif column=="Default":
             table[column]=table[column].astype(int)
             table[column] = table[column].map({1: 'Yes', 0: 'No'})
            
         else:
             table[column]=table[column].astype(str)
 
    except:
         table[column]=table[column]

        
#===============adjust height and width of graph
    if column==Col_lis[1]:
         height=650
         width=1500
    else:
         height=600
         width=1500
         
         
    if analysis=="Bivariate":
        yaxis_title="<b>"+Dependent+"</b>"  #=========bold y axis title
        Cat_col=['ED'] #============lis of categorical variable
        Con_col=['AGE', 'EMPLOY', 'ADDRESS', 'INCOME', 'DEBTINC', 'CREDDEBT', 'OTHDEBT']    #============lis of continous variable
    elif analysis=="Univariate":
        yaxis_title="<b>"+column+"</b>"
        Cat_col=['ED','DEFAULT'] #============lis of categorical variable
        Con_col=['AGE', 'EMPLOY', 'ADDRESS', 'INCOME', 'DEBTINC', 'CREDDEBT', 'OTHDEBT']    #============lis of continous variable
    
    #=============graph
    if (analysis=="Bivariate") & ((graph_drop=="Bar Chart") | (len(str(graph_drop))==0)):
        a=[dict(x=0.5, y=-0.2,
                text="",
                showarrow=False,
                arrowhead=1,
                font=dict(
            family="Courier New, monospace",
            size=25,
            color="rgb(255,255,255)"
            )
           )]

        trace1 = go.Bar(
        x=table[column],
        y=table["Non Default%"],
        name="Non Default",
        hovertemplate=['<b>('+i+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["Non Default%"].to_list())],   #=======text appears when cursor moves
        marker_color="#00BFFF",   #=============color code
                
        text=[str(i)+"%" for i in table["Non Default%"].to_list()],
        textposition="inside",
        textfont=dict(
            family="sans serif",
            size=18,
            color='rgb(255,255,255)'
        )
        )   #=====================first bar of Bivariate (non default)
        
        
        trace2 = go.Bar(
            x=table[column],
            y=table["Default%"],
            name="Default",
            marker_color="#FF8B3D",
            hovertemplate=['<b>('+i+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["Default%"].to_list())],
            text=[str(i)+"%" for i in table["Default%"].to_list()],
            textposition="inside",
            textfont=dict(
            family="sans serif",
            size=18,
            color='rgb(255,255,255)'
    
        )
        ) #=====================second bar  of bivariate (default)

    elif (analysis=="Bivariate") & (graph_drop=="Box Plot"):
        if column1 in Con_col:
            a=[dict(x=0.5, y=-0.2,
                    text="",
                    showarrow=False,
                    arrowhead=1,
                    font=dict(
                family="Courier New, monospace",
                size=25,
                color="rgb(255,255,255)"
                )
               )]
            trace1 = go.Box(
            x=Bank_non_default[column1].to_list(),
            name="Non Default",
            boxpoints='suspectedoutliers',
            marker=dict(color="#00BFFF",outliercolor='#00BFFF',line=dict(
                outliercolor='#00BFFF',
                outlierwidth=2)),   #=============color code
    
            )   #=====================first bar of Bivariate (non default)
            
            
            trace2 = go.Box(
                x=Bank_default[column1].to_list(),
                name="Default",
                boxpoints='suspectedoutliers',
                marker=dict(color="#FF8B3D",outliercolor='#FF8B3D',line=dict(
                outliercolor='#FF8B3D',
                outlierwidth=2))
                                ,
             ) #=====================second bar  of bivariate (default)

        if column1 in Cat_col:
            a=[dict(x=0.5, y=-0.2,
                    text="",
                    showarrow=False,
                    arrowhead=1,
                    font=dict(
                family="Courier New, monospace",
                size=25,
                color="rgb(255,255,255)"
                )
               )]
            trace1 = go.Bar(
            x=[],
            y=[],
            name="Non Default",
            hovertemplate=['<b>('+i+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["Non Default%"].to_list())],   #=======text appears when cursor moves
            marker_color="#00BFFF",   #=============color code
                    
            text=[str(i)+"%" for i in table["Non Default%"].to_list()],
            textposition="inside",
            textfont=dict(
                family="sans serif",
                size=18,
                color='rgb(255,255,255)'
            )
            )   #=====================first bar of Bivariate (non default)
            
            
            trace2 = go.Bar(
                x=[],
                y=[],
                name="Default",
                marker_color="#FF8B3D",
                hovertemplate=['<b>('+i+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["Default%"].to_list())],
                text=[str(i)+"%" for i in table["Default%"].to_list()],
                textposition="inside",
                textfont=dict(
                family="sans serif",
                size=18,
                color='rgb(255,255,255)'
        
            )
            ) #=====================second bar  of bivariate (default)            

    elif (analysis=="Bivariate") & (graph_drop=="Pie Chart"):
        a=[dict(x=0.5, y=-0.2,
                text="",
                showarrow=False,
                arrowhead=1,
                font=dict(
            family="Courier New, monospace",
            size=25,
            color="rgb(255,255,255)"
            )
           )]
        trace1 = go.Bar(
        x=[],
        y=[],
        name="Non Default",
        hovertemplate=['<b>('+i+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["Non Default%"].to_list())],   #=======text appears when cursor moves
        marker_color="#00BFFF",   #=============color code
                
        text=[str(i)+"%" for i in table["Non Default%"].to_list()],
        textposition="inside",
        textfont=dict(
            family="sans serif",
            size=18,
            color='rgb(255,255,255)'
        )
        )   #=====================first bar of Bivariate (non default)
        
        
        trace2 = go.Bar(
            x=[],
            y=[],
            name="Default",
            marker_color="#FF8B3D",
            hovertemplate=['<b>('+i+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["Default%"].to_list())],
            text=[str(i)+"%" for i in table["Default%"].to_list()],
            textposition="inside",
            textfont=dict(
            family="sans serif",
            size=18,
            color='rgb(255,255,255)'
    
        )
        ) #=====================second bar  of bivariate (default)    

#=========================graph for univariate analysis

    elif (analysis=="Univariate") & ((graph_drop=="Bar Chart") | (len(str(graph_drop))==0)):
        text="<b>"+column+"</b>"
        a=[dict(x=0.5, y=-0.2,
                text="",
                showarrow=False,
                arrowhead=1,
                font=dict(
            family="Courier New, monospace",
            size=25,
            color="#000000"
            )
           )]
        trace3 = go.Bar(
        x=table[column],
        y=table["%"],
        name="% OF " +column ,
        hovertemplate=['<b>('+str(i)+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["%"].to_list())],   #=======text appears when cursor moves
        marker_color="#00BFFF",   #=============color code
                
        text=[str(i)+"%" for i in table["%"].to_list()],
        textposition="outside",
        textfont=dict(
            family="sans serif",
            size=18,
            color='#00008B'
        )
        )  #=================first bar of univariate
    elif (analysis=="Univariate") & ((graph_drop=="Pie Chart")):
        text="<b>"+column+"</b>"
        a=[dict(x=0.5, y=-0.2,
                text=text,
                showarrow=False,
                arrowhead=1,
                font=dict(
            family="Courier New, monospace",
            size=25,
            color="#000000"
            )
           )]
        trace3 = go.Pie(
                labels=[i for i in table[column].to_list() if i != "0%"],
                values=[i for i in table["%"].to_list() if i != 0],
                #textinfo='label+percent',
                hovertemplate=['<b>('+str(i)+', '+str(j)+'%)</b><extra></extra>' for i,j in zip(table[column].to_list(),table["%"].to_list())],
                texttemplate="%{value:}"+"%",
                insidetextorientation='radial',
                
                textfont=dict(
                    family="sans serif",
                    size=18,
                    color='rgb(255,255,255)')
        )  #=================first bar of univariate
 
    
    
    elif (analysis=="Univariate") & ((graph_drop=="Box Plot")):
        if column1 in Con_col:
            text="<b>"+column+"</b>"
            a=[dict(x=0.5, y=-0.2,
                    text="",
                    showarrow=False,
                    arrowhead=1,
                    font=dict(
                family="Courier New, monospace",
                size=25,
                color="#000000"
                )
               )]

            trace3 = go.Box(
            x=Bank[column1].to_list(),
            boxpoints='suspectedoutliers',
            name="",
            marker=dict(color="#00BFFF",outliercolor='#00BFFF',line=dict(
                outliercolor='#00BFFF',
                outlierwidth=2)),   #=============color code
    
            )   #=====================first bar of Bivariate (non default)
        elif column1 in Cat_col:
            text="<b>"+column+"</b>"
            a=[dict(x=0.5, y=-0.2,
                    text="",
                    showarrow=False,
                    arrowhead=1,
                    font=dict(
                family="Courier New, monospace",
                size=25,
                color="#000000"
                )
               )]

            trace3 = go.Box(
            x=[],
            boxpoints='suspectedoutliers',
            marker=dict(color="#00BFFF",outliercolor='#00BFFF',line=dict(
                outliercolor='#00BFFF',
                outlierwidth=2)),   #=============color code
    
            )   #=====================first bar of Bivariate (non default)













#==========================display the graph

    if analysis=="Bivariate":
        fig=go.Figure(
                      data=[trace1,trace2],  #============append first and second bar
                      layout=go.Layout(barmode='stack'),
                     
                      
                      )
    elif analysis=="Univariate":
        fig=go.Figure(
                      data=[trace3],  #============first bar of univariate
                      layout=go.Layout(barmode='group'),
                     
                      
                      )    
#====================layout        
    fig.update_layout(    #=========Layout
                #==============align the title text center     
              title={
                'y':1,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
              
              #============bold italics title text
              title_text="<b><i>Bank Loan Data</i></b>",
              
              
              title_font_color='rgb(169, 50, 38)',  #============title font color
              xaxis_title_text="<b>"+column+"</b>",  #===========bold xasis title
              yaxis_title_text=yaxis_title,
              bargap=0.2, # gap between bars of adjacent location coordinates
              bargroupgap=0.1,# gap between bars of the same location coordinates
              plot_bgcolor='rgb(255, 255, 255)',  #===========graph background color
              paper_bgcolor ='rgb(255, 255, 255)', #==============back ground color
              font={'size': 20, 'family': 'Courier'},  #=========font size of all titles
              font_color='rgb(23, 32, 42)',  #==============x axis and y axis color
              
              #yaxis_type='category'
              height=height,         #=======height of the graph
              width=width,  #===========width
              annotations=a
              
              
              
              )
    if column==Col_lis[1]:
        fig.update_xaxes( showgrid=False)  #==============remove grid lines of x axis
    else:
        fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False) #==============remove grid lines of x axis
    return (fig)

#================dynamic data table

@app.callback(
    [Output(component_id='datatable_id', component_property='data'),
    Output('datatable_id', 'columns')],  #=========component id refers graph name
    [Input(component_id='Bins', component_property='value'),
    Input(component_id='Columns', component_property='value'),
    Input(component_id='Analysis', component_property='value')]  #=========component id drop down name and component_property refers "value" in drop down options
)

def update_table(bins,column,analysis):
    if (len(str(bins))==0) |(len(str(column))==0) | (len(str(analysis))==0):
        table=Table(5,"ED","analysis")
    else:
        table = Table(bins,column,analysis)
            
            
    
   
 
    try:
        if column==Col_lis[1]:
            table[column]=table[column].astype(int)
            table[column] = table[column].map({1: 'Did not complete high school', 2: 'High school', 3: 'partime college', 4: 'full time college',5: 'pg degree'})
        elif column=="Default":
             table[column]=table[column].astype(int)
             table[column] = table[column].map({1: 'Yes', 0: 'No'})

        else:
            table[column]=table[column].astype(str)
    
    except:
        table[column]=table[column]

    
    
    
    
    columns=[{"name": str(i), "id": str(i), "deletable": False, "selectable": False} for i in table.columns]


    dash_table.DataTable(
        
        id='datatable_id',
                         data=table.to_dict('records'),
                         columns=columns   #=========columns of Data Frame
            ,  
)
  
    
    return(table.to_dict('records'),columns)


#==============display the graph

if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)




    
    
    
    
    
    
    
    
    
    
    
    