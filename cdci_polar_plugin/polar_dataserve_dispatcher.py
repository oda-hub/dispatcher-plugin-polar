"""
Overview
--------
   
general info about this module


Classes and Inheritance Structure
----------------------------------------------
.. inheritance-diagram:: 

Summary
---------
.. autosummary::
   list of the module you want
    
Module API
----------
"""

from __future__ import absolute_import, division, print_function

from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object, map, zip)

__author__ = "Andrea Tramacere"

# Standard library
# eg copy
# absolute import rg:from copy import deepcopy
import  ast
import requests
# Dependencies
# eg numpy 
# absolute import eg: import numpy as np
import json

# Project
# relative import eg: from .mod import f
import  logging
import  simple_logger
from cdci_data_analysis.analysis.queries import  *
from cdci_data_analysis.analysis.job_manager import  Job
from cdci_data_analysis.analysis.io_helper import FilePath
from cdci_data_analysis.analysis.products import  QueryOutput
import json
import traceback
import time
from ast import literal_eval
import os
from contextlib import contextmanager

# @contextmanager
# def silence_stdout():
#     new_target = open(os.devnull, "w")
#     old_target, sys.stdout = sys.stdout, new_target
#     try:
#         yield new_target
#     finally:
#         sys.stdout = old_target
#
#
#
# def redirect_out(path):
#     #print "Redirecting stdout"
#     sys.stdout.flush() # <--- important when redirecting to files
#     newstdout = os.dup(1)
#     devnull = os.open('%s/SED.log'%path, os.O_CREAT)
#     os.dup2(devnull, 1)
#     os.close(devnull)
#     sys.stdout = os.fdopen(newstdout, 'w')

#def view_traceback():
#    ex_type, ex, tb = sys.exc_info()
#    traceback.print_tb(tb)
#    del tb





class PolarAnalysisException(Exception):

    def __init__(self, message='Polar analysis exception', debug_message=''):
        super(PolarAnalysisException, self).__init__(message)
        self.message=message
        self.debug_message=debug_message



class PolarException(Exception):

    def __init__(self, message='Polar analysis exception', debug_message=''):
        super(PolarException, self).__init__(message)
        self.message=message
        self.debug_message=debug_message


class PolarUnknownException(PolarException):

    def __init__(self,message='polar unknown exception',debug_message=''):
        super(PolarUnknownException, self).__init__(message,debug_message)




class PolarDispatcher(object):

    def __init__(self,config=None,task=None,param_dict=None):
        print('--> building class PolarDispatcher')
        #temp = vars(config)
        #for item in temp:
        #    print(item, ' : ', temp[item])
        simple_logger.log()
        simple_logger.logger.setLevel(logging.ERROR)

        self.task = task

        self.param_dict = param_dict
        if config is not None:
            try:

                self.data_server_url = config.dataserver_url
                self.dataserver_cache = config.dataserver_cache
                self.data_server_port = config.data_server_port
            except Exception as e:
                #print(e)

                print ("ERROR->")
                raise RuntimeError("failed to use config ", e)

        else:
            self.config()





        print("data_server_url:", self.data_server_url)
        #print("dataserver_cache:", self.dataserver_cache)
        print("dataserver_port:", self.data_server_port )
        print('--> done')



    def config(self):
        self.data_server_name='polar'
        self.data_server_locan_mnt_cache=None
        self.data_server_remote_cache=None
        self.dummy_cache='dummy_prods'
        self.data_server_url= 'http://cdcihn.isdc.unige.ch:8893'
        self.data_server_port= 8893
        self.dataserver_url = 'http://%s:%d' % (self.data_server_url, self.data_server_port)
        print ('DONE CONF',self.data_server_url)
        #if self.data_server_local_cache is not None:
        #    FilePath(file_dir=self.data_server_local_cache).mkdir()

        #    self.dataserver_cache=os.path.join(self.data_server_remote_cache,self.data_server_local_cache)
        #else:
        #    self.dataserver_cache=None




    def test_communication(self, max_trial=120, sleep_s=1,logger=None):
        print('--> start test connection')

        query_out = QueryOutput()


        message='connection OK'
        debug_message = ''
        busy_exception=False


        connection_status_message = 'OK'
        query_out.set_done(message='connection OK', debug_message=str(debug_message))


        print('--> end test busy')

        return query_out

    def test_has_input_products(self,instrument,logger=None):


        query_out = QueryOutput()


        message = 'OK'
        debug_message = 'OK'

        query_out.set_done(message=message, debug_message=str(debug_message))



        return query_out,[1]




    def _run_test(self,t1=1482049941, t2=1482049941+100, dt=0.1, e1=10, e2=500):
        return requests.get("http://cdcihn.isdc.unige.ch:8893/api/v1.0/lightcurve/",
                            params=dict(
                                time_start=t1,
                                time_stop=t2,
                                time_bin=dt,
                                energy_min=e1,
                                energy_max=e2,
                            ))

    def _run(self,data_server_url,port,task,param_dict):
        print ('ciccio')
        try:
            url="%s/%s"%(data_server_url,task)
            print ('url',url)
            res = requests.get("%s" % (url),params=param_dict)
        except Exception as e:

            raise PolarAnalysisException(message='Polar Analysis error', debug_message=e)

        return res

    def run_query(self,call_back_url=None,run_asynch=False,logger=None,task=None,param_dict=None,):

        res = None
        # status = 0
        message = ''
        debug_message = ''
        query_out = QueryOutput()


        if task is None:
            task=self.task

        if param_dict is None:
            param_dict=self.param_dict



        try:

            simple_logger.logger.setLevel(logging.ERROR)


            print('--Polar disp1--')
            print('call_back_url',call_back_url)
            print('data_server_url', self.data_server_url)
            print('*** run_asynch', run_asynch)

            res =self._run(self.data_server_url,self.data_server_port,task,param_dict)
            #res =self._run_test()

            #DONE
            query_out.set_done(message=message, debug_message=str(debug_message),job_status='done')

            #job.set_done()

        except PolarAnalysisException  as e:

            run_query_message = 'Polar AnalysisException in run_query'
            debug_message=e.debug_message

            query_out.set_failed('run query ',
                                 message='run query message=%s' % run_query_message,
                                 logger=logger,
                                 excep=e,
                                 job_status='failed',
                                 e_message=run_query_message,
                                 debug_message=debug_message)

            raise PolarException(message=run_query_message,debug_message=debug_message)

        except Exception as e:
            run_query_message = 'Polar UnknownException in run_query'
            query_out.set_failed('run query ',
                                 message='run query message=%s' % run_query_message,
                                 logger=logger,
                                 excep=e,
                                 job_status='failed',
                                 e_message=run_query_message,
                                 debug_message=e)

            raise PolarUnknownException(message=run_query_message,debug_message=e)

        return res,query_out


