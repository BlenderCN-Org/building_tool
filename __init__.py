# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Cynthia",
    "author": "Ian Ichung'wa Karanja (ranjian0)",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Toolshelf > Cynthia",
    "description": "Building Generation Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"
}

import bpy 
from bpy.props import *

from .cynthia_floorplan import Floorplan
from .cynthia_floor import Floor 
from .cynthia_window import Window
from .cynthia_door import *
from .cynthia_balcony import *
from .cynthia_rails import *
from .cynthia_roof import *
from .cynthia_staircase import *
from .cynthia_stairs import *
from .cynthia_update import update_building
from .utils import ray_cast_modal, select_face_callback, hover_face_callback, facedata_from_index

# =======================================================
#
#           PROPERTY GROUPS
#
# =======================================================

class PropertyProxy(bpy.types.PropertyGroup):
    property_items = [
        ("FLOOPLAN", "Floorplan", "", 0),
        ("FLOOR", "Floor", "", 1),
        ("WINDOW", "Window", "", 2)
    ]
    type    = EnumProperty(items=property_items)

    name    = StringProperty(default="Property")
    id      = IntProperty()


class SplitProperty(bpy.types.PropertyGroup):
    amount  = FloatVectorProperty(
        name="Split Amount", description="How much to split geometry", min=.01, max=3.0, 
        subtype='XYZ', size=2, default=(2.0, 2.0),
        update=update_building)

    off     = FloatVectorProperty(
        name="Split Offset", description="How much to offset geometry", min=-1000.0, max=1000.0, 
        subtype='TRANSLATION', size=3, default=(0.0, 0.0, 0.0),
        update=update_building)


class FloorplanProperty(bpy.types.PropertyGroup):
    fp_types = [
        ("RECTANGULAR", "Rectangular", "", 0), 
        ("CIRCULAR", "Circular", "", 1),
        ("COMPOSITE", "Composite", "", 2), 
        ("H-SHAPED", "H-Shaped", "", 3)
    ]

    type    = EnumProperty(
        description="Type of floorplan", items=fp_types, default='RECTANGULAR', 
        update=update_building)

    width   = FloatProperty(
        name="Width", description="Base Width of floorplan", min=0.01, max=100.0, default=2, 
        update=update_building)

    length  = FloatProperty(
        name="Length", description="Base Length of floorplan", min=0.01, max=100.0, default=2,
        update=update_building)

    radius  = FloatProperty(
        name="Radius", description="Radius of circle", min=0.1, max=100.0, default=1.0,
        update=update_building)

    segs    = IntProperty(
        name="Segments", description="Number of segments in the circle", min=3, max=100, default=32,
        update=update_building)

    tw      = FloatProperty(
        name="Tail Width", description="Width of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    tl      = FloatProperty(
        name="Tail Length", description="Length of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    tw1     = FloatProperty(
        name="Tail Width 1", description="Width of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    tl1     = FloatProperty(
        name="Tail Length 1", description="Length of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    tw2     = FloatProperty(
        name="Tail Width 2", description="Width of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    tl2     = FloatProperty(
        name="Tail Length 2", description="Length of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    tw3     = FloatProperty(
        name="Tail Width 3", description="Width of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    tl3     = FloatProperty(
        name="Tail Length 3", description="Length of floorplan segment", min=0.0, max=100.0, default=1,
        update=update_building)

    cap_tris= BoolProperty(
        name='Cap Triangles', description='Set the fill type to triangles', default=False,
        update=update_building)

    def draw(self, context, layout):
        row = layout.row()
        row.prop(self, "type", text="")

        box = layout.box()
        if self.type == 'RECTANGULAR':
            col = box.column(align=True)
            col.prop(self, 'width')
            col.prop(self, 'length')

        elif self.type == 'CIRCULAR':
            col = box.column(align=True)
            col.prop(self, 'radius')
            col.prop(self, 'segs')

            row = box.row()
            row.prop(self, 'cap_tris', toggle=True)

        elif self.type == 'COMPOSITE':
            row = box.row(align=True)
            row.prop(self, 'width')
            row.prop(self, 'length')

            col = box.column(align=True)
            col.prop(self, 'tl')
            col.prop(self, 'tl1')
            col.prop(self, 'tl2')
            col.prop(self, 'tl3')

        elif self.type == 'H-SHAPED':
            row = box.row(align=True)
            row.prop(self, 'width')
            row.prop(self, 'length')

            row = box.row(align=True)

            col = row.column(align=True)
            col.prop(self, 'tw')
            col.prop(self, 'tw1')
            col.prop(self, 'tw2')
            col.prop(self, 'tw3')

            col = row.column(align=True)
            col.prop(self, 'tl')
            col.prop(self, 'tl1')
            col.prop(self, 'tl2')
            col.prop(self, 'tl3')


class FloorProperty(bpy.types.PropertyGroup):
    floor_count     = IntProperty(
        name="Floor Count", description="Number of floors", min=1, max=1000, default=1, 
        update=update_building)

    floor_height    = FloatProperty(
        name="Floor Height", description="Height of each floor", min=0.01, max=1000.0, default=1.0, 
        update=update_building)

    slab_thickness  = FloatProperty(
        name="Slab Height", description="Thickness of each slab", min=0.01, max=1000.0, default=0.15, 
        update=update_building)

    slab_outset     = FloatProperty(
        name="Slab Outset", description="Outset of each slab", min=0.01, max=1000.0, default=0.1, 
        update=update_building)

    mat_slab        = PointerProperty(type=bpy.types.Material,
        name="Slab Material", description="Material for slab faces", update=update_building) 
    mat_wall        = PointerProperty(type=bpy.types.Material,
        name="Wall Material", description="Material for wall faces", update=update_building)

    def draw(self, context, layout):
        box = layout.box()

        col = box.column(align=True)
        col.prop(self, "floor_count")
        col.prop(self, "floor_height")

        col = box.column(align=True)
        col.prop(self, "slab_thickness")
        col.prop(self, "slab_outset")

        col = box.column(align=True)
        col.prop(self, "mat_slab")
        col.prop(self, "mat_wall")


class WindowProperty(bpy.types.PropertyGroup):
    win_types   = [("BASIC", "Basic", "", 0), ("ARCHED", "Arched", "", 1)]
    type        = EnumProperty(
        description="Type of window", items=win_types, default='BASIC',
        update=update_building)

    fill_type   = [("BAR", "Bar", "", 0), ("PANE", "Pane", "", 1)]
    fill        = EnumProperty(
        description="Type of fill for window",items=fill_type, default='BAR',
        update=update_building)

    ft          = FloatProperty(
        name="Frame Thickness", description="Thickness of window Frame", min=0.01, max=100.0, default=0.1,
        update=update_building)

    fd          = FloatProperty(
        name="Frame Depth", description="Depth of window Frame", min=0.0, max=100.0, default=0.1,
        update=update_building)

    px          = IntProperty(
        name="Horizontal Panes", description="Number of horizontal frames", min=0, max=100, default=1,
        update=update_building)

    py          = IntProperty(
        name="Vertical Panes", description="Number of vertical frames", min=0, max=100, default=1,
        update=update_building)

    pt          = FloatProperty(
        name="Pane Frame Thickness", description="Thickness of window pane frame", min=0.01, max=100.0, default=0.1,
        update=update_building)

    pd          = FloatProperty(
        name="Pane Frame Depth", description="Depth of window pane frame", min=0.01, max=100.0, default=0.01,
        update=update_building)

    ares        = IntProperty(
        name="Arc Resolution", description="Number of segements for the arc", min=0, max=1000, default=5,
        update=update_building)

    aoff        = FloatProperty(
        name="Arc Offset", description="How far arc is from top", min=0.01, max=1.0, default=0.5,
        update=update_building)

    aheight     = FloatProperty(
        name="Arc Height", description="Radius of the arc", min=0.01, max=100.0, default=0.5,
        update=update_building)

    adetail     = BoolProperty(
        name="Arc Detail", description="Whether to add detail to arc", default=False,
        update=update_building)

    dthick      = FloatProperty(
        name="Arc Detail Size", description="Size of arc details", min=0.01, max=100.0, default=0.02,
        update=update_building)

    ddepth      = FloatProperty(
        name="Arc Detail Depth", description="Depth of arc details", min=0.01, max=100.0, default=0.02,
        update=update_building)

    has_split = BoolProperty(
        name="Add Split", description="Whether to split the window face", default=False,
        update=update_building)

    split = PointerProperty(type=SplitProperty)

    def draw(self, context, layout):
        row = layout.row()
        row.prop(self, "type", text="")

        box = layout.box()
        if self.type == 'BASIC':
            row = box.row(align=True)
            row.prop(self, 'fill', expand=True)

            col = box.column(align=True)
            col.prop(self, 'ft')
            col.prop(self, 'fd')

            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(self, 'px')
            row.prop(self, 'py')

            col.prop(self, 'pt')
            if self.fill == 'PANE':
                col.prop(self, 'pd')

        elif self.type == 'ARCHED':
            # -- arch
            col = box.column(align=True)
            col.prop(self, 'ares')
            col.prop(self, 'aoff')
            col.prop(self, 'aheight')

            col = box.column(align=True)
            col.prop(self, 'adetail', toggle=True)
            if self.adetail:
                col.prop(self, 'dthick')
                col.prop(self, 'ddepth')

            # -- lower panes/bars
            box.separator()
            row = box.row(align=True)
            row.prop(self, 'fill', expand=True)
            col = box.column(align=True)
            col.prop(self, 'ft')
            col.prop(self, 'fd')

            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(self, 'px')
            row.prop(self, 'py')

            col.prop(self, 'pt')
            if self.fill == 'PANE':
                col.prop(self, 'pd')


        box = layout.box()
        box.prop(self, 'has_split', toggle=True)
        if self.has_split:
            col = box.column(align=True)
            col.prop(self.split, 'amount', slider=True)

            col = box.column(align=True)
            col.prop(self.split, 'off')


class DoorProperty(bpy.types.PropertyGroup):
    oft = FloatProperty(name="OuterFrame Thickness", description="Thickness of outer door Frame", min=0.0, max=100.0,
                        default=0.0)

    ofd = FloatProperty(name="OuterFrame Depth", description="Depth of outer door Frame", min=0.0, max=100.0,
                        default=0.0)

    ift = FloatProperty(name="InnerFrame Thickness", description="Thickness of inner door Frame", min=0.0, max=100.0,
                        default=0.1)

    ifd = FloatProperty(name="InnerFrame Depth", description="Depth of inner door Frame", min=0.0, max=100.0,
                        default=0.1, step=1)

    # Door Split Options
    has_split = BoolProperty(
        name="Add Split", description="Whether to split the door face", default=False)
    split = PointerProperty(type=SplitProperty)

    # Window Panes
    px = IntProperty(name="Horizontal Panes", description="Number of horizontal window panes", min=0, max=100,
                     default=1)

    py = IntProperty(name="Vertical Panes",
                     description="Number of vertical window panes", min=0, max=100, default=1)

    pt = FloatProperty(name="Pane Thickness", description="Thickness of window panes", min=0.01, max=100.0,
                       default=0.05)

    pd = FloatProperty(name="Pane Depth", description="Depth of window panes", min=0.01, max=100.0, default=0.01,
                       step=1)

    offset = FloatProperty(
        name="Pane Offset", description="Offset of window panes", min=-1.0, max=1.0, default=1.0)

    width = FloatProperty(
        name="Pane Width", description="Width of window panes", min=0.0, max=100.0, default=0.5)

    # Grooves
    gx = IntProperty(name="Horizontal Grooves",
                     description="Number of horizontal grooves", min=0, max=100, default=1)

    gy = IntProperty(name="Vertical Grooves",
                     description="Number of vertical grooves", min=0, max=100, default=1)

    gt = FloatProperty(name="Groove Thickness",
                       description="Thickness of groove", min=0.01, max=100.0, default=0.05)

    gd = FloatProperty(name="Groove Depth", description="Depth of groove",
                       min=0.01, max=100.0, default=0.01, step=1)

    gw = FloatProperty(
        name="Groove Width", description="Width of grooves", min=0.01, max=1.0, default=1.0)

    goff = FloatProperty(
        name="Groove Offset", description="Offset of grooves", min=-1.0, max=1.0, default=0.0)

    # Options
    hdd = BoolProperty(name='Double Door',
                       description="If the door is split", default=False)

    grov = BoolProperty(
        name='Grooved', description='Door has grooves', default=False)

    panned = BoolProperty(name='Window Panes',
                          description='Door has window panes', default=False)

    def draw(self, context, layout):
        box = layout.box()
        box.prop(self, "hdd", toggle=True)

        col = box.column(align=True)
        col.prop(self, 'oft')
        col.prop(self, 'ofd')

        col = box.column(align=True)
        col.prop(self, 'ift')
        col.prop(self, 'ifd')

        # Split
        box = layout.box()
        box.prop(self, 'has_split', toggle=True)
        if self.has_split:
            col = box.column(align=True)
            col.prop(self.split, 'amount', slider=True)

            col = box.column(align=True)
            col.prop(self.split, 'off')

        # Panned
        box = layout.box()
        box.prop(self, 'panned', toggle=True)
        if self.panned:
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(self, 'px')
            row.prop(self, 'py')
            col.prop(self, 'pt')
            col.prop(self, 'pd')

            col = box.column(align=True)
            col.prop(self, 'offset')
            col.prop(self, 'width')

        # Groove
        box = layout.box()
        box.prop(self, 'grov', toggle=True)
        if self.grov:
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(self, 'gx')
            row.prop(self, 'gy')
            col.prop(self, 'gt')
            col.prop(self, 'gd')

            col = box.column(align=True)
            col.prop(self, 'goff')
            col.prop(self, 'gw')


class BalconyProperty(bpy.types.PropertyGroup):
    # Balcony Options
    width = FloatProperty(
        name="Balcony Width", description="Width of balcony", min=0.01, max=100.0, default=2)

    railing = BoolProperty(
        name="Add Railing", description="Whether the balcony has railing", default=True)

    # Balcony Split Options
    has_split = BoolProperty(
        name="Add Split", description="Whether to split the balcony face", default=False)
    split = PointerProperty(type=SplitProperty)

    # Rail Options
    pw = FloatProperty(name="Post Width", description="Width of each post",
                       min=0.01, max=100.0, default=0.15)

    ph = FloatProperty(
        name="Post Height", description="Height of each post", min=0.01, max=100.0, default=0.7)

    pd = FloatProperty(name="Post Desnsity", description="Number of posts along each edge", min=0.0, max=1.0,
                       default=0.9)

    rw = FloatProperty(name="Rail Width", description="Width of each rail",
                       min=0.01, max=100.0, default=0.15)

    rh = FloatProperty(name="Rail Height", description="Height of each rail",
                       min=0.01, max=100.0, default=0.025)

    rd = FloatProperty(name="Rail Desnsity", description="Number of rails over each edge", min=0.0, max=1.0,
                       default=0.2)

    ww = FloatProperty(name="Wall Width", description="Width of each wall",
                       min=0.01, max=100.0, default=0.075)

    wh = FloatProperty(
        name="Wall Height", description="Height of each wall", min=0.01, max=100.0, default=0.7)

    cpw = FloatProperty(name="Corner Post Width", description="Width of each corner post", min=0.01, max=100.0,
                        default=0.15)

    cph = FloatProperty(name="Corner Post Height", description="Height of each corner post", min=0.01, max=100.0,
                        default=0.7)

    hcp = BoolProperty(
        name="Corner Posts", description="Whether the railing has corner posts", default=True)

    df = BoolProperty(name="Delete Faces",
                      description="Whether to delete unseen faces", default=True)

    fill_types = [("POSTS", "Posts", "", 0),
                  ("RAILS", "Rails", "", 1), ("WALL", "Wall", "", 2)]
    fill = EnumProperty(description="Type of railing",
                        items=fill_types, default='POSTS')

    def draw(self, context, layout):
        row = layout.row()
        row.prop(self, 'width')

        box = layout.box()
        box.prop(self, 'has_split', toggle=True)
        if self.has_split:
            col = box.column(align=True)
            col.prop(self.split, 'amount', slider=True)

            col = box.column(align=True)
            col.prop(self.split, 'off')

        box = layout.box()
        box.prop(self, 'railing', toggle=True)
        if self.railing:
            row = box.row()
            row.prop(self, "fill", text="")

            col = box.column(align=True)
            if self.fill == 'POSTS':
                col.prop(self, 'pw')
                col.prop(self, 'ph')
                col.prop(self, 'pd')
            elif self.fill == 'RAILS':
                col.prop(self, 'rw')
                col.prop(self, 'rh')
                col.prop(self, 'rd')
            elif self.fill == 'WALL':
                col.prop(self, 'ww')
                col.prop(self, 'wh')

                row = box.row()
                row.prop(self, 'df')

            row = box.row()
            row.prop(self, "hcp", toggle=True)
            if self.hcp:
                # box = layout.box()
                col = box.column(align=True)
                col.prop(self, 'cpw')
                col.prop(self, 'cph')


class RailingProperty(bpy.types.PropertyGroup):
    pw = FloatProperty(name="Post Width", description="Width of each post",
                       min=0.01, max=100.0, default=0.15)

    ph = FloatProperty(
        name="Post Height", description="Height of each post", min=0.01, max=100.0, default=0.7)

    pd = FloatProperty(name="Post Desnsity", description="Number of posts along each edge", min=0.0, max=1.0,
                       default=0.9)

    rw = FloatProperty(name="Rail Width", description="Width of each rail",
                       min=0.01, max=100.0, default=0.15)

    rh = FloatProperty(name="Rail Height", description="Height of each rail",
                       min=0.01, max=100.0, default=0.025)

    rd = FloatProperty(name="Rail Desnsity", description="Number of rails over each edge", min=0.0, max=1.0,
                       default=0.2)

    ww = FloatProperty(name="Wall Width", description="Width of each wall",
                       min=0.01, max=100.0, default=0.075)

    wh = FloatProperty(
        name="Wall Height", description="Height of each wall", min=0.01, max=100.0, default=0.7)

    cpw = FloatProperty(name="Corner Post Width", description="Width of each corner post", min=0.01, max=100.0,
                        default=0.15)

    cph = FloatProperty(name="Corner Post Height", description="Height of each corner post", min=0.01, max=100.0,
                        default=0.7)

    hcp = BoolProperty(
        name="Corner Posts", description="Whether the railing has corner posts", default=True)

    df = BoolProperty(name="Delete Faces",
                      description="Whether to delete unseen faces", default=True)

    fill_types = [("POSTS", "Posts", "", 0),
                  ("RAILS", "Rails", "", 1), ("WALL", "Wall", "", 2)]
    fill = EnumProperty(description="Type of railing",
                        items=fill_types, default='POSTS')

    def draw(self, context, layout):

        row = layout.row()
        row.prop(self, "fill", text="")

        box = layout.box()
        col = box.column(align=True)
        if self.fill == 'POSTS':
            col.prop(self, 'pw')
            col.prop(self, 'ph')
            col.prop(self, 'pd')
        elif self.fill == 'RAILS':
            # col.prop(self, 'rw')
            col.prop(self, 'rh')
            col.prop(self, 'rd')
        elif self.fill == 'WALL':
            col.prop(self, 'ww')
            col.prop(self, 'wh')

            row = box.row()
            row.prop(self, 'df')

        row = layout.row()
        row.prop(self, "hcp", toggle=True)
        if self.hcp:
            box = layout.box()
            col = box.column(align=True)
            col.prop(self, 'cpw')
            col.prop(self, 'cph')


class StairsProperty(bpy.types.PropertyGroup):
    step_count = IntProperty(
        name="Step Count", description="Number of steps", min=1, max=100, default=3)

    step_width = FloatProperty(
        name="Step Width", description="Width of each step", min=0.01, max=100.0, default=.5)

    scale = FloatProperty(
        name="Scale", description="Scale of the steps", min=0.0, max=1.0, default=0.0)

    bottom_faces = BoolProperty(
        name="Bottom Faces", description="Wether to delete bottom faces", default=True)

    def draw(self, context, layout):
        col = layout.column(align=True)
        col.prop(self, 'step_count')
        col.prop(self, 'step_width')

        layout.prop(self, 'scale')
        layout.prop(self, 'bottom_faces', toggle=True)


class StaircaseProperty(bpy.types.PropertyGroup):
    # --landing
    # ****************************
    lcount = IntProperty(name='Landing Count', description='Number of landings in the staircase', min=1, max=100,
                         default=3)

    lwidth = FloatProperty(
        name='Landing Width', description='Width of each landing', min=1.0, max=100.0, default=4.0)

    llength = FloatProperty(name='Landing Length', description='Length of each landing', min=1.0, max=100.0,
                            default=2.5)

    lheight = FloatProperty(name='Landing Height', description='Thickness of each landing', min=0.01, max=100.0,
                            default=.25)

    l_offz = FloatProperty(name='Landing Height Offset', description='Height offset of each landing', min=1.0,
                           max=100.0, default=2.0)

    l_offy = FloatProperty(name='Landing Gap Offset', description='Gap between Each landing', min=1.0, max=100.0,
                           default=4.0)

    #       support
    lsp = FloatProperty(name='Landing Support Width', description='Width of each landing support beam', min=0.01,
                        max=100.0, default=.25)

    #       railing
    lpw = FloatProperty(name='Landing Post Width', description='Width of landing posts ', min=0.01, max=100.0,
                        default=.1)

    lph = FloatProperty(name='Landing Post Height', description='Height of landing posts', min=0.01, max=100.0,
                        default=1.0)

    lpd = FloatProperty(name='Landing Post Density', description='Distribution of landing Posts', min=0.0, max=1.0,
                        default=.4)

    lrw = FloatProperty(name='Landing Rail Width', description='Width of landing rails', min=0.01, max=100.0,
                        default=.2)

    lrh = FloatProperty(name='Landing Rail Height', description='Height of each landing rail', min=0.1, max=100.0,
                        default=1.0)

    # -- steps
    # ****************************
    scount = IntProperty(name='Step Count', description='Number of steps between each landing', min=1, max=100,
                         default=5)

    sgap = FloatProperty(name='Step Gap', description='Gap between each staircase step', min=0.0, max=1.0, default=.25,
                         update=update_sgap)

    #       support
    ssc = IntProperty(name='Step Support Count', description='Number of support beams for steps', min=1, max=10,
                      default=2)

    ssw = FloatProperty(name='Step Support Width', description='Width of each step support beam', min=0.01, max=100.0,
                        default=.2)

    #       railing
    sph = FloatProperty(name='Step Post Height',
                        description='Height of step posts', min=0.01, max=100.0, default=1.0)

    spw = FloatProperty(name='Step Post Width',
                        description='Width of step posts', min=0.01, max=100.0, default=0.1)

    srw = FloatProperty(name='Step Rail Width',
                        description='Width of step rails', min=0.01, max=100.0, default=0.15)

    # -- options
    # ****************************
    hls = BoolProperty(name='Landing Support', description='Whether the staircase landings have support beams',
                       default=False)

    hlr = BoolProperty(name='Landing Rails',
                       description='Whether the staircase landings have railing', default=False)

    hss = BoolProperty(
        name='Step Support', description='Whether the staircase steps have support beams', default=False)

    hsr = BoolProperty(
        name='Step Rails', description='Whether the staircase steps have railing', default=False)

    hisr = BoolProperty(name='Inner Step Rails', description='Whether the staircase steps have inner railing',
                        default=True)

    hosr = BoolProperty(name='Outer Step Rails', description='Whether the staircase steps have outer railing',
                        default=True)

    def draw(self, context, layout):
        box = layout.box()

        col = box.column(align=True)
        col.prop(self, 'lcount')
        col.prop(self, 'lwidth')
        col.prop(self, 'llength')
        col.prop(self, 'lheight')

        box.prop(self, 'l_offz')
        box.prop(self, 'l_offy')

        # -- support
        box = layout.box()
        box.prop(self, 'hls')
        if self.hls:
            col = box.column()
            col.prop(self, 'lsp')

        # -- railing
        box = layout.box()
        box.prop(self, 'hlr')
        if self.hlr:
            # -- Posts
            col = box.column(align=True)
            col.prop(self, 'lpw')
            col.prop(self, 'lph')
            col.prop(self, 'lpd')
            # -- Rails
            col = box.column(align=True)
            col.prop(self, 'lrw')
            # col.prop(self, 'lrh')

        # steps
        layout.label('Steps')
        box = layout.box()

        col = box.column(align=True)
        col.prop(self, 'scount')
        col.prop(self, 'sgap')

        # --support
        box = layout.box()
        box.prop(self, 'hss')
        if self.hss:
            col = box.column()
            col.prop(self, 'ssc')
            # col.prop(self, 'ssw')

        # -- railing
        box = layout.box()
        box.prop(self, 'hsr')
        if self.hsr:
            # -- Posts
            col = box.column(align=True)
            col.prop(self, 'spw')
            col.prop(self, 'sph')

            # -- Rails
            col = box.column(align=True)
            col.prop(self, 'srw')

            # -- Rail options
            box.label('Rail Options')
            row = box.row(align=True)
            row.prop(self, 'hisr', toggle=True)
            row.prop(self, 'hosr', toggle=True)


class RoofProperty(bpy.types.PropertyGroup):
    r_types = [
        ("FLAT", "Flat", "", 0), 
        ("GABLE", "Gable", "", 1),
    ]
    type = EnumProperty(description="Type of roof",
                        items=r_types, default='FLAT')

    thick = FloatProperty(
        name="Thickness", description="Thickness of roof hangs", min=0.01, max=1000.0, default=.1)

    outset = FloatProperty(
        name="Outset", description="Outset of roof hangs", min=0.01, max=1000.0, default=.1)

    height = FloatProperty(
        name="Height", description="Height of entire roof", min=0.01, max=1000.0, default=1)

    o_types = [("LEFT", "Left", "", 0), ("RIGHT", "Right", "", 1), ]
    orient = EnumProperty(description="Orientation of gable",
                          items=o_types, default='LEFT')


    def draw(self, context, layout):
        layout.prop(self, 'type', text="")

        box = layout.box()
        if self.type == 'FLAT':
            col = box.column()
            col.prop(self, 'thick')
            col.prop(self, 'outset')

        elif self.type == 'GABLE':
            col = box.column()
            col.prop(self, 'thick')
            col.prop(self, 'outset')
            col.prop(self, 'height')

            row = box.row(align=True)
            row.prop(self, 'orient', expand=True)


class BuildingProperty(bpy.types.PropertyGroup):

    floorplan   = PointerProperty(type=FloorplanProperty)
    floors      = PointerProperty(type=FloorProperty)
    windows     = CollectionProperty(type=WindowProperty)
    doors       = CollectionProperty(type=DoorProperty)

# =======================================================
#
#           OPERATORS
#
# =======================================================

class FloorplanOperator(bpy.types.Operator):
    """ Create a floorplan object """
    bl_idname = "cynthia.add_floorplan"
    bl_label = "Create Floorplan"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Build the geometry
        fp = Floorplan()
        fp.build()

        # Add property list item
        # -- prop.id is optional, only useful for collectiontypes
        obj         = context.object
        prop        = obj.property_list.add()
        prop.id     = len(obj.property_list)
        prop.type   = "FLOOPLAN"
        prop.name   = "Floorplan Property"

        obj.property_index = len(obj.property_list)-1

        # Add flag to be used in update
        obj['has_floorplan'] = True

        return {'FINISHED'}


class FloorOperator(bpy.types.Operator):
    """ Creates floors from active floorplan object """
    bl_idname = "cynthia.add_floors"
    bl_label = "Add Floors"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        # Build geometry
        floor = Floor()
        floor.build(context)

        # Add property list item
        # -- prop.id is optional, only useful for collectiontypes
        obj         = context.object
        prop        = obj.property_list.add()
        prop.id     = len(obj.property_list)
        prop.type   = "FLOOR"
        prop.name   = "Floor Property"

        obj.property_index = len(obj.property_list)-1

        # Add flag to be used in update
        obj['has_floors'] = True

        return {'FINISHED'}


class WindowOperator(bpy.types.Operator):
    """ Creates windows on selected mesh faces """
    bl_idname = "cynthia.add_window"
    bl_label = "Add Window"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        elif event.type == 'MOUSEMOVE':
            bpy.context.window.cursor_set("HAND")
            ray_cast_modal(self, context, event)
            return {'RUNNING_MODAL'}
        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.selected_faces.append(self.face_index)

            # Add window property
            obj     = context.object
            prop    = obj.property_list[obj.property_index]

            data = obj['window_groups'][str(prop.id)]
            if not isinstance(data, list):
                data = data.to_list()
            face_data = facedata_from_index(obj, self.face_index)
            data.append(face_data)
            obj['window_groups'].update({str(prop.id) : data})

            # Create geometry
            Window.build(context, [self.face_index])

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.context.window.cursor_set("DEFAULT")
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            bpy.types.SpaceView3D.draw_handler_remove(self._handle2, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            # Add modal callbacks
            args            = (self, context)
            self._handle    = bpy.types.SpaceView3D.draw_handler_add(hover_face_callback, args, 'WINDOW', 'POST_PIXEL')
            self._handle2   = bpy.types.SpaceView3D.draw_handler_add(select_face_callback, args, 'WINDOW', 'POST_PIXEL')

            # Face selection states
            self.face_index     = -1
            self.selected_faces = []

            # Add property proxy
            obj         = context.object
            prop        = obj.property_list.add()
            win         = obj.building.windows.add()
            prop.type   = "WINDOW"
            prop.id     = len(obj.building.windows)-1
            prop.name   = "Window Property {}".format(len(obj.building.windows))
            obj.property_index          = len(obj.property_list)-1
            
            # Store face indices for each window property
            if not obj.get('window_groups'):
                obj['window_groups']            = dict()
            obj['window_groups'][str(prop.id)]  = list()

            obj['has_windows'] = True
            
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}


class DoorOperator(bpy.types.Operator):
    """ Creates doors on selected mesh faces """
    bl_idname = "cynthia.add_door"
    bl_label = "Add Door"
    bl_options = {'REGISTER', 'UNDO'}

    props = PointerProperty(type=DoorProperty)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'EDIT'

    def execute(self, context):

        d = Door(self.props)
        d.build()

        return {'FINISHED'}

    def draw(self, context):
        self.props.draw(context, self.layout)


class BalconyOperator(bpy.types.Operator):
    """ Creates balconies on selected mesh faces """
    bl_idname = "cynthia.add_balcony"
    bl_label = "Add Balcony"
    bl_options = {'REGISTER', 'UNDO'}

    props = PointerProperty(type=BalconyProperty)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'EDIT'

    def execute(self, context):
        props = self.props
        sp = props.split

        me = get_edit_mesh()
        bm = bmesh.from_edit_mesh(me)

        make_balcony(props.width, props.railing, props.pw, props.ph, props.pd, props.rw, props.rh, props.rd, props.ww,
                     props.wh, props.cpw, props.cph, props.hcp, props.df, props.fill, sp.amount[
                         0], sp.amount[1],
                     sp.off[0], sp.off[1], sp.off[2], props.has_split)
        bmesh.update_edit_mesh(me)

        return {'FINISHED'}

    def draw(self, context):
        self.props.draw(context, self.layout)


class RailingOperator(bpy.types.Operator):
    """ Create railing on selected mesh edges """
    bl_idname = "cynthia.add_railing"
    bl_label = "Add Railing"
    bl_options = {'REGISTER', 'UNDO'}

    props = PointerProperty(type=RailingProperty)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'EDIT'

    def execute(self, context):
        props = self.props

        me = get_edit_mesh()
        bm = bmesh.from_edit_mesh(me)
        make_railing(bm, [e for e in bm.edges if e.select], props.pw, props.ph, props.pd, props.rw, props.rh, props.rd,
                     props.ww, props.wh, props.cpw, props.cph, props.hcp, props.df, props.fill)
        bmesh.update_edit_mesh(me)

        return {'FINISHED'}

    def draw(self, context):
        self.props.draw(context, self.layout)


class StairsOperator(bpy.types.Operator):
    """ Create stairs on selected mesh faces """
    bl_idname = "cynthia.add_stairs"
    bl_label = "Add Stairs"
    bl_options = {'REGISTER', 'UNDO'}

    props = PointerProperty(type=StairsProperty)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'EDIT'

    def execute(self, context):
        props = self.props

        make_stairs_type2(props.step_count, props.step_width,
                          props.scale, props.bottom_faces)

        return {'FINISHED'}

    def draw(self, context):
        self.props.draw(context, self.layout)


class StaircaseOperator(bpy.types.Operator):
    """ Create a staircase object """
    bl_idname = "cynthia.add_staircase"
    bl_label = "Add Staircase"
    bl_options = {'REGISTER', 'UNDO'}

    props = PointerProperty(type=StaircaseProperty)

    def execute(self, context):
        props = self.props

        # Create Staircase Object
        obj = make_object('staircase', make_mesh('sc.mesh'))
        bm = bm_from_obj(obj)

        case = make_stair_case(bm, props.lcount, props.lwidth, props.llength, props.lheight, props.l_offz, props.l_offy,
                               props.lsp, props.lpw, props.lph, props.lpd, props.lrw, props.lrh, props.scount,
                               props.sgap, props.ssc, props.ssw, props.sph, props.spw, props.srw, props.hls, props.hlr,
                               props.hss, props.hsr, props.hisr, props.hosr)

        bm_to_obj(case, obj)
        link_obj(obj)

        return {'FINISHED'}

    def draw(self, context):
        self.props.draw(context, self.layout)


class RoofOperator(bpy.types.Operator):
    """ Create roof on selected mesh faces """
    bl_idname = "cynthia.add_roof"
    bl_label = "Add Roof"
    bl_options = {'REGISTER', 'UNDO'}

    props = PointerProperty(type=RoofProperty)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'EDIT'

    def execute(self, context):
        props = self.props

        me = get_edit_mesh()
        bm = bmesh.from_edit_mesh(me)

        if props.type == 'FLAT':
            make_flat_roof(bm, props.thick, props.outset)
        elif props.type == 'GABLE':
            make_gable_roof(bm, props.height, props.outset,
                            props.thick, props.orient)
        else:
            make_hip_roof(bm, me, props.hip_amount, props.height, props.hip_region, props.hip_percent, props.outset,
                          props.thick, props.dissolve, props.dissolve_angle)

        bmesh.update_edit_mesh(me, True)
        return {'FINISHED'}

    def draw(self, context):
        self.props.draw(context, self.layout)


# =======================================================
#
#           PANEL UI
#
# =======================================================

class PROP_items(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon='SNAP_PEEL_OBJECT')

    def invoke(self, context, event):
        pass   


class CynthiaPanel(bpy.types.Panel):
    """Docstring of CynthiaPanel"""
    bl_idname = "VIEW3D_PT_cynthia"
    bl_label = "Cynthia Building Tools"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Cynthia Tools'

    def draw(self, context):
        layout = self.layout
        active = context.object

        # Draw the operators
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator("cynthia.add_floorplan")
        row.operator("cynthia.add_floors")

        row = col.row(align=True)
        row.operator("cynthia.add_window")
        row.operator("cynthia.add_door")

        row = col.row(align=True)
        row.operator("cynthia.add_balcony")
        row.operator("cynthia.add_railing")

        col.operator("cynthia.add_stairs")
        # col.operator("cynthia.add_staircase")

        col.operator("cynthia.add_roof")

        # Draw Properties
        col = layout.column(align=True)
        col.box().label("Properties")

        if active:
            box = col.box()
            obj = context.object

            # Draw uilist for all property groups
            rows = 2
            row = box.row()
            row.template_list("PROP_items", "", obj, "property_list", obj, "property_index", rows=rows)


            # draw  properties for active group
            active_index = obj.property_index
            if not len(obj.property_list): 
                return
            active_prop = obj.property_list[active_index]

            if active_prop.type == 'FLOOPLAN':
                fp_props = obj.building.floorplan 
                fp_props.draw(context, box)
            elif active_prop.type == 'FLOOR':
                floor_props = obj.building.floors
                floor_props.draw(context, box)
            elif active_prop.type == 'WINDOW':
                win_prop = obj.building.windows[active_prop.id]
                win_prop.draw(context, box)


# =======================================================
#
#           REGISTER
#
# =======================================================

def register():     
    bpy.utils.register_module(__name__)

    bpy.types.Object.building = PointerProperty(type=BuildingProperty)

    bpy.types.Object.property_list = CollectionProperty(type=PropertyProxy)
    bpy.types.Object.property_index = IntProperty()


def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Object.building
    del bpy.types.Object.property_list
    del bpy.types.Object.property_index


if __name__ == "__main__":
    import os
    os.system("clear")
    # useful for continuous updates
    try:
        unregister()
    except Exception as e:
        import traceback; traceback.print_exc()
        print("UNREGISTERED MODULE .. FAIL", e)
    register()


    # # optional run tests
    # from .tests import CynthiaTest
    # CynthiaTest.run_tests()

    # Dev --init workspace
    # --clear
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)    
    # -- add 
    bpy.ops.cynthia.add_floorplan()
    bpy.ops.cynthia.add_floors()
    bpy.context.object.building.floors.floor_count = 3
    bpy.context.object.building.floors.floor_height = 3