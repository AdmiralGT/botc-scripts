import { Devvit } from '@devvit/public-api';

const MENTION_PATTERN = /\\?\[\\?\[([^\]\\]+)\\?\]\\?\]/g;
const API_BASE = 'https://botcscripts.com/api/scripts';
const SITE_BASE = 'https://botcscripts.com';

Devvit.configure({
  redditAPI: true,
  http: true,
});

Devvit.addTrigger({
  event: 'CommentCreate',
  onEvent: async (event, context) => {
    const body = event.comment?.body ?? '';
    console.log('CommentCreate triggered, body:', body);

    const mentions = [...body.matchAll(MENTION_PATTERN)];
    if (!mentions.length) return;

    const seen = new Set<string>();
    for (const [, rawName] of mentions) {
      const scriptName = rawName.trim();
      if (seen.has(scriptName.toLowerCase())) continue;
      seen.add(scriptName.toLowerCase());

      const response = await fetch(`${API_BASE}?search=${encodeURIComponent(scriptName)}`);
      if (!response.ok) {
        console.log('API request failed for:', scriptName);
        continue;
      }

      const data = await response.json();
      const script = data.results?.[0];
      if (!script) {
        console.log('No results for:', scriptName);
        continue;
      }

      console.log('Replying with script:', script.name);
      const url = `${SITE_BASE}/${script.pk}`;
      const author = script.author ?? 'Unknown';
      await context.reddit.submitComment({
        id: event.comment!.id,
        text: `**[${script.name}](${url})** by ${author}\n\n^(Found via botcscripts.com)`,
      });
      break; // one reply per comment
    }
  },
});

export default Devvit;
