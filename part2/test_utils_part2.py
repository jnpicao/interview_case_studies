import pytest
import pandas as pd
from utils_part2 import clean_csv, Node

df_list = [
    pd.DataFrame(
        {'GAME_NAME': {0: 'The Elder Scrolls V Skyrim',
                       1: 'The Elder Scrolls V Skyrim',
                       2: 'Fallout 4',
                       3: 'Fallout 4',
                       4: 'Fallout 4',
                       5: 'Spore',
                       6: 'Spore',
                       7: 'Spore',
                       8: 'Fallout New Vegas'}
         }
        ),
    pd.DataFrame(
        {'GAME_NAME': {0: 'The Elder Scrolls V Skyrim',
                        1: 'The Elder Scrolls V Skyrim',
                        2: 'Fallout 4',
                        3: 'Fallout 4',
                        4: 'Fallout 4',
                        5: 'Spore',
                        6: 'Spore',
                        7: 'Spore',
                        8: 'Fallout New Vegas'},
            'BEHAVIOUR': {0: 'purchase',
                        1: 'play',
                        2: 'purchase',
                        3: 'purchase',
                        4: 'play',
                        5: 'purchase',
                        6: 'play',
                        7: 'play',
                        8: 'purchase'},
            'ID': {0: 151603712,
                1: 151603712,
                2: 151603712,
                3: 151603712,
                4: 151603712,
                5: 151603712,
                6: 151603712,
                7: 151603712,
                8: 151603712}
            }
    )
]


def test_drop_duplicates():
    
    for df in df_list:
        df_in = df.copy()
        df_out_expected = df_in.drop_duplicates(ignore_index=True)
        
        tree = Node(df_in.columns.to_list())
        tree.add_table(df_in)
        
        df_out_actual = tree.tree_to_df(duplicates ='drop')
        
        pd.testing.assert_frame_equal(df_out_actual, df_out_expected, check_dtype=False)



def test_add_table():
    
    for df in df_list:
        df_in = df.copy()
        df_out_expected = df.copy()
        
        tree = Node(df_in.columns.to_list())
        tree.add_table(df_in)
        
        df_out_actual = tree.tree_to_df(duplicates ='ignore')
        
        pd.testing.assert_frame_equal(df_out_actual, df_out_expected, check_dtype=False)        
        