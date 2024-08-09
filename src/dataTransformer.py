import numpy as np
import pandas as pd



_NEW_NAMES = { 
            'Delhi Daredevils':'Delhi Capitals'
            ,'Gujarat Lions':'Gujarat Titans'
            ,'Punjab Kings':'Kings XI Punjab'
            ,'Deccan Chargers':'Sunrisers Hyderabad'
            ,'Royal Challengers Bengaluru':'Royal Challengers Bangalore'
            ,'Rising Pune Supergiant':'Rising Pune Supergiants'
            ,'Pune Warriors':'Rising Pune Supergiants'
}
_SEASONS = {'2007/08': '2008'
           ,'2009/10': '2010'
           ,'2020/21': '2021'}
            
def clean_matches(df:pd.DataFrame):
    
    new_df =(
        df
        .drop('method', axis=1)
        .assign(season = lambda df_: df_.season.replace(_SEASONS)
                ,team1 = lambda df_: df_.team1.replace(_NEW_NAMES)
                ,team2 = lambda df_: df_.team2.replace(_NEW_NAMES)
                ,toss_winner = lambda df_: df_.toss_winner.replace(_NEW_NAMES)
                ,winner = lambda df_: df_.winner.replace(_NEW_NAMES)
                ,city = lambda df_ : df_.city.fillna(df_.venue.str.split().str[0])
                ,venue = lambda df_ : df_.venue.str.split(',').str[0]
               )
        .assign(
                city = lambda df_: df_.city.replace({'Bengaluru':'Bangalore'})
                ,team1_short = lambda df_ : df_['team1'] 
                .apply(lambda x: ''
                       .join(word if len(word)<=2 else word[0] for word in x.split()))
                ,team2_short = lambda df_ : df_['team2'] 
                .apply(lambda x: ''
                       .join(word if len(word)<=2 else word[0] for word in x.split()))
                ,winner_short = lambda df_ : df_.loc[lambda _df : _df.winner.notnull(),'winner'] 
                                            .apply(lambda x: ''
                                             .join(word if len(word)<=2 else word[0] for word in x.split()))
                ,toss_winner_short =lambda df_ : df_['toss_winner']
                .apply(lambda x: ''
                       .join(word if len(word)<=2 else word[0] for word in x.split()))
 
               )  
    )
    return new_df


def clean_deliveries(df:pd.DataFrame):
    return(
    df
    .assign(batting_team = lambda df_: df_.batting_team.replace(_NEW_NAMES)
            ,bowling_team = lambda df_: df_.bowling_team.replace(_NEW_NAMES)
            ,team_batting = lambda df_ : df_['batting_team'] 
                        .apply(lambda x: ''
                           .join(word if len(word)<=2 else word[0] for word in x.split()))
            ,team_bowling = lambda df_ : df_['bowling_team'] 
                        .apply(lambda x: ''
                           .join(word if len(word)<=2 else word[0] for word in x.split()))
           )
    ) 

def deliveries_transform(data:pd.DataFrame)-> pd.DataFrame:
    return(
    data
    .assign(
        score= lambda _df: _df
                            .groupby(['match_id','inning'])['total_runs']
                            .transform('sum')
        ,wickets_left = lambda _df: 10- _df
                                        .groupby(['match_id','inning'])['is_wicket']
                                        .cumsum()
        ,current_sore = lambda _df: _df
                                    .groupby(['match_id','inning'])['total_runs']
                                    .cumsum()
        ,legal_ball = lambda _df: np.where((_df.extras_type=='wides')|(_df.extras_type=='noballs'),0,1)
        ,balls = lambda _df:_df
                             .groupby(['match_id','inning'])['legal_ball']
                             .cumsum()
        ,ball_left = lambda _df: 120 - _df.balls
        ,run_rate = lambda _df: np.where(_df.balls>0,_df.current_sore/_df.balls,_df.current_sore)
        ,chase_target = lambda _df: _df.groupby('match_id')['total_runs']
                                             .transform(lambda x: x[_df.loc[x.index,'inning']==1].sum())
        ,runs_left = lambda _df: _df.chase_target -_df.current_sore
        ,req_rate = lambda _df: np.where(_df.balls>0,  _df.runs_left / _df.ball_left,_df.runs_left)
        )
    )
    
def features_sectection(bolls_data:pd.DataFrame
                    ,matches_data:pd.DataFrame)-> pd.DataFrame:

    df =(bolls_data
        .loc[lambda _df: _df.inning==2]
        .merge(matches_data
                        .loc[:,['id'
                                ,'city'
                                ,'venue'
                                ,'winner']]
                        ,left_on='match_id'
                        , right_on='id')
    ).assign(result = lambda _df: np.where(_df.winner==_df.batting_team,1,0))
    return df[['batting_team'
            ,'bowling_team'
            ,'city'
            ,'chase_target'
            ,'current_sore'
            ,'run_rate'
            ,'ball_left'
            ,'wickets_left'
            ,'runs_left'
            #,'req_rate'
            ,'result'
            ]]