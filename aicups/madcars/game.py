import asyncio
import gzip
import json
import random
from collections import defaultdict

import math
import os
from itertools import product

import pymunkoptions
from pyglet.gl import *

from mechanic.constants import MAX_TICK_COUNT
from game_math import CarPosition, cars, maps
from geometry2d import Vec2d

pymunkoptions.options["debug"] = False
import pymunk

from mechanic.game_objects.cars import Buggy, Bus, SquareWheelsBuggy
from mechanic.game_objects.maps import PillMap, PillHubbleMap, PillHillMap, PillCarcassMap, IslandMap, IslandHoleMap
from mechanic.match import Match
from mechanic.player import Player

import pyglet

class Game(object):
    CARS_MAP = {
        'Buggy': Buggy,
        'Bus': Bus,
        'SquareWheelsBuggy': SquareWheelsBuggy,

    }

    MAPS_MAP = {
        'PillMap': PillMap,
        'PillHubbleMap': PillHubbleMap,
        'PillHillMap': PillHillMap,
        'PillCarcassMap': PillCarcassMap,
        'IslandMap': IslandMap,
        'IslandHoleMap': IslandHoleMap,
    }

    RESULT_LOCATION = os.environ.get('GAME_LOG_LOCATION', './result')

    BASE_DIR = os.path.dirname(RESULT_LOCATION)

    VISIO_LOCATION = os.path.join(BASE_DIR, 'visio.gz')
    SCORES_LOCATION = os.path.join(BASE_DIR, 'scores.json')
    DEBUG_LOCATION = os.path.join(BASE_DIR, '{}')

    def __init__(self, clients, games_list, extended_save=True):
        self.game_complete = False
        self.extended_save = extended_save

        self.max_match_count = math.ceil(len(games_list)/2)
        self.all_players = [Player(index + 1, client, self.max_match_count) for index, client in enumerate(clients)]

        self.space = pymunk.Space()
        self.space.gravity = (0.0, -700)
        self.space.damping = 0.85
        self.scores = defaultdict(int)
        self.matches = self.parse_games(games_list)
        self.current_match = None
        self.tick_num = 0

        self.game_log = []

    @classmethod
    def parse_games(cls, games_list):
        for g in games_list:
            m, c = g.split(',', maxsplit=1)
            yield (cls.MAPS_MAP.get(m, PillMap), cls.CARS_MAP.get(c, Buggy))

    def clear_space(self):
        self.space.remove(self.space.shapes)
        self.space.remove(self.space.bodies)
        self.space.remove(self.space.constraints)

    def end_game(self):
        self.game_complete = True
        self.game_save()

    def get_winner(self):
        winner = sorted(self.all_players, key=lambda x: x.lives, reverse=True)
        if winner:
            return winner[0]
        return False

    @asyncio.coroutine
    def next_match(self):
        map, car = next(self.matches)
        self.clear_space()
        match = Match(map, car, self.all_players, self.space)
        yield from match.send_new_match_message()
        self.space.add(match.get_objects_for_space())
        self.current_match = match

    @asyncio.coroutine
    def game_loop(self):
        for i in range(MAX_TICK_COUNT):
            if i % 2000 == 0:
                print('tick {}'.format(i))
            is_game_continue = yield from self.tick()
            if is_game_continue == 'end_game':
                break

    @asyncio.coroutine
    def tick(self):
        if self.current_match is None:
            yield from self.next_match()

        yield from self.current_match.tick(self.tick_num)
        self.space.step(0.016)

        if self.current_match.is_match_ended():
            self.game_log.extend(self.current_match.end_match())

            if not all([p.is_alive() for p in self.all_players]):
                self.game_log.append({
                    'type': "end_game",
                    "params": {p.id: p.get_lives() for p in self.all_players}
                })
                self.end_game()

                return 'end_game'
            yield from self.next_match()

        self.tick_num += 1

    def draw(self, draw_options):
        self.space.debug_draw(draw_options)
        self.check_my_code()

    old_angle = 2*[0]
    old_position = [Vec2d(0, 0), Vec2d(0, 0)]
    def check_my_code(self):
        if self.current_match is not None:
            map = maps[self.current_match.map.external_id]
            for arc in map.base_arcs:
                for line_2d in arc.segment_edges:
                    self.draw_line(line_2d)

            for line_2d in map.base_segments:
                self.draw_line(line_2d)

            for arc in map.additional_arcs:
                for line_2d in arc.segment_edges:
                    self.draw_line(line_2d)

        for car_index in range(0, 2):
            if self.all_players[car_index].car is not None:
                car = self.all_players[car_index].car
                car_angular_speed = car.car_body.angle - self.old_angle[car_index]
                self.old_angle[car_index] = car.car_body.angle
                car_position = Vec2d(car.car_body.position.x, car.car_body.position.y)
                car_speed = (self.old_position[car_index] - car_position).length()
                self.old_position[car_index] = car_position
                car_angle = car.car_body.angle
                car_position_obj = CarPosition(car.fast_dump(), 1)
                custom_car = cars[car.external_id]
                obbs = car_position_obj.obbs(custom_car)
                for obb in obbs:
                    self.draw_obb(obb)
                obb2 = custom_car.car_button_obb(car_position_obj)
                self.draw_obb(obb2)
                x = car.car_body.position.x - 100
                y = car.car_body.position.y
                self.log("{0} {1} {2} {3}".format(
                     round(car.car_body.angle, 3),round(car_angular_speed, 3),
                     round(car_speed, 3),round(car_position_obj.norm_angle, 3)), x, y - 100)
                f, r = car_position_obj.is_touch_ground_wheels(custom_car, map)
                self.log("{0} {1}".format(f, r), x, y + 100)


    def draw_obb(self, obb):
        pyglet.gl.glColor4f(0, 0, 0, 2.0)
        edges = obb.edges()
        for line_2d in edges:
            pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2f', (line_2d.st.x, line_2d.st.y, line_2d.ed.x, line_2d.ed.y)))

    def draw_line(self, line_2d):
        pyglet.gl.glColor4f(0, 0, 0, 2.0)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
            ('v2f', (line_2d.st.x, line_2d.st.y, line_2d.ed.x, line_2d.ed.y)))

    def log(self, text, x, y):
         pyglet.text.Label(text,font_size=12, color=(0, 0, 0, 255),
                       x=x, y=y).draw()

    @staticmethod
    def vec2d_pair(vec2d):
        return vec2d.x, vec2d.y

    def get_players_external_id(self):
        return {p.id: p.get_solution_id() for p in self.all_players}

    def save_visio(self):
        d = {
            'config': self.get_players_external_id(),
            'visio_info': self.game_log
        }
        with gzip.open(self.VISIO_LOCATION, 'wb') as f:
            f.write(json.dumps(d).encode())
        return {
            "filename": os.path.basename(self.VISIO_LOCATION),
            "location": self.VISIO_LOCATION,
            "is_private": False
        }

    def save_scores(self):
        d = {p.get_solution_id(): p.get_lives() for p in self.all_players}

        with open(self.SCORES_LOCATION, 'w') as f:
            f.write(json.dumps(d))

        return {
            "filename": os.path.basename(self.SCORES_LOCATION),
            "location": self.SCORES_LOCATION,
            "is_private": False
        }

    def save_debug(self):
        return [
            p.save_log(self.DEBUG_LOCATION) for p in self.all_players
        ]

    def game_save(self):
        if self.extended_save:
            result = {
                "scores": self.save_scores(),
                "debug": self.save_debug(),
                "visio": self.save_visio()
            }

            with open(self.RESULT_LOCATION, 'w') as f:
                f.write(json.dumps(result))
        else:
            self.save_debug()
            self.save_visio()

    @classmethod
    def generate_matches(cls, count):
        available_matches = product(sorted(cls.MAPS_MAP.keys()), sorted(cls.CARS_MAP.keys()))
        return random.sample([','.join(x) for x in available_matches], count)
