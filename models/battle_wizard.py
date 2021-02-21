from odoo import models, fields, api
import random
import string
import json
import math
from datetime import datetime, timedelta

class battle_wizard(models.TransientModel):
    _name = 'batgame.battle_wizard'

    def _default_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))
    player = fields.Many2one('res.partner', readonly=True, required=True, default=_default_player)
    origin_city = fields.Many2one('batgame.city', required=True, ondelete='restrict', readonly=True)
    destiny_city = fields.Many2one('batgame.city', required=True, ondelete='restrict', readonly=True)
    """travel_duration = fields.Integer(default=0, compute='_get_travel_duration')
    battle_duration = fields.Datetime(compute='_get_battle_duration')
    percent = fields.Float(compute='_get_percent')
    launch_time = fields.Datetime(default=lambda t: fields.Datetime.now(), readonly=True)"""

    @api.onchange('player')
    def _onchange_player(self):

        return {
            'domain': {'origin_city': [('player', '=', self.player.id)],
                       'destiny_city': [('player', '!=', self.player.id)]},
        }

    """@api.onchange('origin_city')
    def _onchange_city(self):

        return {
            'domain': {'destiny_city': [('id', '!=', self.origin_city.id)]},

        }"""

    """@api.model
    def update_resources(self):
        print(self.env['batgame.battle'].search([]))

    @api.depends('origin_city', 'destiny_city', 'player')
    def _get_name(self):
        for n in self:
            if (n.origin_city.name == False) or (n.destiny_city.name == False) or (n.player.name == False):
                n.name = "Battle name!"
            else:
                n.name = str(n.player.name) + " (" + str(n.origin_city.name) + " -> " + str(n.destiny_city.name) + ")"

    @api.depends('origin_city', 'destiny_city')
    def _get_percent(self):
        for d in self:
            d.percent = 50.0

    @api.depends('origin_city', 'destiny_city')
    def _get_travel_duration(self):
        for t in self:
            t.travel_duration = ((((t.destiny_city.pos_x - t.origin_city.pos_x) ** 2) + (
                    (t.destiny_city.pos_y - t.origin_city.pos_y) ** 2)) ** 0.5)

            if t.travel_duration < 25:
                t.travel_duration = 25

    @api.depends('battle_duration')
    def _get_battle_duration(self):
        for t in self:
            t.battle_duration = fields.Datetime.from_string(t.launch_time) + timedelta(minutes=t.travel_duration)

            passed = fields.Datetime.from_string(t.battle_duration) - datetime.now()
            t.time_remaining = 100 * passed.seconds / (t.travel_duration * 3600)"""

    def create_battle(self):
        self.env['batgame.battle'].create({
            'player': self.player.id,
            'origin_city': self.origin_city.id,
            'destiny_city': self.destiny_city.id
        })