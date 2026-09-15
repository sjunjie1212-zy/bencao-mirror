# Visual asset import bridge

`main/images/` is the only authoritative store for formal Ben Cao Mirror visual assets.

This directory is only a transient binary-ingest bridge for ChatGPT/session-generated assets that cannot be written directly through the GitHub connector.

## Import behavior

1. Upload a validated ZIP package into `asset-import/`.
2. `.github/workflows/import-visual-assets.yml` unpacks the package into the repository.
3. The workflow moves `ASSET_IMPORT_MANIFEST.csv` into `images/_manifests/`.
4. The import ZIP is deleted.
5. GitHub Actions commits the resulting formal assets to `main/images/`.

Session/local files are never authoritative and should be treated only as transient transfer files.

## Pending migration package

BC.041–BC.045 formal AVIF package prepared 2026-09-15:

- expected file name: `bc041-bc045-formal.zip`
- formal images: 35
- herbs: BC.041–BC.045
- SHA-256: `6e3e554d154762a9338297e01ab6a15a1a9bc99439e7ad246e22baab890704e5`
- archive validation: passed
