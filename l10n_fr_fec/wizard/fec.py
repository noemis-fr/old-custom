# -*- encoding: utf-8 -*-
##############################################################################
#
#    l10n FR FEC module for Odoo
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.exceptions import Warning
import base64
import unicodecsv
import StringIO


class AccountFrFec(osv.TransientModel):
    _name = 'account.fr.fec'
    _description = 'Ficher Echange Informatise'

    _columns = {
        'fiscalyear_id': fields.many2one(
            'account.fiscalyear', string='Fiscal Year', required=True),
        'type': fields.selection([
            ('is_ir_bic', 'I.S. or BIC @ I.R.'),
            ], string='Company Type'),
        'fec_data': fields.binary('FEC File', readonly=True),
        'filename': fields.char(string='Filename', size=256, readonly=True),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ], string='State'),
        'export_type': fields.selection([
            ('official', 'Official FEC report (posted entries only)'),
            (
                'nonofficial',
                'Non-official FEC report (posted and unposted entries)'),
            ], string='Export Type', required=True)
    }

    _defaults = {
        'type': 'is_ir_bic',
        'state': 'draft',
        'export_type': 'official'
    }

    def generate_fec(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "Expected singleton"

        obj = self.browse(cr, uid, ids[0], context)

        assert obj.fiscalyear_id.period_ids,\
            'The Fiscal Year must have periods'

        context = context or {}

        # We choose to implement the flat file instead of the XML
        # file for 2 reasons :
        # 1) the XSD file impose to have the label on the account.move
        # but Odoo has the label on the account.move.line, so that's a
        # problem !
        # 2) CSV files are easier to read/use for a regular accountant.
        # So it will be easier for the accountant to check the file before
        # sending it to the fiscal administration
        header = [
            'JournalCode',    # 0
            'JournalLib',     # 1
            'EcritureNum',    # 2
            'EcritureDate',   # 3
            'CompteNum',      # 4
            'CompteLib',      # 5
            'CompAuxNum',     # 6  We use partner.id
            'CompAuxLib',     # 7
            'PieceRef',       # 8
            'PieceDate',      # 9
            'EcritureLib',    # 10
            'Debit',          # 11
            'Credit',         # 12
            'EcritureLet',    # 13
            'DateLet',        # 14
            'ValidDate',      # 15
            'Montantdevise',  # 16
            'Idevise',        # 17
            ]

        company = obj.fiscalyear_id.company_id

        sql_query = '''
        SELECT
            replace(aj.code, '|', '/') AS JournalCode,
            replace(aj.name, '|', '/') AS JournalLib,
            replace(am.name, '|', '/') AS EcritureNum,
            am.date AS EcritureDate,
            aa.code AS CompteNum,
            replace(aa.name, '|', '/') AS CompteLib,
            CASE WHEN rp.ref IS null OR rp.ref = ''
            THEN 'ID ' || rp.id
            ELSE rp.ref
            END
            AS CompAuxNum,
            replace(rp.name, '|', '/') AS CompAuxLib,
            CASE WHEN am.ref IS null OR am.ref = ''
            THEN '-'
            ELSE replace(am.ref, '|', '/')
            END
            AS PieceRef,
            am.date AS PieceDate,
            replace(aml.name, '|', '/') AS EcritureLib,
            aml.debit AS Debit,
            aml.credit AS Credit,
            replace(amr.name, '|', '/') AS EcritureLet,
            amr.create_date::timestamp::date AS DateLet,
            am.date AS ValidDate,
            aml.amount_currency AS Montantdevise,
            rc.name AS Idevise
        FROM
            account_move_line aml
            LEFT JOIN account_move am ON am.id=aml.move_id
            LEFT JOIN res_partner rp ON rp.id=aml.partner_id
            LEFT JOIN account_move_reconcile amr ON amr.id = aml.reconcile_id
            JOIN account_journal aj ON aj.id = am.journal_id
            JOIN account_account aa ON aa.id = aml.account_id
            LEFT JOIN res_currency rc ON rc.id = aml.currency_id
        WHERE
            am.period_id IN %s
            AND am.company_id = %s
            AND (aml.debit != 0 OR aml.credit != 0)
        '''

        # For official report: only use posted entries
        if obj.export_type == "official":
            sql_query += '''
            AND am.state = 'posted'
            '''

        sql_query += '''
        ORDER BY
            am.date,
            CASE aj.type WHEN 'situation' THEN 1 ELSE 2 END,
            aml.id
        '''
        cr.execute(
            sql_query, (tuple([t.id for t in obj.fiscalyear_id.period_ids]), company.id))

        fecfile = StringIO.StringIO()
        w = unicodecsv.writer(fecfile, encoding='utf-8', delimiter='|')
        w.writerow(header)

        while 1:
            cr.arraysize = 100
            rows = cr.fetchmany()
            if not rows:
                break
            for row in rows:
                # We can't write in a tuple, so I convert to a list
                listrow = list(row)
                # Empty amount_currency i.e. remplace 0.0 by empty field
                if not listrow[16]:
                    listrow[16] = ''
                # Could we set the date format in the SQL query to avoid this?
                listrow[3] = listrow[3].replace('-', '')
                listrow[9] = listrow[9].replace('-', '')
                if listrow[14]:
                    listrow[14] = listrow[14].replace('-', '')
                listrow[15] = listrow[15].replace('-', '')
                # Decimal separator must be a coma
                listrow[11] = ('%.2f' % listrow[11]).replace('.', ',')
                listrow[12] = ('%.2f' % listrow[12]).replace('.', ',')
                if listrow[16]:
                    listrow[16] = ('%.2f' % listrow[16]).replace('.', ',')
                w.writerow(listrow)

        if not company.vat:
            raise Warning(
                _("Missing VAT number for company %s") % company.name)
        if company.vat[0:2] != 'FR':
            raise Warning(
                _("FEC is for French companies only !"))
        siren = company.vat[4:13]
        fy_end_date = obj.fiscalyear_id.date_stop.replace('-', '')
        suffix = ''
        if obj.export_type == "nonofficial":
            suffix = '-NONOFFICIAL'
        fecvalue = fecfile.getvalue()
        obj.write({
            'state': 'done',
            'fec_data': base64.encodestring(fecvalue),
            'filename': '%sFEC%s%s.csv' % (siren, fy_end_date, suffix),
            # Filename = <siren>FECYYYYMMDD where YYYMMDD is the closing date
            })
        fecfile.close()

        action = {
            'name': 'FEC',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': obj._name,
            'res_id': obj.id,
            'target': 'new',
            }
        return action
