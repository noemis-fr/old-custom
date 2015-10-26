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

import e3z_user_session_manager.session_manager
from openerp.addons.web import http, controllers
lbweb = http


__author__ = 'vchemiere'



class lbsession(controllers.main.Session):
    _cp_path = "/web/session"

    @lbweb.jsonrequest
    def destroy(self, req):
        session_manager.SessionManager.destroy_user_context(req.session._uid)
        super(lbsession, self).destroy(req=req)