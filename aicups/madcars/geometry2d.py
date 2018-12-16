import math


def sign(x):
    return 1 - (x <= 0)


class Vec2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_tuple(p):
        return Vec2d(p[0], p[1])

    @staticmethod
    def from_point(p):
        return Vec2d(p.x, p.y)

    def __sub__(self, other):
        return Vec2d(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2d(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y

    def __str__(self) -> str:
        return "({0},{1})".format(self.x, self.y)

    def distance(self, pt):
        return math.sqrt(self.sqrt_dist(pt))

    def sqrt_dist(self, pt):
        return (self.x - pt.x)**2 + (self.y - pt.y)**2

    def length(self):
        return math.sqrt(self.dot(self))

    def cross(self, another):
        return

    def dot(self, another):
        return self.x*another.x + self.y*another.y

    def atan(self):
        return math.atan(self.y/self.x) if self.x != 0 else self.y

    def normalize(self):
        length = self.length()
        if length < .0001:
            return Vec2d(0, 0)
        return Vec2d(self.x / length, self.y / length)

    def angle(self, another):
        return math.acos(another.normalize().dot(self.normalize()))

    def scalar(self, scalar):
        return Vec2d(scalar * self.x, scalar * self.y)

    # Returns right hand perpendicular vector
    @staticmethod
    def normal(vect):
        return Vec2d(-vect.y, vect.x)


class Line2d:
    def __init__(self, xs, ys, xe, ye):
        self.st = Vec2d(xs, ys)
        self.ed = Vec2d(xe, ye)

    @staticmethod
    def points_array(s, e):
        return Line2d(s[0], s[1], e[0], e[1])

    @staticmethod
    def vec2ds(s, e):
        return Line2d(s.x, s.y, e.x, e.y)

    @staticmethod
    def points_2d(s, e):
        return Line2d(s.x, s.y, e.x, e.y)

    @property
    def x(self):
        return self.st.x - self.ed.x

    @property
    def y(self):
        return self.st.y - self.ed.y

    @staticmethod
    def area(a, b, c):
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    @staticmethod
    def intersect_bb(a, b, c, d):
        if a > b:
            temp = b
            b = a
            a = temp
        if c > d:
            temp = c
            c = d
            d = temp
        return max(a, c) <= min(b, d)

    def move_to_point(self, pt):
        return Line2d.points_2d(self.st + pt, self.ed + pt)

    # http://e-maxx.ru/algo/segments_intersection_checking
    def intersect(self, vect):
        a = self.st
        b = self.ed
        c = vect.st
        d = vect.ed
        return Line2d.intersect_bb(a.x, b.x, c.x, d.x) and Line2d.intersect_bb(a.y, b.y, c.y, d.y) \
               and Line2d.area(a, b, c) * Line2d.area(a, b, d) <= 0 \
               and Line2d.area(c, d, a) * Line2d.area(c, d, b) <= 0

    # http://www.gamedev.ru/code/forum/?id=40808
    def intersect_circle(self, arc):
        x, y, r = arc.center.x, arc.center.y, arc.radius
        rr = r * r
        x01, y01 = self.st.x, self.st.y
        x02, y02 = self.ed.x, self.ed.y

        sqrtd1 = (x01 - x) * (x01 - x) + (y01 - y) * (y01 - y)
        sqrtd2 = (x02 - x) * (x02 - x) + (y02 - y) * (y02 - y)
        if sqrtd1 <= rr <= sqrtd2 or sqrtd2 <= rr <= sqrtd1:
            return True

        if x01 == x02:
            return (y01 < y < y02 or y01 > y > y02) and abs(x01 - x) <= r

        if y01 == y02:
            return (x01 < x < x02 or x01 > x > x02) and abs(y01 - y) <= r

        a = (y01 - y02) / (x01 - x02)
        b = y01 - a * x01
        xp = (y - b + x / a) / (a + 1 / a)
        yp = a * xp + b

        if x01 < xp < x02 or x02 < xp and x01 > x:
            if (xp-x) * (xp-x)+(yp-y) * (yp-y) <= rr:
                return True

        return False

    def __str__(self) -> str:
        return "{0}, {1}".format(self.st, self.ed)


class AABB:
    def __init__(self, lx, ly, w, h):
        self.lx = lx
        self.ly = ly
        self.w = w
        self.h = h

        self.l = lx
        self.b = ly
        self.t = ly + h
        self.r = lx + w

    @staticmethod
    def from_wheel(wheel, radius):
        return AABB(wheel.x - radius, wheel.y - radius, 2*radius, 2*radius)

    def edges(self):
        return [Line2d(self.lx, self.ly, self.lx + self.w, self.ly),
                Line2d(self.lx + self.w, self.ly, self.lx + self.w, self.ly + self.h),
                Line2d(self.lx + self.w, self.ly + self.h, self.lx, self.ly + self.h),
                Line2d(self.lx, self.ly + self.h, self.lx, self.ly)]

    def intersect_line(self, line):
        for edge in self.edges():
            if edge.intersect(line):
                return True
        return False

    def intersect(self, box):
        t = self.lx - box.lx
        if t > box.w or -t > self.w:
            return False
        t = self.ly - box.ly
        if t > box.d[1] or -t > self.h:
            return False
        return True

    def compute_vertices(self):
        xy = Vec2d(self.lx, self.ly)
        w = Vec2d(self.w, 0)
        h = Vec2d(0, self.h)
        return [xy, xy + h, xy + h + w, xy + w]

    def __str__(self) -> str:
        return "{0}, {1}, {2}, {3}".format(self.lx, self.ly, self.w, self.h)


class OBB(AABB):
    def __init__(self, x, y, w, h, angle):
        super().__init__(x, y, w, h)
        self.angle = angle
        if abs(self.angle) < .0001:
            self.angle = 0

    @staticmethod
    def from_car(position, car):
        wheels = max(car.rear_wheel_radius, car.front_wheel_radius) + 5
        w, h = car.car_bb_wh[0], car.car_bb_wh[1] + wheels
        angle = position.angle
        sin = math.sin(angle + math.pi/2)
        cos = math.cos(angle + math.pi/2)
        pt = position.point - Vec2d(cos*wheels, sin*wheels)
        # angle += math.pi
        if not position.is_left():
            sin = math.sin(angle)
            cos = math.cos(angle)
            pt -= Vec2d(w * cos, w * sin)
        return OBB(pt.x, pt.y, w, h, position.angle)

    def edges(self):
        vertices = self.compute_vertices()
        return [Line2d.points_2d(vertices[0], vertices[1]),
                Line2d.points_2d(vertices[1], vertices[2]),
                Line2d.points_2d(vertices[2], vertices[3]),
                Line2d.points_2d(vertices[3], vertices[0])]

    @staticmethod
    def from_wheel(wheel, radius):
        return OBB(wheel.x - radius, wheel.y - radius, 2*radius, 2*radius, 0)

    def compute_vertices(self):
        xy = Vec2d(self.lx, self.ly)

        wsin = math.sin(self.angle)
        wcos = math.cos(self.angle)
        hsin = math.sin(self.angle + math.pi/2)
        hcos = math.cos(self.angle + math.pi/2)

        w = Vec2d(wcos * self.w, wsin * self.w)
        h = Vec2d(hcos * self.h, hsin * self.h)
        return [xy, xy + h, xy + h + w, xy + w]

    # OBB collision check and resolution using SAT (SFML, 2D)
    def intersect(self, another):
        vertices1 = self.compute_vertices()
        vertices2 = another.compute_vertices()

        # x,y axis
        axes = [Vec2d(0, 1), Vec2d(1, 0)]

        for axis in axes:
            proj1 = OBB.project_on_axis(vertices1, axis)
            proj2 = OBB.project_on_axis(vertices2, axis)

            overlap = OBB.overlap_length(proj1, proj2)
            # shapes are not overlapping
            if overlap == 0:
                return False
        return True

    @staticmethod
    def project_on_axis(vertices, axis):
        min = math.inf
        max = -math.inf
        for vertex in vertices:
            projection = vertex.dot(axis)
            if projection < min:
                min = projection
            if projection > max:
                max = projection

        return Vec2d(min, max)

    @staticmethod
    def get_perpendicular_axis(a, b):
        return Vec2d.normal((a - b).normalize())

    @staticmethod
    def overlap_length(a, b):
        if not (a.x <= b.y and a.y >= b.x):
            return 0

        return min(a.y, b.y) - max(a.x, b.x)



