# BotC Scripts Bot

A Reddit bot for [r/BloodOnTheClocktower](https://www.reddit.com/r/BloodOnTheClocktower/) that automatically links scripts from [botcscripts.com](https://botcscripts.com) when mentioned in comments.

## Usage

In any comment, wrap a script name in double square brackets:

```
[[Trouble Brewing]]
[[Bad Moon Rising]]
[[Sects and Violets]]
```

The bot will reply with a link to the best matching script on botcscripts.com.

## Fetch Domains

The following domains are requested for this app:

- `botcscripts.com` - Used to search for Blood on the Clocktower scripts by name and retrieve links to matching scripts

## Development

Requires Node.js 22+.

```bash
npm install
npm run login   # Authenticate with your Reddit account
npm run dev     # Build and start a playtest session
```

## Deployment

```bash
npm run deploy  # Build and upload a new version
```

After deploying, a moderator of r/BloodOnTheClocktower can install the app from the [Developer Portal](https://developers.reddit.com/apps/botcscriptbot).

## Legal

- [Terms and Conditions](TERMS.md)
- [Privacy Policy](PRIVACY.md)
