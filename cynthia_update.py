import bpy
from .cynthia_floorplan import Floorplan
from .cynthia_floor import Floor
from .cynthia_window import Window
from .utils import obj_clear_data


def update_building(self, context):
    """Update building geometry
    
    This function is used by all properties as an update callback. 
    It must handle all the update and regeneration of active building object
    geometry
    
    Arguments:
        self     -- the property group containing the property that 
                    was changed/updated
        context  -- current blender context
    
    Returns:
        None
    """

    # Clear mesh data from active object
    obj = context.object
    obj_clear_data(obj)

    # Regenerate
    # --floorplan
    if obj.get('has_floorplan', False):
        Floorplan.build(True, obj)

    # -- floors
    if obj.get('has_floors', False):
        Floor.build(context, True)

    # -- windows
    if obj.get('has_windows', False):
        # Update all window property groups
        for prop in obj.property_list:
            if prop.type == 'WINDOW':
                face_indices = obj['window_groups'][str(prop.id)]
                Window.build(context, face_indices, True)

    return None 
