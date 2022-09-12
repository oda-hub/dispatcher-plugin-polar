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

from __future__ import absolute_import, division, logging.info_function

from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object, map, zip)

__author__ = "Andrea Tramacere"

# Standard library
# eg copy
# absolute import rg:from copy import deepcopy
import requests
# Dependencies
# eg numpy 
# absolute import eg: import numpy as np

# Project
# relative import eg: from .mod import f
import logging
from cdci_polar_plugin import conf_file as plugin_conf_file
from cdci_data_analysis.configurer import DataServerConf
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
#     #logging.info "Redirecting stdout"
#     sys.stdout.flush() # <--- important when redirecting to files
#     newstdout = os.dup(1)
#     devnull = os.open('%s/SED.log'%path, os.O_CREAT)
#     os.dup2(devnull, 1)
#     os.close(devnull)
#     sys.stdout = os.fdopen(newstdout, 'w')

#def view_traceback():
#    ex_type, ex, tb = sys.exc_info()
#    traceback.logging.info_tb(tb)
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

    def __init__(self,config=None,task=None,param_dict=None,instrument=None):
        logging.info('--> building class PolarDispatcher',instrument,config)

        self.task = task

        self.param_dict = param_dict

        #logging.info ('TEST')
        #for k in instrument.data_server_conf_dict.keys():
        #   logging.info ('dict:',k,instrument.data_server_conf_dict[k ])

        config = DataServerConf(data_server_url=instrument.data_server_conf_dict['data_server_url'],
                              data_server_port=instrument.data_server_conf_dict['data_server_port'],
                              data_server_remote_cache=instrument.data_server_conf_dict['data_server_cache'],
                              dispatcher_mnt_point=instrument.data_server_conf_dict['dispatcher_mnt_point'],
                              dummy_cache=instrument.data_server_conf_dict['dummy_cache'])
        #for v in vars(config):
        #   logging.info('attr:', v, getattr(config, v))


        logging.info('--> config passed to init',config)

        if config is not None:

            pass



        elif instrument is not None and hasattr(instrument,'data_server_conf_dict'):

            logging.info('--> from data_server_conf_dict')
            try:
                #config = DataServerConf(data_server_url=instrument.data_server_conf_dict['data_server_url'],
                #                        data_server_port=instrument.data_server_conf_dict['data_server_port'])

                config = DataServerConf(data_server_url=instrument.data_server_conf_dict['data_server_url'],
                                        data_server_port=instrument.data_server_conf_dict['data_server_port'])
                                       # data_server_remote_cache=instrument.data_server_conf_dict['data_server_cache'],
                                       # dispatcher_mnt_point=instrument.data_server_conf_dict['dispatcher_mnt_point'],
                                       #s dummy_cache=instrument.data_server_conf_dict['dummy_cache'])

                logging.info('config', config)
                for v in vars(config):
                    logging.info('attr:', v, getattr(config, v))



            except Exception as e:
                #    #logging.info(e)

                logging.info("ERROR->")
                raise RuntimeError("failed to use config ", e)

        elif instrument is not None:
            try:
                logging.info('--> plugin_conf_file',plugin_conf_file )
                config=instrument.from_conf_file(plugin_conf_file)

            except Exception as e:
                #    #logging.info(e)

                logging.info("ERROR->")
                raise RuntimeError("failed to use config ", e)

        else:

            raise PolarException(message='instrument cannot be None',debug_message='instrument se to None in PolarDispatcher __init__')

        try:
            _data_server_url = config.data_server_url
            _data_server_port = config.data_server_port

        except Exception as e:
            #    #logging.info(e)

            logging.info("ERROR->")
            raise RuntimeError("failed to use config ", e)

        self.config(_data_server_url,_data_server_port)





        logging.info("data_server_url:", self.data_server_url)
        #logging.info("dataserver_cache:", self.dataserver_cache)
        logging.info("dataserver_port:", self.data_server_port )
        logging.info('--> done')



    def config(self,data_server_url,data_server_port):

        logging.info('configuring method')
        logging.info('config done in config method')

        self.data_server_url= data_server_url
        self.data_server_port= data_server_port

        logging.info ('DONE CONF',self.data_server_url)

    def test_communication(self, max_trial=120, sleep_s=1,logger=None):
        logging.info('--> start test connection')

        query_out = QueryOutput()


        message='connection OK'
        debug_message = ''
        busy_exception=False


        connection_status_message = 'OK'
        query_out.set_done(message='connection OK', debug_message=str(debug_message))


        logging.info('--> end test busy')

        return query_out

    def test_has_input_products(self,instrument,logger=None):


        query_out = QueryOutput()


        message = 'OK'
        debug_message = 'OK'

        query_out.set_done(message=message, debug_message=str(debug_message))



        return query_out,[1]




    def _run_test(self,t1=1482049941, t2=1482049941+100, dt=0.1, e1=10, e2=500):
        return requests.get("http://polar-worker:8893/api/v1.0/lightcurve/",
                            params=dict(
                                time_start=t1,
                                time_stop=t2,
                                time_bin=dt,
                                energy_min=e1,
                                energy_max=e2,
                            ))

    def _run(self,data_server_url,task,param_dict):

        try:
            url="%s/%s"%(data_server_url,task)
            logging.info ('url',url)
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

            logging.info('--Polar disp1--')
            logging.info('call_back_url',call_back_url)
            logging.info('data_server_url', self.data_server_url)
            logging.info('*** run_asynch', run_asynch)

            res =self._run(self.data_server_url,task,param_dict)
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


