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


class sessionmanager(object):
    """
    Session Manager store data to be used anywhere in code until user is connected.
    """
    def __init__(self, session=None):
        """

        """
        self.context = {}

    def set_user_context(self, uid, context_dico):
        """
        This function store user context (dico) into context manager object.
           :param uid: User's id
           :param context_dico: User context passed à dico.
        """
        #read then update user context
        user_context = self.context.get(uid, {})
        user_context.update(context_dico)
        # update Session Manager context
        self.context.update({uid: user_context})
        return True

    def get_user_context(self, uid):
        """
        This function get the all user context (dico) from context manager object.
           :param uid: User's id
           :return : user_context (dico).
        """
        user_context = self.context.get(uid, {})
        return user_context

    def get_user_context_bykey(self, uid, key):
        """
        This function get the specific user context (value) by key.
           :param uid: User's id
           :param key: Key of context dico
           :return : value.
        """
        user_context = self.context.get(uid, {})
        return user_context.get(key, False)

    def del_user_context_bykey(self, uid, key):
        """
        This function del the specific user context (value) by key.
           :param uid: User's id
           :param key: Key of context dico
           :return : True.
        """
        if self.context.get(uid, False):
            del self.context.get(uid, {})[key]
        return True

    def destroy_user_context(self, uid):
        """
        This function del the all user context.  Must be called from methode that destroy web session
           :param uid: User's id
           :return : True.
        """
        if self.context.get(uid, False):
            del self.context[uid]
        return True

SessionManager = sessionmanager()
