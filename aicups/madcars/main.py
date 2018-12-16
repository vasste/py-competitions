import json
from enum import Enum

from game_math import *


class GameState(Enum):
    FIRST_GROUND = 5
    BUTTON_HUNT = 1
    BUTTON_HUNT_NON_DEFAULT = 16
    BUTTON_DEFENCE = 2
    DEAD_LINE = 3
    DEAD_LINE_ESCAPE = 4
    TOUCH_GROUND = 6
    BEGIN_STOPPING = 7
    STOP = 8
    BUGGY_SPEED = 9
    STOPPING = 10

    BUS_INCLINE_LEFT = 12
    BUS_INCLINE_RIGHT = 13
    BUS_INCLINE = 15
    REVERSE = 11
    BUGGY_STOP = 14

    BUTTON_ROTATION_CLOCK = 17
    BUTTON_ROTATION_COUNTER = 18

    def __str__(self):
        return "{0}".format(self.name)


game, my_car_pos, enemy_car_pos = None, None, None
dead_line = 0
game_state = GameState.FIRST_GROUND
last_cmd = 'stop'

car_speed = Vec2d(0, 0)
car_angular_speed = 0
strategy_map_default = False

debug = True
debug_message = {}

# tune
# pill bus заехать повыше и стоять
# humble map bus приземление

# hill приземление
# решить проблемы с защитой от аттаки и определдение аттаки
# island holo сломать квдратные колеса на жердочки
# cross нормально стоять автобусом, убивать баг и что просто стоят
# hill map buggy неправильно запрыгивает
def strategy_default(update=False):
    global dead_line, last_cmd, game_state, game, my_car_pos, enemy_car_pos, cmd, debug_message
    global front_wheel_touch, rear_wheel_touch
    global front_wheel_touch_car, rear_wheel_touch_car
    global enemy_rear_wheel_touch_car, enemy_wheel_touch_car
    global strategy_map_default, ready_for_defence

    both_wheels_touch_ground = rear_wheel_touch and front_wheel_touch
    any_wheels_touch_ground = rear_wheel_touch or front_wheel_touch

    change_places = my_car_pos.is_left() and my_car_pos.point.x > enemy_car_pos.point.x or \
        not my_car_pos.is_left() and my_car_pos.point.x < enemy_car_pos.point.x

    if game_state == GameState.FIRST_GROUND:
        if both_wheels_touch_ground:
            game_state = GameState.BUTTON_HUNT
        else:
            if my_car_pos.abs_norm_angle > math.pi / 6:
                cmd = 'left' if my_car_pos.norm_angle > 0 else 'right'
    elif game_state == GameState.BUTTON_HUNT:
        if rear_wheel_touch or front_wheel_touch or front_wheel_touch_car or rear_wheel_touch_car:
            cmd = 'right' if my_car_pos.is_left() else 'left'
            if change_places:
                cmd = 'left' if my_car_pos.is_left() else 'right'
            # if min_button_dist / speed < 10:
            #     cmd = 'stop'
        close_end_cmd = game.map.close_to_end_cmd(my_car_pos)
        if close_end_cmd is not None:
            cmd = close_end_cmd
        if any_wheels_touch_ground:
            if is_buggy() or is_sq_buggy():
                if game.map.external_id == PillHillMap.external_id or \
                                game.map.external_id == PillHubbleMap.external_id:
                    if my_car_pos.abs_norm_angle > math.pi / 3:
                        cmd = 'left' if my_car_pos.norm_angle > 0 else 'right'
                elif game.map.external_id == IslandMap.external_id:
                    if my_car_pos.abs_norm_angle > math.pi / 5:
                        cmd = 'left' if my_car_pos.norm_angle > 0 else 'right'
                else:
                    if car_angular_speed > .01:
                        game_state = GameState.BUTTON_ROTATION_COUNTER
                    elif car_angular_speed < -.01:
                        game_state = GameState.BUTTON_ROTATION_CLOCK
                    cmd = 'right' if my_car_pos.is_left() else 'left'
            else:
                if my_car_pos.abs_norm_angle > math.pi / 6:
                    cmd = 'left' if my_car_pos.norm_angle > 0 else 'right'
        else:
            cmd = 'stop'
        # tune defence
        if ready_for_defence:
            cmd = 'left' if my_car_pos.is_left() else 'right'
    elif game_state == GameState.BUTTON_ROTATION_COUNTER:
        if car_angular_speed < 0:
            game_state = GameState.BUTTON_HUNT
        if car_speed.length() < 1:
            cmd = 'left' if my_car_pos.is_left() else 'right'
    elif game_state == GameState.BUTTON_ROTATION_CLOCK:
        if car_angular_speed > 0:
            game_state = GameState.BUTTON_HUNT
        if car_speed.length() < 1:
            cmd = 'left' if my_car_pos.is_left() else 'right'
    elif game_state == GameState.DEAD_LINE:
        if game.car.button_min_y(enemy_car_pos) >= game.car.button_min_y(my_car_pos):
            game_state = GameState.DEAD_LINE_ESCAPE
        else:
            game_state = GameState.BUTTON_HUNT
            if not update:
                strategy_default(True)
    elif game_state == GameState.DEAD_LINE_ESCAPE:
        if is_bus() and my_car_pos.abs_norm_angle > math.pi / 6:
            bus_strategy_to_stay()
        else:
            game_state = GameState.BUTTON_HUNT
            if not update:
                strategy_default(True)


def strategy_pill_map():
    global dead_line, last_cmd, game_state, game, my_car_pos, enemy_car_pos, cmd
    global front_wheel_touch, rear_wheel_touch, strategy_map_default
    global front_wheel_touch_car, rear_wheel_touch_car, car_body_touch_car, strategy_id

    if is_bus():
        bus_strategy_to_stay(.0012, -.0009, math.pi / 4, 1.23)
    else:
        if not strategy_map_default:
            if rear_wheel_touch or car_speed.length() > 7:
                game_state = GameState.BUTTON_HUNT_NON_DEFAULT
                cmd = 'right' if my_car_pos.is_left() else 'left'
                if car_body_touch_car:
                    strategy_map_default = True
                    game_state = GameState.BUTTON_HUNT
            elif game_state == GameState.BUTTON_HUNT_NON_DEFAULT:
                strategy_map_default = True
                game_state = GameState.BUTTON_HUNT
        else:
            strategy_default()

left_right = (1.24, 1.27)
def strategy_pill_hill_map():
    global dead_line, last_cmd, game_state, game, my_car_pos, enemy_car_pos, cmd
    global front_wheel_touch, rear_wheel_touch
    global front_wheel_touch_car, rear_wheel_touch_car, strategy_id
    global strategy_map_default, bus_strategy_to_stay_first_cmd, strategy_island_map_standing
    global left_right

    if not strategy_map_default and game.car.external_id == Bus.external_id:
        if game_state == GameState.FIRST_GROUND:
            strategy_default()
        elif game_state == GameState.BUTTON_HUNT:
            cmd = 'left' if my_car_pos.is_left() else 'right'
            left_right = (1.24, 1.27)
            if not (front_wheel_touch or rear_wheel_touch):
                game_state = GameState.TOUCH_GROUND
        elif game_state == GameState.TOUCH_GROUND:
            if car_body_touch_car:
                left_right = (1.4, 1.4)
            cmd = 'left' if my_car_pos.is_left() else 'right'
            angle_1 = (left_right[0] if my_car_pos.is_left() else left_right[1]) * math.pi
            if my_car_pos.abs_angle > angle_1:
                cmd = 'right' if my_car_pos.is_left() else 'left'
                angle = (1.65 if my_car_pos.is_left() else 1.65)*math.pi
                if my_car_pos.abs_angle > angle:
                    game_state = GameState.FIRST_GROUND
                    strategy_id = IslandMap.external_id
                    strategy_island_map_standing = \
                        (.9 if my_car_pos.is_left() else .9)
    else:
        strategy_default()


def strategy_pill_carcass_map():
    global dead_line, last_cmd, game_state, game, my_car_pos, enemy_car_pos, cmd
    global front_wheel_touch, rear_wheel_touch, strategy_map_default, strategy_id
    global bus_strategy_to_stay_first_cmd, car_body_touch_car, strategy_island_map_standing

    # think about escape
    if not strategy_map_default:
        if game_state == GameState.FIRST_GROUND:
            if is_bus() or is_sq_buggy():
                strategy_default()
            else:
                if car_speed.length() > 5 and my_car_pos.abs_angle < math.pi / 4:
                    cmd = 'right' if my_car_pos.is_left() else 'left'
                if rear_wheel_touch:
                    game_state = GameState.BUGGY_SPEED
        if game_state == GameState.BUGGY_SPEED:
            cmd = 'right' if my_car_pos.is_left() else 'left'
            if abs(car_speed.x) > 5:
                game_state = GameState.BUTTON_HUNT
        elif game_state == GameState.BUTTON_HUNT:
            if is_buggy() and car_speed.length() > 12:
                cmd = 'stop'
            if is_bus() and car_speed.length() > 8:
                cmd = 'stop'
            else:
                cmd = 'left' if my_car_pos.is_left() else 'right'
            if is_bus():
                if 1.15*math.pi < my_car_pos.abs_angle < 2*math.pi:
                    cmd = 'right' if my_car_pos.is_left() else 'left'
                #  tune it
                if my_car_pos.abs_angle > 1.4*math.pi:
                    game_state = GameState.TOUCH_GROUND
            else:
                angle = math.pi*1.1 if is_buggy() else .9*math.pi
                if my_car_pos.abs_angle > angle:
                    game_state = GameState.STOP
        elif game_state == GameState.TOUCH_GROUND:
            if is_bus():
                if 0.9*math.pi < my_car_pos.abs_norm_angle:
                    cmd = 'left'
                else:
                    game_state = GameState.FIRST_GROUND
                    strategy_island_map_standing = 1.8
                    strategy_id = IslandMap.external_id
            else:
                game_state = GameState.STOP
        elif game_state == GameState.STOP:
            cmd = 'stop'
            if car_body_touch_car:
                strategy_map_default = True
                game_state = GameState.BUTTON_HUNT
    else:
        strategy_default()


def strategy_pill_hubble_map():
    global dead_line, last_cmd, game_state, game, my_car_pos, enemy_car_pos, cmd
    global front_wheel_touch, rear_wheel_touch, strategy_map_default
    global front_wheel_touch_car, rear_wheel_touch_car, car_body_touch_car
    global bus_strategy_to_stay_first_cmd, strategy_id

    if not strategy_map_default:
        if game.car.external_id == Bus.external_id:
            if game_state == GameState.FIRST_GROUND:
                strategy_default()
            elif game_state == GameState.BUTTON_HUNT:
                cmd = 'left' if my_car_pos.is_left() else 'right'
                if is_bus() and car_speed.length() > 10:
                    cmd = 'stop'
                if not (front_wheel_touch or rear_wheel_touch):
                    game_state = GameState.TOUCH_GROUND
            elif game_state == GameState.TOUCH_GROUND:
                #  tune it
                cmd = 'left' if my_car_pos.is_left() else 'right'
                if my_car_pos.abs_angle > 1.4 * math.pi:
                    cmd = 'right' if my_car_pos.is_left() else 'left'
                    if my_car_pos.abs_angle > math.pi:
                        game_state = GameState.FIRST_GROUND
                        strategy_id = IslandMap.external_id
        elif is_buggy() and rear_wheel_touch:
            cmd = 'right' if my_car_pos.is_left() else 'left'
            if enemy_car_pos.abs_angle > math.pi / 4:
                strategy_map_default = True
                game_state = GameState.BUTTON_HUNT
        else:
            strategy_default()
    else:
        strategy_default()


def strategy_island_map():
    global dead_line, last_cmd, game_state, game, my_car_pos, enemy_car_pos, cmd
    global front_wheel_touch, rear_wheel_touch, strategy_map_default

    if not strategy_map_default and game.car.external_id == Bus.external_id:
        bus_strategy_to_stay(.0012, -.0009, math.pi / 4, 1.35)
    else:
        strategy_default()


def strategy_island_hole_map():
    global last_cmd, my_car_pos, cmd, game_state
    global rear_wheel_touch, strategy_map_default

    if not strategy_map_default and game.car.external_id == Bus.external_id:
        bus_strategy_to_stay(.0017, -.0009, math.pi / 3, 1.15)
    elif not strategy_map_default:
        if my_car_pos.abs_norm_angle < math.pi / 4:
            cmd = 'right' if my_car_pos.is_left() else 'left'
        if car_body_touch_car:
            game_state = GameState.BUTTON_HUNT
            strategy_map_default = True
    else:
        strategy_default()


def bus_strategy_to_stay(right=.0017, left=-.0014, angle=math.pi / 3.5, standing=1.1):
    global my_car_pos, cmd, game_state
    global strategy_map_default, bus_strategy_to_stay_first_cmd
    global front_wheel_touch, rear_wheel_touch

    first_cmd = bus_strategy_to_stay_first_cmd
    if first_cmd is None:
        first_cmd = 'right' if my_car_pos.is_left() else 'left'

    delta = .05
    if game_state == GameState.FIRST_GROUND:
        cmd = first_cmd
        if my_car_pos.abs_norm_angle > angle:
            game_state = GameState.BUS_INCLINE_RIGHT
        if not standing - delta < my_car_pos.abs_norm_angle < standing + delta:
            game_state = GameState.BUS_INCLINE
    elif game_state == GameState.BUS_INCLINE_LEFT:
        cmd = 'right'
        if car_angular_speed > right:
            game_state = GameState.BUS_INCLINE_RIGHT
        if my_car_pos.abs_norm_angle > standing + delta:
            game_state = GameState.BUS_INCLINE
    elif game_state == GameState.BUS_INCLINE_RIGHT:
        cmd = 'left'
        if car_angular_speed < left:
            game_state = GameState.BUS_INCLINE_LEFT
        if my_car_pos.abs_norm_angle < standing - delta:
            game_state = GameState.BUS_INCLINE
    elif game_state == GameState.BUS_INCLINE:
        if standing - delta < my_car_pos.abs_norm_angle < standing + delta:
            if car_angular_speed > 0:
                game_state = GameState.BUS_INCLINE_RIGHT
            else:
                game_state = GameState.BUS_INCLINE_LEFT
        elif my_car_pos.abs_norm_angle < standing - delta:
            cmd = 'right' if my_car_pos.is_left() else 'left'
        elif my_car_pos.abs_norm_angle > standing + delta:
            cmd = 'left' if my_car_pos.is_left() else 'right'
    if car_body_touch_car and (front_wheel_touch or rear_wheel_touch):
        strategy_map_default = True
        game_state = GameState.BUTTON_HUNT


def is_buggy():
    global game
    return game.car.external_id == Buggy.external_id


def is_bus():
    global game
    return game.car.external_id == Bus.external_id


def is_sq_buggy():
    global game
    return game.car.external_id == SquareWheelsBuggy.external_id


def log_debug(data):
    if debug:
        debug_message.update(data)


while True:
    z = json.loads(input())
    params = z['params']
    if z['type'] == 'new_match':
        game = Game(params['my_lives'], params['enemy_lives'], params['proto_car']['external_id'],
                    params['proto_map']['external_id'])
        dead_line = 0
        game_state = GameState.FIRST_GROUND
        strategy_map_default = False
        car_speed = Vec2d(0, 0)
        car_angular_speed = 0
        enemy_car_speed = Vec2d(0, 0)
        strategy_island_map_standing = 1.1
        bus_strategy_to_stay_first_cmd = None

        last_cmd = 'stop'
        strategy_id = game.map.external_id
        continue

    old_my_car_pos = my_car_pos
    old_enemy_car_pos = enemy_car_pos
    my_car_pos = CarPosition(params['my_car'], game.car.external_id)
    enemy_car_pos = CarPosition(params['enemy_car'], game.car.external_id)
    current_dead_line = int(params['deadline_position'])
    if old_my_car_pos is not None:
        car_speed = my_car_pos.point - old_my_car_pos.point
        car_angular_speed = my_car_pos.angle - old_my_car_pos.angle
        enemy_car_speed = enemy_car_pos.point - old_enemy_car_pos.point

    if current_dead_line > dead_line:
        if my_car_pos.dead_line_distance(current_dead_line) < 50 and strategy_map_default:
            if (game.map.external_id == PillCarcassMap.external_id or game.map.external_id == PillMap.external_id) \
                    and game_state != GameState.DEAD_LINE_ESCAPE:
                game_state = GameState.DEAD_LINE
        dead_line = current_dead_line

    cmd = 'stop'
    front_wheel_touch, rear_wheel_touch = my_car_pos.is_touch_ground_wheels(game.car, game.map)
    rear_wheel_touch_car, front_wheel_touch_car = my_car_pos.is_wheels_touch_car(game, enemy_car_pos)
    car_body_touch_car = my_car_pos.is_touch_car(game, enemy_car_pos)
    enemy_rear_wheel_touch_car, enemy_wheel_touch_car = enemy_car_pos.is_wheels_touch_car(game, my_car_pos)
    car_touch_ground = my_car_pos.is_touch_car(game, enemy_car_pos)

    ready_for_defence = my_car_pos.any_wheels_touch_button(game, enemy_car_pos)
    ready_for_attack = enemy_car_pos.any_wheels_touch_button(game, my_car_pos)

    if strategy_id == PillMap.external_id:
        strategy_pill_map()
    elif strategy_id == PillHillMap.external_id:
        strategy_pill_hill_map()
    elif strategy_id == PillCarcassMap.external_id:
        strategy_pill_carcass_map()
    elif strategy_id == PillHubbleMap.external_id:
        strategy_pill_hubble_map()
    elif strategy_id == IslandHoleMap.external_id:
        strategy_island_hole_map()
    else:
        strategy_island_map()

    log_debug({"a": round(my_car_pos.angle, 2)})
    log_debug({"na": round(my_car_pos.norm_angle, 2)})
    log_debug({"gs": game_state})
    log_debug({"cmd": cmd})
    log_debug({"sp": round(car_speed.length(), 2)})
    log_debug({"fwtc": front_wheel_touch_car})
    log_debug({"rwtc": rear_wheel_touch_car})
    log_debug({"ctc": car_body_touch_car})
    log_debug({"fwtg": front_wheel_touch})
    log_debug({"rwtg": rear_wheel_touch})
    log_debug({"cas": round(car_angular_speed, 3)})
    if debug:
        print(json.dumps({"command": cmd, "debug": str(debug_message)}))
    else:
        print(json.dumps({"command": cmd}))
