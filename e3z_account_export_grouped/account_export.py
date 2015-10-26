# -*- coding: utf-8 -*-
###############################################################################
#
# Asgard Ledger Export (ALE) module,
# Copyright (C) 2005 - 2013
# Héonium (http://www.heonium.com). All Right Reserved
#
# Asgard Ledger Export (ALE) module
# is free software: you can redistribute it and/or modify it under the terms
# of the Affero GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Asgard Ledger Export (ALE) module
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
import base64
import copy
import time
import pooler
from osv import fields, osv
from tools.translate import _
from heo_common.hnm_lib import *
from heo_common.files_tools import *
import openerp.addons.decimal_precision as dp



class asgard_ledger_export_fields(osv.osv):
    _inherit = "asgard.ledger.export.fields"
    _columns = {
        'field_account': fields.many2one('ir.model.fields', 'Fields', domain=[
            ('model', '=', 'account.export.grouped.statement.line.grouped')
        ],
            help="Select which filed you want export."),

    }





asgard_ledger_export_fields()


class asgard_ledger_export_statement(osv.osv):
    """
    Liste des exports déja réalisé
    """
    _inherit = "asgard.ledger.export.statement"

    #def _get_grouped_ales_line(self, cr, uid, ids, field_name, arg, context=None):used for function field
    def _compute_grouped_ales_line(self, cr, uid, ids, context=None):
        result = {}

        pool = pooler.get_pool(cr.dbname)
        journal_period_obj = pool.get('account.journal.period')
        grouped_ales_line_obj = pool.get('account.export.grouped.statement.line.grouped')

        for ale in self.browse(cr, uid, ids, context={}):
            if not ale.journal_period_id:
                raise osv.except_osv(_('No Journal/Period selected !'), _('You have to select Journal/Period before populate line.'))
            jp_ids = journal_period_obj.read(cr, uid, map(lambda x:x.id,ale.journal_period_id), ['journal_id','period_id'])
            start = time.time()
            #suppression des lignes existantes
            cr.execute('delete  from account_export_grouped_statement_line_grouped where  ales_id = %s',
                       ([str(ale.id)]))

            offset = 0
            results = [1]
            grouped_line_ids=[]
            #
            # while len(results):
            #     cr.execute('SELECT %s, ml.date, l.partner_ref, l.period_id \
            #         ,l.journal_id, sum(ml.credit) as credit, sum(ml.debit) as debit\
            #         ,l.account_id, l.company_id \
            #         FROM \
            #             asgard_ledger_export_statement_line  l \
            #             inner join account_move_line ml on ml.id = l.move_line_id \
            #         WHERE l.partner_is_company = True GROUP BY ml.date, l.partner_ref,l.partner_is_company,l.period_id \
            #         ,l.journal_id \
            #         ,l.account_id, l.company_id \
            #         LIMIT 500 OFFSET %s',
            #                (( ale.id, str(offset))))
            #     results = cr.fetchall()
    # _columns = {
    #     'ales_id': fields.many2one('asgard.ledger.export.statement', 'Asgard Statement', required=True, ondelete='cascade', select=True),
    #     'date': fields.date(string='Date Created Entry', required=True),
    #     'partner_ref': fields.char(string='Partner ref'),
    #     'period_id': fields.many2one('account.period', string='Period', required=True),
    #     'journal_id': fields.many2one('account.journal', string='Journal', required=True),
    #     'credit': fields.float('Credit'),
    #     'debit': fields.float(string='Debit'),
    #     'account_id': fields.many2one('account.account', string='Account', required=True),
    #     'text_line': fields.text('Line exported', readonly=True,
    #                              help="Value of the line when it's exported in file (From format field)"),
    #     'company_id': fields.many2one('res.company', 'Company', required=True),
    #     }
    #             for id, date, partner_ref,partner_is_company, period_id ,journal_id, credit, debit ,account_id, company_id in results:
    #                 ales_line_id = grouped_ales_line_obj.create(cr, uid, {
    #                     'ales_id': ale.id,
    #                     'date': date,
    #                     'partner_ref': partner_ref,
    #                     'period_id': period_id ,
    #                     'journal_id': journal_id,
    #                     'credit': credit,
    #                     'debit': debit ,
    #                     'account_id': account_id,
    #                     'company_id': company_id
    #                     })
    #                 # grouped_line_ids.append((4,ales_line_id)) # used for function field
    #                 grouped_line_ids.append(ales_line_id)
                #offset += len(results)
            #result[ale.id]= grouped_line_ids #  used for function field
            #regoupement des particuliers
            #while len(results):

            #regoupement des pro par debit
            #sum(round(ml.credit,2)) as credit, sum(round(ml.debit,2)) as debit
            cr.execute('INSERT INTO account_export_grouped_statement_line_grouped \
                    (ales_id, date, partner_ref, move_id,period_id, journal_id, credit, debit, account_id, company_id, entry_name) \
                    SELECT l.ales_id , ml.date,l.partner_ref,l.move_id,  l.period_id \
                ,l.journal_id, sum(ml.credit) as credit, sum(ml.debit) as debit\
                ,l.account_id, l.company_id, mv.name\
                FROM \
                    asgard_ledger_export_statement_line  l \
                    inner join account_move_line ml on ml.id = l.move_line_id \
                    inner join account_move mv on mv.id = ml.move_id \
                WHERE l.ales_id = %s AND  l.partner_is_company = True AND ml.credit =0  \
                GROUP BY l.ales_id , ml.date, l.partner_ref, l.move_id, l.partner_is_company,l.period_id \
                ,l.journal_id \
                ,l.account_id, l.company_id  , mv.name \
                order by l.journal_id, ml.date, mv.name, l.account_id  \
                OFFSET %s',
                       (( ale.id, str(offset))))

            #regoupement des pro par credit
            cr.execute('INSERT INTO account_export_grouped_statement_line_grouped \
                    (ales_id, date, partner_ref, move_id,  period_id, journal_id, credit, debit, account_id, company_id, entry_name) \
                    SELECT l.ales_id , ml.date,l.partner_ref,l.move_id,   l.period_id \
                ,l.journal_id,  sum(ml.credit) as credit, sum(ml.debit) as debit\
                ,l.account_id, l.company_id , mv.name\
                FROM \
                    asgard_ledger_export_statement_line  l \
                    inner join account_move_line ml on ml.id = l.move_line_id \
                    inner join account_move mv on mv.id = ml.move_id \
                WHERE l.ales_id = %s AND l.partner_is_company = True AND ml.debit=0 \
                GROUP BY l.ales_id ,ml.date, l.partner_ref, l.move_id, l.partner_is_company,l.period_id \
                ,l.journal_id \
                ,l.account_id, l.company_id , mv.name \
                order by l.journal_id, ml.date, mv.name, l.account_id  \
                 OFFSET %s',
                       (( ale.id, str(offset))))
            #regoupement des particulier par debit
            cr.execute('INSERT INTO account_export_grouped_statement_line_grouped \
                    (ales_id, date, partner_ref, period_id, journal_id, credit, debit, account_id, company_id, entry_name) \
                    SELECT l.ales_id , ml.date,l.partner_ref,  l.period_id \
                ,l.journal_id,  sum(ml.credit) as credit, sum(ml.debit) as debit\
                ,l.account_id, l.company_id , mv.name\
                FROM \
                    asgard_ledger_export_statement_line  l \
                    inner join account_move_line ml on ml.id = l.move_line_id \
                    inner join account_move mv on mv.id = ml.move_id \
                WHERE l.ales_id = %s AND (l.partner_is_company = False or l.partner_is_company is null) AND ml.credit =0  \
                GROUP BY l.ales_id ,ml.date, l.partner_ref,l.partner_is_company,l.period_id \
                ,l.journal_id \
                ,l.account_id, l.company_id , mv.name \
                order by l.journal_id, ml.date, mv.name, l.account_id  \
                 OFFSET %s',
                       (( ale.id, str(offset))))

            #regoupement des particulier par credit
            cr.execute('INSERT INTO account_export_grouped_statement_line_grouped \
                    (ales_id, date, partner_ref, period_id, journal_id, credit, debit, account_id, company_id, entry_name) \
                    SELECT l.ales_id , ml.date,l.partner_ref,  l.period_id \
                ,l.journal_id,  sum(ml.credit) as credit, sum(ml.debit) as debit\
                ,l.account_id, l.company_id , mv.name\
                FROM \
                    asgard_ledger_export_statement_line  l \
                    inner join account_move_line ml on ml.id = l.move_line_id \
                    inner join account_move mv on mv.id = ml.move_id \
                WHERE l.ales_id = %s AND (l.partner_is_company = False or l.partner_is_company is null) AND ml.debit=0 \
                GROUP BY l.ales_id ,ml.date, l.partner_ref,l.partner_is_company,l.period_id \
                ,l.journal_id \
                ,l.account_id, l.company_id , mv.name \
                order by l.journal_id, ml.date, mv.name, l.account_id  \
                 OFFSET %s',
                       (( ale.id, str(offset))))

        return True


    # _grouped_ales_line_ids_store_triggers = {
    #     'asgard.ledger.export.statement': (lambda self,cr,uid,ids,context=None: self.search(cr, uid, [('id','child_of',ids)]),
    #                     ['ales_line_ids',], 10)
    # }

    _columns = {
        'grouped': fields.boolean('Export grouped'),
        'grouped_ales_line_ids': fields.one2many('account.export.grouped.statement.line.grouped', 'ales_id', 'Grouped Lines',
                        readonly=True, states={'draft':[('readonly',False)]}),
        # 'journal_period_id': fields.many2one('account.journal.period', 'Journal/Period', readonly=True, states={'draft':[('readonly',False)]},
        #                                       help="Select which period you want export."),
        # 'grouped_ales_line_ids': fields.function(_get_grouped_ales_line, type='one2many',
        #                                          obj="account.export.grouped.statement.line.grouped",
        #                                          string="Grouped line",)# store=_grouped_ales_line_ids_store_triggers),
    }



    def action_populate(self, cr, uid, ids, context={}):
        """
        parameters :
            journal_period_id
        """

        pool = pooler.get_pool(cr.dbname)
        journal_period_obj = pool.get('account.journal.period')
        ales_line_obj = pool.get('asgard.ledger.export.statement.line')
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=context)
        for ale in self.browse(cr, uid, ids, context={}):
            if not ale.journal_period_id:
                raise osv.except_osv(_('No Journal/Period selected !'), _('You have to select Journal/Period before populate line.'))
            jp_ids = journal_period_obj.read(cr, uid, map(lambda x:x.id,ale.journal_period_id), ['journal_id','period_id'])
            start = time.time()
            for jp in jp_ids:
                offset = 0
                results = (0,)
                #while len(results):
                    #Create line with SQL (for performence)
                cr.execute('SELECT count(*) as num_result\
                    FROM \
                        account_move_line ml \
                        left join res_partner p on p.id = ml.partner_id \
                        inner join asgard_ledger_export_journal targ_j on targ_j.journal_id =ml.journal_id  \
                    WHERE \
                        period_id = %s AND ml.journal_id = %s AND ml.id NOT IN \
                        (SELECT move_line_id FROM asgard_ledger_export_statement_line) \
                     OFFSET %s',
                           ( jp['period_id'][0],jp['journal_id'][0],str(offset)))
                results = cr.fetchone()
                if results:
                    #round(ml.credit,2)   , round(ml.debit,2), \
                    ## date_trunc(\'second\',CURRENT_TIMESTAMP(2) AT TIME ZONE \'MST\')
                    cr.execute('INSERT INTO asgard_ledger_export_statement_line \
                        (name, ales_id, move_line_id, date_created, move_id, period_id, journal_id, credit, debit, account_id, company_id,partner_ref, partner_is_company) \
                        SELECT ml.date, %s\
                                , ml.id,ml.date_created,ml.move_id,ml.period_id,ml.journal_id, \
                                 ml.credit   , ml.debit, \
                                ml.account_id, %s\
                               ,CASE WHEN p.ref is not null  THEN p.ref \
                                    WHEN p.ref is null and (not p.is_company or p.is_company is null)  THEN targ_j.default_partner_ref \
                                    ELSE  p.ref \
                                        END \
                               as partner_ref, p.is_company \
                        FROM \
                            account_move_line ml \
                            left join res_partner p on p.id = ml.partner_id \
                            inner join asgard_ledger_export_journal targ_j on targ_j.journal_id =ml.journal_id  \
                        WHERE \
                            period_id = %s AND ml.journal_id = %s AND ml.id NOT IN \
                            (SELECT move_line_id FROM asgard_ledger_export_statement_line) \
                           OFFSET %s',
                               ( ale.id,company_id, jp['period_id'][0],jp['journal_id'][0],str(offset)))
                #results = map(lambda x:(x[0],x[1],x[2]), cr.fetchall())
                # for mv_id, partner_ref, is_company in results:
                #     ales_line_id = ales_line_obj.create(cr, uid, {
                #         'ales_id': ale.id,
                #         'move_line_id': mv_id,
                #         'partner_ref': partner_ref,
                #         'partner_is_company':is_company,
                #         })
                #offset += results
                row_inserted  =  int(results[0])
                if row_inserted>0:
                    self._compute_grouped_ales_line(cr, uid, ids, context)
                else:
                    raise osv.except_osv(_('No Move line  !'),
                                         _('There is no line to add !\n' \
                                           'Or  Selected journals contain no accounting entry or they \
                                           have already been exported  (or in current exports).'))
                #Soit les journaux séléctionnés ne contiennent pas d'écriture comptable soit ils ont déjà été exportés ( ou encours d'export).

            stop = time.time()


        return True

        # 'name': fields.char('Date', size=64, translate=True, required=True, readonly=True),
        # 'ales_id': fields.many2one('asgard.ledger.export.statement', 'Asgard Statement', required=True, ondelete='cascade', select=True),
        # 'move_line_id': fields.many2one('account.move.line', 'Entry',
        #                                 select=True, required=True,
        #                                 help="Entry selected for ..."),
        # 'date_created': fields.related('move_line_id', 'date_created', type='date', string='Date Created Entry', store=True),
        # 'move_id': fields.related('move_line_id', 'move_id', type='many2one', relation='account.move', string='Entry', store=True),
        # 'period_id': fields.related('move_line_id', 'period_id', type='many2one', relation='account.period', string='Period', store=True),
        # 'journal_id': fields.related('move_line_id', 'journal_id', type='many2one', relation='account.journal', string='Journal', store=True),
        # 'credit': fields.related('move_line_id', 'credit', type='float', string='Credit', store=True),
        # 'debit': fields.related('move_line_id', 'debit', type='float', string='Debit', store=True),
        # 'account_id': fields.related('move_line_id', 'account_id', type='many2one', relation='account.account', string='Account', store=True),
        # 'text_line': fields.text('Line exported', readonly=True,
        #                          help="Value of the line when it's exported in file (From format field)"),
        # 'company_id': fields.many2one('res.company', 'Company', required=True),

        # 'name': lambda *a: time.strftime('%Y/%m/%d-%H:%M:%S'),
        # 'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.account', context=c),
        return True


    def _faccount_field(self, cr, uid, ids, **kwargs):
        """
        Cette fonction peut être remplacée par '_fbuild_field', mais elle est
        gardé pour éviter d'avoir mettre une expression python pour les champs
        simple de l'écriture et leur indirection de niveau 1
        parameters : {'data':[<type_field>,<python_expression>], 'line':<browse_line_record>}
        return : Value of field
        """
        imf_obj = pooler.get_pool(cr.dbname).get('ir.model.fields')


        # Récupération du nom du champs par rapport à l'object 'ir_model_fields' ...
        imf = imf_obj.read(cr, uid, [kwargs['data'][1]], ['name'])[0]['name']

        # ... Contruction du champs et affectation à 'bf.
        t = "kwargs['line'].%s%s" % (str(imf), str(kwargs['data'][2]))

        if isinstance(eval(t), float):
            return str(eval(t))

        return eval(t)

    def _fbuild_field(self, cr, uid, ids, **kwargs):
        """
        Evalue le champ contenant une expression Python
        parameters : {'data':[<type_field>,<python_expression>], 'line':<browse_line_record>}
        return : result of python expression evaluation.
        """
        result = False

        if kwargs['data'][1]:
            # Récupération de l'objet 'account_move_line'
            obj = kwargs['line']
            # Évaluation de l'expression python sur l'objet
            result = eval(kwargs['data'][1], {'object': obj, 'time': time})

        return result

    def get_value(self, cr, uid, ids, **kwargs):
        """
        Call correct method depend on parameters
        parameters : {'data':[<type_field>,<python_expression>],
                    'line':<browse_line_record>}
        return : result of method called
        """   
        method_name = '_f' + str(kwargs['data'][0]).lower()
        try:
            method = getattr(self, method_name)
        except AttributeError:
            print ("The method for verify '%s' type isn't defined (You must "
                   "define it in class 'asgard_ledger_export_statement' of "
                   "module '%s')." % (method_name,__name__))
        else:
            return method(cr, uid, ids, **kwargs)

    def action_confirm(self, cr, uid, ids, *args):
        result = False

        # Si la balance est égale a zéro et qu'il y a des lignes à exporter
        for ale in self.browse(cr, uid, ids, context={}):
            if len(ale.ales_line_ids) == 0:
                raise osv.except_osv(
                    _('No Lines !'),
                    _("You have to add some line to export.")
                )
            results = 0
            cr.execute('SELECT count(*) as num_result\
                    FROM \
                        asgard_ledger_export_statement_line \
                    WHERE \
                        partner_ref is null AND ales_id= %s  \
                     OFFSET %s',
                       ( ale.id,0))
            results = cr.fetchone()
            # if int(results[0]) >0:
            #     raise osv.except_osv(
            #         _('Error !'),
            #         _("Partner ref is required in Statement lines !")
            #     )

            if ale.balance == 0.0:
                result = self.write(cr, uid, ids, {'state':'confirm'})
            else:
                raise osv.except_osv(
                    _('Bad balance !'),
                    _("Balance need to be equal to zero.")
                )

        return result


    def action_export(self, cr, uid, ids, *args):
        """
        For each entry line build the text value
        """
        pool = pooler.get_pool(cr.dbname)
        mod_obj = self.pool.get('ir.model.data')
        ale_obj = pool.get('asgard.ledger.export')
        alej_obj = pool.get('asgard.ledger.export.journal')
        attach_obj = pool.get('ir.attachment')


        for ales in self.browse(cr, uid, ids):

            # We need first to check if we have other attchments
            # (Attachments are limited to 1 per statement)
            attach_ids = []
            attach_ids = attach_obj.search(cr, uid, [
                ('name', 'like', 'export : %'),
                ('res_model', '=', 'asgard.ledger.export.statement'),
                ('res_id', '=', ales.id),
            ])

            if len(attach_ids) >= 1:
                raise osv.except_osv(
                    _('Error !'),
                    _("You cannot have more than one attachment !")
                )


            # Initalisation de l'encodage du fichier
            enc = generic_encode(
                file_header=ales.ale_id.file_header,
                separator=ales.ale_id.separator,
                ext=ales.ale_id.extension,
                ending=ale_obj.get_end_line(cr, uid, ales.ale_id.end_line),
                encoding=ales.ale_id.encoding)
            enc.export_file()
            # Recupération du tableau de construction de ligne
            build_line = ale_obj.get_building_line(cr, uid, [ales.ale_id.id])

            # pour chaque ligne écritures
            num = 0
            order ='journal_id, date,entry_name, account_id'
            grouped_ales_line_ids = pool.get('account.export.grouped.statement.line.grouped').search(
                                                cr, uid, [('id','in',[l.id for l in ales.grouped_ales_line_ids])], 0,
                                                len(ales.grouped_ales_line_ids),order, *args)

            for ales_line in pool.get('account.export.grouped.statement.line.grouped').browse(
                                                                cr,uid,grouped_ales_line_ids,*args):
                # Pour chaque construction de champs dans le tableau 
                # 'build_line', duplication du tableau de génération de ligne
                # de texte
                num += 1
                bl = copy.deepcopy(build_line)
                for bf in bl:
                    bf[0] = self.get_value(cr, uid, ids, data=bf[0],
                                           line=ales_line, num=num)
                result = enc.write_file_in_flow(bl)


            ####
            ## Attachement
            fp = open(os.path.join(enc.dir_tmp, enc.filetmp), 'r')
            file_data = fp.read()
            attach_id = attach_obj.create(cr, uid, {
                'name': 'export : ' + ales.name + '.' + ales.ale_id.extension,
                'datas': base64.encodestring(file_data),
                'datas_fname': enc.filetmp,
                'res_model': 'asgard.ledger.export.statement',
                'res_id': ales.id,
                })
            ## Attachement

        self.write(cr, uid, ids, {'state': 'done'})

        return True


asgard_ledger_export_statement()


class account_export_grouped_statement_line_grouped(osv.osv):
    _name = "account.export.grouped.statement.line.grouped"
    _description = "Export Statement reconcile grouped"
    _order = 'journal_id, date,entry_name, account_id'


    def _get_export_journal(self, cursor, user, ids, name, args, context=None):
        res = {}
        cursor.execute('SELECT journal_id, id\
                    FROM \
                        asgard_ledger_export_journal \
                       ',())
        results = cursor.fetchall()
        results_disct = results and dict(results) or {}
        for grouped_line in self.browse(cursor, user, ids, context=context):
            res[grouped_line.id] = results_disct.get(grouped_line.journal_id.id, False)
        return res

    _columns = {
        'ales_id': fields.many2one('asgard.ledger.export.statement', 'Asgard Statement', required=True, ondelete='cascade', select=True),
        'date': fields.date(string='Date Created Entry', required=True),
        'partner_ref': fields.char(string='Partner ref'),
        'move_id': fields.many2one('account.move', string='Entry'),
        #'move_ref': fields.char(string='Move ref'),
        'period_id': fields.many2one('account.period', string='Period', required=True),
        'journal_id': fields.many2one('account.journal', string='Journal', required=True),
        'credit': fields.float('Credit', digits_compute= dp.get_precision('Account'),),
        'debit': fields.float(string='Debit', digits_compute= dp.get_precision('Account'),),
        'account_id': fields.many2one('account.account', string='Account', required=True),
        'text_line': fields.text('Line exported', readonly=True,
            help="Value of the line when it's exported in file (From format field)"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'entry_name': fields.related('move_id', 'name', type='char', string='Entry Name', store=True),
        'export_journal_id': fields.function(_get_export_journal, type='many2one',
                                                  obj="asgard.ledger.export.journal",
                                                  string="Export Journal",)
    }




    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if context is None:
            context = {}
        if order is None:
            order ='date,entry_name, account_id'
        return super(account_export_grouped_statement_line_grouped, self).search(cr, uid, args, offset, limit,
                                                   order, context=context, count=count)
    # def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
    #
    #     if context is None:
    #         context = {}
    #     order ='date,entry_name, account_id'
    #     ids = self.search(cr, uid, [('id','in',ids)], 0, 1000000,order, context=context)
    #     res = super(account_export_grouped_statement_line_grouped, self).read(cr, uid, ids, fields=fields, context=context, load=load)
    #     #res = sorted(res, key=lambda ord: ord['id'])
    #     return res
account_export_grouped_statement_line_grouped()


class asgard_ledger_export_statement_line(osv.osv):
    _inherit = "asgard.ledger.export.statement.line"
    #_order = 'date,journal_id,entry_name, account_id'
    _columns = {
        'partner_ref': fields.char('Partner ref', size=32, readonly=True),
        'partner_is_company': fields.boolean('Is a company', readonly=True),
        }

class asgard_ledger_export_journal(osv.osv):
    """
    Table d'association entre les journaux comptable d'OpenERP et les noms des
    journaux. + la reférence des clients particuliers dans système cible
    """

    _inherit = "asgard.ledger.export.journal"


    _columns = {
        'default_partner_ref': fields.char('Default partner ref', size=64,  help="Default partner ref used in target system."),
        'name': fields.char('Name', size=64, translate=False, required=True),
    }