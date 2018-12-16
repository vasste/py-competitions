from geometry2d import *
from base_car import Car


class Buggy(Car):
    external_id = 1

    car_body_poly = [
        Vec2d(0, 6),
        Vec2d(0, 25),
        Vec2d(33, 42),
        Vec2d(85, 42),
        Vec2d(150, 20),
        Vec2d(150, 0),
        Vec2d(20, 0)
    ]

    car_bb_wh = (150, 42)

    car_body_mass = 200

    button_position = Vec2d(1, 42)
    button_hw = (30, 122)

    max_speed = 70
    torque = 14000000

    drive = Car.FR

    rear_wheel_mass = 50
    rear_wheel_position = Vec2d(29, -5)
    rear_wheel_damp_position = Vec2d(29, 20)
    rear_wheel_damp_stiffness = 5e4
    rear_wheel_damp_damping = 3e3
    rear_wheel_damp_length = 25
    rear_wheel_radius = 12

    front_wheel_mass = 5
    front_wheel_position = Vec2d(122, -5)
    front_wheel_damp_position = Vec2d(122, 20)
    front_wheel_damp_length = 25
    front_wheel_radius = 12


class Bus(Car):
    external_id = 2

    car_body_poly = [
        Vec2d(0, 6),
        Vec2d(8, 62),
        Vec2d(136, 62),
        Vec2d(153, 32),
        Vec2d(153, 5),
        Vec2d(110, 0),
        Vec2d(23, 0)
    ]

    car_bb_wh = (153, 62)

    car_body_mass = 700

    button_position = Vec2d(137, 59)
    button_angle = -math.atan(3/1.7)
    button_hw = (45, 48)
    standing_button_hw = (100, 48)

    max_speed = 45
    torque = 35000000

    drive = Car.AWD

    rear_wheel_radius = 14
    rear_wheel_position = Vec2d(38, -5)
    rear_wheel_friction = 0.9
    rear_wheel_damp_position = Vec2d(38, 30)
    rear_wheel_damp_length = 35
    rear_wheel_damp_stiffness = 10e4
    rear_wheel_damp_damping = 6e3

    front_wheel_radius = 14
    front_wheel_position = Vec2d(125, -5)
    front_wheel_damp_position = Vec2d(125, 30)
    front_wheel_damp_length = 35
    front_wheel_damp_stiffness = 10e4
    front_wheel_damp_damping = 6e3


class SquareWheelsBuggy(Buggy):
    external_id = 3

    max_speed = 50

    drive = Buggy.AWD

    car_body_mass = 230
    rear_wheel_mass = 10
    rear_wheel_damp_stiffness = 10e4
    rear_wheel_damp_damping = .9e3

    front_wheel_radius = 17
    rear_wheel_radius = 17

    front_wheel_mass = 10