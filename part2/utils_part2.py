import csv
import os
import re

from collections import OrderedDict

from typing import List

import pandas as pd

input_file_path = os.path.join('..', 'algorithms part dataset', 'smpl.csv')

def csv_remove_duplicates(input_file_path=None, drop_header=False,
                          cols_to_drop=[4], chars_to_remove = ['"', ';']):
    
    with open(input_file_path, newline='') as csvfile:
        
        reader = csv.reader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_NONE)
        
        # Initializations
        current_row_idx = -1
        final_list_of_rows = []
        dups_cnt = 0
        dups_idx_list = []
        
        
        if drop_header:
            next(reader)
            current_row_idx += 1       
        
            
        for row in reader:
            current_row_idx += 1
            #remove unwanted chars
            row_cln = row.copy()
            for char in chars_to_remove:
                row_cln = list(map(lambda x: x.replace(char,''), row_cln))
            
            final_row = []
            for idx in range(len(row_cln)):
                if idx not in cols_to_drop:
                    final_row.append(row_cln[idx])
                    
            # Ignore empty rows
            if len(final_row) == 0:
                continue
            
            if final_row in final_list_of_rows:
                dups_cnt +=1
                dups_idx_list.append(current_row_idx)
            else:
                final_list_of_rows.append(final_row)
            
            print(current_row_idx)
            #print(row)
            #print(row_cln)
            print(final_row)
        
    output_file_path = input_file_path.replace('.csv','_output.csv')
    with open(output_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL) # 
        
        for row in final_list_of_rows:
            writer.writerow(row)        
    
    return current_row_idx, dups_cnt, dups_idx_list
    


def clean_csv_old(input_file_path=None, chars_to_remove = ['"', ';']):
    
    with open(input_file_path, newline='') as csvfile:
        
        reader = csv.reader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_NONE)

        # Initializations
        final_list_of_rows = []

        for row in reader:
            row_cln = row.copy()
            for char in chars_to_remove:
                row_cln = list(map(lambda x: x.replace(char,''), row_cln))

            final_list_of_rows.append(row_cln)
            
    
    output_file_path = input_file_path.replace('.csv','_cln.csv')
    
    with open(output_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        for row in final_list_of_rows:
            writer.writerow(row)
            

def clean_csv(input_file_path=None, chars_to_remove = ['"', ';']):
    
    # Read input file
    with open(input_file_path, newline='') as input_file:
        
        line_list = input_file.readlines()
    
    # Output to temp file
    output_file_path = input_file_path.replace('.csv','_cln.csv')
    
    with open(output_file_path, 'w') as output_file:
        
        for line in line_list:
            
            cln_row = line
            # remove first quote
            cln_row = re.sub(r'^"', '', cln_row)
            # replace \r\n by \n ate end of file
            cln_row = re.sub(r'\r\n$', r'\n', cln_row)
            # remove last semicolon
            cln_row = re.sub(r';\n$', r'\n', cln_row)
            cln_row = re.sub(r';$', r'', cln_row)            
            # remove last quote
            cln_row = re.sub(r'"\r\n$', '\r\n', cln_row)
            cln_row = re.sub(r'"$', '', cln_row)
            # replace double quotes by single quotes
            cln_row = re.sub(r'""', '"', cln_row)
            
            output_file.write(cln_row)


class Node:
    def __init__(self, node_hierarchy: List[str], node_type: str = None, value = None):
        
        # No duplicates aloowed in node_hierarchy
        assert len(set(node_hierarchy)) == len(node_hierarchy), \
        "No duplicates allowed in node_hierarchy"
        
        self.node_hierarchy = node_hierarchy
        
        if node_type is None:
            self.node_type = 'root'
        else:
            self.node_type = node_type
        
        self.value = value        
        self.count_rows = 0
        self.children = []
    
    def add_table(self, df):
        
        for index, row in df.iterrows():
            self.add_row(row)            
        return
    
    def add_row(self, row):
        
        assert len(set(self.node_hierarchy) - set(row.index)) == 0, \
        "All node_hierarchy values must be row indexes"
        
        new_val = row[self.node_hierarchy[0]] 
        
        children_idx = self._get_children_value_idx(new_val)
        
        # print(f'Add value: {new_val}')
        
        if children_idx == -1:
            # Value seen for the first time
            self._create_children_node(new_val)
            
            # Update children index
            children_idx = len(self.children)-1
        
        # Update self rows count
        # print(self.node_type, self.value)
        # print(f"Current node type: {self.node_type}, and value: {self.value}")
        self.count_rows +=1

        children_nodes_hierarchy = self.node_hierarchy[1:]        
               
        if len(children_nodes_hierarchy) > 0:
            # Children are still trees: update hierarchy levels below
            self.children[children_idx].add_row(row)
        
        else:
            # Children are final nodes: Update rows count
            self.children[children_idx].count_rows += 1
            
        self._validate_row_counts()

    
    def print_tree(self, ident_count=0):
        
        print("    "*ident_count, self.node_type, self.value, self.count_rows, sep=' | ')
        
        if len(self.children) > 0:
            for child in self.children:
                child.print_tree(ident_count+1)

        return
    
        
    def print_table(self, row_values_dict={}, duplicates='drop', to=None, _depth=0):
        
        if _depth == 0:
            # first function iteration
            if to is None:
                pass
                
            elif isinstance(to, str):
                # overwrite file and insert column headers
                with open(to, "w") as myfile:
                    row_str = ';'.join(self.node_hierarchy) + '\n'
                    myfile.write(row_str)  
                

        if len(self.children) > 0:
            # Children are still trees
            for child in self.children:
                # Add current child's value to dictionary
                row_values_dict[child.node_type] = child.value
                
                child.print_table(row_values_dict, duplicates, to, _depth+1)
                
                # remove current child's value from list 
                del row_values_dict[child.node_type]
        
        else:
            # Children are are final nodes: print the complete row
            if duplicates == 'drop':
                # Print only one row
                self._print_row(row_values_dict, to)
                
            elif duplicates == 'ignore':
                # print all existing rows
                for row in range(self.count_rows):
                    self._print_row(row_values_dict, to)

            elif duplicates == 'find':
                # print duplicated rows only
                for row in range(self.count_rows-1):
                    self._print_row(row_values_dict, to)
        
        return
    
    
    def tree_to_df(self, duplicates='drop'):

        self.print_table(to='_temp_file.csv', duplicates=duplicates)
        df = pd.read_csv('_temp_file.csv', sep=';')
        #os.remove('_temp_file.csv')
        
        return df
    
    def _print_row(self, row_values_dict, to=None):

        if to is None:
            # print to stdout
            print(row_values_dict)
            
        elif isinstance(to, str):
            # print to file
            with open(to, "a") as myfile:
                #row_str = ','.join(str(value) for value in row_values_dict.values()) + '\n'
                row_str = ';'.join([str(value) for value in row_values_dict.values()]) + '\n'
                myfile.write(row_str)            
            
        return
    
    
    def _validate_row_counts(self):
        assert self.count_rows == self._sum_children_rows()
        # print(f"self.count_rows {self.count_rows}; self._sum_children_rows {self._sum_children_rows()}")
        
        if len(self.node_hierarchy) > 1:
            # Children are still trees
            for child in self.children:
                child._validate_row_counts()
        else:
            # Children are are final nodes
            pass
        
    
    def _sum_children_rows(self):
        total_sum = 0
        
        for child in self.children:
            total_sum += child.count_rows
        
        return total_sum
    
    
    def _get_children_value_idx(self, value_to_find):

        for idx, child in enumerate(self.children):
            if child.value == value_to_find:
                return idx

        return -1
    
    
    def _create_children_node(self, new_val):        
        
        # Children nodes' type equals the first level of current hierarchy
        children_nodes_type = self.node_hierarchy[0]
        
        # children nodes hierarchy have one less level
        children_nodes_hierarchy = self.node_hierarchy[1:]
        
        new_node = Node(node_hierarchy=children_nodes_hierarchy,
                        node_type = children_nodes_type,
                        value = new_val)

        hierarchy_diff = [h for h in self.node_hierarchy if h not in new_node.node_hierarchy]

        assert len(hierarchy_diff) == 1
        assert hierarchy_diff[0] == new_node.node_type
        assert self.node_hierarchy[1:] == new_node.node_hierarchy

        self.children.append(new_node)
        
        return 