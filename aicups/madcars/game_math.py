from cars import *
from maps import *
import itertools

cars = {Buggy.external_id: Buggy(), Bus.external_id: Bus(), SquareWheelsBuggy.external_id: SquareWheelsBuggy()}
maps = {PillMap.external_id: PillMap(), PillHubbleMap.external_id: PillHubbleMap(), PillHillMap.external_id: PillHillMap(),
        PillCarcassMap.external_id: PillCarcassMap(), IslandMap.external_id: IslandMap(),
        IslandHoleMap.external_id: IslandHoleMap()}


class Game:
    def __init__(self, ml, el, car_id, map_id):
        self.my_lives = ml
        self.enemy_lives = el
        self.car = cars[car_id]
        self.map = maps[map_id]


class Wheel:
    def __init__(self, car_wheel_json):
        self.pt = Vec2d(car_wheel_json[0], car_wheel_json[1])
        self.angle = car_wheel_json[2]

    @property
    def x(self):
        return self.pt.x

    @property
    def y(self):
        return self.pt.y

    def __str__(self) -> str:
        return "{0},{1}".format(self.pt, self.angle)

    def dead_line_distance(self, dead_line):
        return self.pt.distance(Vec2d(self.x, dead_line))


class CarPosition:
    def __init__(self, car_json_array, external_id):
        self.point = Vec2d.from_tuple(car_json_array[0])
        self.angle = car_json_array[1]
        self.norm_angle = car_json_array[1] % math.pi
        self.left_right = car_json_array[2]
        self.rear_wheel = Wheel(car_json_array[3])
        self.front_wheel = Wheel(car_json_array[4])
        self.car_roof_y = self.point.y + (42 if external_id == Buggy.external_id else 62)

    @property
    def abs_angle(self):
        return abs(self.angle)

    @property
    def abs_norm_angle(self):
        return abs(self.norm_angle)

    @property
    def abs_angle(self):
        return abs(self.angle)

    def is_left(self):
        return self.left_right == 1

    def wheel_distance(self):
        return self.rear_wheel.pt.distance(self.front_wheel.pt)

    def clockwise(self):
        return self.front_wheel.y > self.rear_wheel.y

    def dead_line_distance(self, dead_line):
        return min(self.front_wheel.dead_line_distance(dead_line), self.rear_wheel.dead_line_distance(dead_line))

    def button_y(self, button_min_y):
        if self.angle == 0:
            return self.point.y + button_min_y
        else:
            return self.point.y + math.sin(self.angle)*button_min_y

    def is_touch_car(self, game, another):
        my_obb = OBB.from_car(self, game.car)
        an_obb = OBB.from_car(another, game.car)
        return my_obb.intersect(an_obb)

    def is_wheels_touch_car(self, game, another):
        rear_wheel_box = OBB.from_wheel(self.rear_wheel, game.car.rear_wheel_radius)
        front_wheel_box = OBB.from_wheel(self.front_wheel, game.car.front_wheel_radius)
        an_obb = OBB.from_car(another, game.car)
        return an_obb.intersect(rear_wheel_box), an_obb.intersect(front_wheel_box)

    def any_wheels_touch_button(self, game, another):
        rear_wheel_box = OBB.from_wheel(another.rear_wheel, game.car.rear_wheel_radius)
        front_wheel_box = OBB.from_wheel(another.front_wheel, game.car.front_wheel_radius)
        an_obb = game.car.car_button_obb(self)
        return an_obb.intersect(rear_wheel_box) or an_obb.intersect(front_wheel_box)

    def is_button_touch_ground(self, game):
        aabb = game.car.car_button_aabb(self)
        touch = False
        for seg in itertools.chain(game.map.base_segments, game.map.additional_segments):
            touch |= aabb.intersect_line(seg)

        for arc in itertools.chain(game.map.base_arcs, game.map.additional_arcs):
            for edge in arc.segment_edges:
                touch |= aabb.intersect_line(edge)

        return touch

    def is_touch_ground_wheels(self, car, map):
        rear_wheel_box = AABB.from_wheel(self.rear_wheel, car.rear_wheel_radius)
        front_wheel_box = AABB.from_wheel(self.front_wheel, car.front_wheel_radius)

        rear_wheel_touch, front_wheel_touch = False, False
        for seg in itertools.chain(map.base_segments, map.additional_segments):
            rear_wheel_touch |= rear_wheel_box.intersect_line(seg)
            front_wheel_touch |= front_wheel_box.intersect_line(seg)

        for arc in itertools.chain(map.base_arcs, map.additional_arcs):
            for edge in arc.segment_edges:
                rear_wheel_touch |= rear_wheel_box.intersect_line(edge)
                front_wheel_touch |= front_wheel_box.intersect_line(edge)

        return front_wheel_touch, rear_wheel_touch

    def obbs(self, car):
        return [
            OBB.from_car(self, car),
            OBB.from_wheel(self.rear_wheel, car.rear_wheel_radius),
            OBB.from_wheel(self.front_wheel, car.front_wheel_radius)]
