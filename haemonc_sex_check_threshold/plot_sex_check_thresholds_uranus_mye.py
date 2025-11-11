#!/usr/bin/env python
"""
Sex_check thresholds for uranus. 
"""
import argparse
import pandas as pd
import plotly.express as px
from typing import Dict, Tuple
import os 
import json
import numpy as np

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Process and plot sex_check thresholds for MYE assays."
    )

    parser.add_argument(
        "--samples_tsv", required=True, help="Path to samples tsv in the testing project."
    )
    return parser.parse_args()

def read_samples(samples_tsv):
    """
    Read Uranus samples from a tsv file.
    Args:
        samples_tsv (str): Path to the samples tsv file.
    Returns:
        pd.DataFrame: df of sample data containing sample , validation run and sample_id.
    """
    # make dataframe of samples 
    df = pd.read_csv(samples_tsv, sep='\t',header=None) # file has no column names 
    df.columns = ['samples', 'validation_run']
    df['sample_id']=df['samples'].str.rsplit('-', n=4,expand=True)[0]
    # Confirm no duplicates
    assert len(df) == len(df.samples.unique())
    return df

def read_sex_check_json():
    """
    Read  sex check results in a json file from sex_check_res subfolder .
    Returns:
        pd.DataFrame: 
        df of sample data containing sample , score and reported sex. 
    """
    # get current working dictionary and save in list
    list_files= os.listdir('sex_check_res')
    list_score_to_plot=[]
    # read each json file in loop to extract sample, score and reported sex 
    for file  in list_files :
        if file.endswith('.json'):
            file=os.getcwd() + '/sex_check_res/'+file
            with open(file, 'r') as file:
                data = json.load(file)
                sample = list(data['data'])[0]
                score = data['data'][sample].get('score')
                sex_reported = data['data'][sample].get('reported_sex')
                tuples_samples_scores = (sample,score,sex_reported)
                list_score_to_plot.append(tuples_samples_scores)                                         
    score_df=pd.DataFrame.from_records(list_score_to_plot)
    score_df.columns = ['samples', 'score','reported_sex']
    return score_df

def plot_score(sample_score_df, sample_df):
    """
    Read  2 dataframes ( the left dataframes contains scores ) and aggregate information to form one datafraame for plotting
    Args:
        sample_score_df (df): samples dataframe with score from read_sex_check_json() output.
        sample_df (df): samples dataframe without score from read_samples() output .
    Returns:
        pd.DataFrame: df of sample data containing sample , validation run and sample_id.
    """
    sample_score_df.set_index(['samples'], inplace=True, drop=False)
    # iterate over rows to get sample , validation and sample id to dictionary
    validation_dict= {}
    for index, row in sample_df.iterrows():
        sample = row['samples'] 
        validation=row['validation_run']
        validation_dict[sample] = [validation, row['sample_id']]
    # insert validation and sample id into the df
    for sample, val in validation_dict.items():
        sample_score_df.loc[sample,'validation_run'] = val[0]
        sample_score_df.loc[sample,'sample_id'] = val[1]
    return sample_score_df

def histo_score(df,outliers,male_threshold=None, female_threshold=None):
    """
    Plot filtered aggregated scores dataframe generated 
    Args:
        df (pd.Dataframe): dataframe containing scores and validation run 
        outliers (str): name of plot title and html file
        male_threshold (int) : +/- 3SD
        female_threshold (int) : -/+ 3SD 
    """
    if male_threshold is not None and female_threshold is not None:
        fig = px.histogram(
        df,
        x="score",
        color="reported_sex",
        marginal="box",
        nbins=50, 
        hover_data=['samples','score','reported_sex',"validation_run"]   
        ) 
        # Add threshold lines
        fig.add_vline(
        x= male_threshold,
        line_width=1,
        line_dash="dash",
        annotation_text=f"male_threshold: {male_threshold} (2.d.p)",
        annotation_position="top left"
        )
        fig.add_vline(
        x=female_threshold,
        line_width=1,
        line_dash="dash",
        annotation_text=f"female_threshold: {female_threshold} (2.d.p) "
        )
        fig.update_layout(
        width=900, height=600,
        title=f"Distribution of sex check scores for MYE samples(thresholds calculated {outliers})"
        )
        fig.show()
        fig.write_html(f"distribution_of_scores_MYE_(thresholds calculated {outliers}).html")

   
def score_trend(df,outliers, male_threshold=None, female_threshold=None):
    """
    Plot filtered aggregated scores dataframe 
    Args:
        df (pd.Dataframe): dataframe containing scores and validation run 
        outliers (str): name of plot title and html file
        male_threshold (int) : +/- 3SD
        female_threshold (int) : -/+ 3SD 
    """
    if male_threshold is not None and female_threshold is not None:
        fig = px.scatter(
        df,
        x="sample_id",
        y="score",
        color="reported_sex",
        hover_data=['samples','score','reported_sex',"validation_run"] 
        )
        # Add threshold lines
        fig.add_hline(
        y=male_threshold,
        line_width=1,
        line_dash="dash",
        annotation_text=f"male_threshold: {male_threshold} (2d.p.)",
        annotation_position="top right",
        )
        fig.add_hline(
        y=female_threshold,
        line_width=1,
        line_dash="dash",
        annotation_text=f"female_threshold: {female_threshold} (2d.p.)",
        annotation_position="bottom right",
        )
        fig.update_layout(
        width=900, height=600,
        title=f"Trends of sex check scores for MYE Samples (thresholds calculated {outliers})"
        )
        fig.update_traces(textposition='top center')
        fig.update_xaxes(tickmode='linear')
        fig.show()
        fig.write_html(f"sex_check_thresholds_MYE_(thresholds calculated {outliers}).html")
        
def mean_and_sd_male_and_female_y_score(df):
    """
    Reads  a dataframe (containing scores and validation runs ) and calculate the thresholds.
    Args:
        df (df): samples dataframe with score and validation runs.
    Returns:
        dict: containing the +/-3SD suggested thresholds 
    """
    mean_m_yscore= df.loc[df['reported_sex'] == 'M','score'].mean()
    mean_f_yscore= df.loc[df['reported_sex'] == 'F','score'].mean()
    sd_m_yscore= df.loc[df['reported_sex'] == 'M','score'].std()
    sd_f_yscore= df.loc[df['reported_sex'] == 'F','score'].std()

    male_plus_3sd= mean_m_yscore + 3 * sd_m_yscore
    male_minus_3sd= mean_m_yscore - 3 * sd_m_yscore
    female_plus_3sd=mean_f_yscore + 3 * sd_m_yscore
    female_minus_3sd= mean_f_yscore - 3 * sd_f_yscore

    print(f"male: mean ({mean_m_yscore}) + 3sd = { male_plus_3sd}\n" 
            f"male: mean ({mean_m_yscore}) - 3sd  = {male_minus_3sd}\n" 
            f"female: mean ({mean_f_yscore}) + 3sd ={female_plus_3sd}\n" 
            f"female: mean ({mean_f_yscore}) - 3sd = {female_minus_3sd} ")
    return({'male_mean':mean_m_yscore , 'male_plus_3sd':male_plus_3sd,'male_minus_3sd': male_minus_3sd, 
     'female_mean':mean_f_yscore , 'female_plus_3sd': female_plus_3sd , 'female_minus_3sd': female_minus_3sd
       })

def remove_repeat_samples(df):
    """
    Reads  a dataframe (containing scores and validation runs ) and remove samples with identical ids and sample ids ending with B , C and some A based on conditions.
    Args:
        df (df): samples dataframe with score and validation.
    Returns:
        pd.DataFrame: a datframe with unique sample ids and without sample ids ending with B C and 01A  or [2-9]A . Rescued  TruQ7A-TruQ7A in last row. 
    """ 
    df_no_dups=df.drop_duplicates(subset=['sample_id'],keep='first', inplace=False )
    print('Number of samples with unique sample IDs',len(df_no_dups), sep=':') 
    df_no_repeats= df_no_dups[~df_no_dups['sample_id'].str.endswith(('B','C'))] 
    #removed further repeats                                                                                                                                                                                                                                                                 
    df_exclude_repeats_ending_with_A=df_no_repeats[~df_no_repeats['sample_id'].str.fullmatch('([A-Za-z0-9]+-[A-Za-z0-9]+)(01A$|[2-9]A$)')]
    # save unique id TruQ7A-TruQ7A
    df_all_repeats_removed=pd.concat([df_exclude_repeats_ending_with_A, df_no_repeats[df_no_repeats['sample_id']== 'TruQ7A-TruQ7A']])
    return df_all_repeats_removed
  
def remove_outliers(df , keep_male_outliers):
    """
    Reads a dataframe with unique samples and removes outliers which are visualised outside the box and whiskers plot.
    Always remove the female outlier regardless of the value for keep_male_outliers argument 
    Args:
        df (df): samples dataframe with score and validation.
        keep_male_outliers (boolean) : if true the function filters the female outlier only. If false the function filters out all outliers 
    Returns:
        pd.DataFrame: a datframe without outliers  to be used to calculate thresholds 
    """
    if keep_male_outliers is False:
        df_no_outliers=df[~((df['sample_id'] == '133214140-24296K0004') 
                            | (df['sample_id'] == '128315136-24051K0081')
                            | (df['sample_id'] == '128218817-24047K0063')
                            | (df['sample_id'] == '133658250-24318K0009')
                            | (df['sample_id'] == '128021629-24038K0020')) ]
        return df_no_outliers
    
    if keep_male_outliers is True: 
        # remove female outlier
        df_without_female_outlier=df[~(df['sample_id'] == '133214140-24296K0004') ]                       
        return df_without_female_outlier 

def main():
    args = parse_arguments()
    # read in samples,validation tsv 
    samples_df=read_samples(args.samples_tsv)
    score_df=read_sex_check_json()
    # make df for histogram and scatter plot 
    score_plot=plot_score(score_df,samples_df)
    print('Number of samples before filtering for repeats and outliers', len(score_plot),sep=':')
    num_samples_prefilter=len(score_plot)

    # remove identical sample ids, repeat samples B , C and some A
    score_plot=remove_repeat_samples(score_plot)
    num_samples_postfilter_repeats=len(score_plot)
    score_plot.to_csv('new_panel_all_unique_samples_score_plot.csv')
    # sense check filer of repeats
    print('Number of samples after filtering for repeats', len(score_plot),sep=':')  

    # sense check number of unknown samples
    print('Number of samples with reported sex as unknown:',len(score_plot[~((score_plot['reported_sex'] == 'M') | (score_plot['reported_sex'] == 'F'))]))
    score_plot_filtered=score_plot[(score_plot['reported_sex'] == 'M') | (score_plot['reported_sex'] == 'F')]
    #sense check filter of unknown samples
    print('Number of samples reported male and female:',len(score_plot_filtered))   

    # remove female outlier sample from dataframe 
    df_without_female_outlier=remove_outliers(score_plot_filtered , keep_male_outliers=True)   

    # remove female outlier only
    if '133214140-24296K0004' not in df_without_female_outlier['sample_id']: 
        print('Number of unique samples reported male or female after filtering for female outlier ',len(df_without_female_outlier),sep=':')  
        # calculate thresholds
        threshold=mean_and_sd_male_and_female_y_score(df_without_female_outlier)
        female=threshold['female_minus_3sd']
        male=threshold['male_plus_3sd']
        female= round(female,2)
        male=round(male,2)
        #write out dataset used to calculate thresholds
        df_without_female_outlier.to_csv('df_without_female_outlier.csv')
        # plotting 
        histo_score(df_without_female_outlier , 'without_female_outlier', male_threshold=male, female_threshold= female)
        score_trend(df_without_female_outlier, 'without_female_outlier',male_threshold=male, female_threshold= female)

    # remove all outliers 
    df_all_outliers_removed=remove_outliers(score_plot_filtered , keep_male_outliers=False)
    print('Number of unique samples reported male or female after filtering for all outliers ',len(df_all_outliers_removed),sep=':') 
    threshold=mean_and_sd_male_and_female_y_score(df_all_outliers_removed)
    female=threshold['female_minus_3sd']
    male=threshold['male_plus_3sd']
    female= round(female,2)
    male=round(male,2)
    df_all_outliers_removed.to_csv('df_all_outliers_removed.csv')
    frequency={'count_total_sample':num_samples_prefilter,
        'count_unique_sample_count':num_samples_postfilter_repeats,
        'count_unique_samples_with_male_and_female':len(score_plot_filtered)}
    pd.DataFrame([frequency]).to_csv('frequency_samples.csv')
    #plotting
    histo_score(score_plot_filtered , 'without_outliers', male_threshold=male, female_threshold= female)
    score_trend(score_plot_filtered, 'without_outliers',male_threshold=male, female_threshold= female)

if __name__ == "__main__":
    main()
