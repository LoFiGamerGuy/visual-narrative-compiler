#!/usr/bin/env python3
"""Render original SVG controls with installed librsvg/Cairo, no raster editing."""
from pathlib import Path
import ctypes as c,ctypes.util,json,hashlib,struct,datetime
HERE=Path(__file__).resolve().parent
rsvg=c.CDLL(ctypes.util.find_library('rsvg-2'));cairo=c.CDLL(ctypes.util.find_library('cairo'));go=c.CDLL(ctypes.util.find_library('gobject-2.0'))
rsvg.rsvg_handle_new_from_file.argtypes=[c.c_char_p,c.POINTER(c.c_void_p)];rsvg.rsvg_handle_new_from_file.restype=c.c_void_p
rsvg.rsvg_handle_render_cairo.argtypes=[c.c_void_p,c.c_void_p];rsvg.rsvg_handle_render_cairo.restype=c.c_int
cairo.cairo_image_surface_create.argtypes=[c.c_int,c.c_int,c.c_int];cairo.cairo_image_surface_create.restype=c.c_void_p
cairo.cairo_create.argtypes=[c.c_void_p];cairo.cairo_create.restype=c.c_void_p
cairo.cairo_surface_write_to_png.argtypes=[c.c_void_p,c.c_char_p];cairo.cairo_surface_write_to_png.restype=c.c_int
cairo.cairo_destroy.argtypes=[c.c_void_p];cairo.cairo_surface_destroy.argtypes=[c.c_void_p];go.g_object_unref.argtypes=[c.c_void_p]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((HERE/'v5-sword-continuity/manifest.json').read_text());rows=[]
for row in manifest['records']:
 svg=HERE/row['svg'];png=svg.with_suffix('.png')
 if png.exists():raise FileExistsError('Preserve existing PNG')
 if sha(svg)!=row['svg_sha256']:raise ValueError('Editable source changed')
 error=c.c_void_p();handle=rsvg.rsvg_handle_new_from_file(str(svg).encode(),c.byref(error))
 if not handle:raise RuntimeError('librsvg could not read SVG')
 surface=cairo.cairo_image_surface_create(0,1200,800);context=cairo.cairo_create(surface)
 try:
  if not rsvg.rsvg_handle_render_cairo(handle,context):raise RuntimeError('SVG render failed')
  if cairo.cairo_surface_write_to_png(surface,str(png).encode()):raise RuntimeError('PNG write failed')
 finally:cairo.cairo_destroy(context);cairo.cairo_surface_destroy(surface);go.g_object_unref(handle)
 if struct.unpack('>II',png.read_bytes()[16:24])!=(1200,800):raise ValueError('Wrong raster dimensions')
 rows.append({'id':row['id'],'svg':row['svg'],'source_sha256':sha(svg),'png':str(png.relative_to(HERE)),'sha256':sha(png),'width':1200,'height':800})
receipt={'schema':'CombatDepthNativeSvgRendering/1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'renderer':'Installed librsvg-2 + Cairo via ctypes; original SVG-to-PNG conversion, no existing raster edits','script_sha256':sha(Path(__file__)),'rendered':rows,'visual_acceptance':'Pending actual image inspection'}
with (HERE/'v5-sword-continuity/render-receipt-native.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'rendered':len(rows),'renderer':receipt['renderer']}))
