# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random
import string
import re
import logging

_logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


def name_generator():
    letters = list(string.ascii_lowercase)
    first = list(string.ascii_uppercase)
    vocals = ['a', 'e', 'i', 'o', 'u', 'y', '']
    name = random.choice(first)
    for i in range(0, random.randint(3, 5)):
        name = name + random.choice(letters) + random.choice(vocals)
    return name


def image_generator_player(self):
    images = self.env['batgame.template'].search([('type', '=', '1')]).mapped('image')
    image = random.choice(images)

    return image


def image_generator_city(self):
    images = self.env['batgame.template'].search([('type', '=', '2')]).mapped('image')
    image = random.choice(images)

    return image


class player(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'
    _description = 'Players'

    # name = fields.Char(string="Name Player")
    is_player = fields.Boolean(default=True)
    is_premium = fields.Boolean(default=False, readonly=True)
    image = fields.Image(default=image_generator_player, max_width=60, max_height=60)
    type_race = fields.Selection([('1', 'Human'), ('2', 'Orc')], required=True)
    cities = fields.One2many('batgame.city', 'player', readonly=True)
    cities_attack = fields.Many2many('batgame.city', compute='_get_cities_attack')
    battles = fields.One2many('batgame.battle', 'player', readonly=True)
    level = fields.Integer(default=1, readonly=True)
    clan = fields.Many2one('batgame.clan')
    image_small = fields.Image(max_width=50, max_height=50, related='image', store=True)

    @api.constrains('name')
    def _check_name(self):
        regex = re.compile('[a-z]{1,10}\Z', re.I)
        for n in self:
            if regex.match(n.name):
                _logger.info('The name is correct')
            else:
                raise ValidationError("The name isn't correct, only letters with maximum 10")

    _sql_constraints = [('name_uniq', 'unique(name)', 'The name cannot be repeated')]

    def filter_cities(self, c, p):  # Only cities for attack (level >= 10)
        if c.level >= 10:
            if c.player != p:
                return True
            else:
                return False
        return False

    def _get_cities_attack(self):
        for p in self:
            cities = self.env['batgame.city'].search([]).filtered(lambda c: self.filter_cities(c, p))

            p.cities_attack = cities.ids


class city(models.Model):
    _name = 'batgame.city'
    _description = 'Cities'

    name = fields.Char()
    level = fields.Integer(default=1)
    player = fields.Many2one('res.partner')
    imageCity = fields.Image(default=image_generator_city, max_width=200, max_heigth=200)
    citizens = fields.One2many('batgame.citizen', 'city', ondelete='cascade')
    buildings = fields.One2many('batgame.building', 'city', ondelete='cascade')
    status = fields.Selection(
        [('1', 'Ruins'), ('2', 'Disrepair'), ('3', 'Good'), ('4', 'Better'), ('5', 'Top')], default='3')
    """available_buildings = fields.Many2many('batgame.building_type', compute='_get_available_buildings')"""
    food = fields.Integer(default=random.randint(1000, 1500))
    wood = fields.Integer(default=random.randint(100, 250))
    stone = fields.Integer(default=random.randint(100, 250))

    imageCity_small = fields.Image(max_width=50, max_height=50, related='imageCity', store=True)
    pos_x = fields.Integer(default=lambda self: self.random_generator(-100, 100))
    pos_y = fields.Integer(default=lambda self: self.random_generator(-100, 100))
    city_changes = fields.One2many('batgame.city_changes', 'city')

    @api.constrains('name')
    def _check_name(self):
        regex = re.compile('[a-z]{1,10}\Z', re.I)
        for n in self:
            if regex.match(n.name):
                _logger.info('The name is correct')
            else:
                raise ValidationError("The name isn't correct, only letters with maximum 10")

    _sql_constraints = [('name_uniq', 'unique(name)', 'The name cannot be repeated')]

    def create_citizen(self):
        if self.food < 100:
            raise ValidationError("Not enough food to create citizen")
        else:
            citizen = self.env.ref('batgame.add_citizen').read()[0]
            return citizen

    def create_building(self):
        if self.wood < 250 or self.stone < 250:
            raise ValidationError("Not enough wood or stone to create building")
        else:
            building = self.env.ref('batgame.add_building').read()[0]
            return building

    @api.model
    def random_generator(self, a, b):
        return random.randint(a, b)

    def calculate_production(self):
        for c in self:
            date = fields.Datetime.now()
            if c.player:
                final_food = c.food + self.random_generator(5, 10)
                final_wood = c.wood + self.random_generator(5, 10)
                final_stone = c.stone + self.random_generator(5, 10)
                city_changes = c.env['batgame.city_changes'].create(
                    {'city': c.id, 'time': date, 'name': c.name + " " + str(date)})

                c.write({
                    'food': final_food,
                    'wood': final_wood,
                    'stone': final_stone,
                })

                if c.player:
                    city_changes = c.env['batgame.city_changes'].create(
                        {'city': c.id, 'time': date, 'name': c.name + " " + str(date)})

                    city_changes.write({
                        'food': final_food,
                        'wood': final_wood,
                        'stone': final_stone,
                    })

                    if len(self.env['batgame.city_changes'].search([('city', '=', c.id)])) > 100:
                        n = len(self.env['batgame.city_changes'].search([('city', '=', c.id)])) - 100
                        eliminar = self.env['batgame.city_changes'].search([('city', '=', c.id)], limit=n)
                        eliminar.unlink()

    @api.model
    def update_resources(self):
        """users = self.env['res.partner'].search([])
        for s in users:
            s.is_player = False
        print("Players -> is_player = False")"""
        cities = self.env['batgame.city'].search([])
        cities.calculate_production()
        print("Resource updated")

    def _get_available_buildings(self):
        for p in self:
            c = self.env['batgame.construction'].search([('city', '=', p.id)])
            p.construction_buildings = c.ids

    def modified_city(self):
        records = self.browse(self.env.context.get('active_ids'))
        for p in records:
            p.write({'wood': 5000})
            p.write({'food': 5000})
            p.write({'stone': 5000})


class citizen(models.Model):
    _name = 'batgame.citizen'
    _description = 'Citizens'

    name = fields.Char(default=name_generator())
    type = fields.Selection([('1', 'Villager'), ('2', 'Soldier')], required=True, default='1')
    age = fields.Integer(default=random.randint(15, 25))
    resistance = fields.Float(default=random.randint(15, 25))
    attack = fields.Float(default=random.randint(25, 35))
    city = fields.Many2one('batgame.city', ondelete='restrict')
    requirements = fields.Integer(default=100)

    @api.model
    def create(self, value):
        new_id = super(citizen, self).create(value)
        c = new_id.city
        less_food = c.food - 100

        c.write({
            'food': less_food,
        })

        return new_id

    def calculate_attack_resistance(self):
        for c in self:
            if c.type_race == 1:
                c.resistance = self.random_generator(5, 10)
                c.attack = self.random_generator(5, 10)

            if c.type_race == 2:
                c.resistance = self.random_generator(15, 20)
                c.attack = self.random_generator(15, 20)


class building(models.Model):
    _name = 'batgame.building'
    _description = 'Buildings'

    name = fields.Many2one('batgame.building_type', 'name')
    resistance = fields.Integer(default=100)
    city = fields.Many2one('batgame.city', ondelete='restrict')

    @api.model
    def create(self, value):
        new_id = super(building, self).create(value)
        c = new_id.city
        less_wood = c.wood - 250
        less_stone = c.stone - 250

        c.write({
            'wood': less_wood,
            'stone': less_stone,
        })

        return new_id


class building_type(models.Model):
    _name = 'batgame.building_type'
    _description = 'Building types'

    name = fields.Selection([('Armery', 'Armery'), ('Farm', 'Farm'), ('House', 'House')])
    requirements = fields.Integer(default=100)
    building = fields.One2many('batgame.building', 'city', ondelete='cascade')
    time = fields.Float(default=10)
    """req_buildings = fields.Many2many('batgame.building_type', relation='req_buildings_many2many',
                                          column1='buildings', column2='required')"""


class clan(models.Model):
    _name = 'batgame.clan'
    _description = 'Clan'

    name = fields.Char()
    level = fields.Integer()
    players = fields.One2many('res.partner', 'clan')


class construction(models.Model):
    _name = 'batgame.construction'
    _description = 'Construction'

    name = fields.Char(compute='_get_name')
    city = fields.Many2one('batgame.city')
    building_type = fields.Many2one('batgame.building_type', ondelete='cascade', required=True)
    time = fields.Float()
    progress = fields.Float(compute='_get_progress')

    @api.depends('city', 'building_type')
    def _get_name(self):

        for c in self:
            if (c.city.name == False) or (c.building_type.name == False):
                c.name = "Construction name!"
            else:
                c.name = str(c.city.name) + " " + str(c.building_type.name)

    def update_progress(self):
        for c in self:
            if c.time <= 1:
                self.env['batgame.building'].create({'name': c.building_type.id, 'city': c.city.id})
                c.unlink()
            else:
                c.write({'time': c.time - 1})

    @api.depends('time')
    def _get_progress(self):
        for c in self:
            if c.building_type:
                c.progress = 100 * (1 - c.time / c.building_type.time)
            else:
                c.progress = 0


class battle(models.Model):
    _name = 'batgame.battle'
    _description = 'Battle vs other city'

    name = fields.Char(compute='_get_name')
    player = fields.Many2one('res.partner')
    origin_city = fields.Many2one('batgame.city', required=True, ondelete='restrict')
    destiny_city = fields.Many2one('batgame.city', required=True, ondelete='restrict')
    travel_duration = fields.Integer(default=0, compute='_get_travel_duration')
    battle_duration = fields.Datetime(compute='_get_battle_duration')
    launch_time = fields.Datetime(default=lambda t: fields.Datetime.now(), readonly=True)
    percent = fields.Float(compute='_get_percent')
    finished = fields.Boolean(default=False)
    terminated = fields.Boolean(default=False)
    instant = fields.Boolean(default=False)

    @api.onchange('player')
    def _onchange_player(self):

        return {
            'domain': {'origin_city': [('player', '=', self.player.id)],
                       'destiny_city': [('player', '!=', self.player.id)]},
        }

    """@api.onchange('origin_city')
    def _onchange_city(self):
        return {
            'domain': {'origin_city': [('id', '!=', self.origin_city.id)]},
        }"""

    @api.model
    def update_resources(self):
        print(self.env['batgame.battle'].search([]))

    def change_materials(self, winner, loser):
        food_temp = loser.food
        wood_temp = loser.wood
        stone_temp = loser.stone

        if loser.food > 500:
            if (loser.food - (loser.food * 20 / 100)) <= 500:
                loser.food = 500
            else:
                loser.food = loser.food - (loser.food * 20 / 100)

        if loser.wood > 500:
            if (loser.wood - (loser.wood * 20 / 100)) <= 500:
                loser.wood = 500
            else:
                loser.wood = loser.wood - (loser.wood * 20 / 100)

        if loser.stone > 500:
            if (loser.stone - (loser.stone * 20 / 100)) <= 500:
                loser.stone = 500
            else:
                loser.stone = loser.stone - (loser.stone * 20 / 100)

        change_food = food_temp - loser.food
        change_wood = wood_temp - loser.wood
        change_stone = stone_temp - loser.stone

        winner.food = winner.food + change_food
        winner.wood = winner.wood + change_wood
        winner.stone = winner.stone + change_stone

    def winner_up_level(self, winner):
        if winner.level < 20:
            winner.level = winner.level + 1
        if winner.player.level < 50:
            winner.player.level = winner.player.level + 1

    def change_status(self, winner, loser):
        if winner.status <= '4':
            winner.status = str(int(winner.status) + 1)

        if loser.status >= '2':
            loser.status = str(int(loser.status) - 1)

    def win_resist_attack(self, citizens):
        for s in citizens:
            if s.resistance < 30:
                s.resistance = s.resistance + (s.resistance * 10 / 100)
            if s.attack < 50:
                s.attack = s.attack + (s.attack * 10 / 100)

    def misses_resist_attack(self, citizens):
        for s in citizens:
            s.resistance = s.resistance - (s.resistance * 20 / 100)
            s.attack = s.attack - (s.attack * 20 / 100)
            if s.resistance <= 5:
                s.unlink()

    def misses_resist_building_winner(self, origin_city):
        for b in origin_city.buildings:
            b.resistance -= 10

    def misses_resist_building_loser(self, origin_city):
        for b in origin_city.buildings:
            b.resistance -= 25

    @api.model
    def update_battle(self):
        origin_resistance = 0
        origin_attack = 0

        destiny_resistance = 0
        destiny_attack = 0

        change_food = 0
        change_wood = 0
        change_stone = 0

        combates = self.search([('finished', '=', True), ('terminated', '=', False)])
        if combates:
            for c in combates:
                origin_citizens = self.env['batgame.citizen'].search([('city', '=', c.origin_city.id)])
                for s in origin_citizens:
                    origin_resistance += s.resistance
                    origin_attack += s.attack
                origin_total = origin_resistance + origin_attack

                destiny_citizens = self.env['batgame.citizen'].search([('city', '=', c.destiny_city.id)])
                for s in destiny_citizens:
                    destiny_resistance += s.resistance
                    destiny_attack += s.attack
                destiny_total = destiny_resistance + destiny_attack

                """Mayor probabilidad de ganar, quien tenga más resistance y attack"""
                rnd_origin = random.randint(1, int(origin_total))
                rnd_destiny = random.randint(1, int(destiny_total))

                if rnd_origin >= rnd_destiny:
                    winner = c.origin_city
                    loser = c.destiny_city
                    change_food = winner.food
                    change_wood = winner.wood
                    change_stone = winner.stone

                    """Limite de nivel para ciudad = 20 y para jugador = 50"""
                    self.winner_up_level(winner)

                    """Se le quita resistencia y ataque a los ciudadanos perdedores"""
                    self.misses_resist_attack(destiny_citizens)

                    """Se le añade resistencia y ataque a los ciudadanos ganadores"""
                    self.win_resist_attack(origin_citizens)

                    """El perdedor baja el estado de la ciudad en uno y el ganador sube en uno"""
                    self.change_status(winner, loser)

                    """Al perdedor se le quita el 20% de materiales si tiene más de 500
                    y al ganador se le añade los materiales que se le han quitado al perdedor"""
                    self.change_materials(winner, loser)

                    """Los edificios atacados pierden 10 puntos de resistencia si ganan
                    y 25 si pierden"""
                    self.misses_resist_building_loser(loser)

                else:
                    winner = c.destiny_city
                    loser = c.origin_city
                    change_food = winner.food
                    change_wood = winner.wood
                    change_stone = winner.stone

                    self.winner_up_level(winner)

                    self.misses_resist_attack(origin_citizens)

                    self.win_resist_attack(destiny_citizens)

                    self.change_status(winner, loser)

                    self.change_materials(winner, loser)

                    self.misses_resist_building_winner(winner)

                change_food -= winner.food
                change_wood -= winner.wood
                change_stone -= winner.stone

                print()
                print("Probability Origin City -> ", rnd_origin)
                print("Probability Destiny City -> ", rnd_destiny)
                print("Winner: ", winner.player.name, " lvl-", winner.player.level, " (", winner.name, " lvl-",
                      winner.level, ")")
                print("Win mats -> Food:", abs(change_food), "  Wood:", abs(change_wood), "  Stone:", abs(change_stone))
                print("Total ----> Food:", winner.food, "  Wood:", winner.wood, "  Stone:", winner.stone)
                print("-------------------------------------------")
                print("Loser: ", loser.player.name, " lvl-", loser.player.level, " (", loser.name, " lvl-",
                      loser.level, ")")
                print("Lost mats -> Food:", change_food, "  Wood:", change_wood, "  Stone:", change_stone)
                print("Total -----> Food:", loser.food, "  Wood:", loser.wood, "  Stone:", loser.stone)
                print("//////////////  BATTLE OVER  //////////////")
                print()

                c.terminated = True

        else:
            print("No battles going on")

    @api.depends('origin_city', 'destiny_city', 'player')
    def _get_name(self):
        for n in self:
            if (n.origin_city.name == False) or (n.destiny_city.name == False) or (n.player.name == False):
                n.name = "Battle name!"
            else:
                n.name = str(n.player.name) + " (" + str(n.origin_city.name) + " -> " + str(n.destiny_city.name) + ")"

    @api.depends('travel_duration')
    def _get_percent(self):
        for t in self:
            t.battle_duration = fields.Datetime.from_string(t.launch_time) + timedelta(minutes=t.travel_duration)

            passed = fields.Datetime.from_string(t.battle_duration) - datetime.now()

            if t.travel_duration == 0:
                t.percent = 0
                t.name += ' Battle Finish'
                t.finished = True
            else:
                t.percent = (100 * passed.seconds) / (t.travel_duration * 60)

            if t.percent > 100:
                t.percent = 0
                t.name += ' Battle Finish'
                t.finished = True

    @api.depends('origin_city', 'destiny_city')
    def _get_travel_duration(self):
        for t in self:
            if t.instant:
                t.travel_duration = 0
            else:
                t.travel_duration = ((((t.destiny_city.pos_x - t.origin_city.pos_x) ** 2) + (
                        (t.destiny_city.pos_y - t.origin_city.pos_y) ** 2)) ** 0.5)

    @api.depends('battle_duration')
    def _get_battle_duration(self):
        for t in self:
            t.battle_duration = fields.Datetime.from_string(t.launch_time) + timedelta(minutes=t.travel_duration)

            """passed = fields.Datetime.from_string(t.battle_duration) - datetime.now()
            t.time_remaining = 100 * passed.seconds / (t.travel_duration * 3600)"""

    def speed_up_battle(self):
        for t in self:
            if t.player.is_premium == True:
                t.instant = True
            else:
                raise ValidationError("You need to be premium!")


class city_changes(models.Model):
    _name = 'batgame.city_changes'
    _description = 'Changes in city'

    name = fields.Char()
    city = fields.Many2one('batgame.city', ondelete='cascade', required=True)
    time = fields.Char()

    food = fields.Integer()
    wood = fields.Integer()
    stone = fields.Integer()

    food_reduction = fields.Integer(digits=(12, 4))
    food_increment = fields.Integer(digits=(12, 4))

    wood_reduction = fields.Integer(digits=(12, 4))
    wood_increment = fields.Integer(digits=(12, 4))

    stone_reduction = fields.Integer(digits=(12, 4))
    stone_increment = fields.Integer(digits=(12, 4))


class template(models.Model):
    _name = 'batgame.template'
    _description = 'Templates of the game'

    name = fields.Char()
    type = fields.Selection([('1', 'Player'), ('2', 'City')])
    image = fields.Image()


"""class citizen_type(models.Model):
    _name = 'batgame.citizen_type'
    _description = 'Citizen types'

    name = fields.Char()"""
