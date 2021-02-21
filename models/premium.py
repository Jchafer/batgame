# -*- coding: utf-8 -*-

from odoo import models, fields, api
# herència de classe
class player_premium(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'
    _description = 'Player Premium'
    # Main fields
    is_premium = fields.Boolean()

    def _get_travel_duration(self):
        for t in self:
            super(player_premium, self)._get_travel_duration()
            t.travel_duration = ((((t.destiny_city.pos_x - t.origin_city.pos_x) ** 2) + (
                    (t.destiny_city.pos_y - t.origin_city.pos_y) ** 2)) ** 0.5)

            if t.travel_duration > 25:
                t.travel_duration = 1
