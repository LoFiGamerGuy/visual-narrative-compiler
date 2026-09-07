"""Build the bounded original pilot scene and editable structural passes.

Run Blender --factory-startup --background --python this_file -- --version v1.
All outputs are task owned. No external assets or protected files are loaded.
"""
import argparse, json, math, sys, time
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--version',default='v1')
parser.add_argument('--panels',nargs='*')
parser.add_argument('--passes',nargs='*',default=['full','background','sentinel','actors','props','foreground'])
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=ROOT/args.version
OUT.mkdir(exist_ok=True)
spec=json.loads((OUT/'scene.json').read_text())
started=time.time()

PALETTE={'ivory':(.79,.78,.69),'stone':(.61,.66,.69),'shadow':(.32,.40,.47),
 'water':(.66,.77,.80),'dark':(.075,.09,.12),'slate':(.22,.25,.32),'slate_light':(.39,.43,.5),
 'violet':(.57,.27,.83),'cyan':(.16,.82,.90),'yellow':(.85,.69,.27),'blue':(.11,.27,.56),
 'skin':(.56,.31,.16),'skin_light':(.72,.45,.26),'hair':(.035,.026,.023),'silver':(.55,.56,.55),
 'wood':(.32,.18,.085),'amber':(.76,.36,.055),'wound':(.66,.035,.04),'white':(.94,.92,.82)}
materials={}
for name,color in PALETTE.items():
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);materials[name]=m

def attach(obj,name,mat,group):
 obj.name=name
 if mat: obj.data.materials.append(materials[mat])
 obj['semantic_group']=group
 return obj

def cube(name,center,size,mat,group):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center)
 o=bpy.context.object;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return attach(o,name,mat,group)

def ellipsoid(name,center,size,mat,group,segments=12,rings=8):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=center)
 o=bpy.context.object;o.scale=size
 return attach(o,name,mat,group)

def segment(name,a,b,radius,mat,group,radius2=None,vertices=10):
 a,b=Vector(a),Vector(b);d=b-a
 if d.length<1e-6:return None
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius if radius2 is None else radius2,depth=d.length,location=(a+b)/2)
 o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
 return attach(o,name,mat,group)

def mesh(name,verts,faces,mat,group):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
 return attach(o,name,mat,group)

def line(name,points,radius,mat,group):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=1;data.resolution_u=1
 poly=data.splines.new('POLY');poly.points.add(len(points)-1)
 for p,co in zip(poly.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
 return attach(o,name,mat,group)

def architecture(panel):
 cube('gallery.exterior_ivory_field',(4.0,2.80,2.5),(24,.12,13),'white','background')
 cube('gallery.floor',(4.25,0,-.12),(10.5,3.8,.20),'ivory','background')
 cube('gallery.shallow_water',(3.0,0,.012),(7.9,3.65,.035),'water','background')
 cube('gallery.dry_ridge',(4.15,0,.07),(10.0,1.08,.12),'ivory','background')
 cube('gallery.north_sill',(3.10,1.77,.28),(7.1,.28,.55),'stone','background')
 cube('gallery.north_lintel',(3.15,1.77,3.33),(7.2,.34,.25),'ivory','background')
 for x in [0,2.15,4.3,6.55]:
  cube('gallery.pillar.%s'%x,(x,1.76,1.80),(.26,.38,3.15),'stone','background')
  cube('gallery.pillar_foot.%s'%x,(x,1.76,.37),(.46,.53,.24),'shadow','background')
 for x in [-.4,.5,1.4,2.3,3.2,4.1,5.0,5.9,6.8,7.7,8.6]:
  line('ridge.joint.%s'%x,[[x,-.53,.132],[x,.53,.132]],.007,'shadow','background')
 # Shutter is a real X-normal plane. South wall is cut away to expose both sides.
 shutter_x=spec['gallery']['shutter_x']
 cube('shutter.north_jamb',(shutter_x,1.65,1.7),(.35,.32,3.4),'stone','foreground')
 cube('shutter.south_cutaway_jamb',(shutter_x,-1.1,1.7),(.35,.21,3.4),'stone','foreground')
 cube('shutter.header',(shutter_x,.27,3.4),(.4,3.0,.28),'stone','foreground')
 bottom=panel['shutter_bottom'];height=3.3-bottom
 cube('shutter.blade',(shutter_x,.27,bottom+height/2),(.16,2.54,height),'shadow','foreground')
 cube('shutter.bottom_contact_edge',(shutter_x,.27,bottom+.06),(.23,2.54,.12),'dark','foreground')
 for z in [bottom+.24+i*.23 for i in range(int(height/.23))]:
  for side in [-1,1]:
   line('shutter.slats.%s.%s'%(z,side),[[shutter_x+side*.083,-1.0,z],[shutter_x+side*.083,1.54,z]],.008,'stone','foreground')
 # One continuous mechanical line connects west pulley to east overhead pulley.
 line('cable.overhead',[[.85,.5,3.33],[6.7,.5,3.33]],.022,'wood','background')
 for x in [.85,6.7]:
  segment('cable.pulley.%s'%x,[x,.43,3.33],[x,.57,3.33],.125,'dark','background',vertices=20)
 if panel['cable_hand']:
  a,hand=panel['cable_hand'].split('.')
  grip=panel[a]['joints'][hand]
  line('cable.west_control_to_hand',[[.85,.5,3.33],grip],.026,'wood','props')
  line('cable.trailing_end',[grip,[grip[0]-.13,grip[1]+.08,.26]],.022,'wood','props')
 else:
  line('cable.released_west_end',[[.85,.5,3.33],[.85,.5,.22]],.022,'wood','background')

def adult(name,data):
 j={k:Vector(v) for k,v in data['joints'].items()}
 cloth='yellow' if name=='nera' else 'blue'
 torso_color='dark' if name=='nera' else 'blue'
 group='actors'
 hip,chest=j['hip'],j['chest']
 # Mesh torso has explicit shoulder/waist widths and front/back depth.
 verts=[]
 for center,halfwidth,depth in [(hip,.18,.115),(chest,.26 if name=='odo' else .22,.14)]:
  for dx,dy in [(-depth,-halfwidth),(depth,-halfwidth),(depth,halfwidth),(-depth,halfwidth)]:verts.append(tuple(center+Vector((dx,dy,0))))
 mesh(name+'.torso',verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],torso_color,group)
 segment(name+'.neck',j['neck']-Vector((0,0,.10)),j['neck']+Vector((0,0,.075)),.076,'skin',group)
 for side in ['right','left']:
  shoulder,elbow,hand=(j[side+'_'+k] for k in ['shoulder','elbow','hand'])
  segment(name+'.'+side+'.upper_arm',shoulder,elbow,.10 if name=='odo' else .083,torso_color,group,.08)
  segment(name+'.'+side+'.forearm',elbow,hand,.079,torso_color,group,.052)
  ellipsoid(name+'.'+side+'.elbow',elbow,(.081,.081,.081),torso_color,group)
  if name=='odo':segment(name+'.'+side+'.cream_cuff',hand+(elbow-hand)*.18,hand,.075,'ivory',group,.065)
  hand_obj=ellipsoid(name+'.'+side+'_hand',hand,(.08,.065,.095),'skin_light',group)
  hand_obj['anatomical_side']=side
  hipj,knee,ankle=(j[side+'_'+k] for k in ['hip','knee','ankle'])
  segment(name+'.'+side+'.thigh',hipj,knee,.115,'dark',group,.088)
  segment(name+'.'+side+'.shin',knee,ankle,.089,'dark',group,.063)
  ellipsoid(name+'.'+side+'.knee',knee,(.087,.087,.087),'dark',group)
  toe=ankle+Vector(data['facing'])*.09-Vector((0,0,.055))
  ellipsoid(name+'.'+side+'.boot',toe,(.155,.09,.082),'dark',group)
 head=j['head']; gaze=Vector(data['gaze'])-head;gaze.normalize()
 right=gaze.cross(Vector((0,0,1))).normalized();up=right.cross(gaze).normalized()
 def hp(x,y,z):return head+right*x+gaze*y+up*z
 ho=ellipsoid(name+'.adult_head',head,(.135,.135,.194),'skin_light',group,16,10)
 ho.rotation_euler=gaze.to_track_quat('-Y','Z').to_euler()
 for side in [-1,1]:
  ellipsoid(name+'.ear.'+str(side),hp(side*.136,0,-.015),(.032,.035,.049),'skin',group)
  eye=ellipsoid(name+'.eye.'+str(side),hp(side*.060,.125,.035),(.035,.017,.020),'white',group)
  eye.rotation_euler=ho.rotation_euler
  ellipsoid(name+'.pupil.'+str(side),hp(side*.060,.141,.035),(.012,.012,.016),'dark',group)
  line(name+'.brow.'+str(side),[hp(side*.092,.129,.074),hp(side*.030,.138,.065)],.012,'hair',group)
 mesh(name+'.nose',[tuple(hp(-.027,.12,.045)),tuple(hp(.027,.12,.045)),tuple(hp(0,.196,-.019)),tuple(hp(0,.12,-.035))],[(0,1,2),(0,2,3),(1,3,2)],'skin',group)
 line(name+'.mouth',[hp(-.042,.133,-.083),hp(0,.147,-.078),hp(.038,.131,-.079)],.008,'wood',group)
 hair='hair' if name=='nera' else 'silver'
 ellipsoid(name+'.hair_cap',head+up*.085-gaze*.022,(.147,.146,.142),hair,group)
 if name=='nera':
  for index,(xx,yy,zz) in enumerate([(-.09,.06,.13),(.09,.05,.14),(0,.08,.18),(-.12,-.02,.08),(.12,-.02,.08),(0,-.09,.14)]):
   ellipsoid(name+'.curl.'+str(index),hp(xx,yy,zz),(.057,.055,.055),hair,group)
  # Asymmetric cape extends behind the movement; mesh remains independently editable.
  s=j['left_shoulder'];r=j['right_shoulder'];tail=hip+Vector((-.43,.28,.03))
  mesh(name+'.asymmetric_cape',[tuple(r+Vector((0,0,.06))),tuple(s+Vector((0,0,.06))),tuple(tail),tuple(hip+Vector((-.20,-.22,.20))),tuple(chest+Vector((.17,-.25,-.14)))],[(0,1,2,3),(0,3,4)],'yellow',group)
  segment(name+'.cape_clasp',r+Vector((.015,-.015,-.035)),r+Vector((.06,-.035,-.035)),.038,'ivory',group)
 else:
  segment(name+'.cream_shirt',hip+Vector((.128,0,.08)),chest+Vector((.16,0,.06)),.10,'ivory',group,.11,vertices=4)

def sentinel(data):
 c=Vector(data['center']);yaw=math.radians(data['yaw'])
 def pos(p):
  x,y,z=p;return tuple(c+Vector((x*math.cos(yaw)-y*math.sin(yaw),x*math.sin(yaw)+y*math.cos(yaw),z)))
 verts=[pos(p) for p in [(0,0,.64),(-.73,-.07,0),(0,-.29,-.53),(.73,-.07,0),(0,.35,0)]]
 mesh('sentinel.kite_body',verts,[(0,1,2),(0,2,3),(0,4,1),(0,3,4),(1,4,2),(2,4,3)],'slate','sentinel')
 line('sentinel.single_violet_gill',[pos((-.36,-.21,-.02)),pos((.35,-.21,-.02))],.026,'violet','sentinel')
 for name,chain in data['limbs'].items():
  for i,(a,b) in enumerate(zip(chain,chain[1:])):
   ob=segment('sentinel.'+name+'.segment'+str(i),a,b,.10 if i==0 else .068,'slate_light','sentinel',.07 if i==0 else .045,vertices=5)
   ob['limb_id']=name
  for i,p in enumerate(chain[:-1]):ellipsoid('sentinel.'+name+'.joint'+str(i),p,(.13,.13,.13),'slate','sentinel')
  foot=Vector(chain[-1]); direction=(foot-Vector(chain[-2]));direction.z=0;direction.normalize()
  side=Vector((-direction.y,direction.x,0)); tip=foot+direction*.20
  mesh('sentinel.'+name+'.foot',[tuple(foot+side*.12+Vector((0,0,.05))),tuple(foot-side*.12+Vector((0,0,.05))),tuple(tip-Vector((0,0,.065))),tuple(foot+Vector((0,0,.15)))],[(0,1,2),(0,3,1),(1,3,2),(2,3,0)],'slate','sentinel')

def props(panel):
 for i,(a,b) in enumerate(panel['staff']['segments']):
  segment('staff.fragment_'+str(i) if panel['staff']['state']=='broken' else 'staff.intact',a,b,.033,'wood','props',vertices=10)
  if panel['staff']['state']=='broken':
   end=Vector(b if i==0 else a);d=(Vector(a)-Vector(b)).normalized()
   for k in range(3):
    offset=Vector((0,math.sin(k*2.1)*.025,math.cos(k*2.1)*.025))
    segment('staff.fracture_splinter_%s_%s'%(i,k),end+offset,end+offset-d*(.055+.015*k),.012,'ivory','props',.004,vertices=5)
 loc=Vector(panel['flask']['location'])
 segment('flask.single_sealed_body',loc-Vector((0,0,.095)),loc+Vector((0,0,.09)),.062,'amber','props',vertices=12)
 segment('flask.single_sealed_cap',loc+Vector((0,0,.09)),loc+Vector((0,0,.124)),.065,'silver','props',vertices=12)
 if panel['injury']:
  hand=Vector(panel['nera']['joints']['right_hand'])
  for i in range(3):
   a=hand+Vector((-.030+i*.020,-.066,.025));b=a+Vector((.017,-.003,-.04))
   wound=line('nera.right_hand.dorsal_scrape.'+str(i),[a,b],.0075,'wound','props');wound['anatomical_side']='right'
 for fx in panel['effects']:
  line('effect.'+fx['id'],fx['points'],.018,fx['color'],'effects')
  # Single triangular terminal accent; no duplicated character silhouettes.
  end=Vector(fx['points'][-1]);before=Vector(fx['points'][-2]);d=(end-before).normalized();side=d.cross(Vector((0,1,0))).normalized()
  mesh('effect.'+fx['id']+'.tip',[tuple(end),tuple(end-d*.18+side*.06),tuple(end-d*.18-side*.06)],[(0,1,2)],fx['color'],'effects')
 if 'air_brake_arrival' in [fx['id'] for fx in panel['effects']]:
  for i in range(3):
   x=3.52+i*.12
   line('effect.braking_tick.'+str(i),[[x,-.70,3.43],[x+.18,-.7,3.05]],.023,'cyan','effects')

def projection(scene,point):
 p=world_to_camera_view(scene,scene.camera,Vector(point));w,h=scene.render.resolution_x,scene.render.resolution_y
 return {'normalized':[round(p.x,6),round(1-p.y,6)],'pixel':[round(p.x*w,2),round((1-p.y)*h,2)],'depth':round(p.z,5),'inside_frame':0<=p.x<=1 and 0<=p.y<=1 and p.z>0}

def export_anchors(scene,panel_id,panel):
 points={}
 for actor in ['nera','odo']:
  for joint,p in panel[actor]['joints'].items():points[actor+'.'+joint]=projection(scene,p)
 for name,chain in panel['sentinel']['limbs'].items():
  for i,p in enumerate(chain):points['sentinel.'+name+'.'+str(i)]=projection(scene,p)
 for i,(a,b) in enumerate(panel['staff']['segments']):
  points['staff.segment%s.a'%i]=projection(scene,a);points['staff.segment%s.b'%i]=projection(scene,b)
 points['flask.center']=projection(scene,panel['flask']['location'])
 points['required_contact']=projection(scene,panel['contact']['point'])
 points['shutter.bottom']=projection(scene,[6.7,0,panel['shutter_bottom']])
 data={'panel':panel_id,'status':'GEOMETRY_ONLY_NOT_SEMANTIC_ACCEPTANCE','resolution':[scene.render.resolution_x,scene.render.resolution_y],
  'camera':panel['camera'],'anatomy_note':spec['anatomy'],'contact':panel['contact'],'anchors':points}
 (OUT/(panel_id+'-anchors.json')).write_text(json.dumps(data,indent=2)+'\n')
 w,h=data['resolution'];svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<title>Editable structural lines; not finished art</title>']
 def path(name,coords,color,width=4):
  pts=[projection(scene,p)['pixel'] for p in coords]
  svg.append(f'<polyline id="{name}" points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
 for actor,col in [('nera','#bb991d'),('odo','#2159a0')]:
  j=panel[actor]['joints'];path(actor+'.spine',[j[k] for k in ['hip','chest','neck','head']],col)
  for side in ['right','left']:
   for chain in [['shoulder','elbow','hand'],['hip','knee','ankle']]:path(actor+'.'+side+'.'+chain[0],[j[side+'_'+k] for k in chain],col)
 for name,chain in panel['sentinel']['limbs'].items():path('sentinel.'+name,chain,'#63527f',7)
 for i,seg in enumerate(panel['staff']['segments']):path('staff.segment'+str(i),seg,'#513422',7)
 for i in [-1,1]:path('shutter.edge'+str(i),[[6.7,i,3.3],[6.7,i,panel['shutter_bottom']]],'#404e5c',5)
 x,y=points['required_contact']['pixel'];svg.append(f'<circle id="required_contact" cx="{x}" cy="{y}" r="17" fill="none" stroke="#d03939" stroke-width="4"/>')
 svg.append('</svg>');(OUT/(panel_id+'-projected-lines.svg')).write_text('\n'.join(svg)+'\n')

PASS_GROUPS={'full':{'background','foreground','sentinel','actors','props','effects'},'background':{'background'},
 'sentinel':{'sentinel'},'actors':{'actors'},'props':{'props'},'foreground':{'foreground'},'effects':{'effects'}}
manifest={'schema':'StructuralPassManifest/1','experiment':spec['experiment'],'version':args.version,'start_epoch':started,
 'blender_version':bpy.app.version_string,'blender_build_hash':bpy.app.build_hash.decode(),'direct_paid_spend_usd':0,
 'status':'UNACCEPTED_STRUCTURAL_CONTROLS_NOT_FINISHED_ART','panels':{}}
bpy.context.preferences.filepaths.temporary_directory=str(ROOT/'runtime')
for panel_id,panel in spec['panels'].items():
 if args.panels and panel_id not in args.panels:continue
 scene=bpy.data.scenes.new(panel_id)
 bpy.context.window.scene=scene
 scene.render.engine='BLENDER_WORKBENCH'
 scene.render.resolution_x,scene.render.resolution_y=panel['resolution'];scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
 scene.render.film_transparent=True
 scene.display.shading.light='FLAT';scene.display.shading.color_type='MATERIAL'
 scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False
 scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=.6
 scene.display.shading.show_object_outline=True;scene.display.shading.object_outline_color=(.045,.052,.063)
 scene.display.shading.background_type='WORLD'
 scene.world=bpy.data.worlds.new(panel_id+'.world');scene.world.color=(.92,.92,.89)
 scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [i.name for i in scene.view_settings.bl_rna.properties['look'].enum_items] else 'None'
 architecture(panel);sentinel(panel['sentinel']);adult('nera',panel['nera']);adult('odo',panel['odo']);props(panel)
 camera_data=bpy.data.cameras.new(panel_id+'.camera');camera=bpy.data.objects.new(panel_id+'.camera',camera_data);scene.collection.objects.link(camera)
 camera.location=panel['camera']['location'];target=Vector(panel['camera']['target']);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
 camera_data.type=panel['camera'].get('type','ORTHO');camera_data.ortho_scale=panel['camera']['ortho'];camera_data.lens=panel['camera'].get('lens',42);camera_data.clip_end=100;scene.camera=camera
 bpy.context.view_layer.update();export_anchors(scene,panel_id,panel)
 manifest['panels'][panel_id]={'passes':[],'objects':len(scene.objects),'resolution':panel['resolution'],'camera':panel['camera']}
 for pass_name in args.passes:
  groups=PASS_GROUPS[pass_name]
  for obj in scene.objects:
   if obj.type!='CAMERA':obj.hide_render=obj.get('semantic_group') not in groups
  scene.render.filepath=str(OUT/(panel_id+'-'+pass_name+'.png'))
  bpy.ops.render.render(write_still=True)
  manifest['panels'][panel_id]['passes'].append(panel_id+'-'+pass_name+'.png')
 for obj in scene.objects:obj.hide_render=False
 print('CONTROL_PANEL_COMPLETE',panel_id,flush=True)
manifest['elapsed_seconds']=round(time.time()-started,2)
out_suffix='-'.join(args.panels) if args.panels else 'all'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('scene-'+out_suffix+'.blend')))
(OUT/('render-record-'+out_suffix+'.json')).write_text(json.dumps(manifest,indent=2)+'\n')
print('STRUCTURAL_CONTROL_COMPLETE',OUT,flush=True)
