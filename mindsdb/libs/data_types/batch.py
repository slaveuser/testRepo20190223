"""
*******************************************************
 * Copyright (C) 2017 MindsDB Inc. <copyright@mindsdb.com>
 *
 * This file is part of MindsDB Server.
 *
 * MindsDB Server can not be copied and/or distributed without the express
 * permission of MindsDB Inc
 *******************************************************
"""

from mindsdb.libs.constants.mindsdb import *
import numpy as np
import torch
import logging
import traceback

class Batch:
    def __init__(self, sampler, data_dict, mirror = False, group=None, column=None, start=None, end=None):
        """

        :param sampler: The object generating batches
        :type sampler: libs.data_types.sampler.Sampler
        :param data_dict: the actual data
        :param mirror: if you want input and target to be the same
        """
        self.data_dict = data_dict
        self.sampler = sampler
        self.mirror = mirror
        self.number_of_rows = None
        self.blank_columns = []

        # these are pointers to trace it back to the original data
        self.group_pointer = group
        self.column_pointer = column
        self.start_pointer = start
        self.end_pointer = end

        # some usefule variables, they can be obtained from sambpler and metada but its a pain, so we keep them here
        self.target_column_names = self.sampler.meta_data.predict_columns
        self.input_column_names = [col for col in self.sampler.model_columns if col not in self.target_column_names]

        # This is the template for the response
        ret = {'input':{}, 'target':{}}

        # this may change as we have more targets
        # TODO: if the target is * how do we go about it here
        # Ideas: iterate over the missing column

        # populate the ret dictionary,
        # where there are inputs and targets and each is a dictionary
        # with key name being the column and the value the column data
        for col in self.sampler.model_columns:
            # this is to populate always in same order
            if col not in self.data_dict:
                continue

            if self.mirror:
                ret['target'][col] = self.data_dict[col]
                ret['input'][col] = self.data_dict[col]

            elif col in self.sampler.meta_data.predict_columns:
                ret['target'][col] = self.data_dict[col]
            else:
                ret['input'][col] = self.data_dict[col]

            if self.number_of_rows is None:
                self.number_of_rows = self.data_dict[col][0].size


        self.xy = ret

        return

    def getColumn(self, what, col, by_buckets = False):

        if by_buckets and self.sampler.stats[col][KEYS.DATA_TYPE]==DATA_TYPES.NUMERIC:
            col_name = EXTENSION_COLUMNS_TEMPLATE.format(column_name=col)
            if col_name in self.data_dict:
                ret = self.data_dict[col_name]
            else:
                raise Exception('No extension column {col}'.format(col=col_name))
            return ret
        else:
            ret = self.xy[what][col]
        if col in self.blank_columns:
            return np.zeros_like(ret)
        return ret

    def get(self, what, flatten = True, by_buckets = False):
        ret = None
        if flatten:
            # make sure we serialize in the same order that input metadata columns
            for col in self.sampler.model_columns:
                if col not in self.xy[what]:
                    continue

                # do not include full text as its a variable length tensor, which we cannot wrap
                if self.sampler.stats[col][KEYS.DATA_TYPE] == DATA_TYPES.FULL_TEXT:
                    continue

                # make sure that this is always in the same order, use a list or make xw[what] an ordered dictionary
                if ret is None:
                    ret = self.getColumn(what,col, by_buckets)
                else:
                    ret = np.concatenate((ret, self.getColumn(what,col, by_buckets)), axis=1)

            if self.sampler.variable_wrapper is not None:
                return self.sampler.variable_wrapper(ret)
            else:
                return ret

        if self.sampler.variable_wrapper is not None:
            ret = {}
            for col in self.xy[what]:
                if self.sampler.stats[col][KEYS.DATA_TYPE] == DATA_TYPES.FULL_TEXT:
                    continue
                try:
                    ret[col] = self.sampler.variable_wrapper(self.getColumn(what,col, by_buckets))
                except:
                    logging.error(traceback.format_exc())
                    raise ValueError('Could not decode column {what}:{col}'.format(what=what, col=col))
            return ret
        else:
            return self.xy[what]

    def getFullTextInput(self):
        """
        TODO: mOVE THE WRAPPER function to the model, so we can keep this batch framework agnostic
        :return:
        """
        what = 'input'
        ret = {}
        for col in self.sampler.model_columns:
            if col not in self.xy[what] or self.sampler.stats[col][KEYS.DATA_TYPE] != DATA_TYPES.FULL_TEXT:
                continue

            ret[col] = [torch.tensor(row, dtype=torch.long).view(-1, 1) for row in self.getColumn(what, col)]



        return ret



    def getInput(self, flatten = True):
        return self.get('input', flatten)


    def getTarget(self, flatten = True, by_buckets = False):
        return self.get('target', flatten, by_buckets)

    def deflatTarget(self, flat_vector):
        ret = {}
        start = 0
        for col in self.sampler.model_columns:
            # this is to populate always in same order

            if col in self.sampler.meta_data.predict_columns:
                end = self.data_dict[col].shape[1] # get when it ends
                ret[col] = flat_vector[:,start:end]
                start = end

        return ret

    def getTargetStats(self):

        stats = {}

        for col in self.sampler.meta_data.predict_columns:
            stats[col] = self.sampler.stats[col]

        return stats

    def getInputStats(self):

        stats = {}

        for col in self.sampler.model_columns:
            if col not in self.sampler.meta_data.predict_columns:
                stats[col] = self.sampler.stats[col]

        return stats


    def size(self):
        return self.number_of_rows







