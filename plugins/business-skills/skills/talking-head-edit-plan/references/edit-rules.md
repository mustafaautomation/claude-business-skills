# Edit rules

The script plans a cut. It does not grade performance, and it does not render a video.

## Filler

A cue is filler when nothing is left after removing these tokens: um, uh, er, ah, hmm, uhh, umm, and the phrases "you know", "i mean", "kind of", "sort of". "Um, you know" is filler. "I think you know the cut" is not, because "i", "think", "the", and "cut" remain. The word "like" is never treated as filler.

Filler cues are listed in `removed` with reason `filler`. They are not shortened. They are gone.

## Dead air

After filler cues are gone, a gap between remaining cues that is longer than `max_pause_ms` (default 800) is tightened. The previous keep is extended by `retained_pause_ms` (default 120) so a breath remains, and the rest of the gap is `dead-air` in `removed`. A shorter gap stays inside one keep, including the silence, so the cut list does not chop natural pauses into jump cuts.

## Timecode

Frame rate is a positive integer. The EDL is non-drop. Milliseconds convert to frames with half-up rounding: `(ms * fps + 500) // 1000`. Out points are exclusive. A keep that ends at frame 94 is written as out `00:00:03:04` at 30 fps, which is the first frame not in the keep.

Record timecodes start at zero and follow the program timeline, not the source clock. Source timecodes stay on the source clock so an editor can find the frames.

## Chapters, cover, warnings

- A cue whose text is `[chapter] Title` becomes a chapter at that cue's program time. The cue is still picture. It is not deleted.
- A keep of 8 seconds or longer gets a b-roll window from 2 seconds in to 1 second before the end. The note is a suggestion to cover the stretch. It is not an automatic overlay.
- A keep under 400 milliseconds raises `short-cut`. Do not hide that warning. A cut that short on a face will read as a jump.

## Ledger

Keeps do not overlap. Dead-air spans sit in the holes between keeps. Program keeps are contiguous from zero. Filler cues may sit partly under a retained breath and partly under dead air. That overlap in the removed list is expected. Do not "correct" it by editing the EDL by hand. Change a threshold and rerun.
