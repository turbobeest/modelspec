# Vendored libraries

The graph explorer loads its JavaScript only from `/graph/vendor/`. The build
copies this directory there. Every file here is byte-identical to the upstream
release named below; the SHA-256 lets anyone check that.

| File | Upstream | Version | Licence | SHA-256 |
|---|---|---|---|---|
| `three.min.js` | https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js | three.js r160 (npm 0.160.0) | MIT | `170c6789f43217c96b3170f4b42fafe135de7f7cd48497a4218f9757ee1d49fa` |
| `3d-force-graph.min.js` | https://cdn.jsdelivr.net/npm/3d-force-graph@1.73.3/dist/3d-force-graph.min.js | 1.73.3 | MIT | `19b3be27040fc894e56d684d53c5f62526c25e5d27f37e8fe91fafff605e4ef4` |

`3d-force-graph` bundles its own copy of three.js and uses the global `THREE`
from `three.min.js` when one is present. The console warning about multiple
instances of three.js comes from that and is harmless.

## Post-processing is not vendored

three.js dropped the non-module `examples/js` files in r148. At r160 the
post-processing passes (`EffectComposer`, `UnrealBloomPass`, `BokehPass`) and
`CSS2DRenderer` exist only as ES modules that import `three` by name, which the
UMD build here cannot satisfy without an import map and a second, module copy
of three.js. The explorer uses cheaper techniques instead: additive halo sprites
on the hub nodes for bloom, scene fog for depth, and HTML labels positioned from
the scene for text.
