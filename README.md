# Notes

A note-taking app where rules file each note for you. Built from
[app-template](https://github.com/Eli-Meyer42/app-template): one `index.html`,
no build step, hosted on GitHub Pages, data in Firebase Realtime Database.

## How it works

- **Capture.** Type or dictate. The text is saved exactly as written.
- **Rules.** When a note is saved, the rules run from the top and the first one
  that matches sets the note's type. No AI is involved.
- **Unsorted.** A note that matches no rule stays Unsorted. That pile is the
  gap AI is meant to bridge later.
- **By hand.** Any note's type can be set by hand, and the rules then leave it alone.
- **Keep-style organising.** Labels, pin, archive, trash and search.

A rule is: *if a note* **starts with** / **contains** some words, **has a
link**, or **is a checklist**, *file it as* a type. A rule can also add a
label or pin the note. Rules, types and labels are all edited inside the app.

## What's here

| File | What it is |
|---|---|
| `index.html` | The whole app. Config at the top, then the rules engine, the interface, and the plumbing. |
| `manifest.webmanifest` | Makes it installable, with **New note** and **Dictate a note** shortcuts. |
| `sw.js` | Service worker. Network-first, so deploys show up immediately. |
| `make-icons.py` | Regenerates the icons. `python3 make-icons.py` |
| `icon-*.png` | App icons. |

## Data

Everything lives in one object, saved locally and mirrored to Firebase at
`notes/main`:

| Key | Holds |
|---|---|
| `notes` | `text`, `type`, `typeBy` (`rule`, `hand` or empty), `rule`, `labels`, `pinned`, `archived`, `trashed`, `created`, `updated`, `src` |
| `types` | `name`, `color`, `pos` |
| `rules` | `cond` (`starts`, `contains`, `link`, `checklist`), `words`, `type`, `label`, `pin`, `on`, `pos` |
| `labels` | `name` |
| `originals` | locked copies of notes: `text`, `labels`, `created`, `at`. Same id as the note, never edited |
| `gone` | ids of notes deleted for good |

The online copy is scrambled. A passphrase, typed once per device, makes a
key (PBKDF2, then AES-GCM) that stays on the device; what goes to Firebase is
`{rev, enc: {salt, iv, ct}}` and cannot be read without it. Nothing syncs
until a passphrase is set. A copy online that the device cannot open is
replaced from the device.

Sync also differs from the template in one way: instead of the newest whole copy
winning, two copies are merged item by item (the newer version of each note,
type, rule and label wins). A note written on one device while another is
offline is therefore never dropped. Deleted types, rules and labels are kept
with `del: true` so the deletion reaches every device.

The draft in the new-note box, the layout choice, the dictation setting and
the activity log stay on the device and are not synced.

## Rules worth keeping

- **Bump the build stamp every push** (`APP.build`). It is the quickest way to
  confirm a deploy landed.
- **Keep every path relative** (`./`) in the manifest and service worker.
  Pages serves the app from `/Notes/`, not `/`.
- **Keep the service worker network-first** for the page, and only let it
  delete caches named `notes-…`. Every app on `eli-meyer42.github.io` shares
  one cache store.
- **Never use `window.storage`.** It only exists inside Claude's preview.
- **Text is verbatim.** Nothing should rewrite a note's text except the person
  editing it or ticking a checklist line.
- The Firebase config is meant to be public. Security comes from the rules.

## Working with Claude

The app and Claude exchange two files in the private repo
`Eli-Meyer42/shopping-logs`, under `notes/share/`:

- `notes.json`: written by the app (**Send notes to Claude**, and again after
  suggestions are handled). A readable copy of every note with its id, text,
  type, labels, flags and `updated` time, plus the rules, types, labels, the
  nothing-lost result (`missingText`) and `decided`.
- `proposals.json`: written by Claude. The app shows each item and applies it
  only on **Yes**. Shape:

```json
{ "id": "r3", "note": "One line shown above the list.",
  "items": [
    { "id": "r3-1", "kind": "combine", "title": "…", "why": "…",
      "sources": ["noteId", "noteId"], "text": "the combined text",
      "type": "To-do", "labels": ["Home"], "seen": { "noteId": 1764000000000 } },
    { "id": "r3-2", "kind": "edit",  "note": "noteId", "text": "new text" },
    { "id": "r3-3", "kind": "file",  "note": "noteId", "type": "Idea", "labels": ["Work"], "pinned": true, "archived": false },
    { "id": "r3-4", "kind": "trash", "note": "noteId" },
    { "id": "r3-5", "kind": "split", "note": "noteId", "parts": ["first", "second"] },
    { "id": "r3-6", "kind": "rule",  "cond": "starts|contains|link|checklist", "words": ["call"], "type": "To-do", "label": "", "pin": false, "first": true },
    { "id": "r3-7", "kind": "type",  "name": "Appointment" },
    { "id": "r3-8", "kind": "label", "name": "Errands" } ] }
```

Any item may carry `"drops": ["a line"]`: lines removed on purpose (a
header, say), which the nothing-lost check then stops counting for those
notes.

Item ids must be unique for ever (prefix them with the round). `seen` is each
note's `updated` from `notes.json`, so the app can warn if a note changed
since. `combine` keeps the first source and moves the others to the trash.
`type` and `labels` are names; missing ones are created. Keep the words of
the notes when combining, so the nothing-lost check stays green.

## AI key

Settings → **AI** holds an Anthropic API key. It lives only in the local storage slot `shop-ai-1`, the same slot the Shopping app uses, so one paste serves both apps. It is not in the code, the synced state, the activity log, or anything sent to GitHub; it leaves the phone only in a request to `api.anthropic.com`. `askAI(prompt, maxTokens)` is the one way to ask. Nothing in Notes uses it yet; any future feature must check `aiKey` and work without one.
