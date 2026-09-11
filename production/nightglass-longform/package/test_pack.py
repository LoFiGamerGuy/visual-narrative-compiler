"""Focused regression checks for portable case-alias inventories."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


def load(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pack=load('pack')
verifier=load('verify_package')


class CaseAliasRegression(unittest.TestCase):
    def test_same_file_alias_has_one_manifest_entry_and_strict_extraction_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            folder=root/'production/test'
            folder.mkdir(parents=True)
            canonical=folder/'Daro.png'
            canonical.write_bytes(b'unchanged native stand-in')
            alias=folder/'daro.png'
            record=folder/'reference.json'
            original=json.dumps({'path':'production/test/daro.png'})
            record.write_text(original)
            real_is_file=Path.is_file
            real_samefile=Path.samefile

            # Simulate only NTFS's same-file alias lookup on a case-sensitive
            # test host; directory enumeration keeps the real uppercase name.
            def is_file(path):
                return real_is_file(canonical if path==alias else path)

            def samefile(path,other):
                return real_samefile(canonical if path==alias else path,
                                     canonical if Path(other)==alias else other)

            with patch.object(pack,'SEED_ROOTS',('production/test',)), \
                 patch.object(pack,'EXTRA_FILES',()), \
                 patch.object(Path,'is_file',is_file), \
                 patch.object(Path,'samefile',samefile):
                plan=pack.collect(root)
                self.assertEqual(plan['files'],['production/test/Daro.png','production/test/reference.json'])
                self.assertEqual(plan['total_bytes'],len(canonical.read_bytes())+len(record.read_bytes()))
                self.assertEqual(len(plan['case_aliases']),1)
                self.assertEqual(plan['case_aliases'][0],{
                    'from':'production/test/reference.json','path':'production/test/daro.png',
                    'canonical_path':'production/test/Daro.png','same_file_verified':True,
                    'sha256':pack.digest(canonical),'bytes':canonical.stat().st_size})
                with patch.object(pack,'gate',return_value=[]):
                    built=pack.build(root,'CaseAlias-v1','trial',root/'output')
            extracted,manifest=verifier.extract(Path(built['zip']),root/'verification')
            with zipfile.ZipFile(built['zip']) as archive:
                self.assertEqual(len(archive.infolist()),built['file_count'])
            self.assertEqual(len(manifest['files'])+1,built['file_count'])
            self.assertEqual(manifest['case_aliases'],plan['case_aliases'])
            self.assertEqual((extracted/'production/test/Daro.png').read_bytes(),canonical.read_bytes())
            self.assertEqual((extracted/'production/test/reference.json').read_text(),original)
            self.assertEqual(record.read_text(),original)

    def test_distinct_case_colliding_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            folder=root/'production/test'
            folder.mkdir(parents=True)
            first=folder/'Daro.png'; second=folder/'daro.png'
            first.write_bytes(b'first')
            second.write_bytes(b'different')
            if first.samefile(second):
                self.skipTest('Distinct-file collision requires a case-sensitive test directory')
            with patch.object(pack,'SEED_ROOTS',('production/test',)),patch.object(pack,'EXTRA_FILES',()):
                with self.assertRaisesRegex(RuntimeError,'Case-colliding source files'):
                    pack.collect(root)


if __name__=='__main__':
    unittest.main()
