# Design: Twitch script tracking

**Status:** Proposal. No implementation or Twitch setup is assumed.

## Goal

Show which scripts in the BotC Scripts catalogue are played on participating Twitch channels. Let broadcasters announce the current script from their Twitch Creator Dashboard. Let viewers type `!script` in chat to get the script name and a link.

The statistic is **announced broadcasts**, not total games played, Twitch-wide popularity, or viewer approval. Do not infer plays from titles, tags, chat messages, or viewing time. Viewer notifications, version-specific rankings, and automatic game detection are out of scope.

## 1. Twitch Extension: build this first

1. Register a Twitch Extension. Configure its **Live Config Path** to point to a page such as `live_config.html`. This is the broadcaster's control page in the Creator Dashboard. Use a minimal viewer panel rather than an overlay. Showing the current script and link in the panel is optional for the pilot.
2. On the Live Config page, use `window.Twitch.ext.onAuthorized` from the Twitch Extension Helper. Keep the latest signed token in memory and disable actions until Twitch provides it. Send it as `Authorization: Bearer <token>` on requests to the BotC Scripts backend. Do not store or log the token.
3. Give the broadcaster a one-time opt-in. Explain that announcements contribute to public counts and the site may display a link to their public Twitch channel. Do not require a separate BotC Scripts login or ask for a Twitch username, password, stream key, or access to audio or video.
4. Let the broadcaster search for a catalogue script or use a recent pick. Show the script name and author to help distinguish results, and send the underlying `Script` ID. For the first test, use one fixed test script instead of building search.
5. Provide **Now playing**, **Clear**, and **Undo mistaken announcement**. Only show success after the server accepts the action. Explain failures in the dashboard, including offline status and a temporary Twitch lookup failure.

Use Twitch's Local Test or Hosted Test before submitting for review. In the Extension settings, add the BotC Scripts backend to Twitch's URL-fetching allowlist. On the backend, permit the expected Extension origin and required methods and headers for these routes only. The existing app-wide Cross-Origin Resource Sharing (CORS) settings allow only `GET`; do not open all site routes to cross-origin writes. See [`botc/settings.py`](../botc/settings.py).

## 2. Backend contract

The dashboard tells the backend **which script** and **what action**. The backend determines **which channel** and **which broadcast**.

| Input or lookup | Rule |
|---|---|
| Extension token | Verify the signature and expiry using the server-side Extension secret. Require `role=broadcaster` for broadcaster actions. Take `channel_id` from the verified token, never from a client-supplied ID or username. |
| Channel identity | Use Twitch Helix **Get Users** with the verified ID and the site's app access token. Store the stable Twitch channel ID as the key. Cache and refresh the Twitch `login` and `display_name`. Build the public link as `https://www.twitch.tv/<login>` and use `display_name` as its label. A rename must not split the history. |
| Broadcast identity | Use Twitch Helix **Get Streams** to check if the channel is live and obtain its current stream ID. Refuse announcements when offline. Report Twitch lookup failures as temporary errors, not as offline. |
| Script identity | Use the parent `Script` ID, not the name or `ScriptVersion` ID. All versions contribute to the same script. Reject unknown IDs. See [`scripts/models.py`](../scripts/models.py). |

Keep two kinds of records:

- **Current selection:** at most one script per channel, tied to the Twitch stream ID. Selecting another script replaces the current selection. Clearing it does not erase a play that happened earlier. An unlisted script should clear the current selection rather than leave the old one visible.
- **Countable play:** one record per `(Twitch channel ID, Twitch stream ID, Script ID)`, with the first valid announcement time. Enforce uniqueness in the database, and update the play and current selection together. Repeated clicks, retries, or switching from A to B and back to A must not add another play for A. Undo removes a mistaken play for that broadcast and clears the current selection only if it still points at that play. Use **Clear**, not **Undo**, to end a normal round. If the broadcaster later actually plays the same script, a new announcement can count it again.

When serving the panel or chat command, only return a selection for an opted-in channel's **current live broadcast**. For a small pilot, check Get Streams with a short cache to limit API calls. Do not serve a stale selection if the lookup fails; report temporary unavailability. Twitch EventSub online/offline events can be added later if needed.

## 3. Chat command

The Extension and chat command must read the same current selection. An Extension can post to chat but does not listen for `!script` through the Extension interface.

- **Pilot:** provide a public, read-only endpoint that accepts a Twitch channel ID and returns a short plain-text reply. Configure a participating channel's existing bot to fetch it if the bot supports URL-backed commands. A successful reply looks like `Now playing: Example Script - https://<site>/<script-page>`. With no live selection, return `No script announced for this broadcast.` A chat lookup never records a play.
- **Later, if needed:** run a BotC Scripts chat bot. Subscribe to Twitch EventSub `channel.chat.message`, recognise `!script`, and reply with **Send Chat Message**. This needs separate chat authorization; installing the Extension does not grant it. Add a per-channel cooldown to prevent repeated replies. Do not store viewer chat messages or viewer identities for the leaderboard.

## 4. Public popularity display

Label the leaderboard **Most played on participating Twitch channels - last 30 days**. For each script, count valid play records whose first announcement falls in the rolling 30-day window, and display the number of distinct channels represented. Rank by broadcast count. Example: **12 broadcasts across 5 channels**.

Use the verified Twitch login when showing a channel link. A co-stream on two participating channels can contribute two broadcasts; this is intentional because the design does not identify unique games across channels. A script with no announcements has no measured plays, not necessarily no Twitch plays. Do not combine these counts with favourites or votes.

## Build order and acceptance checks

| Phase | Acceptance checks |
|---|---|
| **1. Twitch identity test** | In Twitch test mode, announce a fixed script ID from a live test channel. Show the resolved channel name and confirm its link opens the correct channel. Reject expired, invalid, and non-broadcaster tokens. Refuse announcements while offline. |
| **2. Streamer pilot** | Add opt-in, script search, recent picks, and correction. Try two scripts on one broadcast: both count once, even after retries or switching back. Clear preserves valid history; undo removes only the mistaken play. Start a new broadcast and confirm the old pick does not reappear. |
| **3. Chat and public stats** | Try `!script` on a pilot channel with a compatible bot. Confirm it follows script switches, never increments the count, and gives a useful response when there is no selection. Verify the rolling window, distinct channel count, and channel links after a rename. |

**Open decisions before public release:** Decide what happens to past announcements and channel attribution after a broadcaster opts out or requests removal; agree on that policy before enrolling participants. Confirm a pilot broadcaster has a compatible chat bot before building a dedicated one. Review the dashboard flow with a pilot broadcaster and the identity checks and public wording with the BotC Scripts maintainer.

## References

- [Twitch Extensions and Live Config](https://dev.twitch.tv/docs/extensions/)
- [Extension Helper and signed token reference](https://dev.twitch.tv/docs/extensions/reference/)
- [Extension testing, review, and release](https://dev.twitch.tv/docs/extensions/life-cycle)
- [Helix Get Users](https://dev.twitch.tv/docs/api/reference/users#get-users) and [Get Streams](https://dev.twitch.tv/docs/api/reference/streams#get-streams)
- [Twitch chat bot: sending and receiving messages](https://dev.twitch.tv/docs/chat/send-receive-messages)
