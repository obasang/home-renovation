"""Render the worked example. Python standard library only."""

from dataclasses import asdict, dataclass, replace
from html import escape
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class Box:
    x: int
    y: int
    w: int
    d: int

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.d // 2)


@dataclass(frozen=True)
class Scheme:
    version: str
    title: str
    table: Box
    seats: int
    island: Box | None
    floor: str = "#e8d7bf"
    cabinets: str = "#bc9673"

    @property
    def pendant(self):
        return self.table.center

    @property
    def east_clearance(self):
        return ROOM.w - (self.table.x + self.table.w + CHAIR_PULL)

    @property
    def geometry(self):
        return self.table, self.seats, self.island, self.pendant


ROOM = Box(0, 0, 6400, 4300)
COUNTER = Box(0, 250, 600, 3050)
DW_OPEN = Box(600, 1500, 600, 600)
ENTRY = Box(4750, 3650, 1300, 450)
SINK = (300, 1125)
DISHWASHER = (COUNTER.w // 2, DW_OPEN.center[1])
CHAIR_PULL = 500
ROOMS = [
    ("卧室一", Box(0, 4300, 3000, 2900)),
    ("卧室二", Box(3000, 4300, 3100, 2900)),
    ("卫生间", Box(6400, 0, 2200, 2500)),
    ("门厅", Box(6400, 2500, 2200, 1800)),
]
OPENINGS = [
    ((6400, 3000), (6400, 3800)),
    ((8600, 3250), (8600, 4150)),
    ((800, 4300), (1700, 4300)),
    ((4150, 4300), (5050, 4300)),
    ((6850, 2500), (7650, 2500)),
]
WINDOW = ((2850, 0), (5550, 0))
V1 = Scheme("V1", "带岛台 · 四人餐桌", Box(3500, 1200, 1200, 800), 4, Box(1650, 650, 700, 1600))
V1B = replace(V1, version="V1-B", title="无岛台对照 · 四人餐桌", island=None)
V2 = replace(V1B, version="V2", title="取消岛台 · 六人餐桌", table=Box(3100, 1350, 1800, 900), seats=6)
V3 = replace(V2, version="V3", title="六人餐桌 · 浅灰地砖与暖白柜门", floor="#cbd0d2", cabinets="#ede5d6")
SCHEMES = (V1, V1B, V2, V3)


def label(x, y, value, size=16, fill="#263534"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}">{escape(str(value))}</text>'


def polygon(points, fill, stroke="#566862"):
    positions = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polygon points="{positions}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'


def line(a, b, stroke, width=2):
    return f'<path d="M {a[0]},{a[1]} L {b[0]},{b[1]}" fill="none" stroke="{stroke}" stroke-width="{width}"/>'


def chairs(scheme):
    table = scheme.table
    along = [table.x + table.w // 2] if scheme.seats == 4 else [table.x + 450, table.x + 1350]
    for x in along:
        yield Box(x - 190, table.y - 430, 380, 340)
        yield Box(x - 190, table.y + table.d + 90, 380, 340)
    yield Box(table.x - 430, table.center[1] - 190, 340, 380)
    yield Box(table.x + table.w + 90, table.center[1] - 190, 340, 380)


def plan(scheme, left, top, handoff=False):
    scale = 0.044

    def point(x, y):
        return left + x * scale, top + y * scale

    def rect(box, fill, stroke="#65746b", dash=""):
        x, y = point(box.x, box.y)
        return (f'<rect x="{x}" y="{y}" width="{box.w * scale}" height="{box.d * scale}"'
                f' fill="{fill}" stroke="{stroke}" stroke-dasharray="{dash}"/>')

    def tag(x, y, value, size=12):
        return label(*point(x, y), value, size)

    items = [rect(ROOM, "#f5eee3")]
    for name, box in ROOMS:
        items.extend([rect(box, "#f2f3ef"), tag(box.x + 200, box.y + 500, name)])
    items.extend(line(point(*a), point(*b), "#f8faf6", 4) for a, b in OPENINGS)
    items.append(line(point(*WINDOW[0]), point(*WINDOW[1]), "#5898a1", 4))
    items.extend([rect(COUNTER, "#b99d82"), rect(ENTRY, "#a8bda7"), rect(scheme.table, "#bc9673")])
    items.extend(rect(chair, "#dfc1a5") for chair in chairs(scheme))
    items.append(rect(DW_OPEN, "none", "#b05333", "3 3"))
    if scheme.island:
        items.append(rect(scheme.island, "#c6a88a"))

    if handoff:
        for key, (x, y), dx, dy in [
            ("L1", scheme.pendant, 10, -8),
            ("W1", SINK, 8, -7),
            ("D1", DISHWASHER, 8, 12),
            ("C1", ENTRY.center, -18, -13),
        ]:
            px, py = point(x, y)
            items.extend([f'<circle cx="{px}" cy="{py}" r="4.5" fill="#b05333"/>',
                          label(px + dx, py + dy, key, 12, "#913d24")])
    else:
        items.extend([
            tag(4850, 3980, "保留柜"),
            tag(scheme.table.x + 100, scheme.table.y + 625, f"{scheme.seats} 人桌"),
            tag(2900, 350, "北窗"),
            tag(650, 2380, "洗碗机门", 10),
        ])
        east_edge = scheme.table.x + scheme.table.w + CHAIR_PULL
        y = scheme.table.center[1]
        items.append(line(point(east_edge, y), point(ROOM.w, y), "#478590", 1.4))
        for x in (east_edge, ROOM.w):
            items.append(line(point(x, y - 65), point(x, y + 65), "#478590", 1.4))
        if scheme.island:
            items.append(tag(1690, 850, "岛台"))
    return "".join(items)


def perspective(scheme):
    def point(x, y, z=0):
        return 645 + (x - y) * 0.037, 221 + (x + y) * 0.020 - z * 0.042

    def corner(box, z):
        return [point(box.x, box.y, z), point(box.x + box.w, box.y, z),
                point(box.x + box.w, box.y + box.d, z), point(box.x, box.y + box.d, z)]

    def cuboid(box, height, color):
        low, high = corner(box, 0), corner(box, height)
        return "".join([
            polygon([low[1], low[2], high[2], high[1]], color),
            polygon([low[2], low[3], high[3], high[2]], color),
            polygon(high, color),
        ])

    items = [polygon(corner(ROOM, 0), scheme.floor)]
    if scheme.floor == V3.floor:
        items.extend(line(point(x, 0), point(x, ROOM.d), "#aeb7bb", 0.7)
                     for x in range(600, ROOM.w, 600))
        items.extend(line(point(0, y), point(ROOM.w, y), "#aeb7bb", 0.7)
                     for y in range(600, ROOM.d, 600))
    items.append(polygon([point(0, 0), point(6400, 0), point(6400, 0, 1900), point(0, 0, 1900)],
                         "#f5f2e9"))
    west, east = WINDOW
    items.append(polygon([point(*west, 780), point(*east, 780), point(*east, 1690),
                          point(*west, 1690)], "#a5c5cd"))
    items.append(cuboid(COUNTER, 860, scheme.cabinets))
    items.append(polygon(corner(Box(110, 930, 385, 390), 865), "#849797"))
    if scheme.island:
        items.append(cuboid(scheme.island, 875, scheme.cabinets))
    furniture = [(x, 450, "#d1ac86") for x in chairs(scheme)]
    furniture.extend([(scheme.table, 730, "#bc9673"), (ENTRY, 1350, "#ad8c6a")])
    for box, height, color in sorted(furniture, key=lambda item: sum(item[0].center)):
        items.append(cuboid(box, height, color))
    x, y = scheme.pendant
    items.append(line(point(x, y, 2350), point(x, y, 1570), "#916741"))
    px, py = point(x, y, 1540)
    items.append(f'<ellipse cx="{px}" cy="{py}" rx="10" ry="4" fill="#e5bb83" stroke="#916741"/>')
    return "".join(items)


def render(scheme):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1390" height="570" viewBox="0 0 1390 570">',
           '<rect width="1390" height="570" fill="#f3f3ec"/>',
           '<g font-family="PingFang SC,Noto Sans CJK SC,sans-serif">',
           label(28, 42, f"{scheme.version}　{scheme.title}", 24),
           label(28, 67, "虚构两居室 · 客餐厨示例 · 尺寸单位 mm · 交底点位待现场复核", 14)]
    for left, title in [(18, "01　平面方案"), (477, "02　空间效果 · 固定视角"), (936, "03　交底示意 · 待复核")]:
        svg.extend([f'<rect x="{left}" y="88" width="436" height="460" rx="10" fill="#fcfcf8"/>',
                    label(left + 16, 115, title, 17)])
    svg.extend([plan(scheme, 43, 143), perspective(scheme), plan(scheme, 958, 143, handoff=True)])
    if scheme.island:
        aisle = scheme.island.x - COUNTER.w
        svg.append(label(43, 490, f"柜台至岛台 {aisle} · 洗碗机门展开后 {scheme.island.x - DW_OPEN.x - DW_OPEN.w}", 13))
    else:
        svg.append(label(43, 490, "移除岛台，西侧操作区释放", 13))
    svg.append(label(43, 515, f"东端椅拉出 500 后至东边界 {scheme.east_clearance}", 13))
    svg.append(label(495, 490, "浅灰哑光地砖 · 暖白厨房柜门" if scheme == V3 else "浅橡木地面 · 木色柜门", 13))
    svg.append(label(495, 515, "窗、玄关柜及机位沿用同一底图", 13))
    svg.append(label(958, 488, f"L1 灯位 ({scheme.pendant[0]}, {scheme.pendant[1]}) · 电工核对接线", 13))
    svg.append(label(958, 509, "W1 给排水 · D1 洗碗机 · C1 保留柜", 13))
    svg.append(label(958, 530, "柜体完成面、门扇及材料厚度现场复核", 13))
    svg.append("</g></svg>")
    return "\n".join(svg) + "\n"


def record(scheme):
    previous = {V1: None, V1B: "V1", V2: "V1", V3: "V2"}
    changes = {
        V1: ["带岛台，四人餐桌"],
        V1B: ["取消岛台作对照"],
        V2: ["取消岛台，换六人桌，吊灯移动至桌中心"],
        V3: ["客餐厨地面换浅灰哑光砖，厨房柜门换暖白"],
    }
    return {
        "units": "mm",
        "coordinates": "客餐厨西北角为原点，x 向东，y 向南。矩形家具用西北角定位，点位为中心坐标。",
        "base": "虚构量房数据 v1，见 input.md",
        "previous": previous[scheme],
        "layout_and_finishes": asdict(scheme),
        "approved_to_keep": {"entry_cabinet": asdict(ENTRY), "north_window": WINDOW, "sink": SINK},
        "view": "同一轴测视角",
        "handoff": {"L1": scheme.pendant, "W1": SINK, "D1": DISHWASHER, "C1": ENTRY.center},
        "site_checks": ["柜体完成面", "洗碗机实际门扇", "吊灯接线", "地面材料厚度"],
        "changes": changes[scheme],
    }


def main():
    output = Path(sys.argv[1] if len(sys.argv) > 1 else "output")
    output.mkdir(parents=True, exist_ok=True)
    for scheme in SCHEMES:
        stem = scheme.version.lower()
        (output / f"{stem}.svg").write_text(render(scheme), encoding="utf-8")
        (output / f"{stem}.json").write_text(
            json.dumps(record(scheme), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
