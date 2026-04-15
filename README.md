# Heroes Rogue
Singleplayer rogue-like mod for Heroes of the Storm.

<img width="1919" height="1080" alt="heroesrogue" src="https://github.com/user-attachments/assets/25dcc8fc-9d86-49cf-ac81-ccc224881242" />


**How to Play:**

1- Go to the Releases section and download the latest version of the mod.

2- Extract the contents of the zip file into your Heroes of the Storm installation path (e.g. C:/Program Files (x86)/Heroes of the Storm). The maps and mods folder should be in the same location as the Heroes of the Storm executable.

3- Start the game, open the menu in the bottom right (cog icon), press Challenges, and then press Play.

**Info:**

- You gain permanent benefits or buffs called boons when reaching level 1, 4, 7, and 10. Choose one of three options or reroll if you do not like what you see.

- Curses are permanent downsides that increases the difficulty of the game. You obtain curses every time the enemy Team reaches a talent tier, as well as at level 24, level 27, and level 30.

- Level 4 and 7 curses are obtained at the start of the game if you did not get them in the previous game.

- Completing a map objective (for example getting 3 tributes on Cursed Hollow) replaces a future curse with a boon, once per game.

- Some Heroes have unique boons, indicated with a golden border. There will be more in the future!

- Game progress is automatically saved after destroying the enemy Core, boons and curses persist every game. You can quit and play at another time, the game will resume from where you left of.

- If your Core gets destroyed, all boons and curses are reset and you have to start over. You can also type 'resetgame' in chat to manually restart the run.


#### Disclaimer:
This is a fan-made project and is not affiliated with or endorsed by Blizzard Entertainment. The mod runs locally and does not interact with Blizzard's servers. All original game assets, characters, and intellectual property belong to Blizzard Entertainment.

## GitHub Pages

The static compendium under `docs/` can be published directly with GitHub Pages.

1. Push this repository, including the `docs/` folder, to GitHub.
2. In GitHub, open `Settings` -> `Pages`.
3. Under `Build and deployment`, set `Source` to `Deploy from a branch`.
4. Set `Branch` to `master` and the folder to `/docs`, then save.

After that, each push to `master` that updates `docs/` will republish the site at:

`https://errorb0t.github.io/heroesrogue/`

## Syncing This Fork

This fork can sync upstream changes from `sobbyellow/heroesrogue`, regenerate the
affix overview under `docs/`, and push the result back to `errorb0t/heroesrogue`.
During generation, any `.dds` files under
`mods/HeroesRogue.StormMod/Base.StormAssets/Assets/Textures` are also exported to
matching `.png` files in `docs/icons`.

### Local one-command sync

Run:

```bash
./scripts/sync_upstream.sh --push
```

The script will:

1. Ensure your worktree is clean.
2. Add or update an `upstream` remote pointing to `https://github.com/sobbyellow/heroesrogue.git`.
3. Fetch and merge `upstream/master` into your current branch.
4. Run `python3 scripts/generate_affix_overview.py`.
5. Commit any `docs/` changes as `Regenerate affix overview`.
6. Push the final result to `origin`.

If you want to review before pushing, omit `--push`.

If the upstream merge conflicts with fork-specific changes, the script stops and
lets you resolve the conflict manually instead of trying to guess.

### GitHub automation

Two GitHub Actions workflows are included:

- `Sync Upstream`: runs on a daily schedule and on manual dispatch. It merges
  `sobbyellow/heroesrogue` into `master`, regenerates `docs/`, and pushes the
  result to your fork.
- `Regenerate Docs`: runs when files under `mods/` or `scripts/` change on
  `master`, so your published `docs/` stays in sync with changes you push to
  the fork.

### GitHub settings to check once

1. In `Settings` -> `Actions` -> `General`, set `Workflow permissions` to
   `Read and write permissions` so workflows can push commits.
2. If `master` is branch-protected, allow GitHub Actions to push to it or use a
   different deployment branch.
3. Keep GitHub Pages configured as `Deploy from a branch`, branch `master`,
   folder `/docs`.
