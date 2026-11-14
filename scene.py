import bpy
import math
import random
import os

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Set color management to AgX or Filmic
    scene = bpy.context.scene
    scene.display_settings.display_device = 'sRGB'
    try:
        scene.view_settings.view_transform = 'AgX'
        scene.view_settings.look = 'AgX - Punchy'
    except Exception:
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = 0.2

def create_materials():
    mats = {}

    # 1. Dark Ceramic Bowl Material
    mat_bowl = bpy.data.materials.new(name="M_Bowl")
    mat_bowl.use_nodes = True
    nodes = mat_bowl.node_tree.nodes
    links = mat_bowl.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.04, 0.04, 0.05, 1.0) # Deep charcoal/tenmoku
    bsdf.inputs["Roughness"].default_value = 0.22
    bsdf.inputs["Specular IOR Level"].default_value = 0.6
    
    # Subtle noise for ceramic glaze texture
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 40.0
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.03
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mats['bowl'] = mat_bowl

    # 2. Tonkotsu Broth Material (Creamy pale, SSS, glossy oil sheen)
    mat_broth = bpy.data.materials.new(name="M_Broth")
    mat_broth.use_nodes = True
    nodes = mat_broth.node_tree.nodes
    links = mat_broth.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    
    # Base color pale warm ivory-cream
    bsdf.inputs["Base Color"].default_value = (0.88, 0.78, 0.65, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.12
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.35
        bsdf.inputs["Subsurface Radius"].default_value = (0.8, 0.6, 0.4)
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = (0.92, 0.82, 0.68, 1.0)
    elif "Subsurface" in bsdf.inputs: # Older blender syntax fallback
        bsdf.inputs["Subsurface"].default_value = 0.35
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = (0.92, 0.82, 0.68, 1.0)
    
    # Procedural oil spots on broth surface
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 25.0
    voronoi.feature = 'F1'
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1)
    ramp.color_ramp.elements[1].position = 0.35
    ramp.color_ramp.elements[1].color = (0.25, 0.25, 0.25, 1)
    links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
    # Mix with roughness for glossy oil sheen patches
    links.new(ramp.outputs['Color'], bsdf.inputs['Roughness'])
    mats['broth'] = mat_broth

    # 3. Noodles Material
    mat_noodle = bpy.data.materials.new(name="M_Noodle")
    mat_noodle.use_nodes = True
    nodes = mat_noodle.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.92, 0.82, 0.52, 1.0) # Springy wheat yellow
    bsdf.inputs["Roughness"].default_value = 0.25
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.2
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = (0.95, 0.85, 0.55, 1.0)
    mats['noodle'] = mat_noodle

    # 4. Chashu Pork Material (Meat & Seared crust)
    mat_chashu = bpy.data.materials.new(name="M_Chashu")
    mat_chashu.use_nodes = True
    nodes = mat_chashu.node_tree.nodes
    links = mat_chashu.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    
    # Procedural gradient from dark seared crust to pink-brown meat
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.gradient_type = 'RADIAL'
    ramp = nodes.new('ShaderNodeValToRGB')
    
    # Colors: dark seared rim -> fatty white layer -> tender braised meat center
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.22, 0.10, 0.06, 1.0) # Seared outer crust
    
    e1 = ramp.color_ramp.elements.new(0.4)
    e1.color = (0.85, 0.75, 0.68, 1.0) # Fat layer
    
    e2 = ramp.color_ramp.elements.new(0.65)
    e2.color = (0.55, 0.28, 0.22, 1.0) # Pinkish braised pork
    
    ramp.color_ramp.elements[-1].position = 1.0
    ramp.color_ramp.elements[-1].color = (0.42, 0.20, 0.15, 1.0)
    
    links.new(coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    bsdf.inputs["Roughness"].default_value = 0.18 # Glistening sheen
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.3
    
    # Noise bump for meat fibers
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 50.0
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.05
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mats['chashu'] = mat_chashu

    # 5. Soft Boiled Egg White Material
    mat_egg_white = bpy.data.materials.new(name="M_EggWhite")
    mat_egg_white.use_nodes = True
    nodes = mat_egg_white.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.92, 0.90, 0.85, 1.0) # Soft soy-tinged white
    bsdf.inputs["Roughness"].default_value = 0.3
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = (0.95, 0.92, 0.88, 1.0)
    mats['egg_white'] = mat_egg_white

    # 6. Egg Yolk Material (Jammy Deep Orange)
    mat_yolk = bpy.data.materials.new(name="M_EggYolk")
    mat_yolk.use_nodes = True
    nodes = mat_yolk.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.95, 0.32, 0.02, 1.0) # Jammy deep orange yolk
    bsdf.inputs["Roughness"].default_value = 0.08 # Glossy wet liquid look
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.45
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = (1.0, 0.45, 0.05, 1.0)
    mats['yolk'] = mat_yolk

    # 7. Spring Onion Material
    mat_onion = bpy.data.materials.new(name="M_SpringOnion")
    mat_onion.use_nodes = True
    nodes = mat_onion.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.15, 0.55, 0.12, 1.0) # Vibrant fresh green
    bsdf.inputs["Roughness"].default_value = 0.2
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.15
        if "Subsurface Color" in bsdf.inputs:
            bsdf.inputs["Subsurface Color"].default_value = (0.25, 0.65, 0.18, 1.0)
    mats['onion'] = mat_onion

    # 8. Nori Seaweed Material
    mat_nori = bpy.data.materials.new(name="M_Nori")
    mat_nori.use_nodes = True
    nodes = mat_nori.node_tree.nodes
    links = mat_nori.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.015, 0.02, 0.015, 1.0) # Dark matte black-green
    bsdf.inputs["Roughness"].default_value = 0.75
    
    # Crisp roasted texture bump
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 120.0
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mats['nori'] = mat_nori

    # 9. Wooden Chopsticks & Table Material
    mat_wood = bpy.data.materials.new(name="M_Wood")
    mat_wood.use_nodes = True
    nodes = mat_wood.node_tree.nodes
    links = mat_wood.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.35, 0.20, 0.12, 1.0) # Warm wood tone
    bsdf.inputs["Roughness"].default_value = 0.35
    
    # Procedural wood grain
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 30.0
    noise.inputs['Detail'].default_value = 4.0
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.18, 0.09, 0.05, 1.0)
    ramp.color_ramp.elements[1].color = (0.38, 0.22, 0.14, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    mats['wood'] = mat_wood

    # 10. Table Material (Dark Walnut)
    mat_table = bpy.data.materials.new(name="M_Table")
    mat_table.use_nodes = True
    nodes = mat_table.node_tree.nodes
    links = mat_table.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 6.0
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.08, 0.04, 0.03, 1.0)
    ramp.color_ramp.elements[1].color = (0.16, 0.09, 0.06, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs["Roughness"].default_value = 0.28
    mats['table'] = mat_table

    return mats

def build_scene():
    reset_scene()
    mats = create_materials()

    # --- 1. Table ---
    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.08))
    table = bpy.context.active_object
    table.name = "Table"
    table.data.materials.append(mats['table'])

    # --- 2. Ramen Bowl ---
    # Create smooth ceramic bowl profile using lathe/cylinder geometry
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.10, vertices=48, location=(0, 0, 0))
    bowl = bpy.context.active_object
    bowl.name = "RamenBowl"
    
    # Shape the bowl: taper bottom, flared rim
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Subdivide & smooth bowl shape
    bpy.ops.object.mode_set(mode='OBJECT')
    mod_subsurf = bowl.modifiers.new(name="Subsurf", type='SUBSURF')
    mod_subsurf.levels = 2
    mod_subsurf.render_levels = 3
    
    # Scale bottom loop to taper bowl bottom
    for v in bowl.data.vertices:
        if v.co.z < -0.04:
            v.co.x *= 0.65
            v.co.y *= 0.65
        elif v.co.z > 0.03:
            v.co.x *= 1.08
            v.co.y *= 1.08
            
    bpy.ops.object.shade_smooth()
    bowl.data.materials.append(mats['bowl'])

    # --- 3. Broth Surface ---
    bpy.ops.mesh.primitive_cylinder_add(radius=0.118, depth=0.01, vertices=48, location=(0, 0, 0.025))
    broth = bpy.context.active_object
    broth.name = "Broth"
    bpy.ops.object.shade_smooth()
    broth.data.materials.append(mats['broth'])

    # --- 4. Noodles (Swirled loops on broth) ---
    for i in range(16):
        angle = random.uniform(0, math.pi * 2)
        radius = random.uniform(0.02, 0.08)
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        z = 0.028 + random.uniform(0, 0.005)
        
        bpy.ops.mesh.primitive_torus_add(
            major_radius=random.uniform(0.015, 0.03),
            minor_radius=0.0022,
            major_segments=24,
            minor_segments=8,
            location=(x, y, z),
            rotation=(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), random.uniform(0, math.pi))
        )
        nd = bpy.context.active_object
        nd.name = f"Noodle_{i}"
        bpy.ops.object.shade_smooth()
        nd.data.materials.append(mats['noodle'])

    # --- 5. Chashu Pork (2 overlapping slices) ---
    def create_chashu(name, loc, rot_z):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.008, vertices=36, location=loc)
        ch = bpy.context.active_object
        ch.name = name
        ch.scale[0] = 1.15 # slightly elliptical slice
        ch.rotation_euler = (math.radians(6), math.radians(-4), rot_z)
        
        # Subtle vertex displace for natural organic slice shape
        for v in ch.data.vertices:
            v.co.x += random.uniform(-0.002, 0.002)
            v.co.y += random.uniform(-0.002, 0.002)
            
        bpy.ops.object.shade_smooth()
        ch.data.materials.append(mats['chashu'])
        return ch

    chashu1 = create_chashu("Chashu_1", (-0.03, -0.01, 0.034), math.radians(15))
    chashu2 = create_chashu("Chashu_2", (-0.015, -0.045, 0.036), math.radians(-25))

    # --- 6. Soft Boiled Egg (2 halves) ---
    def create_egg_half(name, loc, rot_euler):
        # Egg white base half dome
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=loc)
        egg = bpy.context.active_object
        egg.name = name
        egg.scale[2] = 0.7 # flattened half egg
        egg.rotation_euler = rot_euler
        bpy.ops.object.shade_smooth()
        egg.data.materials.append(mats['egg_white'])
        
        # Jammy Yolk dome
        yolk_loc = (loc[0] + 0.003, loc[1] + 0.003, loc[2] + 0.006)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.016, location=yolk_loc)
        yolk = bpy.context.active_object
        yolk.name = f"{name}_Yolk"
        yolk.scale[2] = 0.55
        yolk.rotation_euler = rot_euler
        bpy.ops.object.shade_smooth()
        yolk.data.materials.append(mats['yolk'])

    create_egg_half("Egg_Half_1", (0.04, 0.02, 0.035), (math.radians(-12), math.radians(10), math.radians(45)))
    create_egg_half("Egg_Half_2", (0.02, 0.06, 0.033), (math.radians(-8), math.radians(-15), math.radians(120)))

    # --- 7. Spring Onion Rings ---
    for i in range(18):
        ox = random.uniform(-0.06, 0.06)
        oy = random.uniform(-0.06, 0.06)
        oz = 0.032 + random.uniform(0, 0.008)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0045, depth=0.0025, vertices=16, location=(ox, oy, oz))
        on = bpy.context.active_object
        on.name = f"SpringOnion_{i}"
        on.rotation_euler = (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), random.uniform(0, math.pi))
        bpy.ops.object.shade_smooth()
        on.data.materials.append(mats['onion'])

    # --- 8. Dark Nori Sheet ---
    bpy.ops.mesh.primitive_plane_add(size=0.05, location=(-0.03, 0.05, 0.04))
    nori = bpy.context.active_object
    nori.name = "NoriSheet"
    nori.scale[0] = 0.7
    nori.scale[1] = 1.0
    nori.rotation_euler = (math.radians(20), math.radians(-15), math.radians(45))
    nori.data.materials.append(mats['nori'])

    # --- 9. Wooden Chopsticks ---
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0035, depth=0.24, vertices=16, location=(0.06, 0.0, 0.068))
    cs1 = bpy.context.active_object
    cs1.name = "Chopstick_1"
    cs1.scale[0] = 0.7 # taper
    cs1.rotation_euler = (math.radians(78), math.radians(-10), math.radians(-20))
    cs1.data.materials.append(mats['wood'])

    bpy.ops.mesh.primitive_cylinder_add(radius=0.0035, depth=0.24, vertices=16, location=(0.072, 0.01, 0.069))
    cs2 = bpy.context.active_object
    cs2.name = "Chopstick_2"
    cs2.scale[0] = 0.7
    cs2.rotation_euler = (math.radians(77), math.radians(-8), math.radians(-22))
    cs2.data.materials.append(mats['wood'])

    # --- 10. Lighting (Warm studio food lighting) ---
    # Key Light (Warm window light from upper left)
    bpy.ops.object.light_add(type='AREA', location=(-0.45, -0.35, 0.55))
    key_light = bpy.context.active_object
    key_light.name = "KeyLight"
    key_light.data.energy = 45.0
    key_light.data.size = 0.5
    key_light.data.color = (1.0, 0.92, 0.82) # Warm 4500K tint
    key_light.rotation_euler = (math.radians(48), math.radians(-25), math.radians(-35))

    # Rim Light (Back light for edge separation)
    bpy.ops.object.light_add(type='AREA', location=(0.35, 0.4, 0.45))
    rim_light = bpy.context.active_object
    rim_light.name = "RimLight"
    rim_light.data.energy = 25.0
    rim_light.data.size = 0.35
    rim_light.data.color = (0.9, 0.95, 1.0) # Cool rim highlight
    rim_light.rotation_euler = (math.radians(-45), math.radians(30), math.radians(135))

    # Soft Fill Light (Warm gentle fill)
    bpy.ops.object.light_add(type='AREA', location=(0.3, -0.3, 0.3))
    fill_light = bpy.context.active_object
    fill_light.name = "FillLight"
    fill_light.data.energy = 10.0
    fill_light.data.size = 0.6
    fill_light.data.color = (1.0, 0.88, 0.78)

    # --- 11. Camera ---
    bpy.ops.object.camera_add(location=(0.0, -0.42, 0.36))
    cam = bpy.context.active_object
    cam.name = "Camera"
    cam.data.lens = 75 # Cinematic 75mm lens compression
    cam.rotation_euler = (math.radians(48), 0, 0)
    
    # Depth of Field setup
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 0.52
    cam.data.dof.aperture_fstop = 3.2
    
    bpy.context.scene.camera = cam

def render_scene(output_path="entry.png", samples=128, use_cycles=True):
    scene = bpy.context.scene
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.filepath = os.path.abspath(output_path)
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    if use_cycles:
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = samples
        scene.cycles.use_denoiser = False
    else:
        scene.render.engine = 'BLENDER_EEVEE'
        try:
            scene.eevee.taa_render_samples = 64
        except Exception:
            pass

    print(f"Rendering scene using {scene.render.engine} with {samples} samples to {output_path}...")
    bpy.ops.render.render(write_still=True)
    print("Render complete!")

if __name__ == "__main__":
    import sys
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    engine = argv[0] if len(argv) > 0 else "cycles"
    samples = int(argv[1]) if len(argv) > 1 else 96
    output_path = argv[2] if len(argv) > 2 else "entry.png"

    use_cycles = (engine.lower() == "cycles")

    build_scene()
    render_scene(output_path, samples=samples, use_cycles=use_cycles)
