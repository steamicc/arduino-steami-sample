# arduino-steami-sample

Arduino sketches for the [STeaMi](https://github.com/steamicc) board, in French.
They are the source of the sketches shown in the
[STeaMi wiki](https://github.com/steamicc/wiki_steami): every sketch is
compiled here with `arduino-cli`, and each release publishes the compiled
binaries as an archive that the wiki uses for its **Téléverser** (upload)
button.

## Layout

```text
examples/
  <GROUP>/
    <Name>/
      <Name>.ino
```

- One folder per sketch; the `.ino` file has the name of its folder (an
  Arduino requirement).
- The wiki identifies a sketch as `GROUP/Name` (for example
  `BOUTONS/LedsBoutons`): the group is in upper case, the name is CamelCase.
- Groups: `CAPTEURS`, `ECRAN`, `PREMIERS`, `CARTE`, `BOUTONS`, `BUZZER`, `BLE`.
- `versions.json` is the single place that names the toolchain: STM32 core,
  board (FQBN), STM32duinoBLE and STeaMi library versions.
  Nothing else in the repository repeats them.

## Conventions

- Plain Arduino sketches with `setup()` and `loop()`; no PlatformIO project.
- Comments and messages may be in French, the language of the wiki.
- Use the STeaMi library headers (`#include <STeaMi.h>`, ...) for the
  sensors and the displays, and the board pin names (`LED_RED`, `A_BUTTON`,
  `SPEAKER`, ...) for the rest.
- A sketch must compile for the board named by `fqbn` in `versions.json`, with
  the versions listed there; the CI refuses the pull request otherwise.

## Compile locally

Requirements: [arduino-cli](https://arduino.github.io/arduino-cli/) on the
`PATH`, `python3`.

```bash
scripts/compile-examples.sh build/bins
```

The script installs the core and the libraries at the versions of
`versions.json` if needed, compiles every sketch and copies each binary to
`build/bins/<GROUP>/<Name>.bin`. It does not stop at a failure: it names
each failing sketch (`FAIL GROUP/Name`) and exits non-zero at the end if any
of them failed.

To run the checks of the scripts:

```bash
python3 -m pytest scripts/tests -q
```

## Releases

Each merge to `main` is released by
[semantic-release](https://semantic-release.gitbook.io/) from the
[Conventional Commits](https://www.conventionalcommits.org/) messages
(`feat` gives a minor version, `fix` a patch). The release `vX.Y.Z` carries
the asset `steami-exemples-vX.Y.Z.zip`: an `index.json` and one
`<GROUP>/<Name>.bin` per sketch, in the format of the
[arduino-steami-lib](https://github.com/steamicc/arduino-steami-lib) examples
archive. Releases are immutable: the archive is attached to a draft release,
checked, then the release is published.

## License

GPL-3.0, see [LICENSE](LICENSE). Sketches written in the wiki pages are
republished here under the same license.

## Credits

The `BOUTONS/LedsBoutons` and `BUZZER/Melodie` sketches come from the pull
requests #3 and #4 by Aline Dumont.
