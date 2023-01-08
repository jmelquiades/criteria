# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
from PIL import Image
import logging
#import pytesseract
import requests


class SunatPartnerConflux(object):

    def __init__(self, nro_doc, document_type, token):
        self.nro_doc = nro_doc
        self.document_type = document_type
        self.url_ruc = 'https://ruc.conflux.pe/ruc'
        self.url_dni = 'https://ruc.conflux.pe/dni'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        # Deprecated attrs
        self.url_post = 'http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/'
        self.url_captcha = self.url_post + 'captcha?accion=image'
        self.url_sunat_1 = self.url_post + 'jcrS00Alias?accion={}&razSoc=&nroRuc=&nrodoc={}&contexto={}&' \
                                           'tQuery=on&search1=&codigo={}&tipdoc=1&search2={}&coddpto=&codprov=&coddist=&search3='
        self.url_sunat_6 = self.url_post + 'jcrS00Alias?accion={}&razSoc=&nroRuc={}&nrodoc=&contexto=rrrrrrr&' \
                                           'tQuery=on&search1={}&codigo={}&tipdoc=1&search2=&coddpto=&codprov=&coddist=&search3='
        self.old_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6',
            'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300'
        }

    def action_validate_api(self):
        result = False
        for i in range(4):
            try:
                instante_inicial = datetime.now()
                values = self._action_validate_api()
                instante_final = datetime.now()
                tiempo = instante_final - instante_inicial
                logging.info('{} segundos'.format(tiempo.seconds))
                if values:
                    if self.document_type == '1':
                        result = {
                            'name': values.get('name'),
                            #'partner_name': values.get('nombres'),
                            #'first_name': values.get('apellido_paterno'),
                            #'second_name': values.get('apellido_materno'),
                            'vat': values.get('_id'),
                            'document_type_sunat_id': self.document_type,
                            'company_type': 'person',
                        }
                    elif self.document_type == '6':
                        ubigeo = values.get('ubigeo', [])
                        if len(ubigeo) == 3:
                            state_id = ubigeo[0]
                            city_id = ubigeo[1]
                            l10n_pe_district = ubigeo[2]
                        else:
                            state_id = False
                            city_id = False
                            l10n_pe_district = False
                            country = False
                        result = {
                            'name': values.get('nombre'),
                            'vat': values.get('_id'),
                            'state_contributor_sunat': values.get('estado'),
                            'condition_contributor_sunat': values.get('condicion'),
                            'street': values.get('direccion'),
                            'document_type_sunat_id': self.document_type,
                            'company_type': 'company',
                            'state_id': state_id,
                            'city_id': city_id,
                            'zip': ubigeo,
                            'l10n_pe_district': l10n_pe_district
                        }
                    break
            except Exception:
                continue
            except requests.exceptions.Timeout as e:
                continue
        return result

    def _action_validate_api(self):
        response = False
        if self.document_type == '1':
            try:
                r = requests.get(
                    '{}/{}'.format(self.url_dni, self.nro_doc),
                    headers=self.headers,
                )
                if not r.json()['_id']:
                    return False
                response = r.json()
            except Exception as e:
                logging.info("exeption 1.1 {}".format(e))
            except requests.exceptions.RequestException as e:
                logging.info("exeption 1.2 {}".format(e))
        elif self.document_type == '6':
            try:
                r = requests.get(
                    '{}/{}'.format(self.url_ruc, self.nro_doc),
                    headers=self.headers,
                )
                if not r.json()['_id']:
                    return False
                response = r.json()
            except Exception as e:
                logging.info("exeption 2.1 {}".format(e))
            except requests.exceptions.RequestException as e:
                logging.info("exeption 2.2 {}".format(e))
        return response

    def get_captcha(self):
        """
        Deprecated method
        :return:
        """
        s = requests.Session()
        try:
            s = requests.Session()
            r = s.get(
                self.url_captcha,
                headers=self.headers
            )
        except Exception as e:
            return False, e

        try:
            img = Image.open(BytesIO(r.content))
            #captcha_val = pytesseract.image_to_string(img)
        except Exception as e:
            return False, e

        captcha_val = captcha_val.strip().upper()
        return s, captcha_val

    def search_soup(self, html_parser):
        """
        Deprecated method
        :return:
        """
        obj_soup = BeautifulSoup(html_parser)
        values = {
            'numeroruc': '',
            'direccion_domicilio_fiscal': '',
            'tipo_cont': '',
            'tipo_doc': '',
            'nombre_comercial': '',
            'fecha_inscripcion': '',
            'fecha_inicio_actividades': '',
            'estado_contribuyente': '',
            'condicion_contribuyente': '',
            'profesion_u_oficio': '',
            'sistema_emision_comprobante': '',
            'actividad_comercio_exterior': '',
            'sistema_contabilidad': '',
            'actividades_economicas': [],
            'comprobante_pago': [],
            'sistema_emision_electronica': [],
            'emisor_electronico_desde': '',
            'comprobante_electronico': '',
            'afiliado_ple_desde': '',
            'padrones': []
        }
        obj_soup_tr = obj_soup.find_all('tr')
        for obj_tr in obj_soup_tr:
            if 'Número de RUC' in obj_tr.text or 'Tipo Contribuyente' in obj_tr.text or 'Tipo de Documento' in obj_tr.text or \
                    'Fecha de Inscripción' in obj_tr.text or 'Fecha de Inicio de Actividades' in obj_tr.text or 'Estado del Contribuyente' or \
                    'Condición del Contribuyente' in obj_tr.text or 'Profesión u Oficio:' in obj_tr.text or \
                    'Dirección del Domicilio Fiscal' in obj_tr.text or 'Sistema de Emisión de Comprobante' in obj_tr.text:
                list_obj_td = obj_tr.find_all('td')
                if list_obj_td:
                    for i in [0, 2]:
                        if len(list_obj_td) < 4 and i == 2:
                            continue
                        c = i + 1
                        if list_obj_td[i].text.find('Número de RUC') != -1 and not values['numeroruc']:
                            values['numeroruc'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Tipo Contribuyente') != -1 and not values['tipo_cont']:
                            values['tipo_cont'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Tipo de Documento') != -1 and not values['tipo_doc']:
                            values['tipo_doc'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Nombre Comercial') != -1 and not values['nombre_comercial']:
                            values['nombre_comercial'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Fecha de Inscripción') != -1 and not values['fecha_inscripcion']:
                            if list_obj_td[c].text:
                                values['fecha_inscripcion'] = list_obj_td[c].text.replace(' ', '').split('/')
                        elif list_obj_td[i].text.find('Fecha de Inicio de Actividades') != -1 and not values['fecha_inicio_actividades']:
                            if list_obj_td[c].text:
                                values['fecha_inicio_actividades'] = list_obj_td[c].text.replace(' ', '').split('/')
                        elif list_obj_td[i].text.find('Estado del Contribuyente') != -1 and not values['estado_contribuyente']:
                            values['estado_contribuyente'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Condición del Contribuyente') != -1 and not values['condicion_contribuyente']:
                            values['condicion_contribuyente'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Profesión u Oficio') != -1 and not values['profesion_u_oficio']:
                            values['profesion_u_oficio'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Dirección del Domicilio Fiscal') != -1 and not values['direccion_domicilio_fiscal']:
                            values['direccion_domicilio_fiscal'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Sistema de Emisión de Comprobante') != -1 and not values['sistema_emision_comprobante']:
                            values['sistema_emision_comprobante'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Actividad de Comercio Exterior') != -1 and not values['actividad_comercio_exterior']:
                            values['actividad_comercio_exterior'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Sistema de Contabilidad') != -1 and not values['sistema_contabilidad']:
                            values['sistema_contabilidad'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Actividad(es) Económica(s)') != -1 and not values['actividades_economicas']:
                            for obj_select in list_obj_td[c].find_all('select'):
                                option_tag = obj_select.find_all('option')
                                for op in range(len(option_tag)):
                                    values['actividades_economicas'].append(option_tag[op].text)
                        elif list_obj_td[i].text.find('Comprobantes de Pago c/aut. de impresión (F. 806 u 816)') != -1 and not values['comprobante_pago']:
                            for obj_select in list_obj_td[c].find_all('select'):
                                option_tag = obj_select.find_all('option')
                                for op in range(len(option_tag)):
                                    values['comprobante_pago'].append(option_tag[op].text)
                        elif list_obj_td[i].text.find('Sistema de Emision Electronica') != -1 and not values['sistema_emision_electronica']:
                            for obj_select in list_obj_td[c].find_all('select'):
                                option_tag = obj_select.find_all('option')
                                for op in range(len(option_tag)):
                                    values['sistema_emision_electronica'].append(option_tag[op].text)
                        elif list_obj_td[i].text.find('Emisor electrónico desde') != -1 and not values['emisor_electronico_desde']:
                            if list_obj_td[c].text:
                                values['emisor_electronico_desde'] = list_obj_td[c].text.replace(' ', '').split('/')
                        elif list_obj_td[i].text.find('Comprobantes Electrónicos') != -1 and not values['comprobante_electronico']:
                            values['comprobante_electronico'] = list_obj_td[c].text
                        elif list_obj_td[i].text.find('Afiliado al PLE desde') != -1 and not values['afiliado_ple_desde']:
                            if list_obj_td[c].text:
                                values['afiliado_ple_desde'] = list_obj_td[c].text.replace(' ', '').split('/')
                        elif list_obj_td[i].text.find('Padrones') != -1 and not values['padrones']:
                            for obj_select in list_obj_td[c].find_all('select'):
                                option_tag = obj_select.find_all('option')
                                for op in range(len(option_tag)):
                                    values['padrones'].append(option_tag[op].text)
        return values

    def search_soup_ruc(self, html_parser):
        """
        Deprecated method
        :return:
        """
        query_ruc = False
        obj_soup = BeautifulSoup(html_parser)
        for obj_a in obj_soup.find_all('a'):
            if not query_ruc:
                query_ruc = obj_a.text
        return query_ruc

    def action_validate(self):
        result = False
        for i in range(6):
            try:
                instanteInicial = datetime.now()
                values = self._action_validate()
                instanteFinal = datetime.now()
                tiempo = instanteFinal - instanteInicial
                segundos = tiempo.seconds
                logging.info("segundos")
                logging.info(segundos)
                if values:
                    name_ruc = values.get('numeroruc').split('-')
                    ruc, name = name_ruc[0], '-'.join(name_ruc[1:])
                    result = {
                        'name': name.strip(),
                        #'social_reason': name.strip(),
                        #'tradename': values.get('nombre_comercial'),
                        'street': values.get('direccion_domicilio_fiscal').replace('--', '').split('-')[0].strip(),
                        'city': values.get('direccion_domicilio_fiscal').replace('--', '').split('-')[1].strip(),
                        'document_type_sunat_id': self.document_type,
                        'vat': ruc.strip(),
                        'type_contributor_sunat': values.get('tipo_cont'),
                        'document_electronic_sunat': values.get('comprobante_electronico'),
                        'state_contributor_sunat': values.get('estado_contribuyente'),
                        'condition_contributor_sunat': values.get('condicion_contribuyente').strip(),
                        'office_sunat': values.get('profesion_u_oficio'),
                        'system_emission_sunat': values.get('sistema_emision_comprobante'),
                        'system_account_sunat': values.get('sistema_contabilidad'),
                        'foreign_activity_commerce_sunat': values.get('actividad_comercio_exterior'),
                        'activity_economic_ids': list(map(lambda x: (0, 0, {'name': x}), values['actividades_economicas'])),
                        'document_pay_ids': list(map(lambda x: (0, 0, {'name': x}), values['comprobante_pago'])),
                        'system_electronic_ids': list(map(lambda x: (0, 0, {'name': x}), values['sistema_emision_electronica'])),
                        'pattern_sunat_ids': list(map(lambda x: (0, 0, {'name': x}), values['padrones'])),
                        'company_type': 'company'
                    }
                    if len(values['fecha_inscripcion']) == 3:
                        if int(values['fecha_inscripcion'][2]) <= 1900:
                            result.update({
                                'date_inscription_sunat': '1900-01-01'
                            })
                        else:
                            result.update({
                                'date_inscription_sunat': '{}-{}-{}'.format(
                                    values['fecha_inscripcion'][2],
                                    values['fecha_inscripcion'][1],
                                    values['fecha_inscripcion'][0]
                                )
                            })
                    else:
                        result.update({'date_inscription_sunat': False})
                    if len(values['fecha_inicio_actividades']) == 3:
                        if int(values['fecha_inicio_actividades'][2]) <= 1900:
                            result.update({
                                'date_start_activity_sunat': '1900-01-01'
                            })
                        else:
                            result.update({
                                'date_start_activity_sunat': '{}-{}-{}'.format(
                                    values['fecha_inicio_actividades'][2],
                                    values['fecha_inicio_actividades'][1],
                                    values['fecha_inicio_actividades'][0]
                                )
                            })
                    else:
                        result.update({'date_start_activity_sunat': False})
                    if len(values['afiliado_ple_desde']) == 3:
                        result.update({
                            'ple_date_sunat': '{}-{}-{}'.format(
                                values['afiliado_ple_desde'][2],
                                values['afiliado_ple_desde'][1],
                                values['afiliado_ple_desde'][0]
                            )
                        })
                    else:
                        result.update({'ple_date_sunat': False})
                    if len(values['emisor_electronico_desde']) == 3:
                        result.update({
                            'emissor_date_sunat': '{}-{}-{}'.format(
                                values['emisor_electronico_desde'][2],
                                values['emisor_electronico_desde'][1],
                                values['emisor_electronico_desde'][0]
                            )
                        })
                    else:
                        result.update({'emissor_date_sunat': False})
                    if values.get('tipo_doc'):
                        type_doc_sunat = values['tipo_doc'].split('-')[0].strip()
                        surname_sunat, name_sunat = values['tipo_doc'].split('-')[1].strip().split(',')
                        result.update({
                            'partner_name': name_sunat.strip(),
                            'first_name': surname_sunat.split(' ')[0],
                            'second_name': surname_sunat.split(' ')[1],
                            'type_document_sunat': type_doc_sunat.split(' ')[0],
                            'number_document_sunat': type_doc_sunat.split(' ')[2],
                        })
                    break

            except Exception:
                continue
            except requests.exceptions.Timeout as e:
                continue
        return result

    def _action_validate(self):
        """
        Deprecated method
        :return:
        """
        query_ruc = False
        if self.document_type == '1':
            captcha_session, captcha_val = self.get_captcha()
            if not captcha_session:
                return False

            values = {
                'accion': 'consPorTipdoc',
                'nrodoc': self.nro_doc,
                'contexto': 'ti - it',
                'codigo': captcha_val,
                'search2': self.nro_doc
            }
            try:
                url_sunat = self.url_sunat_1.format(
                    values['accion'],
                    values['nrodoc'],
                    values['contexto'],
                    values['codigo'],
                    values['search2']
                )
                response_post_1 = captcha_session.get(
                    url_sunat,
                    headers=self.headers,
                    timeout=4
                )
            except requests.exceptions.RequestException as e:
                logging.info("exeption 1.1")
                return False
            except requests.exceptions.Timeout as e:
                logging.info("exeption 1.2")
                return False

            query_ruc = self.search_soup_ruc(response_post_1.text)

        if self.document_type == '6' or query_ruc:
            captcha_session, captcha_val = self.get_captcha()
            if not captcha_session:
                return False
            values = {
                'accion': 'consPorRuc',
                'nroRuc': query_ruc and query_ruc or self.nro_doc,
                'codigo': captcha_val
            }
            try:
                response_post_6 = captcha_session.get(
                    self.url_sunat_6.format(
                        values['accion'],
                        values['nroRuc'],
                        values['nroRuc'],
                        values['codigo']
                    ),
                    headers=self.headers,
                    timeout=4
                )
            except Exception as e:
                logging.info("exeption 2.2")
                return False
            except requests.exceptions.RequestException as e:
                logging.info("exeption 2.1")
                return False
            except requests.exceptions.Timeout as e:
                logging.info("exeption 2.2")
                return False

            val_response = self.search_soup(response_post_6.text)
            return val_response
        return False
