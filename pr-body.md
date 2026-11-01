## Docs
- README reorganised for users: where to go next, what to download, try your first prediction, the dataset, how the blocks work, use your own model, if it does not run, learn more, a short section for supporters.
- Learning guide, training/export guide and a developer guide (component overview, files, build, checks, release, native packaging, model contract, troubleshooting).
- New generated block reference: a picture of every call and event block plus a table of each parameter, built from components.json by scripts/make_block_reference.py and run in CI.
- Removed "unverified on device" and "not official" wording throughout.

## Fruit app screen
- Numbered steps, result card with status, "What is running on this phone" card filled from ModelLoaded, "Learn more" links with one-line descriptions, photo attribution footer.

## Repository
- Iris and add-one smoke examples removed from examples/, models/, scripts/, CI and the notices. verify.py and the release step simplified to the fruit project.

verify_fruit.py and the Python unit tests pass locally; CI runs the full set.
