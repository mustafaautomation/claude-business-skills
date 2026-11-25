# Channel rules

Every claim in the pack has to be in the source. Cut a story rather than import one from outside the transcript. The checker does not know whether a sentence is true. You do.

## LinkedIn

- `hook` is 40 to 150 characters. It is the first line, not a headline with a colon stack.
- `body` is 500 to 1800 characters and does not repeat the hook verbatim as its opening.
- 3 to 5 hashtags. Letters and digits only. No `#` in the JSON. No hashtag that the source did not earn.
- Short paragraphs. One concrete moment from the source.

## X thread

- 5 to 9 posts.
- Each post is 1 to 280 characters.
- The first post is the claim. It does not start with a number or `1/`.
- The last post tells a person what to do next and includes one of: follow, reply, newsletter, link, read, watch.
- Do not split a sentence just to hit a count.

## Newsletter

- Exactly three subject lines, each 15 to 70 characters. They are different angles, not three punctuation tweaks.
- Preview text is 40 to 120 characters and can stand alone in an inbox.
- At least two sections. Each has a heading and a body of 40 or more characters.
- This is the place for the teaching. Do not dump the transcript.

## Short video

- `duration_seconds` is an integer from 20 to 45.
- `hook` is required and at most 90 characters.
- At least three beats. Each has `spoken` and `on_screen`. On-screen text matches the spoken line. It does not introduce a new claim.
- Spoken words should land near 150 words per minute. The checker allows eight seconds of slack.
- `cta` is required and is something the viewer can actually do.

## Pack shape

`source_title`, `linkedin`, `x_thread`, `newsletter`, `short_video`. The checker report lists every rule by name. A pack is not done until the report says PASS. Fix the pack. Do not relax a number in the conversation and ship the failure.
