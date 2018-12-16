from geometry2d import *


class Car(object):
    RIGHT_DIRECTION = 0
    LEFT_DIRECTION = 1

    external_id = 0

    FF = 1
    FR = 2
    AWD = 3

    car_body_poly = []
    car_body_mass = 100
    car_body_friction = 0.9
    car_body_elasticity = 0.5

    button_hw = (3, 30)
    standing_button_hw = button_hw
    button_position = Vec2d(0, 0)
    button_angle = 0
    button_poly = []
    standing_button_poly = []

    max_speed = 300
    max_angular_speed = 2
    torque = 20000000
    drive = FR

    rear_wheel_mass = 60
    rear_wheel_radius = 10
    rear_wheel_position = Vec2d(0, 0)
    rear_wheel_friction = 1
    rear_wheel_elasticity = 0.8
    rear_wheel_joint = (0, 0)
    rear_wheel_groove_offset = 5
    rear_wheel_damp_position = Vec2d(0, 0)
    rear_wheel_damp_length = 20
    rear_wheel_damp_stiffness = 6e4
    rear_wheel_damp_damping = 1e3

    front_wheel_mass = 60
    front_wheel_radius = 10
    front_wheel_position = Vec2d(0, 0)
    front_wheel_friction = 1
    front_wheel_elasticity = 0.8
    front_wheel_joint = (0, 0)
    front_wheel_groove_offset = 5
    front_wheel_damp_position = Vec2d(0, 0)
    front_wheel_damp_length = 20
    front_wheel_damp_stiffness = 6e4
    front_wheel_damp_damping = 0.9e3

    def __init__(self):
        self.button_poly = []
        self.create_button_poly(self.button_hw[0], self.button_hw[1], self.button_poly)
        self.standing_button_poly = []
        self.create_button_poly(self.standing_button_hw[0], self.standing_button_hw[1], self.standing_button_poly)

    def create_button_poly(self, h, w, button_poly):
        button_poly.append(self.button_position)
        if self.button_angle != 0:
            sw = math.sin(self.button_angle) * w
            cw = math.cos(self.button_angle) * w
            button_poly.append(button_poly[-1] + Vec2d(h, 0))
            button_poly.append(button_poly[-1] + Vec2d(cw, sw))
            button_poly.append(button_poly[-1] - Vec2d(h, 0))
        else:
            button_poly.append(button_poly[-1] + Vec2d(0, h))
            button_poly.append(button_poly[-1] + Vec2d(w, 0))
            button_poly.append(button_poly[-1] - Vec2d(0, h))

    def button_min_y(self, car_position):
        car_angle = car_position.abs_norm_angle
        if not car_position.clockwise():
            car_angle += math.pi

        car_point = car_position.point
        if car_angle == 0:
            return min([pt.y + car_point.y for pt in self.button_poly])
        else:
            return min([pt.length() * math.sin(car_angle) + car_point.y for pt in self.button_poly])

    def car_poly(self, car_position):
        return Car.real_poly(car_position, self.car_body_poly)

    def car_ages(self, car_position):
        car_body_edges = []
        car_pole = self.car_poly(car_position)
        for i, p in enumerate(car_pole):
            ni = 0 if i + 1 == len(car_pole) else i + 1
            car_body_edges.append(Line2d.points_2d(car_pole[i], car_pole[ni]))
        return car_body_edges

    def car_pt_button_lines(self, car_position):
        return [Line2d.vec2ds(car_position.point, pt) for pt in Car.real_poly(car_position, self.button_poly)]

    def car_button_aabb(self, car_position):
        obb = self.car_button_obb(car_position)
        return AABB(obb.lx, obb.ly, obb.w, obb.h)

    def car_standing_button_obb(self, car_position):
        return Car.button_obb(car_position, self.button_poly, self.button_angle, self.standing_button_hw)

    def car_button_obb(self, car_position):
        return Car.button_obb(car_position, self.button_poly, self.button_angle, self.button_hw)

    @staticmethod
    def button_obb(car_position, button_poly, button_angle, button_hw):
        poly = [button_poly[0]]
        button_angle = button_angle
        if not car_position.is_left():
            poly[0] = button_poly[3]
            button_angle = -button_angle
        points = Car.real_poly(car_position, poly)
        return OBB(points[0].x, points[0].y, button_hw[1], button_hw[0], car_position.angle + button_angle)

    @staticmethod
    def real_poly(car_position, poly):
        car_angle = car_position.angle

        is_left = 1 if car_position.is_left() else -1
        car_point = car_position.point
        if car_angle == 0 or car_angle == math.pi:
            return [car_point + pt for pt in poly]
        else:
            return [car_point + Vec2d(is_left * pt.length() * math.cos(pt.atan() + is_left*car_angle),
                   pt.length() * math.sin(pt.atan() + is_left*car_angle)) for pt in poly]
