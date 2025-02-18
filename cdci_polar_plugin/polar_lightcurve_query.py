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

__author__ = "Andrea Tramacere"

import logging
import numpy as np
import pandas as pd
import json

from cdci_data_analysis.analysis.queries import LightCurveQuery
from cdci_data_analysis.analysis.products import LightCurveProduct,QueryProductList,QueryOutput
from cdci_data_analysis.analysis.io_helper import FilePath
from oda_api.data_products import NumpyDataProduct,NumpyDataUnit,BinaryData
from cdci_data_analysis.configurer import DataServerConf

from .polar_dataserve_dispatcher import PolarDispatcher
from .polar_dataserve_dispatcher import  PolarAnalysisException


class DummyPolarRes(object):

    def __init__(self):
        pass
    def json(self):

        data = NumpyDataProduct.from_fits_file(self.dummy_lc)
        lc = data.get_data_unit_by_name('POLAR_LC')

        data = dict(rate=lc.data['rate'].tolist())
        data['rate_err'] = lc.data['rate_err'].tolist()
        data['time'] = lc.data['time'].tolist()
        data = json.dumps(data)
        _d = dict(data=data)
        _d['status'] = dict(success=True)
        _d['status']['exceptions']=[None]
        _d['root_file_b64']=self.dummy_root
        return _d

class PolarLigthtCurve(LightCurveProduct):
    def __init__(self,name,file_name,data,header,prod_prefix=None,out_dir=None,src_name=None,meta_data={}):


        if meta_data == {} or meta_data is None:
            self.meta_data = {'product': 'polar_lc', 'instrument': 'polar', 'src_name': src_name}
        else:
            self.meta_data = meta_data

        self.meta_data['time'] = 'time'
        self.meta_data['rate'] = 'rate'
        self.meta_data['rate_err'] = 'rate_err'



        super(LightCurveProduct, self).__init__(name=name,
                                               data=data,
                                               name_prefix=prod_prefix,
                                               file_dir=out_dir,
                                               file_name=file_name,
                                               meta_data=meta_data)


    @classmethod
    def build_from_res(cls,
                             res,
                             src_name='',
                             prod_prefix='polar_lc',
                             out_dir=None,
                             delta_t=None,
                             skip_root=False):



        lc_list = []

        if out_dir is None:
            out_dir = './'

        if prod_prefix is None:
            prod_prefix=''







        file_name =  src_name+'.fits'
        logging.info('file name',file_name)

        meta_data={}
        meta_data['src_name'] = src_name
        meta_data['time_bin'] = delta_t

        res_json = res.json()
        #logging.info(res_json)
        #logging.info(type(res_json))
        df = pd.read_json(res_json['data'])

        root_file_path= prod_prefix + '_' + src_name+'.root'
        root_file_path=FilePath(file_name=root_file_path,file_dir=out_dir)
        #NOTE np.array(df.to_records()) does not work with decoding in py27, because pandas puts the u in the dtyep name
        #NOTE works only if decoded with py36

        
        if res_json['status']['success']:
            data=np.zeros(len(df['rate']), dtype=[('rate', '<f8'), ('rate_err', '<f8'),('time', '<f8')])
            data['rate']=df['rate']
            data['rate_err'] = df['rate_err']
            data['time'] = df['time']
            npd = NumpyDataProduct(data_unit=NumpyDataUnit(data=data,
                                                           hdu_type='bintable',name='POLAR_LC'),meta_data=meta_data)

            lc = cls(name=src_name, data=npd, header=None, file_name=file_name, out_dir=out_dir, prod_prefix=prod_prefix,
                     src_name=src_name,meta_data=meta_data)


        else:
            logging.info("result",res) # logging?
            _d=res_json['status']
            logging.info('remote problem',_d)
            message = 'remote problem'
            if 'kind' in _d:
                message = _d['kind']
            elif 'exceptions' in _d:
                if _d['exceptions'][0]['kind'] is not None:
                    message = _d['exceptions'][0]['kind']
                if _d['exceptions'][0]['comment'] is not None:
                    message += ': ' + _d['exceptions'][0]['comment']
            raise PolarAnalysisException(message='polar light curve failed: %s'%_d, debug_message=message)


        if skip_root is False:
            try:
                open(root_file_path.path, "wb").write(BinaryData().decode(res_json['root_file_b64']))
                lc.root_file_path=root_file_path
                #lc.root_file_b64=res_json['root_file_b64']
            except Exception as e:
                logging.info(e)
                raise PolarAnalysisException(message='polar failed to open/decode root_file')
        else:
            lc.root_file_path=None

        lc_list.append(lc)

        return lc_list



class PolarLightCurveQuery(LightCurveQuery):

    def __init__(self, name):

        super(PolarLightCurveQuery, self).__init__(name)

    def build_product_list(self, instrument, res, out_dir, prod_prefix='polar',api=False):

        delta_t = instrument.get_par_by_name('time_bin')._astropy_time_delta.sec
        prod_list = PolarLigthtCurve.build_from_res(res,
                                                      src_name='lc',
                                                      prod_prefix=prod_prefix,
                                                      out_dir=out_dir,
                                                      delta_t=delta_t)

        # logging.info('spectrum_list',spectrum_list)

        return prod_list


    def get_data_server_query(self, instrument,
                              config=None):

        #scwlist_assumption, cat, extramodules, inject=OsaDispatcher.get_osa_query_base(instrument)
        E1=instrument.get_par_by_name('E1_keV').value
        E2=instrument.get_par_by_name('E2_keV').value
        src_name = instrument.get_par_by_name('src_name').value
        T1=instrument.get_par_by_name('T1')._astropy_time.unix
        T2=instrument.get_par_by_name('T2')._astropy_time.unix
        delta_t = instrument.get_par_by_name('time_bin')._astropy_time_delta.sec
        param_dict=self.set_instr_dictionaries(T1,T2,E1,E2,delta_t)

        #logging.info ('build here',config,instrument)
        q = PolarDispatcher(instrument=instrument,config=config,param_dict=param_dict,task='api/v1.0/lightcurve/')

        return q


    def set_instr_dictionaries(self, T1,T2,E1,E2,delta_t):
        return  dict(
            time_start=T1,
            time_stop=T2,
            time_bin=delta_t,
            energy_min=E1,
            energy_max=E2,
        )


    def process_product_method(self, instrument, prod_list,api=False):

        _names = []
        _lc_path = []
        _root_path=[]
        _html_fig = []

        _data_list=[]
        _binary_data_list=[]
        for query_lc in prod_list.prod_list:
            #logging.info('->name',query_lc.name)
            query_lc.add_url_to_fits_file(instrument._current_par_dic, url=instrument.disp_conf.products_url)
            query_lc.write()

            if api == False:
                _names.append(query_lc.name)
                _lc_path.append(str(query_lc.file_path.name))
                if query_lc.root_file_path is not None:
                    _root_path.append(str(query_lc.root_file_path.name))
                #logging.info ('_root_path',_root_path)
                #x_label='MJD-%d  (days)' % mjdref,y_label='Rate  (cts/s)'
                dx = (query_lc.data.data_unit[1].data['time'][1:] - query_lc.data.data_unit[1].data['time'][0:-1]) / 2
                dx = np.pad(dx, (0, 1), 'edge')
                _html_fig.append(query_lc.get_html_draw(x=query_lc.data.data_unit[1].data['time'],
                                                        y=query_lc.data.data_unit[1].data['rate'],
                                                        dy=query_lc.data.data_unit[1].data['rate_err'],
                                                        dx=dx,
                                                        title='Start Time: %s'%instrument.get_par_by_name('T1')._astropy_time.utc.value,
                                                        x_label='Time  (s)',
                                                        y_label='Rate  (cts/s)'))

            if api==True:
                _data_list.append(query_lc.data)
                #try:
                #    open(root_file_path.path, "wb").write(BinaryData().decode(res_json['root_file_b64']))
                #    lc.root_file_path = root_file_path
                #except:
                #    pass
                if query_lc.root_file_path is not None:
                    _d,md=BinaryData(str(query_lc.root_file_path)).encode()
                    _binary_data_list.append(_d)

        query_out = QueryOutput()

        if api == True:
            query_out.prod_dictionary['numpy_data_product_list'] = _data_list
            query_out.prod_dictionary['binary_data_product_list'] = _binary_data_list
        else:
            query_out.prod_dictionary['name'] = _names
            query_out.prod_dictionary['file_name'] = _lc_path
            query_out.prod_dictionary['root_file_name'] = _root_path
            query_out.prod_dictionary['image'] =_html_fig
            query_out.prod_dictionary['download_file_name'] = 'light_curves.tar.gz'

        query_out.prod_dictionary['prod_process_message'] = ''


        return query_out

    def get_dummy_products(self, instrument, config, out_dir='./',prod_prefix='polar',api=False):
        config = DataServerConf(data_server_url=instrument.data_server_conf_dict['data_server_url'],
                                data_server_port=instrument.data_server_conf_dict['data_server_port'],
                                data_server_remote_cache=instrument.data_server_conf_dict['data_server_cache'],
                                dispatcher_mnt_point=instrument.data_server_conf_dict['dispatcher_mnt_point'],
                                dummy_cache=instrument.data_server_conf_dict['dummy_cache'])
        #logging.info('config',config)
        meta_data = {'product': 'light_curve', 'instrument': 'isgri', 'src_name': ''}
        meta_data['query_parameters'] = self.get_parameters_list_as_json()

        dummy_cache = config.dummy_cache

        res = DummyPolarRes()
        res.__setattr__('dummy_src', 'dummy_src')
        res.__setattr__('dummy_lc', '%s/polar_query_lc.fits' % dummy_cache)
        res.__setattr__('dummy_root', '%s/polar_query_lc.root' % dummy_cache)
        res.__setattr__('extracted_sources', [('dummy_src', 'dummy_lc')])

        prod_list=PolarLigthtCurve.build_from_res(res,
                                        src_name='lc',
                                        prod_prefix=prod_prefix,
                                        out_dir=out_dir,
                                        skip_root=True)



        prod_list = QueryProductList(prod_list=prod_list)
        #
        return prod_list













