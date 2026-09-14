# Visual Asset Storage Policy

GitHub is the single source of truth for formal Ben Cao Mirror visual assets.

## Authoritative location

- Repository: `sjunjie1212-zy/bencao-mirror`
- Branch: `main`
- Formal asset directory: `images/`
- Asset index: `images/ASSET_INDEX.md`

## Formal asset rule

Each herb has exactly seven formal visual assets:

1. Hero × 1
2. Specimen Plate × 1
3. Detail × 5

An image is not a formal asset until it has been committed to GitHub under the correct BC number and herb identity.

## Generation workflow

New images may exist transiently during generation or conversion, but local/session files are not an archive and are not authoritative. After validation, the approved assets must be committed to `images/` and the GitHub manifest/index updated. Downstream agents should read formal assets from GitHub, not from local ChatGPT session storage.

## Naming

Preferred naming:

- `bcXXX-<pinyin>-hero-v1.avif`
- `bcXXX-<pinyin>-specimen-v1.avif`
- `bcXXX-<pinyin>-detail-01-v1.avif` … `detail-05-v1.avif`

Legacy formal files already in the repository may retain their existing names until deliberately migrated.
