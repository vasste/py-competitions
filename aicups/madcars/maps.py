from geometry2d import *


class MapArc:
    def __init__(self, center, radius, start_angel, end_angle, segments):
        self.center = Vec2d.from_tuple(center)
        self.radius = radius
        self.start_angel = start_angel
        self.end_angle = end_angle
        self.segments = segments
        self.segment_edges = []
        segment_angle = abs(self.end_angle - self.start_angel) / self.segments
        if self.end_angle < self.start_angel:
            segment_angle *= -1
        i_segment_angle = start_angel
        for i in range(1, segments + 1):
            x = radius * math.cos(i_segment_angle) + self.center.x
            y = radius * math.sin(i_segment_angle) + self.center.y
            x2 = radius * math.cos(i_segment_angle + segment_angle) + self.center.x
            y2 = radius * math.sin(i_segment_angle + segment_angle) + self.center.y
            self.segment_edges.append(Line2d(x, y, x2, y2))
            i_segment_angle += segment_angle


class Map(object):
    external_id = 0

    base_arcs = []
    base_segments = []

    additional_arcs = []
    additional_segments = []

    segment_friction = 1
    segment_elasticity = 0
    segment_height = 10

    cars_start_position = []

    max_width = 1200
    max_height = 800

    def close_to_end_cmd(self, car_position):
        return None


class PillMap(Map):
    external_id = 1

    base_arcs = [MapArc((300, 400), 300 - Map.segment_height, math.pi/2, math.pi * 3/2, 30),
                 MapArc((900, 400), 300 - Map.segment_height, math.pi/2, -math.pi / 2,  30)]

    base_segments = [Line2d.points_array((300, 100 + Map.segment_height), (900, 100 + Map.segment_height)),
                     Line2d.points_array((300, 700 - Map.segment_height), (900, 700 - Map.segment_height))]


class PillHubbleMap(PillMap):
    external_id = 2

    additional_arcs = [MapArc((600, -150), 300 + Map.segment_height, math.pi/3.2, math.pi/1.45, 40)]

    base_segments = [
        Line2d.points_array((300, 100 + Map.segment_height), (465, 100 + Map.segment_height)),
        Line2d.points_array((750, 100 + Map.segment_height), (900, 100 + Map.segment_height)),
        Line2d.points_array((300, 700 - Map.segment_height), (900, 700 - Map.segment_height))]


class PillHillMap(PillMap):
    external_id = 3

    additional_arcs = [
        MapArc((300, 300), 200 - Map.segment_height, -math.pi / 2, -math.pi / 6, 30),
        MapArc((900, 300), 200 - Map.segment_height, math.pi * 3 / 2, math.pi * 7 / 6, 30),
    ]

    additional_segments = [
        Line2d.points_array((465, 195 + Map.segment_height), (735, 195 + Map.segment_height))
    ]

    base_segments = [Line2d.points_array((300, 700 - Map.segment_height), (900, 700 - Map.segment_height))]


class PillCarcassMap(PillMap):
    external_id = 4

    additional_segments = [
        Line2d.points_array((300, 400 + Map.segment_height), (900, 400 + Map.segment_height))
    ]


class IslandMap(Map):
    external_id = 5

    base_segments = [
        Line2d.points_array((100, 100 + Map.segment_height), (1100, 100 + Map.segment_height)),
    ]

    def close_to_end_cmd(self, car_position):
        car_front_wheel = car_position.front_wheel
        car_rear_wheel  = car_position.rear_wheel
        car_position_left = car_position.is_left()
        if car_position_left:
            if self.base_segments[0].ed.distance(car_front_wheel) < 100:
                return 'left'
            if self.base_segments[0].st.distance(car_rear_wheel) < 100:
                return 'right'
        else:
            if self.base_segments[0].st.distance(car_front_wheel) < 100:
                return 'right'
            if self.base_segments[0].ed.distance(car_rear_wheel) < 100:
                return 'left'


class IslandHoleMap(Map):
    external_id = 6

    base_segments = [
        Line2d.points_array((10, 400), (50, 200)),

        Line2d.points_array((50, 200 + Map.segment_height), (300, 200 + Map.segment_height)),
        Line2d.points_array((380, 150 + Map.segment_height), (820, 150 + Map.segment_height)),
        Line2d.points_array((900, 200 + Map.segment_height), (1150, 200 + Map.segment_height)),

        Line2d.points_array((1150, 200), (1190, 400))
    ]

    base_arcs = [
        MapArc((300, 100), 100 + Map.segment_height, math.pi / 6, math.pi / 2, 30),
        MapArc((900, 100), 100 + Map.segment_height, math.pi / 2, math.pi * 5 / 6, 30),
    ]