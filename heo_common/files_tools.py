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

import os
import time, datetime
import codecs
from Crypto.Hash import SHA256
from heo_common.hnm_lib import fvalue
from unidecode import unidecode

class file_hash:
    """Operations with sha hash from file."""

    def get_SHA256(self, filename):
        """
        Compute sha hash from file.

        Return : string
        """
        h = SHA256.new()
        h.update(open(filename, 'rb').read())
        return h.hexdigest()

    def dispatch(self, filename, _hash="SHA256"):
        method_name = 'get_' + str(_hash).upper()
        try:
            method = getattr(self, method_name)
        except AttributeError:
            error = "Unavaillable method : %s !!!" % method_name
            print error
            return False
        else:
            return method(filename)


def build_filename(ext='txt', random=True, prefix='F'):
    """
    Build/Create a filename
    Parameter(s)
        suffix : Extension without dot.
    Return :
        string : New filename + ext
    """
    if random:
        random.seed()
        y = random.randint(1, 999999)
        fname = "%6.6d%s.%s" % (y, datetime.datetime.now().strftime("%S"), ext)
    else:
        fname = "%s%s.%s" % (prefix, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), ext)
    return fname


class generic_encode:
    """
    Building and encoding file in temporary directory and return the file result
    ...
    """
    #dir_tmp = 'addons-heo/heo_common/tmp'
    dir_tmp = '/tmp'
    filetmp = ''
    file_header = ''
    ending = "\n"
    encoding = 'utf-8'
    ext = 'csv'
    separator = ';'
    fobj = None
    lmsg = []

    def __init__(self, **kargs):
        """
        parameter :
            kargs can contains key :
                file_header :
                ending : End of line
                ...
        """
        for k, v in kargs.iteritems():
            if k == 'ending' and v == 'nothing':
                self.ending = ''
            else:
                setattr(self, k, v)
        self.filetmp = build_filename(self.ext,False)

    def __del__(self):
        """
        Destruction du fichier temporaire, si il existe lors de la
        destruction de l'objet 'generic_encode'
        """
        if self.fobj != None and self.filetmp != "":
            self.fobj.close()
            if os.access(os.path.join(self.dir_tmp, self.filetmp), os.F_OK):
                os.unlink(os.path.join(self.dir_tmp, self.filetmp))
            self.fobj = None


    def build_line(self, data):
        """ """
        value = ""
        fmt = fvalue()
        # Traitement de l'entête
        # if data.has_key('header'):
        #    header = params['header']
        #    #self.setHdr ( header[0], header [1])
        for val in data:
            # Formatage de la valeur
            if len(val) > 4 and not val[0] and val[3][0] == 'string':
                val[0] =''
            result = fmt.build_value(val)
            if len(val) > 2 and len(result) <val[2] and val[3][0] == 'string':
                result = result.ljust(val[2])
            elif len(val) > 2 and len(result) <val[2] and val[3][0] == 'float':
                result = result.rjust(val[2]) #Les montant de crédit et débit sont justifié à droite
            elif len(val) > 2 and len(result) <val[2]:
                result = result.ljust(val[2])
            # Vérification de la présence d'une valeur si celle-ci est
            # obligatoire.
            if len(val) > 4 and val[4] != '' and result.strip == '':
                raise Exception, "un champ obligatoire n'est pas rempli : %s " % (val[4])
            # Positionnement de la valeur de retour
            if value != '':
                value += str(self.separator or '').decode('string_escape')
            if self.encoding == 'ascii':
                result = unidecode(result)
                value += result.encode(self.encoding,'ignore')
            else:
                value += result.encode(self.encoding)
        return '%s%s' % (value, str(self.ending))


    def write_file_in_flow(self, data):
        """ Write value in flow (in temp. file already opened)."""
        if self.fobj == None:
            # Ouverture du fichier et écriture de l'entête
            self.fobj = open(os.path.join(os.path.abspath(self.dir_tmp), self.filetmp), 'w+')
            # Cas ou le fichier sera de l'utf-8.
            # Mis en remarque car certain parser de banque ne l'accepte pas.
            #if self.encoding == 'utf-8':
            #    self.fobj.write(codecs.BOM_UTF8)
            if self.file_header and self.file_header != '':
                self.fobj.write(self.file_header.encode(self.encoding).decode('string-escape') + str(self.ending))
        self.fobj.write(self.build_line(data))
        self.fobj.flush()
        return True


    def export_file(self, dest='addons/hnm_common/tmp'):
        """ """
        dest = os.path.abspath(dest)
        if os.access(os.path.join(os.path.abspath(self.dir_tmp), self.filetmp), os.F_OK):
            os.rename(os.path.join(os.path.abspath(self.dir_tmp), self.filetmp), os.path.join(dest, self.filetmp))
        return True
