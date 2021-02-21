from odoo import models, fields, api
import random
import string
import json
import math
from datetime import datetime, timedelta


class city_wizard(models.TransientModel):
    _name = 'batgame.city_wizard'

    def _default_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    def image_generator_city(self):
        images = self.env['batgame.template'].search([('type', '=', '2')]).mapped('image')
        image = random.choice(images)

        return image

    name = fields.Char()
    player = fields.Many2one('res.partner', readonly=True, required=True, default=_default_player)
    imageCity = fields.Image(default=image_generator_city, max_width=200, max_heigth=200)
    food = fields.Integer(default=random.randint(100, 250), readonly=True)
    wood = fields.Integer(default=random.randint(100, 250), readonly=True)
    stone = fields.Integer(default=random.randint(100, 250), readonly=True)
    pos_x = fields.Integer(default=lambda self: self.random_generator(-100, 100), readonly=True)
    pos_y = fields.Integer(default=lambda self: self.random_generator(-100, 100), readonly=True)

    """citizens = fields.Many2many('batgame.citizen')"""
    """buildings = fields.Many2many('batgame.building')"""

    """citizens = fields.Many2many('batgame.citizen_type_wizard', compute='_get_citizens')"""
    buildings = fields.Many2many('batgame.building_type_wizard', compute='_get_buildings')

    def _get_buildings(self):
        building_types = self.env['batgame.building_type'].search([]).mapped(
            lambda bt: self.env['batgame.building_type_wizard'].create({'building_type': bt.id}))

        """for p in building_types:
            a_b = building_types.search([]).filtered(lambda b: self.filter_building(b, p))
            p.available_buildings = a_b.ids"""

        self.buildings = building_types

    buildings_aux = fields.Many2one('batgame.building_type')
    buildings_new = fields.One2many('batgame.building_wizard', 'city_wizard')

    state = fields.Selection([('initial', 'Initial data'),
                              ('buildings', 'Buildings')],
                             default='initial'
                             )

    def _get_citizens(self):
        citizens_types = self.env['batgame.citizen'].search([]).mapped(
            lambda bt: self.env['batgame.citizen_type_wizard'].create({'citizen_type': bt.id}))

        """for p in building_types:
            a_b = building_types.search([]).filtered(lambda b: self.filter_building(b, p))
            p.available_buildings = a_b.ids"""

        self.citizens = citizens_types

    """citizens_aux = fields.Many2one('batgame.citizens')
    citizens_new = fields.One2many('batgame.citizen_wizard', 'city_wizard')"""

    @api.onchange('name')
    def onchange_name(self):
        name = self.name
        if len(self.env['batgame.city'].search([('name', '=', name)])) > 0:
            self.name = str(name) + str("_other name")
            return (
                {'warning': {'title': "Name Repeated", 'message': "The name is repeated", 'type': 'notification'}, })

    def random_generator(self, a, b):
        return random.randint(a, b)

    def calculate_production(self):
        for c in self:
            if c.player:
                final_food = c.food + self.random_generator(5, 10)
                final_wood = c.wood + self.random_generator(5, 10)
                final_stone = c.stone + self.random_generator(5, 10)

                c.write({
                    'food': final_food,
                    'wood': final_wood,
                    'stone': final_stone,
                })

    @api.model
    def update_resources(self):
        cities = self.env['batgame.city'].search([])
        cities.calculate_production()
        print("Resource updated")

    def add_building(self):
        b = self.env['batgame.building_wizard'].create({'name': self.buildings_aux.id, 'city_wizard': self.id})
        return {
            'name': "City Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batgame.city_wizard',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def add_citizen(self):
        """b = self.env['batgame.citizen_wizard'].create({'name': self.citizens_aux.id, 'city_wizard': self.id})"""
        return {
            'name': "City Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batgame.city_wizard',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def next(self):
        if self.state == 'initial':
            self.state = 'buildings'
        """elif self.state == 'buildings':
            self.state = 'citizens'"""
        return {
            'name': "City Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batgame.city_wizard',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def previous(self):
        if self.state == 'buildings':
            self.state = 'initial'
        """elif self.state == 'citizens':
            self.state = 'buildings'"""
        return {
            'name': "City Wizard",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batgame.city_wizard',
            'res_id': self.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def create_city(self):
        new_city = {}
        new_city['name'] = self.name
        new_city['player'] = self.player.id
        new_city['imageCity'] = self.imageCity

        city = self.env['batgame.city'].create(new_city)

        for b in self.buildings_new:
            new_building = self.env['batgame.building'].create({
                'city': city.id,
                'name': b.name.id,
            })

        """for c in self.citizens:
            new_citizen = self.env['batgame.citizen'].create({
                'city': city.id,
                'name': c.id,
            })"""

        return {
            'name': 'New City',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'batgame.city',
            'res_id': city.id,
            'context': self._context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    class building_wizard(models.TransientModel):
        _name = 'batgame.building_wizard'

        name = fields.Many2one('batgame.building_type')
        city_wizard = fields.Many2one('batgame.city_wizard')

    class building_type_wizard(models.TransientModel):
        _name = 'batgame.building_type_wizard'

        building_type = fields.Many2one('batgame.building_type')
        name = fields.Selection(related='building_type.name')

        def add(self):
            city_wizard = self.env.context.get('city_wizard')
            b = self.env['batgame.building_wizard'].create({'name': self.building_type.id,
                                                            'city_wizard': city_wizard})
            return {
                'name': "City Wizard",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'batgame.city_wizard',  # Modelo destino
                'res_id': city_wizard,  # Id para abrir form
                # 'view_id': self.ref('wizards.reserves_form') # Opcional si hay mas de una vista posible.
                'context': self._context,  # El context se puede ampliar para anyadir opciones
                'type': 'ir.actions.act_window',
                'target': 'new',  # Si se hace en current, cambia la ventana actual.
            }

    """class citizen_wizard(models.TransientModel):
        _name = 'batgame.citizen_wizard'

        name = fields.Many2one('batgame.citizen')
        city_wizard = fields.Many2one('batgame.city_wizard')

    class citizen_type_wizard(models.TransientModel):
        _name = 'batgame.building_type_wizard'

        citizen_type = fields.Many2one('batgame.citizen')
        name = fields.Selection(related='citizen.name')

        def add(self):
            city_wizard = self.env.context.get('city_wizard')
            b = self.env['batgame.citizen_wizard'].create({'name': self.building_type.id,
                                                            'city_wizard': city_wizard})
            return {
                'name': "City Wizard",
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'batgame.city_wizard',  # Modelo destino
                'res_id': city_wizard,  # Id para abrir form
                # 'view_id': self.ref('wizards.reserves_form') # Opcional si hay mas de una vista posible.
                'context': self._context,  # El context se puede ampliar para anyadir opciones
                'type': 'ir.actions.act_window',
                'target': 'new',  # Si se hace en current, cambia la ventana actual.
            }"""
