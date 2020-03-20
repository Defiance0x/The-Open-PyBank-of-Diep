"""
For appending into team scores instead of getting errors
"""

import pandas as pd


def CategoryScore(Category):
    
    """
    Creates an ordered list of archers with their score, hits and golds from
    the excel file containing all scores, named "OutdoorScores.xlsx"
    
    """
    
    Category = pd.read_excel('OutdoorScores.xlsx', Category , 
                             usecols=[0,1,2,3,4])
    ResultCategory = Category.sort_values(['Score','Golds','Hits'],
                        ascending=[False,False,False],na_position='last')
    ResultCategory = ResultCategory.reset_index(drop=True)
    N=0
    for i in range(100):
        N += 1
        if pd.isnull(Category.loc[N,'Name']) == True: 
                                               # looks at row N, column 'Name'
            break
    return ResultCategory[0:N] # if the cell is NaN, stops at row N


def PrintCategoryScore(Cat):
    
    """
    Function to print individual scores per category
    
    """
    print()
    print("########## Individual Category Results ##########")
    for i in range(len(Cat)): # prints out the results per category   
        print()
        print(Cat[i])
        print(CategoryScore(Cat[i]))
    print()
    return print("----- End of Individuals Category Results -----")


def Combined_Non_Compound_Results(level):
    
    """
    Combines all scores from all categories, except compound categories, such
    that an experienced team can be created.
    
    """
    
    CombinedResults =  pd.DataFrame({},columns=['Name','Club','Score',
                                    'Golds', 'Hits'])
       # Initial empty dataframe to append in to
    
    for i in level:
        CombinedResults = CombinedResults.append(CategoryScore(i))
        
    CombinedResults = CombinedResults.sort_values(['Score','Golds','Hits'],
                        ascending=[False,False,False],na_position='last')
    
    CombinedResults = CombinedResults.reset_index(drop=True)
    # print(CombinedResults) # uncomment to see complete almost results
    return CombinedResults


def TeamScores(level,team_N):
    
    """
    "level" refers to either NovCategories or AllCategories, i.e. this function
    returns either novice or experienced teams, where experienced teams can
    contain novices.
    
    "team_N" refers to the maximum number of archers per team:
        Novice teams have a maximum of 3
        Experienced teams have a maximum of 4
    
    """
    
    groupresults = Combined_Non_Compound_Results(level).groupby('Club') 
    # groups clubs together in a big list just for NMR
    # will need to generalise for all categories

    LoR = [ frame for LoRs, frame in groupresults ]
    
    TeamTable = pd.DataFrame({},columns=['Club','Total Score', # initial empty
                                    'Total Golds', 'Total Hits']) # dataframe
    
#    Uni = pd.DataFrame({},columns=['Name','Club','Score','Golds', 'Hits'])
    TeamComposition = [[],[],[],[]]
    for j in range(4): # only four clubs in the dataframe

        Uni = LoR[j][0:team_N] # jth club in index, gets top team_N archers
        Uni = Uni.reset_index(drop=True) # resets the index for UCL sublist
        UniName = Uni.loc[0,'Club']

        Scores=0
        Golds=0
        Hits=0
        
        TeamComposition[j].append(UniName)

        for i in range(team_N): # sums the score,golds and hits for uni club j
            Scores += Uni.loc[i,'Score']
            Golds += Uni.loc[i,'Golds']
            Hits += Uni.loc[i,'Hits']

            TeamComposition[j].append(Uni.loc[i,'Name'])
            
        TeamTable2 = pd.DataFrame({'Club': [UniName], 
                                         'Total Score': [Scores],
                                        'Total Golds': [Golds], 
                                        'Total Hits': [Hits]},
                                        columns=['Club','Total Score', 
                                    'Total Golds', 'Total Hits'])
    
        TeamTable = TeamTable.append(TeamTable2) # appends each club data

    TeamTable = TeamTable.sort_values(['Total Score','Total Golds',
                                       'Total Hits'],ascending=[False,False,
                                                   False],na_position='last')
    TeamTable = TeamTable.reset_index(drop=True)
    print()
    print(TeamTable)
    print()
    
 
    FinalList = [[],[],[],[]]
    
    for h in range(4):
        for g in range(4):
            if TeamTable.iloc[h,0] == TeamComposition[g][0]:
                FinalList[h] = TeamComposition[g]

    
    for k in range(4):
        print(FinalList[k])
        print()

    if level == NovCategories:
        
        return print("----- End of Novice Team Scores -----")
    
    if level == AllCategories:
        
        return print("----- End of Experienced Team Scores -----")

AllCategories = ['NWL','NWB','NML','NMB','NMR', # nov. categories
                 'EWB','EWR','EML','EMB','EMR'] # exp. categories
                 # note that these categories are non-compound!

NovCategories = ['NWB','NWL','NML','NMB','NMR'] # non-compound nov. categories

ActualAllCategories = ['NWC','NWL','NWB','NML','NMB','NMR','EWC',
                       'EWB','EWR','EMC','EML','EMB','EMR'] # includes compound

PrintCategoryScore(ActualAllCategories) # prints individual category results

TeamScores(NovCategories,3) # prints novice team scores

TeamScores(AllCategories,4) # prints experienced team scores

"""
Next thing to do is to make it so that it takes at most 3/4 archers from each
club per novice/experienced to create a team with, but call at least 1 or none
archers without error
"""