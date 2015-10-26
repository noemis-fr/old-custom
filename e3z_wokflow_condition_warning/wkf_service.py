# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Elanz (<http://www.openelanz.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
import instance
import openerp.netsvc as netsvc
from openerp.workflow.wkf_service import workflow_service



class e3z_workflow_service(workflow_service):
    
    def trg_validate(self, uid, res_type, res_id, signal, cr):
        """
        Méthode redéfinie pour permettre l'appele wkf_expr.check 
        modifiée dans ce module. 
        
        Fire a signal on a given workflow instance

        :param res_type: the model name
        :param res_id: the model instance id the workflow belongs to
        :signal: the signal name to be fired
        :param cr: a database cursor
        """
        result = False
        ident = (uid,res_type,res_id)
        # ids of all active workflow instances for a corresponding resource (id, model_nam)
        cr.execute('select id from wkf_instance where res_id=%s and res_type=%s and state=%s', (res_id, res_type, 'active'))
        for (id,) in cr.fetchall():
            res2 = instance.validate(cr, id, ident, signal)
            result = result or res2
        return result
e3z_workflow_service()