import os
import json

import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


def load_data_to_df(input_path):
    
    df_data = pd.DataFrame(columns=['form', 'id', 'text', 'box_0', 'box_1',
                                    'box_2', 'box_3', 'label'])

    for file_path in os.listdir(input_path):
        
        input_file_path = os.path.join(input_path, file_path)
        json_df = pd.read_json(input_file_path)
        json_form = json.loads(json_df.to_json())['form']

        for text_id in json_form:

            box_0 = json_form[str(text_id)]['box'][0]
            box_1 = json_form[str(text_id)]['box'][1]
            box_2 = json_form[str(text_id)]['box'][2]
            box_3 = json_form[str(text_id)]['box'][3]
            
            text = json_form[str(text_id)]['text']
            label = json_form[str(text_id)]['label']

            df_new_row = pd.DataFrame({'form': [input_file_path],
                                       'id': [text_id],
                                       'box_0': [box_0],
                                       'box_1': [box_1],
                                       'box_2': [box_2],
                                       'box_3': [box_3],
                                       'text': [text],
                                       'label': [label]})

            df_data = pd.concat([df_data, df_new_row])
    
    df_data = df_data.reset_index(drop=True)
    
    for col in ['box_0', 'box_1', 'box_2', 'box_3']:
        df_data[col] = pd.to_numeric(df_data[col])
    
    return df_data


class CreateFeatures(BaseEstimator, TransformerMixin):
    # initializer 
    def __init__(self, text_col='text'):
        # save the features list internally in the class
        self.text_col = text_col
        
    def fit(self, X, y = None):
        return self 
    
    def transform(self, X, y = None):
        
        X_new = X.copy()
        
        X_new['text_len'] = self._feat_text_len(X_new)
        
        X_new['is_number'] = self._feat_is_number(X_new)
        
        X_new['final_colon'] = self._feat_final_colon(X_new)
        
        X_new['has_unit'] = self._feat_has_unit(X_new)
        
        X_new['is_date'] = self._is_date(X_new)
        
        X_new['digit_ratio'] = self._feat_digit_ratio(X_new)        
        
        return X_new
    
    
    def _feat_text_len(self, X, y = None):
        
        new_feat = X[self.text_col].copy().str.len().fillna(0)
        
        return new_feat
    
    def _feat_is_number(self, X, y = None):
        
        new_feat = (pd.to_numeric((X[self.text_col].copy()
                                   .str.replace("*", "", regex=False)),
                                  errors='coerce')
                    .notna().astype('int8'))
        
        return new_feat
    
    def _feat_final_colon(self, X, y = None):
        
        new_feat = (X[self.text_col].copy()
                    .str.rstrip().str[-1:].eq(':').astype('int8'))
        
        return new_feat
    
    def _feat_has_unit(self, X, y = None):
        
        unit_name_list = [r'millimeter', r'centimeter', r'meter', r'inch',
                          r'inche', r'feet', r'yard', r'liter', r'gallon',
                          r'gram', r'milligram', r'kilogram', r'tonne',
                          r'pound', r'ounce']
        
        unit_symbol_list = [r'mm', r'cm', r'm', r'ft', r'yd', r'ltr', r'in',
                            r'gal', r'g', r'mg', r'kg', r't', r'lb', r'oz']
        
        unit_list = unit_name_list + unit_symbol_list
        
        regex_pat_list = [r'\d\s*' + unit + r's?\b' for unit in unit_list]
        regex_pat_str = r'|'.join(regex_pat_list)
        
        new_feat = (X[self.text_col].copy()
                    .str.contains(regex_pat_str, regex=True).fillna(False).astype('int8'))
        
        return new_feat
    
    def _feat_digit_ratio(self, X, y = None):
        
        X_text_original = X[self.text_col].copy()
        
        new_feat = (X_text_original.str.count('\d')
                    .div(X_text_original.str.len())
                    .fillna(0))
        
        return new_feat
        
    def _is_date(self, X, y = None):
        
        new_feat = (pd.to_datetime(X[self.text_col].copy().str.replace('EST|CET|CST|CEST', '', regex=True),
                                   errors='coerce')
                    .notna().astype('int8'))

        return new_feat


class TextCleaner(TransformerMixin):
    def __init__(self, text_col='text'):        
        self.text_col = text_col
        
    def fit(self, *_):
        return self
        
    def transform(self, X, *_):
        
        X_new = X.copy()        
        X_new[self.text_col] = self._clean_text(X_new[self.text_col])
        
        return X_new[self.text_col]
    
    def _clean_text(self, X, y = None):
        
        new_feat = X.copy()
        new_feat = new_feat.astype(str)        
        new_feat = new_feat.str.lower()
        new_feat = X.copy().str.replace('[^\w\s]', '', regex=True) 
        new_feat = new_feat.fillna('')
        
        return new_feat
    

class Selector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a column from the dataframe to perform additional transformations on
    """ 
    def __init__(self, cols_to_drop=[]):
        self.cols_to_drop = cols_to_drop
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        # Drop the column containing the original text            
        return X.drop(columns=self.cols_to_drop)
    
