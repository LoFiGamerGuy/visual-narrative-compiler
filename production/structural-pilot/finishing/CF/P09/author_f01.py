"""Explicit conventional drawing of P09 foot contact; no generation or inpainting."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[5]
P=Path('production/structural-pilot/finishing/CF/P09/F01')
source='production/structural-pilot/candidates/C00010-f617453f42669035.png'
# The patch samples the same dry paving/channel boundary 180px east and43px up.
# Clip coordinates are output pixels; no third-party texture or hidden image source.
patch='M899 744 L941 742 L974 759 L997 788 L990 817 L955 829 L917 815 L899 790 Z'
metal='''<path d="M860 746 L872 748 L904 758 L923 764 L928 781 L900 779 L866 773 Z" fill="#333b40" stroke="#171d21" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M867 749 L903 761 L922 766 L919 771 L887 763 L867 758 Z" fill="#596065"/>
<path d="M867 762 L898 773 L925 779 L900 778 L868 772 Z" fill="#242c32"/>
<path d="M875 752 L895 758 M902 760 L914 764" fill="none" stroke="#89908e" stroke-width="1.2"/>
<path d="M879 762 L886 765 M891 763 L897 766 M906 774 L913 775 M874 766 L878 769" fill="none" stroke="#151b20" stroke-width="1"/>
'''
wood='''<path d="M896 748 L918 763 Q921 766 918 770 L914 772 L891 757 Z" fill="#8f663c" stroke="#201d17" stroke-width="2"/>
<path d="M897 750 L916 763 L915 766 L894 755 Z" fill="#b99059"/>
<path d="M894 756 L914 769 L915 771 L893 758 Z" fill="#5d422b"/>
<path d="M916 763 Q921 766 918 770 L914 772 L914 768 Z" fill="#c5a471" stroke="#342b20" stroke-width="1.1"/>
<path d="M916 766 L918 768 M915 769 L917 770" stroke="#795b38" stroke-width=".8"/>
'''
contact='''<path d="M918 765 L920 769 L917 773" fill="none" stroke="#12191d" stroke-width="2.3" stroke-linecap="round"/>
<path d="M925 786 l7 2 M928 777 l7 -1 M913 787 l-1 4" fill="none" stroke="#504e43" stroke-width="1.4" stroke-linecap="round"/>
'''
spec={'id':'CF-P09-F01','width':1430,'height':1100,'output_svg':str(P/'P09-F01.svg'),'description':'Conventional source-bound floor cloning removes disconnected impact spark and extra shaft tip. Editable drawn foretoe facets and shortened wooden endpoint meet at explicit contact. Agent-authored; actual-art review pending.','defs_svg':'<clipPath id="floor-repair" clipPathUnits="userSpaceOnUse"><path d="'+patch+'"/></clipPath>', 'layers':[
{'id':'unchanged-generated-source','path':source,'sha256':'f617453f4266903532138003a78d0dac770683d8928651173211d1252e5651ef','kind':'preserved-generated-raster'},
{'id':'local-paving-clone','path':source,'x':-180,'y':43,'width':1430,'height':1100,'clip':'floor-repair','kind':'explicit-source-clone'},
{'id':'foretoe-structure','svg':metal,'kind':'editable-drawn-metal'},
{'id':'wooden-contact-end','svg':wood,'kind':'editable-drawn-wood'},
{'id':'contact-seam-and-ground-pressure','svg':contact,'kind':'editable-local-contact-ink'}],
'edit_intent':{'contact_pixel':[918,769],'old_gap_preserved_in_source':True,'floor_clone_translation':[-180,43],'changes':'Local tip/toe contour and contact only; no body/camera/limb-count/ownership changes.'}}
out=ROOT/P/'spec.json'
with out.open('x') as f:f.write(json.dumps(spec,indent=2)+'\n')
print(out.relative_to(ROOT))
