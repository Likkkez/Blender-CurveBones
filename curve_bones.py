
bl_info = {
    "name": "Curve control bones",
    "author": "Likkez",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "description": "Make spline ik bones without pain",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}


import bpy
from numpy import matmul
from mathutils import Vector as Vec
from bpy.app.handlers import persistent


def find_objects(context):
    arm=None
    curves=[]
    check_objects=True
    if len(context.selected_editable_objects)>=2:
        for obj in context.selected_editable_objects:
            if obj.type=='CURVE':
                curves.append(obj)
            elif obj.type=='ARMATURE':
                if arm: #check if more than one armature
                    check_objects=False 
                arm=obj
    if not (arm and curves):
        check_objects=False
    return curves, arm, check_objects

def make_control_bones(context,name):
    bezier=True
    scene=context.scene
    curves,arm,check_objects=find_objects(context)
    if not check_objects:
        return False
    name_index=-2
    if curves and arm:
        for curve in curves:
            name_index+=1
            vertex_index=0
            for sp in curve.data.splines:
                name_index+=1
                if sp.points:
                    points=sp.points
                    bezier=False
                elif sp.bezier_points:
                    points=sp.bezier_points
                    bezier=True
                for bp in points:
                    context.view_layer.objects.active=arm
                    bpy.ops.object.mode_set(mode='EDIT',toggle=False)
                    name_index_str=""
                    if name_index>0:
                        name_index_str="_"+str(name_index-1)
                    bone=arm.data.edit_bones.new(name+name_index_str)
                    if bezier:
                        bone.head = arm.matrix_world.inverted() @ curve.matrix_world @ bp.co
                        bone.tail = arm.matrix_world.inverted() @ curve.matrix_world @ bp.handle_right
                    else:
                        point_loc=(bp.co).xyz
                        bone.head = arm.matrix_world.inverted() @ curve.matrix_world @ point_loc
                        offset = Vec((0.0, 0.0, 0.5))
                        bone.tail = bone.head + offset
                    bpy.ops.object.mode_set(mode='OBJECT',toggle=False)
                    
                    mod=curve.modifiers.new(name="Hook",type="HOOK")
                    mod.object=arm
                    mod.subtarget=bone.name
                    if bezier:
                        mod_points=(vertex_index+0,vertex_index+1,vertex_index+2)
                    else:
                        mod_points=(vertex_index,)
                        print(vertex_index)
                    mod.vertex_indices_set(mod_points)
                    
                    if bezier:
                        vertex_index+=3 #bezier has 3 verticies per point
                    else:
                        vertex_index+=1
    return True
        

class CALL_OT_MakeSplineBones(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.make_spline_bones"
    bl_label = "Make Curve/Spline Bones"
    bl_options = set({'REGISTER', 'UNDO'})
    name: bpy.props.StringProperty(
        name="Name",
        description="Name to use for created bones.",
        default="SplineBone",
        )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if make_control_bones(context,self.name):
            return {'FINISHED'}
        else:
            self.report(type={"ERROR_INVALID_INPUT"},message="Select an armature and at least one curve.")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(CALL_OT_MakeSplineBones)


def unregister():
    bpy.utils.unregister_class(CALL_OT_MakeSplineBones)


if __name__ == "__main__":
    register()



