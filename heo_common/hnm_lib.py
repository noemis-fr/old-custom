# -*- coding: utf-8 -*-
###############################################################################
#
# heo_common module,
# Copyright (C) 2005 - 2013
# Héonium (http://www.heonium.com). All Right Reserved
#
# heo_common module
# is free software: you can redistribute it and/or modify it under the terms
# of the Affero GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# heo_common module
# is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the Affero GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import time
import netsvc
from tools.translate import _


class hlog(Exception):
    """  """
    dmsg = {}
    log_obj = None

    def __init__(self):
        self.dmsg['date'] = time.strftime("%Y-%m-%d %H:%M:%S")

    def add_value(self, value=None):
        if value:
            self.dmsg.update(value)


class hlog_info(hlog):
    """  """
    def __init__(self, value=None):
        hlog.__init__(self)
        hlog.add_value(self, {'name': _("Information !!!"), 'type':'*I*'})
        if value:
            hlog.add_value(self, value)


class hlog_error(hlog):
    """  """
    def __init__(self, value=None):
        hlog.__init__(self)
        hlog.add_value(self, {'name': _("Error !!!"), 'type':'*E*'})
        if value:
            hlog.add_value(self, value)
        #hlog.add_value(self, {'name': _("Error !!!"), 'type':'*E*'})


class hlog_debug(hlog):
    """  """
    def __init__(self, value=None):
        hlog.__init__(self)
        hlog.add_value(self, {'type':'*D*'})
        if value:
            hlog.add_value(self, value)


class hfmt:
    """
    """
    def __init__(self):
        pass

    def str2string(self, data, format):
        """
        Retourne la chaine passé en paramètre avec le format spécifié
        """
        return format % data

    def str2date(self, data, format):
        result = ''
        print "[HNM]", __name__, ".str2date", data
        if type(data) == str:
            if  data != '':
                result= time.strftime(data, time.strptime(data.strip()[0:10], '%Y-%m-%d'))
            else:
                result = data.strftime(format)
        return result


    def float2float(self, data, format):
        """
        Conversion en float
        """
        return format % data


    def str2float(self, data, format):
        """
        Conversion en float
        """
        # Si la chaine est vide il faut l'affecter la fonction doit retourner 0
        if data == '':
            data = '0'
        import locale
        # Récupération de la locale en cours sur le système
        locale.setlocale(locale.LC_ALL, '')
        return format % locale.atof(data)


    def convert(self, data, fmt):
        """
        Select methode from type Switch by 'format' and return the value.
        Return : method for convert field"""

        method_name = type(data).__name__ + "2" + str(fmt[0]).lower()
        try:
            method = getattr(self, method_name)
        except AttributeError:
            print ("The method for verify '%s' type isn't defined (You must define it in class 'hfmt' of module '%s')." % (method_name, __name__))
        else:
            return method(data, fmt[1])


class fvalue:
    """
    """
    def __init__(self):
        pass

    def fint2str(self, data):
        """
        Format value following parameters in data
        @param data: list of param : [value,position,length,[type,format]]
        @return: Formated value or raise exception if error
        """
        try:
            result = data[3][1] % data[0]
            if data[2] != 0 and len(result) > data[2]:
                #La chaine doit être tronquée.
                result = result[:data[2]]
        except Exception, e:
            e.args += (data,)
            raise
        return result


    def fstring(self, data):
        """
        Retour la chaine de caractère passée en parametre avec la longeur
        spécifiée.
        Parametre :
            data : ['chaine',position,longueur,format]
        """
        result = data[0]
        # print "[HNM][",__name__,"] [fstring] result: %s" % (result)
        # print "[HNM][",__name__,"] [fstring] data: %s" % (data)
        if data[2] != 0:
            # Suppose que la chaine est en 'unicode' sinon :
            #   result=unicode(data[3][1] % result[:data[2]),"utf-8",errors='ignore')
            result = data[3][1] % result[:data[2]]
        else:
            # print "[HNM][",__name__,"] [fstring] data: %s |result: %s" % (data,result)
            result = data[3][1] % result
        return result


    def fdate(self, data):
        result = ''
        if type(data[0]) == str:
            if  data[0] != '':
                result = time.strftime(data[3][1], time.strptime(data[0].strip()[0:10], '%Y-%m-%d'))
            else:
                result = data[0].strftime(data[3][1])
        return result.ljust(data[2])


    def ffloat(self, data):
        return data[3][1] % float(data[0])


    def build_value(self, data):
        """Switch by 'format' and return the value.
        Return : method for verify field"""

        method_name = 'f' + str(data[3][0]).lower()
        try:
            method = getattr(self, method_name)
        except AttributeError:
            print ("The method for verify '%s' type isn't defined (You must define it in class 'format_value' of module '%s')." % (method_name,__name__))
        else:
            return method(data)
