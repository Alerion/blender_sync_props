bl_info = {
    "name": "Sync objects properties",
    "author": "Dmytro Kostochko",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > SyncProps",
    "description": "Sync properties of a selected object and the current view layer.",
    "warning": "",
    "wiki_url": "",
    "category": "3D View"
}

import bpy
import bpy_types


def is_readonly_property(obj: bpy.types.bpy_struct, property_name: str) -> bool:
    try:
        return obj.is_property_readonly(property_name)
    except TypeError:
        return False


class SyncPropertiesOperator(bpy.types.Operator):
    bl_idname = "view_layout_sync.sync_properties"
    bl_label = "Sync properties"
    bl_options = {'UNDO'}    
    
    def execute(self, context: bpy_types.Context) -> set[str]:
        if context.scene.addon_sync_props_source_object == None:
            self.report({'ERROR'}, "Properties source object must be set")
            return {'FINISHED'}

        obj = context.scene.addon_sync_props_source_object
        
        # Sync missing selected object's properties to all view layers.
        for view_layer in context.scene.view_layers:
            for property_name, property_value in obj.items():
                if is_readonly_property(obj, property_name):
                    continue            
                if property_name not in view_layer:
                    view_layer[property_name] = property_value
        
        # Switch to the next view layers.
        new_view_layer = get_next_view_layer(context)
        context.window.view_layer = new_view_layer

        # Sync current view layer's properties to the selected object.
        synced_properties = 0
        for property_name, property_value in new_view_layer.items():
            if is_readonly_property(new_view_layer, property_name):
                continue
            
            synced_properties += 1
            obj[property_name] = property_value
        
        # Trigger properties panel update.
        obj.update_tag()
        for area in context.screen.areas:
            area.tag_redraw()
        
        self.report({"INFO"}, f"{synced_properties} properties synced!")
        return {'FINISHED'}


def get_next_view_layer(context: bpy_types.Context) -> bpy.types.ViewLayer:
    view_layers = context.scene.view_layers
    current_view_layer = context.window.view_layer
    for i, view_layer in enumerate(view_layers):
        if current_view_layer == view_layer:
            break
    next_layer_index = i + 1
    if next_layer_index == len(view_layers):
        next_layer_index = 0
    return view_layers[next_layer_index]



class SP_PT_SharePropertiesPanel(bpy.types.Panel):
    bl_label = "Sync Properties"
    bl_category = "SyncProps"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: bpy_types.Context) -> bool:
        return context.active_object is not None
    
    def draw(self, context: bpy_types.Context) -> None:
        view_layer = context.view_layer
        layout = self.layout
        
        col = layout.column(align=True)
        col.label(text=f"View Layer: {view_layer.name}")
        col.prop_search(context.scene, "addon_sync_props_source_object", context.scene, "objects", text="")
        col.operator(SyncPropertiesOperator.bl_idname, text="Sync Properties (Alt+Q)")

        
classes = (
    SyncPropertiesOperator,
    SP_PT_SharePropertiesPanel,
)

addon_keymaps = []


def register() -> None:
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.addon_sync_props_source_object = bpy.props.PointerProperty(type=bpy.types.Object)

    # Add a keymap entry
    global addon_keymaps
    window_manager = bpy.context.window_manager
    if key_config := window_manager.keyconfigs.addon:
        key_map = key_config.keymaps.new(name="3D View", space_type='VIEW_3D')
        key_map_index = key_map.keymap_items.new(SyncPropertiesOperator.bl_idname, type="Q", value="PRESS", alt=True)
        addon_keymaps.append((key_map, key_map_index))
    else:
        print('Keyconfig unavailable, no keybinding items registered')


def unregister() -> None:
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.addon_sync_props_source_object

    # Remove the keymap entry
    global addon_keymaps
    window_manager = bpy.context.window_manager
    for key_map, key_map_index in addon_keymaps:
        key_map.keymap_items.remove(key_map_index)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
