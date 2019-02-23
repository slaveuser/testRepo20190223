from mindsdb.libs.constants.mindsdb import *

from mindsdb.libs.helpers.logging import logging

class TransactionOutputData():

    def __init__(self, predicted_columns=[], columns_map = {}):
        self.data_array = []
        self.columns = []
        self.predicted_columns = predicted_columns
        self.columns_map = columns_map

    def _getOrigColum(self, col):

        for orig_col in self.columns_map:
            if self.columns_map[orig_col] == col:
                return orig_col

        return col

    @property
    def predicted_values(self, as_list=False, add_header = False):
        """
        Get an array of dictionaries (unless as_list=True) for predicted values
        :return: predicted_values
        """
        ret = []

        # foreach row in the result extract only the predicted values
        for row in self.data_array:

            # prepare the result, either a dict or a list
            if as_list:
                ret_row = []
            else:
                ret_row = {}

            # append predicted values
            for col in self.predicted_columns:
                col_index = self.columns.index(col)
                if as_list:
                    ret_row += [row[col_index]]
                else:
                    ret_row[self._getOrigColum(col)] = row[col_index]


            # append confidence
            col_index = self.columns.index(KEY_CONFIDENCE)
            if as_list: # add confidence if its a dictionary
                ret_row += row[col_index]
            else:
                if len(row) < col_index:
                    logging.warning('Output is smaller than expected, see transaction_output_data.py')
                    ret_row[KEY_CONFIDENCE] = 0
                else:
                    try:
                        ret_row[KEY_CONFIDENCE] = row[col_index]
                    except:
                        ret_row[KEY_CONFIDENCE] = 0

            # append row to result
            ret += [ret_row]

        # if add_header and as_list True, add the header to the result
        if as_list and add_header:
            header = [self._getOrigColum(col) for col in self.predicted_columns] + [KEY_CONFIDENCE]
            ret = [header] + ret

        return ret
