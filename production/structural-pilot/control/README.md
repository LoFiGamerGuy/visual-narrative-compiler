# Original structural controls — SC-20260907-01

These are editable geometry and drawing guides, not finished candidate art or evidence of human acceptance. No generative model was called by the control author. Direct paid spend: **$0**.

The active frozen set is **v8 for all seven panels**, with P09/P11/P13/P14 selected by the lead for the raster tests. It fixes the intact staff at 1.683479 m and creates persistent retained/discarded pieces of 0.644127 m and 1.039351 m at P12. The physical shutter partition spans the gallery's full 3.8 m floor width. Every earlier guide remains in its original version directory. A separate **v9/P12** correction is available for inspection; it does not replace any frozen selected input.

Each panel supplies matching-resolution `full`, `background`, `sentinel`, `actors`, `props`, `foreground`, and `effects` PNGs; camera-projected anchor JSON; and editable SVG skeleton/prop/limb lines. `full` and `background` are opaque; the separated passes preserve alpha. The shutter and jambs are in `foreground`: composite this above west-side threat pixels, and explicitly handle any actor/prop overlap. A sentinel-only layer is not an occlusion proof.

Open **v8/scene-all.blend** for seven named panel scenes. The meshes remain separate named objects. `semantic_group` distinguishes architecture, threat, actor guides, props and effects. Sentinel segments carry one of three `limb_id` values. Hand objects carry anatomical side metadata; the right dorsal scrape is a separate red curve group.

The original coordinate source is `v1/scene.json`; `author_scene.py` documents its construction. Small `revise_scene_vN.py` scripts record subsequent explicit changes. Each version's `build_blender.py` is an archival copy of the builder used at that point. The root builder is the active implementation and now refuses to overwrite any directory containing PNGs. To rebuild, copy an existing scene JSON into a **new** version directory and pass that new name:

```text
blender.exe --factory-startup --background --python C:/AgentWorkspaces/anime-pipeline-structural-20260907-054652/production/structural-pilot/control/build_blender.py -- --version NEW_VERSION --passes full background sentinel actors props foreground effects
```

The builder sets its Blender temporary directory to the task-owned `control/runtime/`, reads no external assets, saves no user preferences, and writes outputs only inside the chosen control version. Actual executable used: the existing Blender 5.2.1 LTS Windows installation; exact build metadata and measured render durations appear in each render record.

Run `python -B production/structural-pilot/control/validate_control.py` from the new worktree to verify dimensions, explicit state/anchor facts and source hashes. These checks do not score appeal or prove the final composited pixels.

Known limitations: actor models are coarse pose guides, not mature finished faces/anatomy. The P11 high vault has no roof collision simulation. P12's v8 fragments look almost collinear and the fracture partly hides behind the joint; v9 moves the discarded piece and adds three explicit splinter strokes, while preserving lengths and the retained-piece/joint contact. That exposes separation but does not prove a fully clear impact. P13's solid foreground return partially occludes Nera's far torso edge while leaving her face, supported right hand and held remnant visible.

The source-control verification is separate from final composite review. `mesh-alpha-verification.json` measures the saved Blender geometry and rendered alpha, including a 0.443 m minimum world-space boot/kite clearance and the continuous partition. The preserved `verification-v5v6.json` records earlier unlocked rod lengths and an overly broad framing check that flagged Odo's intentionally cropped hand in the P08 contact close shot; the active checks cover required in-frame hands for each shot and canonical lengths. This is an intentionally small scene controller, with no rig framework, animation engine, downloaded assets or hidden full-frame repaint.
