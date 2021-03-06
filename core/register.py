import bpy

from .fill import register_fill, unregister_fill
from .rails import register_rail, unregister_rail

from .door import register_door, unregister_door
from .floor import register_floor, unregister_floor
from .window import register_window, unregister_window
from .floorplan import register_floorplan, unregister_floorplan
from .balcony import register_balcony, unregister_balcony
from .stairs import register_stairs, unregister_stairs
from .roof import register_roof, unregister_roof
from .generic import register_generic, unregister_generic

# -- take care here --
# -- ORDER MATTERS --

register_funcs = (
    register_generic,
    register_fill,
    register_rail,
    register_door,
    register_floor,
    register_window,
    register_floorplan,
    register_balcony,
    register_stairs,
    register_roof,
)

unregister_funcs = (
    unregister_generic,
    unregister_fill,
    unregister_rail,
    unregister_door,
    unregister_floor,
    unregister_window,
    unregister_floorplan,
    unregister_balcony,
    unregister_stairs,
    unregister_roof,
)


def register_core():
    for func in register_funcs:
        func()


def unregister_core():
    for func in unregister_funcs:
        func()
