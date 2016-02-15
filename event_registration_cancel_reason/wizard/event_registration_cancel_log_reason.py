# -*- coding: utf-8 -*-
# © 2016 Antiun Ingeniería S.L.
# © 2016 Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, exceptions, fields, models


class EventRegistrationCancelLogReason(models.TransientModel):
    _name = 'event.registration.cancel.log.reason'

    event_type_id = fields.Many2one(
        comodel_name="event.type", string="Event type")
    reason_id = fields.Many2one(
        comodel_name="event.registration.cancel.reason", required=True,
        domain="['|', "
               " ('event_type_ids', '=', False), "
               " ('event_type_ids', '=', event_type_id)]")

    @api.model
    def default_get(self, var_fields):
        res = super(EventRegistrationCancelLogReason, self).default_get(
            var_fields)
        registrations = self.env['event.registration'].browse(
            self.env.context['active_ids'])
        event_type = registrations.mapped("event_id.type")
        try:
            event_type.ensure_one()
        except exceptions.except_orm:
            raise exceptions.ValidationError(
                _("You cannot cancel registrations from events of different "
                  "types at once."))
        res['event_type_id'] = event_type.id
        return res

    @api.multi
    def button_log(self):
        self.ensure_one()
        registrations = self.env['event.registration'].browse(
            self.env.context['active_ids'])
        registrations.write({'cancel_reason_id': self.reason_id.id})
        registrations.with_context(bypass_reason=True).button_reg_cancel()
