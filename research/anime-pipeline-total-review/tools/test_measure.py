import tempfile,unittest
from pathlib import Path
from measure import leaf,sha,summary,image_metrics
from PIL import Image
import io

class EvidenceSemantics(unittest.TestCase):
 def test_wrapper_novelty_does_not_hide_same_source(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'.scratch')as tmp:
   p=Path(tmp);im=Image.new('RGB',(20,30),'white');im.save(p/'source.png')
   for name,label in [('a','First dialogue'),('b','Completely different text')]:
    (p/f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg"><image href="source.png"/><text>{label}</text></svg>')
   self.assertNotEqual(sha((p/'a.svg').read_bytes()),sha((p/'b.svg').read_bytes()))
   self.assertEqual(sha(leaf(p/'a.svg')[1]),sha(leaf(p/'b.svg')[1]))
 def test_nested_cycle_and_missing_art_are_not_passes(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'.scratch')as tmp:
   p=Path(tmp);(p/'loop.svg').write_text('<svg><image href="loop.svg"/></svg>')
   with self.assertRaises(ValueError):leaf(p/'loop.svg')
   with self.assertRaises(FileNotFoundError):leaf(p/'missing.png')
 def test_held_panel_is_reported_as_reuse_not_double_generated(self):
  buf=io.BytesIO();Image.new('RGB',(20,30),'white').save(buf,format='PNG');data=buf.getvalue();m=image_metrics(data)
  rows=[{'id':i,'sha256':sha(data),'source_bytes':len(data),**m}for i in ['a','b']]
  s=summary(rows);self.assertEqual(s['unique_source_hashes'],1);self.assertEqual(s['exact_reuse_pct'],50)
  self.assertEqual(s['near_duplicate_pairs_excluding_exact'],[])
 def test_dark_proxy_is_not_aesthetic_score(self):
  buf=io.BytesIO();Image.new('RGB',(20,30),'black').save(buf,format='PNG');m=image_metrics(buf.getvalue())
  self.assertEqual(m['dark_pixel_pct'],100);self.assertEqual(m['edge_over24_pct'],0);self.assertNotIn('quality',m)

if __name__=='__main__':unittest.main()
