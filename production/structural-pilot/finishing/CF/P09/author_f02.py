"""One declared correction round: preserve source shaft texture and most original toe."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[5]
P=Path('production/structural-pilot/finishing/CF/P09/F02')
s=json.loads((ROOT/'production/structural-pilot/finishing/CF/P09/F01/spec.json').read_text())
source=s['layers'][0]['path'];s['id']='CF-P09-F02';s['output_svg']=str(P/'P09-F02.svg')
s['description']='Declared conventional correction of F01: original-source wood texture follows continuous shaft axis, most original toe retained, small shaded raised metal lip receives endpoint. Actual-art review pending.'
s['defs_svg']+='''<clipPath id="wood-extension" clipPathUnits="userSpaceOnUse"><path d="M891 737 L918 754 L924 760 L923 765 L918 771 L887 752 Z"/></clipPath>'''
metal='''<path d="M891 758 L909 761 L918 757 Q922 757 924 762 L927 776 L929 780 L912 779 L898 776 L887 769 Z" fill="#333d45" stroke="#1b2328" stroke-width="1.7" stroke-linejoin="round"/>
<path d="M893 759 L909 764 L918 760 L921 763 L919 769 L902 767 Z" fill="#535e64"/>
<path d="M891 769 L908 774 L926 778 L913 778 L897 775 Z" fill="#222c34"/>
<path d="M897 761 L906 764 M912 763 L917 761" fill="none" stroke="#7b8588" stroke-width=".8"/>
<path d="M903 769 l4 1 M911 772 l4 1 M919 774 l3 1 M896 771 l2 1 M916 767 l2 1" fill="none" stroke="#1b242a" stroke-width=".7"/>
'''
end='''<path d="M918 757 Q923 759 923 763 L919 769 L916 767 L918 763 Z" fill="#997345" stroke="#29251b" stroke-width="1.1"/>
<path d="M919 760 L921 762 L919 766 M918 762 l1 1" fill="none" stroke="#60462d" stroke-width=".8"/>
<path d="M923 761 L924 766 L920 770" fill="none" stroke="#172126" stroke-width="1.7" stroke-linecap="round"/>
<path d="M930 781 l4 1 M927 773 l5 -1 M913 783 l-1 3" fill="none" stroke="#504e43" stroke-width="1.1" stroke-linecap="round"/>
'''
s['layers']=s['layers'][:2]+[{'id':'small-raised-toe-lip','svg':metal,'kind':'editable-local-metal-contour'}, {'id':'continuous-source-wood-texture','path':source,'x':28,'y':18.2,'width':1430,'height':1100,'clip':'wood-extension','kind':'explicit-source-clone'}, {'id':'wood-end-and-metal-contact','svg':end,'kind':'editable-local-contact-ink'}]
s['edit_intent']={'contact_pixel':[923,765],'correction_of':'CF-P09-F01','source_wood_translation':[28,18.2],'retains_original_joint_and_most_toe':True,'changes':'Remove abrupt F01 collar and broadened flat toe; keep correction local and exact input immutable.'}
with (ROOT/P/'spec.json').open('x') as f:f.write(json.dumps(s,indent=2)+'\n')
